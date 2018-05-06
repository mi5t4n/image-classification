import os, uuid, json, subprocess, sys
from flask import (
    Flask, render_template, url_for, redirect,
    request, flash, Response, jsonify
)
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/home/kazekage/websites/image-classification/cnn/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
train_proc = {}

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
        uid = uuid.uuid4()
        if request.method == 'GET':
            return render_template('train.html')
        elif request.method == 'POST':
            print (request.form.getlist('label[]'))
            print (request.files.getlist('sagar'))

            # Creating a random directory to hold the images
            directory = UPLOAD_FOLDER + '/' + str(uid) + '/datasets' 
            if not os.path.exists(directory):
                os.makedirs(directory)
                
            tf_files = UPLOAD_FOLDER + '/' + str(uid) + '/tf_files'
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
                        print (filename)
                        file.save(os.path.join(label_dir, filename))

        train_proc[uid] = subprocess.Popen(cmd)

    
    @app.route('/test')
    def test():
        return render_template('test.html')

    @app.route('/trainstatus/<uid>', methods=('GET', 'POST'))
    def process_train(uid):
        print (uid)
        train_proc[uid] = uid
        return json.dumps(train_proc, ensure_ascii=False)

    return app