# LOAD STANDARD PACKAGE
import os
from flask import Blueprint, jsonify, request
import datetime
from dotenv import load_dotenv

# LOAD CUSTOMIZED PACKAGE
from app import db, Camera, Thumbnail

# Load ENV Values
load_dotenv()
ROOT_PATH = os.getenv("ROOT_PATH")

# RANDOM Path
RANDOM_PATH = os.getenv("RANDOM_PATH")

# RETURN BLUEPRINT FILE


def create_thumbnail_blueprint(blueprint_name: str, resource_type: str, resource_prefix: str) -> Blueprint:
    blueprint = Blueprint(blueprint_name, __name__)

    # ============================================================================================
    # desc: ADD RANDOM IMAGES
    # path: /test [GET]
    @blueprint.route(f'/{resource_prefix}/random/<camera_id>', methods=['GET'])
    def create_random(camera_id):
        date = datetime.datetime(2023, 2, 1, 12, 20, 5)
        for i in range(0, 300):
            date += datetime.timedelta(seconds=2)
            imgpath = "/share/random/thumbnails/{}.jpg"
            imgpath = imgpath.format(i)
            db.session.add(Thumbnail(imgpath, date, camera_id))
        db.session.commit()
        return "success"

    # desc: ADD NEW THUMBNAIL IN THE TABLE & UPDATE THE CAMERA THUMBNAIL
    # path: /thumbnail [POST]
    @blueprint.route(f'/{resource_prefix}', methods=['POST'])
    def create_thumbnail():
        # ADD NEW THUMBNAIL
        body = request.get_json()
        db.session.add(
            Thumbnail(body['path'], body['time'], body['camera_id']))
        db.session.commit()

        # UPDATE THUMBNAIL OF CAMERA
        db.session.query(Camera).filter_by(id=body['camera_id']).update(
            dict(thumbnail=body['path']))
        db.session.commit()

        return "Thumbnail created & Camera thumbnail updated"

    # desc: View VIDEO IN VOD MOD
    # path: /thumbnail/<id> [GET]
    @blueprint.route(f'/{resource_prefix}/<id>', methods=['GET'])
    def vod_mod(id):
        return jsonify({"id": id, "action": "VOD MOD"})

    # desc: GET THUMBNAILS WITH FILTERS
    # path: /thumbnail/<camera_id>/<start>/<end>/<duration> [GET]
    @blueprint.route(f'/{resource_prefix}/<camera_id>/<start>/<end>/<duration>', methods=['GET'])
    def search_thumbnail(camera_id, start, end, duration):
        thumbnails = []
        for item in db.session.query(Thumbnail).filter(Thumbnail.camera_id == camera_id, Thumbnail.time >= start, Thumbnail.time <= end).order_by(Thumbnail.id):
            del item.__dict__['_sa_instance_state']
            thumbnails.append(item.__dict__)
        return jsonify(thumbnails)

    return blueprint
