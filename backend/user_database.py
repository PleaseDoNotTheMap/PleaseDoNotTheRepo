import sqlite3
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from send_notification import send_email, send_SMS

def print_database_contents():
    script = """SELECT * FROM notifications WHERE DATE(notify_date) = date('now')"""
    
    with sqlite3.connect('user_notifications.db') as conn:
        cur = conn.cursor()
        cur.execute(script)

        rows = cur.fetchall()

        for row in rows:
            print(row)

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
        email TEXT,
        phone number TEXT,
        notify_date DATETIME,
        flyover_date DATETIME,
        location TEXT,
        type TEXT
        );"""
    
    with sqlite3.connect(db) as conn:
            cursor = conn.cursor()
            cursor.execute(script)
            conn.commit()

def add_notification(conn, notification):
    sql = ''' INSERT INTO notifications(name,email,notify_date,flyover_date,location,type)
              VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, notification)
    conn.commit()
    return cur.lastrowid

def remove_notification(conn, id):
    cur = conn.cursor()
    delete_stmt = 'DELETE FROM notifications WHERE id = ?'
    cur.execute(delete_stmt, (id,))
    conn.commit()


# Form submit: add new notification to branch
def add_to_database():
    with sqlite3.connect('user_notifications.db') as conn:

        # parse information from json
        # fix datetimes
        name = "Ayoung"
        email = "pvgandhi@uwaterloo.ca"
        notify_by = "2024-10-05 17:04:25"
        flyover_on = "2025-12-15 12:55:26"
        location = "Paris, Country"
        type = "email"

        notification = (name, email, notify_by, flyover_on, location, type)
        notif_id = add_notification(conn, notification)

        return

def send_notifications():
    
    with sqlite3.connect('user_notifications.db') as conn:
        now = datetime.now()
        two_minutes_later = now + timedelta(minutes=2)

        print(now)
        print(two_minutes_later)

        script = """
                    SELECT * FROM notifications 
                    WHERE notify_date >= ? AND notify_date <= ?; 
                 """

        cur = conn.cursor()
        cur.execute(script, (now.strftime("%Y-%m-%d %H:%M:%S"), two_minutes_later.strftime("%Y-%m-%d %H:%M:%S")))
        rows = cur.fetchall()

        for row in rows:
            print(row)
            
            if(row[6] == "email"):
                send_email(row[1], row[2], row[3], row[4], row[5])
            elif(row[6] == "sms"):
                send_SMS(row[1], row[2], row[3], row[4], row[5])

            print(f"Removing: {row}")
            remove_notification(conn=conn, id=row[0]) # pass notification id to remove 

app = Flask(__name__)
scheduler = BackgroundScheduler()

# Schedule the notification check every minute
scheduler.add_job(send_notifications, 'interval', minutes=1)

@app.route('/signup')
def index():
    return "Notification Service is Running!"

if __name__ == '__main__':
    scheduler.start()
    try:
        app.run(port=5000)

    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()




# PUWRW4SHLU996XH5XTLJB8E2


