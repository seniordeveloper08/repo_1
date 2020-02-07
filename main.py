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
  ipadress = db.Column(db.String(30), nullable=False)
  location = db.Column(db.String(120), nullable=False)
  thumbnail = db.Column(db.String(200))
  thumbnails = db.relationship("Thumbnail", backref=backref("camera", lazy=True))

  def __init__(self, name, location, thumbnail):
    self.title = name
    self.location = location
    self.thumbnail = thumbnail

# DEFINE SCHEMA Table OF THUMBNAIL LIST
class Thumbnail(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  path = db.Column(db.String(80), nullable=False)
  time = db.Column(db.Date, nullable=False)
  camera_id = db.Column(db.Integer, db.ForeignKey('camera.id'))

  def __init__(self, path, time, camera_id):
    self.path = path
    self.time = time
    self.camera_id = camera_id

# Create & Migrate the TABLE
@app.before_first_request
def init():
    db.create_all()

# desc: Get Items OF THE table
# path: /camera [GET]
@app.route('/camera', methods=['GET'])
def get_items():
  cameras = []
  for item in db.session.query(Camera).all():
    del item.__dict__['_sa_instance_state']
    cameras.append(item.__dict__)
  return jsonify(cameras)

# desc: ADD Camera
# path: /camera [POST]
@app.route('/camera', methods=['POST'])
def create_thumbnail():
  # ADD NEW Thumbnail
  body = request.get_json()
  db.session.add(Camera(body['name'], body['ipadress'], body['location']), "")
  db.session.commit()

  return "Thumbnail created & Camera thumbnail updated"


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

# RUN THE APP IN PORT 5000
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)