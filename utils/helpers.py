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



 
def send_to_zapier(data):
    zapier_url = "https://hooks.zapier.com/hooks/catch/13525156/uocxdu6/"
    
    try:
        
        print("Zapier Hook triggered")
        print(zapier_url)
        print(data)
    except Exception as e:
        print(f"Error sending to Zapier: {e}")
        return None




def is_cv(text: str) -> int:
    """
    Check if the given text is likely a CV/resume.
    
    Args:
        text (str): Text extracted from the PDF
    
    Returns:
        int: Confidence rating from 0-100
    """
    # Convert to lowercase for case-insensitive matching
    text = text.lower()
    
    # Define CV-specific keywords and phrases
    cv_keywords = [
        # Personal details
        'contact information', 'phone', 'email', 'address', 
        'personal details', 'mobile number',
        
        # Professional sections
        'professional summary', 'career objective', 'professional profile',
        'work experience', 'employment history', 'professional experience',
        'education', 'academic background', 'qualifications',
        'skills', 'technical skills', 'professional skills',
        
        # Professional terms
        'curriculum vitae', 'resume', 'cv', 
        'job title', 'position', 'role',
        'company', 'organization', 'employer',
        'degree', 'certification', 'diploma',
        
        # Action words
        'responsible for', 'managed', 'developed', 
        'created', 'implemented', 'led'
    ]
    
    # Check for common professional section formats
    section_patterns = [
        'work experience:', 'education:', 'skills:', 
        'professional experience:', 'academic background:'
    ]
    
    # Initialize score
    score = 0
    
    # Check for keywords
    keyword_matches = sum(1 for keyword in cv_keywords if keyword in text)
    score += min(keyword_matches * 3, 40)  # Max 40 points for keywords
    
    # Check for section patterns
    section_matches = sum(1 for pattern in section_patterns if pattern in text)
    score += min(section_matches * 10, 30)  # Max 30 points for sections
    
    # Check for potential contact information
    contact_checks = [
        '@' in text,  # Email check
        any(phone in text for phone in ['tel:', 'phone:', 'mobile:']),
        any(str(year) in text for year in range(1950, 2024))  # Year of experience
    ]
    score += sum(contact_checks) * 10  # Max 30 points for contact info
    
    # Ensure score is between 0 and 100
    return min(max(score, 0), 100)




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







