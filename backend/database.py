import sqlite3
from datetime import datetime, timedelta
from send_notification import send_email, send_SMS


class Database:
    def __init__(self, db_file):
        self.db_file = db_file
        self.version = sqlite3.sqlite_version
        self.start()

    def start(self):
        script = """CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY, 
                    name text NOT NULL, 
                    email TEXT,
                    phone number TEXT,
                    notify_date DATETIME,
                    flyover_date DATETIME,
                    location TEXT,
                    );"""
        self._exec(script)

    def _exec(self, script, params=None):
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            if params:
                cur.execute(script, params)
            else:
                cur.execute(script)
            conn.commit()

    def add_notification(self, notification: tuple):
        sql = """INSERT INTO notifications(name, email, phone_number, notify_date, flyover_date, location)
                 VALUES(?, ?, ?, ?, ?, ?)"""

        if(notification[3] == 1):
            notify_time = notification[4] - timedelta(days=1)
        elif(notification[3] == 2):
            notify_time = notification[4] - timedelta(days=7)

        notification[3] = notify_time

        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute(sql, notification)
            conn.commit()
            return cur.lastrowid

    def remove_notification(self, id_num):
        sql = """DELETE FROM notifications WHERE id = ?""" 
        self._exec(sql, (id_num))
    
    def get_user_notifications(self, email):
        sql = """SELECT * FROM notifications
                WHERE email = ?;
            """
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute(sql, (email))
            return cur.fetchall()

    def get_within_timeframe(self, start_time, end_time):
        """ Fetch notifications that should be sent within a specific timeframe """
        sql = """
            SELECT * FROM notifications 
            WHERE notify_date >= ? AND notify_date <= ?; 
            """
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute(sql, (start_time, end_time))
            return cur.fetchall()

    def send_notifications(self):
        now = datetime.now()
        one_hour_later = now + timedelta(hours=1, minutes=20)

        rows = self.get_within_timeframe(now.strftime("%Y-%m-%d %H:%M:%S"),
                                        one_hour_later.strftime(
                                        "%Y-%m-%d %H:%M:%S"))

        for row in rows:
            if(self.is_valid_email(row[2])):
                send_email(row[1], row[2], row[4], row[5], row[6])
            if(self.is_valid_phone_number(row[3])):
                send_SMS(row[1], row[3], row[4], row[5], row[6])

            self.remove_notification(row[0])

