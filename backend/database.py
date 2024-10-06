import sqlite3
from datetime import datetime, timedelta
from send_notification import send_email, send_SMS
from landsat_sr import get_next_acq


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
                    phone_number TEXT NOT NULL,
                    notify_date DATETIME,
                    flyover_date DATETIME,
                    lat FLOAT,
                    long FLOAT,
                    address_pretty TEXT,
                    address_components TEXT
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
        sql = """INSERT INTO notifications(name, email, phone_number, 
        notify_date, flyover_date, lat, long, address_pretty, address_components)
                 VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)"""

        flyover_info = get_next_acq(notification[6], notification[7])

        landsat8 = flyover_info.get("landsat_8", {}).get("date")
        landsat9 = flyover_info.get("landsat_9", {}).get("date")
        # landsat8 = datetime.now()
        # landsat9 = datetime.now()

        if landsat8 and landsat9:
            flyover_date = min(landsat8, landsat9)
        elif landsat8:  # If only landsat8 date is present
            flyover_date = landsat8
        elif landsat9:  # If only landsat9 date is present
            flyover_date = landsat9

        if(notification[3] == 1):
            notify_time = flyover_date - timedelta(days=1)
        elif(notification[3] == 2):
            notify_time = flyover_date - timedelta(days=7)

        notification[3] = notify_time
        notification[4] = flyover_date

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
                 WHERE email = ?"""
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute(sql, (email,))
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

