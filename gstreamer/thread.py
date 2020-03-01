import threading
import time
from gstreamer import CCTV_VOD_THUMBNAIL
from db import run_query, select_query
import psycopg2
from datetime import datetime

def thread_camera(id, url):
    sql = "SELECT * FROM camera WHERE id = {};".format(id)
    while (True):
        result = select_query(sql)
        online = result[0][5]

        if online == "NO":
            query = "UPDATE camera SET online = 'YES' where id = {}".format(id)
            run_query(query)

            time.sleep(2.1)

            start_video = datetime.utcnow()
            start_thumbnail = datetime.utcnow()

            result1 = select_query("SELECT * FROM video WHERE camera_id={};".format(id))
            result2 = select_query("SELECT * FROM thumbnail WHERE camera_id={};".format(id))
            if len(result1) > 0:
                start_video = result1[0][2]
            if len(result2) > 0:
                start_thumbnail = result2[0][2]
            print(id, url, start_video, start_thumbnail)
            threading.Thread(target=CCTV_VOD_THUMBNAIL, args=(id, url, start_video, start_thumbnail)).start()

        time.sleep(4)