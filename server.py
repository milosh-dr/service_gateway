import os, gridfs, pika, json
from flask import Flask, request
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util

server = Flask(__name__)
server.config['MONGO_URI'] = 'http://localhost:27017/videos'

mongo = PyMongo(server)

fs = gridfs.GridFS(mongo.db)

connection = pika.BlockingConnection(pika.ConnectionParameters('rabitmq'))
channel = connection.channel()

@server.route('/login', methods=['POST'])
def login():
    token, err = access.login(request)
    # timestamp 1:58:45
    if not err:
        return token
    else:
        return err
    
@server.route('/upload', methods=['POST'])
def upload():
    access, err = validate.token(request)

    access = json.loads(access)
    
    if access['admin']:
        if len(request.files) != 1:
            return "Upload only one file", 400
        
        for _, file in request.files.items():
            err = util.upload(file, fs, channel, access)
            if err:
                return err
        
        return "Success", 200
    else:
        return "Not authorized", 401
    
@server.route('/download', methods=['GET'])
def download():
    pass

if __name__ == '__main__':
    server.run(host='0.0.0.0', port=8080)