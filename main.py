# LOAD STANDARD PACKAGE
import os
from flask import request, jsonify
from db import create_database
# LOAD CUSTOMIZED PACKAGE
from app import app, db

# LOAD BLUEPRINT FILES FOR ROUTING
from apis.camera import create_camera_blueprint
from apis.thumbnail import create_thumbnail_blueprint
from apis.video import create_video_blueprint

# LOAD ENV VARIABLE
HOST = os.getenv("HOST")
DB_NAME = os.getenv("DB_NAME")

create_database(DB_NAME)

# CREATE & MIGRATE THE TABLE
@app.before_first_request
def init():
    db.create_all()

# REGISTER APIS FOR CAMERA
app.register_blueprint(create_camera_blueprint(
    blueprint_name="CameraBlueprint", resource_type="Camera", resource_prefix="cameras"), url_prefix="/api")

# REGISTER APIS FOR CAMERA
app.register_blueprint(create_thumbnail_blueprint(
    blueprint_name="ThumbnailBlueprint", resource_type="Thumbnail", resource_prefix="thumbnails"), url_prefix="/api")

# REGISTER APIS FOR VIDEOS
app.register_blueprint(create_video_blueprint(
    blueprint_name="VideoBlueprint", resource_type="Video", resource_prefix="videos"), url_prefix="/api")

# RUN THE APP IN PORT 5000
if __name__ == "__main__":
    app.run(host=HOST, port=5000, debug=True)
