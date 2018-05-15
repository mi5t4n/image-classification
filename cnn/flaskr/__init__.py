import os, uuid, json, subprocess, sys, hashlib
from flask import (
    Flask, render_template, url_for, redirect,
    request, flash, Response, jsonify
)
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, send, emit

UPLOAD_FOLDER = '/home/kazekage/websites/image-classification/cnn/uploads'
TEST_FOLDER = '/home/kazekage/websites/image-classification/cnn/uploads/test'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
train_done = {}
socketio = None

# Constants for CNN
CMD_TEST = "python -m flaskr.scripts.label_image --graph={} --labels={} --image={}"
CMD_TRAIN = "python -m flaskr.scripts.retrain --bottleneck_dir={} --how_many_training_steps=500 --model_dir={} --summaries_dir={} --output_graph={} --output_labels={} --architecture=\"{}\" --image_dir={}"
ARCHITECTURE = os.environ['ARCHITECTURE']
TF_FILES = '/home/kazekage/websites/image-classification/cnn/tf_files/'
SUMMARIES_DIR = TF_FILES + 'training_summaries/' + ARCHITECTURE
MODEL_DIR = TF_FILES + 'models/'
BOTTLENECK_DIR = TF_FILES + 'bottlenecks'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_app(test_config=None):
    global socketio
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    socketio = SocketIO(app)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/')
    def hello():
        return render_template('home.html')
    
    @app.route('/train', methods=('GET','POST'))
    def train():
        directory = ''
        uid = uuid.uuid4()
        if request.method == 'GET':
            return render_template('train.html')
        elif request.method == 'POST':
            # print (request.form.getlist('label[]'))
            # print (request.files.getlist('sagar'))

            # Creating a random directory to hold the images
            directory = UPLOAD_FOLDER + '/' + str(uid) + '/datasets' 
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            # Creating directories for labels and saving images
            labels = request.form.getlist('label[]')
            for label in labels:
                label_dir = directory + '/' + label
                if not os.path.exists(label_dir):
                    os.makedirs(label_dir)
                # Saving images to the label directory
                files = request.files.getlist(label)
                for file in files:
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename) 
                        # print (filename)
                        file.save(os.path.join(label_dir, filename))

        json_res = {}
        json_res ["uid"] = str(uid)
        json_res = json.dumps(json_res, ensure_ascii=False)
        return Response(json_res, mimetype="application/json")

               
    @app.route('/test', methods=('GET', 'POST'))
    def test():
        if request.method == 'GET':
            return render_template('test.html')
        elif request.method == 'POST':
            uid = request.form['uid']
            test_image = request.files['image']

            print (uid)
            print (test_image)

            # Creating test folder
            if not os.path.exists(TEST_FOLDER):
                os.makedirs(TEST_FOLDER)
            
            if test_image and allowed_file(test_image.filename): 
                filename = secure_filename(test_image.filename)
                ext = filename.split(".")[-1]
                test_img_filename = "{}.{}".format(uuid.uuid4(),ext)
                #print (test_img_filename)
                test_image_location = os.path.join(TEST_FOLDER,test_img_filename)
                train_graph = os.path.join(UPLOAD_FOLDER, uid, "retrained_graph.pb")
                train_labels = os.path.join(UPLOAD_FOLDER, uid, "retrained_labels.txt")
                #print (train_graph)
                #print (test_image_location)
                test_image.save(test_image_location)
                cmd = CMD_TEST.format(train_graph, train_labels, test_image_location)
                print (cmd)

                p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                (output, err) = p.communicate()

                p_status = p.wait()

                print ("Command output : {}".format(output))
                print ("Command exit status/return code : {}".format(p_status))

                if (p_status == 1):
                    flash("Not trained or could not found the data")
                else :
                    output = output.decode("utf-8")
                    output = output.split("\n")[3:][:-1]
                    result = ""
                    for out in output:
                        temp = out.split(" ");
                        lbl = temp[0]
                        percent = round(float(temp[1])*100.0,2)
                        result = result + lbl + " = " + str(percent) + "% \n"

                    #output = output[-2]
                    print (result)
                    flash(result)
                return render_template("test.html")
            
        

    # @app.route('/trainstatus/<uid>', methods=('GET', 'POST'))
    @socketio.on('connect')
    def handle_connect():
        print ("Websocket connected")

    @socketio.on('train')
    def handle_train(json_res):
        global train_done
        print (json_res)
        uid = json_res['uid']
       
        output_graph = UPLOAD_FOLDER + '/' + uid + '/retrained_graph.pb'
        output_labels = UPLOAD_FOLDER + '/' + uid + '/retrained_labels.txt'
        image_dir = UPLOAD_FOLDER + '/' + uid + '/datasets' 
        cmd = CMD_TRAIN.format(BOTTLENECK_DIR,MODEL_DIR,SUMMARIES_DIR, output_graph, output_labels, ARCHITECTURE, image_dir)
        print (cmd)

        if not uid in train_done:
            p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)

            while True:
                out = p.stderr.read(1)
                out_utf = out.decode("utf-8")
                if p.poll() != None:
                    train_done[uid]= uid
                    break
                if out != '':
                    sys.stdout.write(out_utf)
                    sys.stdout.flush()
        json_res = {}
        json_res["uid"] = uid
        json_res["complete"] = "true"
        print (json_res)
        json_res = json.dumps(json_res, ensure_ascii=False)
        emit('trainstatus',json_res, json=True)
 

    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app)