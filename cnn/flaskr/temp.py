t@socketio.on('train')
    def handle_train(json_res):
        global train_done, train_proc
        print (json_res)
        uid = json_res['uid']
        # uid_key = uid.encode("utf-8")
        # uid_key = hashlib.sha1(uid_key).hexdigest()
        
        if uid in train_done:
            print ("{} is already trained.".format(uid))
            json_res = {}
            json_res ["uid"] = uid
            json_res ["complete"] = "true"
            json_res ["data"] = "Already trained"
            json_res = json.dumps(json_res, ensure_ascii=False)
            emit("trainstatus",json_res, json=True)
        else:
            print ("{} is not trained".format(uid))
            if not uid in train_proc:
                print ("{} training starts.".format(uid))
                json_res = {}
                json_res ["uid"] = uid
                json_res["complete"] = "false"
                json_res["data"] = "Training starts"
                json_res = json.dumps(json_res, ensure_ascii=False)
                emit("trainstatus",json_res, json=True)
            
                output_graph = UPLOAD_FOLDER + '/' + uid + '/retrained_graph.pb'
                output_labels = UPLOAD_FOLDER + '/' + uid + '/retrained_labels.txt'
                image_dir = UPLOAD_FOLDER + '/' + uid + '/datasets' 
                cmd = CMD.format(BOTTLENECK_DIR,MODEL_DIR,SUMMARIES_DIR, output_graph, output_labels, ARCHITECTURE, image_dir)
                print (cmd)
                train_proc[uid] = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)

        if uid in train_proc:
            p = train_proc[uid]
            json_res = {}
            json_res["complete"] = "false"
            json_res ["uid"] = uid
            out = p.stderr.read(25)
            out_utf = out.decode("utf-8")
            if out == '' and p.poll() != None:
                p.kill()
                train_done[uid]= uid
                del (train_proc[uid])
            if out != '':
                sys.stdout.write(out_utf)
                sys.stdout.flush()
            json_res["data"] = str(out_utf)
            json_res = json.dumps(json_res, ensure_ascii=False)
            emit('trainstatus',json_res, json=True)
 
