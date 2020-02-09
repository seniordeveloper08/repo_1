# LOAD STANDARD PACKAGE
import os
from flask import Blueprint, jsonify, request
import datetime

# LOAD CUSTOMIZED PACKAGE
from app import db, Camera, Thumbnail

# Load ENV Values
ROOT_PATH = "./thumbnails"

# RANDOM Path
RANDOM_PATH = "./thumbnails/random"

# RETURN blueprint FILE


def create_thumbnail_blueprint(blueprint_name: str, resource_type: str, resource_prefix: str) -> Blueprint:
    blueprint = Blueprint(blueprint_name, __name__)

    # ============================================================================================
    # desc: ADD RANDOM images
    # path: /test [GET]
    @blueprint.route(f'/{resource_prefix}/random/<camera_id>', methods=['GET'])
    def create_random(camera_id):
        date = datetime.datetime(2022, 8, 1, 12, 20, 5)
        for i in range(0, 300):
            date += datetime.timedelta(seconds=2)
            imgpath = "/thumbnails/random/{}.jpg"
            imgpath = imgpath.format(i)
            db.session.add(Thumbnail(imgpath, date, camera_id))
        db.session.commit()
        return "success"

    # desc: ADD NEW Thumbnail IN THE table & UPDATE the CAMERA THUMBNAIL
    # path: /thumbnail [POST]
    @blueprint.route(f'/{resource_prefix}', methods=['POST'])
    def create_thumbnail():
        # ADD NEW Thumbnail
        body = request.get_json()
        db.session.add(
            Thumbnail(body['path'], body['time'], body['camera_id']))
        db.session.commit()

        # UPDATE THUMBNAIL of CAMERA
        db.session.query(Camera).filter_by(id=body['camera_id']).update(
            dict(thumbnail=body['path']))
        db.session.commit()

        return "Thumbnail created & Camera thumbnail updated"

    # desc: View VIDEO IN VOD MOD
    # path: /thumbnail/<id> [GET]
    @blueprint.route(f'/{resource_prefix}/<id>', methods=['GET'])
    def vod_mod(id):
        return jsonify({"id": id, "action": "VOD MOD"})

    # desc: GET Thumbnails WITH FILTERS
    # path: /thumbnail/<camera_id>/<start>/<end>/<duration> [GET]
    @blueprint.route(f'/{resource_prefix}/<camera_id>/<start>/<end>/<duration>', methods=['GET'])
    def search_thumbnail(camera_id, start, end, duration):
        thumbnails = []
        for item in db.session.query(Thumbnail).filter(Thumbnail.camera_id == camera_id, Thumbnail.time >= start, Thumbnail.time <= end):
            del item.__dict__['_sa_instance_state']
            thumbnails.append(item.__dict__)
        return jsonify(thumbnails)

    return blueprint
