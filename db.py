import psycopg2

def create_database(database_name):
    
    #establishing the connection
    conn = psycopg2.connect(
    database="postgres", user='postgres', password='iwantbefree', host='127.0.0.1', port= '5432'
    )
    conn.autocommit = True

    cur = conn.cursor()

    cur.execute("SELECT datname FROM pg_database;")

    list_database = cur.fetchall()

    if (database_name,) in list_database:
        print("'{}' Database already exist".format(database_name))
    else:
        print("'{}' Database not exist.".format(database_name))
        sql = 'CREATE database {}'.format(database_name)
        #Creating a database
        cur.execute(sql)
        #Closing the connection
        print('Done')
    #Preparing query to create a database