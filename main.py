from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from dotenv import load_dotenv
import os

# LOAD ENV VALUES
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URI")
ROOT_PATH = os.getenv("ROOT_PATH")

# Create APP Instance
app = Flask(__name__)

# SET DATABASE URI in CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

db = SQLAlchemy(app)

# DEFINE SCHEMA Table OF CAMER LIST
class Camera(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), nullable=False)
  ipaddress = db.Column(db.String(30), nullable=False)
  location = db.Column(db.String(120), nullable=False)
  thumbnail = db.Column(db.String(200))
  thumbnails = db.relationship("Thumbnail", backref=backref("camera", lazy=True))

  def __init__(self, name, ipaddress, location, thumbnail):
    self.name = name
    self.ipaddress = ipaddress
    self.location = location
    self.thumbnail = thumbnail

# DEFINE SCHEMA Table OF THUMBNAIL LIST
class Thumbnail(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  path = db.Column(db.String(80), nullable=False)
  time = db.Column(db.DateTime, nullable=False)
  camera_id = db.Column(db.Integer, db.ForeignKey('camera.id'))

  def __init__(self, path, time, camera_id):
    self.path = path
    self.time = time
    self.camera_id = camera_id

# Create & Migrate the TABLE
@app.before_first_request
def init():
    db.create_all()

# desc: Get cameras OF THE table
# path: /camera [GET]
@app.route('/camera', methods=['GET'])
def get_items():
  cameras = []
  for item in db.session.query(Camera).all():
    del item.__dict__['_sa_instance_state']
    cameras.append(item.__dict__)
  return jsonify(cameras)

# desc: USE CAMERA IN LIVE MOD
# path: /camera/<id> [GET]
@app.route('/camera/<id>', methods=['GET'])
def live_mod(id):
  return jsonify({"id": id, "action" : "Live MOD"})

# desc: GET cameras WITH FILTERS 
# path: /camera/<location>/<name> [GET]
@app.route('/camera/<location>/<name>', methods=['GET'])
def search_camera(location, name):

  # SEARCH WITH NAME AND LOCATION
  cameras = []
  for item in db.session.query(Camera).filter(Camera.name.contains(name), location==location):
    del item.__dict__['_sa_instance_state']
    cameras.append(item.__dict__)
  return jsonify(cameras)

# desc: ADD Camera
# path: /camera [POST]
@app.route('/camera', methods=['POST'])
def create_camera():
  # ADD NEW CAMERA
  body = request.get_json()
  db.session.add(Camera(body['name'], body['ipaddress'], body['location'], body["thumbnail"]))
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


# desc: ADD NEW Thumbnail IN THE table & UPDATE the CAMERA THUMBNAIL
# path: /thumbnail [POST]
@app.route('/thumbnail', methods=['POST'])
def create_thumbnail():
  # ADD NEW Thumbnail
  body = request.get_json()
  db.session.add(Thumbnail(body['path'], body['time'], body['camera_id']))
  db.session.commit()

  # UPDATE THUMBNAIL of CAMERA
  db.session.query(Camera).filter_by(id=body['camera_id']).update(
    dict(thumbnail=body['path']))
  db.session.commit()

  return "Thumbnail created & Camera thumbnail updated"

# desc: View VIDEO IN VOD MOD
# path: /thumbnail/<id> [GET]
@app.route('/thumbnail/<id>', methods=['GET'])
def vod_mod(id):
  return jsonify({"id": id, "action" : "VOD MOD"})

# desc: GET Thumbnails WITH FILTERS 
# path: /thumbnail/<camera_id>/<start>/<end>/<duration> [GET]
@app.route('/thumbnail/<camera_id>/<start>/<end>/<duration>', methods=['GET'])
def search_thumbnail(camera_id, start, end, duration):
  thumbnails = []
  for item in db.session.query(Thumbnail).filter(camera_id == camera_id, Thumbnail.time >= start, Thumbnail.time <= end):
    del item.__dict__['_sa_instance_state']
    thumbnails.append(item.__dict__)
  return jsonify(thumbnails)

# RUN THE APP IN PORT 5000
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)