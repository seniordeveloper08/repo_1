import os, gi, time, sys
gi.require_version("Gst", "1.0")
from gi.repository import GObject, Gst
from sources import RTSPH264Source
from utils import must_link
from converter import H264Decode
from sink import HLSAPPSINK
from jpegenc import JpegSink
import threading
import requests
from datetime import datetime

from db import run_query, select_query
import time

Gst.init(None)
GObject.threads_init()

def CCTV_VOD_THUMBNAIL(camera_id, rtsp_url):

    pipeline = Gst.Pipeline()
    bus = pipeline.get_bus()

    # TEST : "rtsp://83.229.5.36:1935/vod/sample.mp4"
    rtsp_uri = rtsp_url
    # Video elements.

    src = RTSPH264Source(rtsp_uri)   #### de soruce to video using H264
    pipeline.add(src)


    decoder = H264Decode()
    pipeline.add(decoder)

    recording_sink = HLSAPPSINK().genObj(
        location=camera_id
    )
    pipeline.add(recording_sink)

    jpeg_sink = JpegSink().genObj(
        location=camera_id
    )
    pipeline.add(jpeg_sink)


    videotee = Gst.ElementFactory.make("tee", "tee")
    pipeline.add(videotee)

    recording_queue = Gst.ElementFactory.make("queue", "recordqueue")
    pipeline.add(recording_queue)


    teepad_recording = videotee.get_request_pad('src_%u')
    recording_pad = recording_queue.get_static_pad('sink')


    jpeg_queue = Gst.ElementFactory.make("queue", "jpeg_queue")
    pipeline.add(jpeg_queue)


    teepad_osd =  videotee.get_request_pad('src_%u')
    jpeg_pad = jpeg_queue.get_static_pad('sink')

    try:
        must_link(src.link(decoder))
        # must_link(decoder.link(recording_sink))
        # must_link(decoder.link(osd_sink))

        must_link(decoder.link(videotee))
        must_link(teepad_recording.link(recording_pad))
        must_link(recording_queue.link(recording_sink))
        must_link(teepad_osd.link(jpeg_pad))
        must_link(jpeg_queue.link(jpeg_sink))
    except RuntimeError as err:
        raise RuntimeError('Could not link source') from err


    # Start pipeline.
    pipeline.set_state(Gst.State.PLAYING)

    while True:
        try:
            message = bus.timed_pop(Gst.SECOND)
            if message == None:
                pass
            elif message.type == Gst.MessageType.EOS:
                query = "UPDATE camera SET online = 'NO' where id = {}".format(camera_id)
                run_query(query)
                while(True):
                    r = requests.post("http://localhost:5000/api/thumbnails", json={
                            "path" : "/gray/gray.jpg",
                            "time" : datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "camera_id" : camera_id
                        })
                    r = requests.post("http://localhost:5000/api/videos", json={
                            "path" : "/gray/gray.ts",
                            "time" : datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "camera_id" : camera_id
                        })
                    print("/gray/gray.jpg")
                    query = "SELECT * FROM camera WHERE id = {}".format(camera_id)
                    list = select_query(query)
                    if list[0][5] == "YES":
                        break
                    time.sleep(2)
                print("END")
                break
            elif message.type == Gst.MessageType.ERROR:
                query = "UPDATE camera SET online = 'NO' where id = {}".format(camera_id)
                run_query(query)
                error, debug = message.parse_error()
                print("ERROR")
                print(error, debug)
                break
        except KeyboardInterrupt:
            break

    pipeline.set_state(Gst.State.NULL)