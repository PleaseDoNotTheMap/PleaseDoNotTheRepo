import sqlite3
from datetime import datetime, timedelta
from send_notification import send_email, send_SMS
import re


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

    def add_notification(self, notification: tuple, time_zone: str):
        sql = """INSERT INTO notifications(name, email, phone_number, notify_date, flyover_date, location)
                 VALUES(?, ?, ?, ?, ?)"""
        
        # CONVERT NOTIFICATION AND FLY DATES INTO "%Y-%m-%d %H:%M:%S"

        not_date = datetime.strptime(notification[3], "%Y-%m-%d %H:%M:%S")
        user_time = time_zone.localize(datetime(not_date.year, not_date.month, not_date.day, 9, 0))
        notification[3] = user_time

        fly_date = datetime.strptime(notification[4], "%Y-%m-%d %H:%M:%S")
        user_time = time_zone.localize(datetime(fly_date.year, fly_date.month, fly_date.day, 9, 0))
        notification[4] = user_time

        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute(sql, notification)
            conn.commit()
            return cur.lastrowid

    def remove_notification(self, notif_id):
        sql = """DELETE FROM notifications WHERE id = ?"""
        self._exec(sql, (notif_id,))

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

    def is_valid_email(self, email):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email) is not None
    
    def is_valid_phone_number(phone_number):
        phone_regex = r'^[\d\s\-\(\)]+$'
        digits_only = re.sub(r'\D', '', phone_number)
        return re.match(phone_regex, phone_number) and 9 <= len(digits_only) <= 15

    def send_notifications(self):
        now = datetime.now()
        one_hour_later = now + timedelta(hours=1, minutes=10)

        rows = self.get_within_timeframe(now.strftime("%Y-%m-%d %H:%M:%S"),
                                        one_hour_later.strftime(
                                        "%Y-%m-%d %H:%M:%S"))

        for row in rows:
            if(self.is_valid_email(row[2])):
                send_email(row[1], row[2], row[4], row[5], row[6])
            if(self.is_valid_phone_number(row[3])):
                send_SMS(row[1], row[3], row[4], row[5], row[6])
                
            self.remove_notification(row[0])


