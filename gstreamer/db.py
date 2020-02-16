import psycopg2

conn = psycopg2.connect(
    database="db_products", user='postgres', password='postgres', host='127.0.0.1', port= '5432'
    )

conn.autocommit = True

cur = conn.cursor()

# cur.execute("DELETE FROM camera;")

def run_query(sql):
    cur.execute(sql)

def select_query(sql):
    cur.execute(sql)
    result = cur.fetchall()
    return result