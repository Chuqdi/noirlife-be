import threading
from django.utils import timezone
from utils.randomString import GenerateRandomString
from users.models import  User, UserEmailActivationCode
from datetime import timedelta
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from utils.TokenGenerator import generateToken
from django.conf import settings
from django.conf import settings
from datetime import datetime
from django.conf import settings



 



def send_email_here( subject, message, recipient_list, ):
    message = EmailMessage(subject, message,  settings.DEFAULT_FROM_EMAIL,recipient_list)
    message.content_subtype = 'html' 
    message.send()

    

def formatResumeDownloadLink(role_id):
    path = f"{settings.BACKEND_URL}api/v1/roles/download_role_data/{role_id}/"
    return path
     

def generateUserOTP(email):
    user = User.objects.get(email=email)
    code = GenerateRandomString.randomStringGenerator(6).upper()
    c = UserEmailActivationCode.objects.create(user=user, code =code)
    return code


def generateSecureEmailCredentials(user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = generateToken.make_token(user)

    return {"uidb64": uidb64, "token": token}




def validateOTPCode(code):
    
        c = UserEmailActivationCode.objects.filter(code = code)

        if not c.exists():
            return {
                "message":"OTP does not exist",
                "type":False
            }

        code = c[0]
        if (code.date_created + timedelta(minutes=30)) < timezone.now():
            code.delete()
            return {
                "message":"OTP has expired",
                "type":False,
            }
        code.delete()

        return  {
                "message":"OTP is valid",
                "type":True,
                "code":code
            }







