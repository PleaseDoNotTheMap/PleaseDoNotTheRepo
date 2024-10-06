import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime 
import vonage


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



# Send the email
def send_email(name, receiver_email, date_to_notify, date_of_flyover, location):
  sender_email = "pleasedonotthemap@gmail.com"
  password = "tlicxaprtqdrrvcg"

  date_notify = datetime.strptime(date_to_notify, "%Y-%m-%d %H:%M:%S")
  date_flyover = datetime.strptime(date_of_flyover, "%Y-%m-%d %H:%M:%S")

  time_difference = calc_dates(date_flyover, date_notify)

  message = MIMEMultipart("alternative")
  message["Subject"] = "Heads Up! Landsat is arriving soon!"
  message["From"] = sender_email
  message["To"] = receiver_email

  html = f"""\
  <html>
    <head>
      <style>
        body {{
          font-family: Arial, sans-serif;
          background-color: #f4f4f9;
          margin: 0;
          padding: 20px;
          color: #333;
        }}
      
        h1 {{
          color: #574AE2;
        }}
        p {{
          font-size: 16px;
          line-height: 1.6;
        }}
        a {{
          color: #574AE2;
          text-decoration: none;
        }}
        a:hover {{
          text-decoration: underline;
        }}
        .highlight {{
          font-weight: bold;
          color: #574AE2;
        }}
      </style>
    </head>
    <body>
        <h1>Heads up, {name}!</h1>
        <p>
          NASA's Landsat satellite will be flying over <span class="highlight">{location}</span> in 
          <span class="highlight">{time_difference}</span> on 
          <span class="highlight">{datetime.strftime(date_notify, "%B %d, %Y")}</span> at 
          <span class="highlight">{datetime.strftime(date_notify, "%H:%M:%S")}</span>.
        </p>
        <p>
          Check out <a href="https://pleasedonotthemap.space">Please Do Not the Map</a> for more information!
        </p>
    </body>
  </html>
  """

  # Plain-text content as a fallback
  text = f"""\
  Heads up {name}!
  NASA's Landsat satellite will be flying over {location} in {time_difference} on 
  {datetime.strftime(date_notify, "B %d, %Y")} at {datetime.strftime(date_notify, "%H:%M:%S")}
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
    
  print("Email sent!")
  return


def send_SMS(name, phone_number, date_to_notify, date_of_flyover, location):

  date_notify = datetime.strptime(date_to_notify, "%Y-%m-%d %H:%M:%S")
  date_flyover = datetime.strptime(date_of_flyover, "%Y-%m-%d %H:%M:%S")

  time_difference = calc_dates(date_flyover, date_notify)

  client = vonage.Client(key="4bdfb3ba", secret="BfsaXVcp9LnvBXhj")
  sms = vonage.Sms(client)

  responseData = sms.send_message(
    {
        "from": "17783905789",
        "to": f"{phone_number}",
        "text":f"""Heads up {name}! NASA's Landsat satellite will be flying over {location} in {time_difference} on {datetime.strftime(date_notify, "%B %d, %Y")} at {datetime.strftime(date_notify, "%H:%M:%S")}. Check out Please Do Not the Map for more information: https://pleasedonotthemap.space""",
      }
  )

  if responseData["messages"][0]["status"] == "0":
      print("Message sent successfully.")
  else:
      print(f"Message failed with error: {responseData['messages'][0]['error-text']}")

