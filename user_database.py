import sqlite3

def create_sqlite_database(filename):
    """ create a database connection to an SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(filename)
        print(sqlite3.sqlite_version)
        
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()\
            
def create_table(db):
    script = """CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY, 
        name text NOT NULL, 
        email text NOT NULL,
        notify_date DATETIME,
        flyover_date DATETIME,
        location TEXT
        );"""
    
    with sqlite3.connect(db) as conn:
            cursor = conn.cursor()
            cursor.execute(script)
            conn.commit()


def add_notification(conn, notification):
    sql = ''' INSERT INTO notifications(name,email,notify_date,flyover_date,location)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, notification)
    conn.commit()
    return cur.lastrowid

def remove_notification(conn, id):
    cur = conn.cursor()
    delete_stmt = 'DELETE FROM notifications WHERE id = ?'
    cur.execute(delete_stmt, (id,))
    conn.commit()


# MAIN:
# create_sqlite_database('user_notifications.db')
# create_table('user_notifications.db')

with sqlite3.connect('user_notifications.db') as conn:
    # notification = ("Ayoung", "test@example.com", "10/6/2024 11:53:25", "05/15/2025 12:55:26", "Paris, Country")
    # notif_id = add_notification(conn, notification)

    cur = conn.cursor()

    script = """ SELECT * FROM notifications """

    # script = """ SELECT * FROM notifications WHERE notify_date >= datetime('now'); """
    # script = """SELECT date('now')"""

    cur.execute(script)
    rows = cur.fetchall()

    for row in rows:
        print(row)




