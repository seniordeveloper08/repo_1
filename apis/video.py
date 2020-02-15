# LOAD STANDARD PACKAGE
import os
from flask import Blueprint, jsonify, request
import datetime

# LOAD CUSTOMIZED PACKAGE
from app import db, Camera, Thumbnail, Video

# Load ENV Values
ROOT_PATH = "./share"

# RANDOM Path
RANDOM_PATH = "./share/random/videos"

# RETURN BLUEPRINT FILE


def create_video_blueprint(blueprint_name: str, resource_type: str, resource_prefix: str) -> Blueprint:
    blueprint = Blueprint(blueprint_name, __name__)

    # ============================================================================================
    # desc: ADD RANDOM IMAGES
    # path: /test [GET]
    @blueprint.route(f'/{resource_prefix}/random/<camera_id>', methods=['GET'])
    def create_random(camera_id):
        date = datetime.datetime(2023, 2, 1, 12, 20, 5)
        for i in range(0, 300):
            date += datetime.timedelta(seconds=2)
            video_path = "output{}.ts"
            video_path = video_path.format(i)
            db.session.add(Video(video_path, date, camera_id))
        db.session.commit()
        return "success"
    # ============================================================================================

    # desc: REQUEST FOR HLS PLAY
    # path: /play/<camera_id> [POST]
    @blueprint.route(f'/{resource_prefix}/play/<camera_id>/<start>/<end>', methods=['GET'])
    def play_hls(camera_id, start, end):
        videos = []
        output = '''#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:2
#EXT-X-MEDIA-SEQUENCE:0
'''
        for item in db.session.query(Video).filter(Video.camera_id == camera_id, Video.time >= start, Video.time <= end):
            del item.__dict__['_sa_instance_state']
            output = output+"#EXTINF:2.000000,\n"+item.__dict__["path"]+"\n"
        output += "#EXT-X-ENDLIST"
        f = open("./share/random/videos/output1.m3u8", "w")
        f.write(output)
        f.close()
        return jsonify("/share/random/videos/output1.m3u8")
    return blueprint
