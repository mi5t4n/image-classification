import os, uuid, json, subprocess, sys
from flask import (
    Flask, render_template, url_for, redirect,
    request, flash, Response, jsonify
)
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/home/kazekage/websites/image-classification/cnn/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
train_proc = {}
train_done = {}

# Constants for CNN
CMD = "python -m flaskr.scripts.retrain --bottleneck_dir={} --how_many_training_steps=500 --model_dir={} --summaries_dir={} --output_graph={} --output_labels={} --architecture=\"{}\" --image_dir={}"
ARCHITECTURE = os.environ['ARCHITECTURE']
TF_FILES = '/home/kazekage/websites/image-classification/cnn/tf_files/'
SUMMARIES_DIR = TF_FILES + 'training_summaries/' + ARCHITECTURE
MODEL_DIR = TF_FILES + 'models/'
BOTTLENECK_DIR = TF_FILES + 'bottlenecks'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_app(test_config=None):
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

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/')
    def hello():
        return render_template('home.html')
        
    @app.route('/large.csv')
    def generate_large_csv():
        def generate():
            for row in range(0,100000):
                yield str(row) + '\n'
        return Response(generate(), mimetype='text/csv')
    
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

        # output_graph = UPLOAD_FOLDER + '/' + str(uid) + '/retrained_graph.pb'
        # output_labels = UPLOAD_FOLDER + '/' + str(uid) + '/retrained_labels.txt'
        # image_dir = directory
        # cmd = CMD.format(BOTTLENECK_DIR,MODEL_DIR,SUMMARIES_DIR, output_graph, output_labels, ARCHITECTURE, image_dir)
        # print (cmd)

        json_res = {}
        json_res ["uid"] = uid

        return jsonify(json_res)
        
        #Training start
        # train_proc[uid] = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
        # p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
        # def generate():
        #     while True:
        #         out = p.stderr.read(1)
        #         if out == '' and p.poll() != None:
        #             break
        #         if out != '':
        #             out = out.decode("utf-8")
        #             yield out
        #             sys.stdout.write(out)
        #             sys.stdout.flush()
                                        
        # return Response(generate(), mimetype='text/html')


    
    @app.route('/test')
    def test():
        return render_template('test.html')

    @app.route('/trainstatus/<uid>', methods=('GET', 'POST'))
    def process_train(uid):
        dict_res = {}
        try:
            # UID is trained
            uid_done = train_done[uid]
        except KeyError:
            #UID is not trained
            try:
                # UID is already started training process
                p = train_proc[uid]
                out = p.stderr.read(35)
                out = out.decode("utf-8")
                dict_res["data"] = out
                dict_res[ "uid"] = uid
                if out == '' and p.poll() != None:
                    p.kill()
                    del (train_proc[uid])
                    train_done[uid]=uid
                    dict_res["complete"] = True

                if out != '':
                    dict_res["complete"] = False
                    sys.stdout.write(out)
                    sys.stdout.flush()
                return Response(jsonify(dict_res), mimetype="text/json")

            except KeyError:
                # UID has not started training process
                # So start the process
                output_graph = UPLOAD_FOLDER + '/' + uid + '/retrained_graph.pb'
                output_labels = UPLOAD_FOLDER + '/' + uid + '/retrained_labels.txt'
                image_dir = UPLOAD_FOLDER + '/' + uid + '/datasets' 
                cmd = CMD.format(BOTTLENECK_DIR,MODEL_DIR,SUMMARIES_DIR, output_graph, output_labels, ARCHITECTURE, image_dir)
                print (cmd)
                train_proc[uid] = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
                p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
                                        
        return Response(generate(), mimetype='text/html')

    return app