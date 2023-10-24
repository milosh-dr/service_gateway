# Timestamp 4:19:18

import os, gridfs, pika, json
from flask import Flask, request, send_file
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from auth import validate
from auth_svc import access
from storage import util

server = Flask(__name__)

mongo_video = PyMongo(server, uri='mongodb://localhost:27017/videos')
mongo_mp3 = PyMongo(server, uri='mongodb://localhost:27017/mp3s')

fs_videos= gridfs.GridFS(mongo_video.db)
fs_mp3s = gridfs.GridFS(mongo_mp3.db)

# Change the host if run in the cluster
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

@server.route('/login', methods=['POST'])
def login():
    token, err = access.login(request)
    if not err:
        return token
    else:
        return err
    
@server.route('/upload', methods=['POST'])
def upload():
    access, err = validate.token(request)
    if err:
        return err

    access = json.loads(access)
    
    if access['admin']:
        if len(request.files) != 1:
            return "Upload only one file", 400
        
        for _, file in request.files.items():
            err = util.upload(file, fs_videos, channel, access)
            if err:
                return err
        
        return "Success", 200
    else:
        return "Not authorized", 401
    
@server.route('/download', methods=['GET'])
def download():
    access, err = validate.token(request)
    if err:
        return err

    access = json.loads(access)

    if access['admin']:
        fid_string = request.args.get('fid')
        if not fid_string:
            return "Fid is required", 400
        try:
            out = fs_mp3s.get(ObjectId(fid_string))
            return send_file(out, download_name=f'{fid_string}.mp3')
        except Exception as err:
            print(err)
            return 'Internal server error', 500

    return "Not authorized", 401

if __name__ == '__main__':
    server.run(host='0.0.0.0', port=8080)