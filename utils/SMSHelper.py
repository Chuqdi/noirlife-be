from django.conf import settings
from twilio.rest import Client



account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)

def send_message(to_number, body):
    try:
        client.messages \
                        .create(
                            body=body,
                            from_=settings.TWILIO_SENDER_ID,
                            to=to_number
                        )
    except Exception as ex:
        pass








