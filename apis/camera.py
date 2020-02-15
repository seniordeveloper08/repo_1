# LOAD STANDARD PACKAGE
import os
from flask import Blueprint, jsonify, request

# LOAD CUSTOMIZED PACKAGE
from app import db, Camera, Thumbnail
from sqlalchemy import or_

# Load ENV Values
ROOT_PATH = "./share"

# RETURN blueprint FILE


def create_camera_blueprint(blueprint_name: str, resource_type: str, resource_prefix: str) -> Blueprint:
    blueprint = Blueprint(blueprint_name, __name__)

    # desc: Get cameras OF THE table
    # path: /cameras [GET]
    @blueprint.route(f'/{resource_prefix}', methods=['GET'])
    def get_items():
        cameras = []
        for item in db.session.query(Camera).all():
            del item.__dict__['_sa_instance_state']
            cameras.append(item.__dict__)
        return jsonify(cameras)

    # desc: USE CAMERA IN LIVE MOD
    # path: /cameras/<id> [GET]
    @blueprint.route(f'/{resource_prefix}/<id>', methods=['GET'])
    def live_mod(id):
        return jsonify({"id": id, "action": "Live MOD"})

    # desc: GET cameras WITH FILTERS
    # path: /cameras/<location>/<name> [GET]
    @blueprint.route(f'/{resource_prefix}/search/<name>', methods=['GET'])
    def search_camera(name):

        # SEARCH WITH NAME AND LOCATION
        cameras = []
        for item in db.session.query(Camera).filter(or_(Camera.name.contains(name), Camera.location.contains(name))):
            del item.__dict__['_sa_instance_state']
            cameras.append(item.__dict__)
        return jsonify(cameras)

    # desc: ADD Camera
    # path: /cameras [POST]
    @blueprint.route(f'/{resource_prefix}', methods=['POST'])
    def create_camera():
        # ADD NEW CAMERA
        body = request.get_json()
        db.session.add(
            Camera(body['name'], body['ipaddress'], body['location'], body["thumbnail"], body["online"]))
        db.session.commit()

        # CREATE NEW SUB ROOT DIR FOR NEW CAMERA
        sub_root = os.path.join(ROOT_PATH, body['ipaddress'])
        os.mkdir(sub_root)

        # CREATE DIR FOR VIDEO STORE
        video_dir = os.path.join(sub_root, "videos")
        os.mkdir(video_dir)

        # CREATE DIR FOR THUMBNAIL STORE
        thumbnail_dir = os.path.join(sub_root, "thumbnails")
        os.mkdir(thumbnail_dir)

        return "NEW CAMERA ADDED"

    return blueprint
