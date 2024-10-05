import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime 

# Calculate the time difference between notification and flyover
def calc_dates(date_flyover, date_notify):
    time_diff = date_flyover - date_notify
    time_difference = ""

    # Calculate hours, minutes, and seconds
    hours = (time_diff.seconds // 3600)
    minutes = (time_diff.seconds % 3600) // 60
    seconds = time_diff.seconds % 60

    if(time_diff.days > 0 ):
        time_difference += f"{time_diff.days}"
        time_difference += " days, " if time_diff.days != 1 else " day, "

    time_difference += str(hours)
    time_difference += " hours, " if hours != 1 else " hour, " 

    time_difference += str(minutes)
    time_difference += " minutes, and " if minutes != 1 else " minute, and"

    time_difference += str(seconds)
    time_difference += " seconds" if seconds != 1 else " second"

    return time_difference



sender_email = "pleasedonotthemap@gmail.com"
password = "tlicxaprtqdrrvcg"

# all given to us
name = "John"
receiver_email = "verahhxii@gmail.com"
# receiver_email = "test-x6sxqcq3q@srv1.mail-tester.com"
date_to_notify = "02/13/2025 11:53:25"
date_of_flyover = "08/15/2025 13:55:26"
location = "Toronto, Canada"

date_notify = datetime.strptime(date_to_notify, "%m/%d/%Y %H:%M:%S")
date_flyover = datetime.strptime(date_of_flyover, "%m/%d/%Y %H:%M:%S")

time_difference = calc_dates(date_flyover, date_notify)

message = MIMEMultipart("alternative")
message["Subject"] = "Heads Up! Landsat is here!"
message["From"] = sender_email
message["To"] = receiver_email


html = f"""\
<html>
  <body>
    <p>Heads up {name}!<br><br>
       NASA's Landsat satellite will be flying over <b>{location}</b> in <b>{time_difference}</b> on 
       <b> {datetime.strftime(date_notify, "%B %d, %Y")}</b> at <b>{datetime.strftime(date_notify, "%H:%M:%S")}</b> .<br><br>
       Check out <a href="https://pleasedonotthemap.space">Please Do Not the Map</a> for more information!
    </p>
  </body>
</html>
"""

# Plain-text content as a fallback
text = f"""\
Heads up {name}!
NASA's Landsat satellite will be flying over {location} in {time_difference} on 
{datetime.strftime(date_notify, "%m/%d/%y")} at {datetime.strftime(date_notify, "%H:%M:%S")}
Check out Please Do Not the Map for more information: https://pleasedonotthemap.space
"""

# Attach both parts (plain-text and HTML) to the message
part1 = MIMEText(text, "plain")
part2 = MIMEText(html, "html")
message.attach(part1)
message.attach(part2)

# Create secure connection with server and send email
context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(
        sender_email, receiver_email, message.as_string()
    )




