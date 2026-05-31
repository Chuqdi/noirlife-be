from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from users.models import User


def send_email( subject, message, recipient_list, ):
    message = EmailMessage(subject, message,  settings.DEFAULT_FROM_EMAIL,recipient_list)
    message.content_subtype = 'html' 
    message.send()
    print(recipient_list)
    print("email sent")


# second, third,fourth,
def send_onboarding_email (user_email, email_type):
    user = User.objects.get(email=user_email)
    if(email_type== "second"):
        email_template ="emails/chance_to_call.html" 
    elif(email_type== "third"):
        email_template ="emails/most_people.html" 
    else:
        email_template ="emails/if_buying_propery.html" 
        
        
        
    message = render_to_string(
        email_template, {"name": user.full_name}
    )
    send_email("Notification", message, [user.email])