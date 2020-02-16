import threading
import time
from gstreamer import CCTV_VOD_THUMBNAIL
from db import run_query, select_query
import psycopg2

thread_list = []

# cur.execute("DELETE FROM camera;")

while(True):
    list = select_query("SELECT * FROM camera;")
    for item in list:
        if (item[0] not in thread_list):
            query = "UPDATE camera SET online = 'YES' where id = {}".format(item[0]);
            run_query(query)
            thread_list.append(item[0])
            threading.Thread(target=CCTV_VOD_THUMBNAIL, args=(item[0],)).start()
        if (item[5] == "NO"):
            thread_list.remove(item[0])
    print(thread_list)
    time.sleep(5)