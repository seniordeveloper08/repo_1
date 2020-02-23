import threading
import time
from gstreamer import CCTV_VOD_THUMBNAIL
from db import run_query, select_query
import psycopg2
from datetime import datetime

thread_list = []

# cur.execute("DELETE FROM camera;")

while(True):
    list = select_query("SELECT * FROM camera;")
    for item in list:
        if (item[0] in thread_list and item[5] == "NO"):
            thread_list.remove(item[0])
        if (item[0] not in thread_list):
            query = "UPDATE camera SET online = 'YES' where id = {}".format(item[0])
            run_query(query)

            time.sleep(2)

            start_video = datetime.utcnow()
            start_thumbnail = datetime.utcnow()
            
            result1 = select_query("SELECT * FROM video WHERE camera_id={};".format(item[0]))
            result2 = select_query("SELECT * FROM thumbnail WHERE camera_id={};".format(item[0]))
            if len(result1) > 0:
                start_video = result1[0][2]
            if len(result2) > 0:
                start_thumbnail = result2[0][2]
            thread_list.append(item[0])
            print(len(thread_list))
            threading.Thread(target=CCTV_VOD_THUMBNAIL, args=(item[0], item[2], start_video, start_thumbnail)).start()
    print(thread_list)
    time.sleep(4)