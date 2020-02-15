import threading
import time
from gstreamer import CCTV_VOD_THUMBNAIL
import psycopg2

conn = psycopg2.connect(
    database="db_products", user='postgres', password='postgres', host='127.0.0.1', port= '5432'
    )

thread_list = []

conn.autocommit = True

cur = conn.cursor()

# cur.execute("DELETE FROM camera;")

while(True):
    cur.execute("SELECT * FROM camera;")
    list = cur.fetchall()
    for item in list:
        if (item[0] not in thread_list):
            thread_list.append(item[0])
            threading.Thread(target=CCTV_VOD_THUMBNAIL, args=(item[0],)).start()
    print(thread_list)
    time.sleep(5)