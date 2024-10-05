import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime 

sender_email = "pleasedonotthemap@gmail.com"
password = "tlicxaprtqdrrvcg"

# all given to us
name = "John"
receiver_email = "perigandhi@gmail.com"
date_to_notify = "07/13/2025 13:55:26"
date_of_flyover = "08/15/2025 13:55:26"
location = "Toronto, Canada"


date_notify = datetime.strptime(date_to_notify, "%m/%d/%Y %H:%M:%S")
date_flyover = datetime.strptime(date_of_flyover, "%m/%d/%Y %H:%M:%S")

time_diff = date_flyover - date_notify

# time_diference = datetime.strftime(time_diff, "%B %d, %Y")
# print(time_diference)
time_difference = ""

# Calculate hours, minutes, and seconds
hours = (time_diff.seconds // 3600)
minutes = (time_diff.seconds % 3600) // 60
seconds = time_diff.seconds % 60

if(date_notify.month != date_flyover.month and date_notify.year == date_flyover.year):
  month_diff = date_flyover.month - date_notify.month
  time_difference += f"{month_diff}"
  time_difference += lambda month_diff : "months" if month_diff>1 else "month"

if(time_diff.days > 0):
  days = time_diff.days
  time_difference += days
  time_difference += lambda days : "days" if days>1 else "day"

time_difference += hours
time_difference += lambda hours : "hours" if hours>0 else "hour" 

time_difference += minutes
time_difference += lambda minutes : "minutes" if minutes>0 else "minute"
# {minutes} minutes, and {seconds} seconds"

print(time_difference)

message = MIMEMultipart("alternative")
message["Subject"] = "Heads Up! Landsat is here!"
message["From"] = sender_email
message["To"] = receiver_email


html = f"""\
<html>
  <body>
    <p>Heads up {name}!<br>
       NASA's Landsat satellite will be flying over <b>{location}</b> in <b>{time_difference} on 
       {datetime.strftime(date_notify, "%B %d, %Y")} at {datetime.strftime(date_notify, "%H:%M:%S")}</b> .<br><br>
       Welcome to Please do not the map! You requested to be notified about the Landsat satellite.<br><br>
       Check out <a href="http://www.realpython.com">Real Python</a> for great tutorials!
    </p>
  </body>
</html>
"""

# Plain-text content as a fallback
text = f"""\
Heads up {name}!
NASA's Landsat satellite will be flying over {location}.
Welcome to Please do not the map! You requested to be notified about the Landsat satellite.
Visit Real Python for tutorials: http://www.realpython.com
"""


# Attach both parts (plain-text and HTML) to the message
part1 = MIMEText(text, "plain")
part2 = MIMEText(html, "html")
message.attach(part1)
message.attach(part2)

# # Create secure connection with server and send email
# context = ssl.create_default_context()
# with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
#     server.login(sender_email, password)
#     server.sendmail(
#         sender_email, receiver_email, message.as_string()
#     )

