import sqlite3
from datetime import datetime, timedelta
from send_notification import send_email


class Database:
    def __init__(self, db_file):
        self.db_file = db_file
        self.version = sqlite3.sqlite_version
        self.start()

    def start(self):
        script = """CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY, 
                    name TEXT NOT NULL, 
                    email TEXT NOT NULL,
                    notify_date DATETIME,
                    flyover_date DATETIME,
                    location TEXT
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
        sql = """INSERT INTO notifications(name, email, notify_date, flyover_date, location)
                 VALUES(?, ?, ?, ?, ?)"""
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute(sql, notification)
            conn.commit()
            return cur.lastrowid

    def remove_notification(self, location, email):
        sql = """DELETE FROM notifications WHERE location = ?
                AND email = ?""" 
        self._exec(sql, (location,email))
    
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
        two_minutes_later = now + timedelta(minutes=2)

        rows = self.get_within_timeframe(now.strftime("%Y-%m-%d %H:%M:%S"),
                                        two_minutes_later.strftime(
                                        "%Y-%m-%d %H:%M:%S"))

        for row in rows:
            send_email(row[1], row[2], row[3], row[4], row[5])
            self.remove_notification(row[0])

