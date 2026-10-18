from django.conf import settings
from twilio.rest import Client



account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)


for c in client.outgoing_caller_ids.list():
    print(c.phone_number, c.friendly_name)

print(client.api.accounts(settings.TWILIO_ACCOUNT_SID).fetch().friendly_name)

def send_message(to_number, body):
    try:
        message = client.messages.create(
            body=body,
            messaging_service_sid=settings.TWILIO_MESSAGING_SERVICE_SID,
            to=to_number,
            status_callback=settings.TWILIO_STATUS_CALLBACK_URL,
        )
        return message.sid
    except Exception as ex:
        print(ex)








