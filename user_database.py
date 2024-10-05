import sqlite3
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler



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

app = Flask(__name__)
scheduler = BackgroundScheduler()

# MAIN:
# create_sqlite_database('user_notifications.db')
# create_table('user_notifications.db')


# Form submit: add new notification to branch
def add_to_database():
    with sqlite3.connect('user_notifications.db') as conn:

        # parse information from json
        # fix datetimes
        name = "Ayoung"
        email = "pvgandhi@uwaterloo.ca"
        notify_by = "2024-10-05 05:53:25"
        flyover_on = "2025-04-15 12:55:26"
        location = "Paris, Country"

        notification = (name, email, notify_by, flyover_on, location)
        notif_id = add_notification(conn, notification)

        return

def check_notifications():
    

# def send_notification(notification):
    
#     with sqlite3.connect('user_notifications.db') as conn:
#         cur = conn.cursor()

#         # script = """ SELECT * FROM notifications WHERE DATE(notify_date) = date('now'); """
#         script = """ SELECT * FROM notifications """
#         # script = """SELECT date('now')"""

#         cur.execute(script)
#         rows = cur.fetchall()

#         for row in rows:
#             print(row)


# Schedule the notification check every minute
scheduler.add_job(check_notifications, 'interval', minutes=1)
scheduler.start()

@app.route('/')
def index():
    return "Notification Service is Running!"

if __name__ == '__main__':
    try:
        app.run(port=5000)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()



