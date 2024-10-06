# PleaseDoNotTheRepo


# # Initialize a session using your AWS credentials
#   session = boto3.Session(
#     aws_access_key_id='YOUR_ACCESS_KEY',
#     aws_secret_access_key='YOUR_SECRET_KEY',
#     region_name='YOUR_REGION'  # e.g., 'us-west-2'
# )

#   # Create SNS client
#   sns = session.client('sns')

#   # Send SMS message
#   response = sns.publish(
#       PhoneNumber='+1234567890',  # Replace with the recipient's phone number
#       Message='Hello! This is a test message from AWS SNS.',
#   )

#   print(response)