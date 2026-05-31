from django.core.mail import EmailMultiAlternatives
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from users.models import User
from django.urls import reverse
import threading





class SendEmail:
    def __init__(self, template, subject, to) -> None:
        self.template = template
        self.subject = subject
        self.to = to
        self.send()

    def send(self):
        self.sendEmailNow(),

    def sendEmailNow(self):
        e = EmailMultiAlternatives(
            subject=self.subject,
            body=strip_tags(self.template),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=self.to,
        )
        e.attach_alternative(self.template, "text/html")
        e.send()


def send_activation_email(user, template, urlPath, subject):
    email = user.email
    user = User.objects.get(email=email)

    template = render_to_string(template, {"urlPath": urlPath, "user": user})

    s = SendEmail(template=template, subject=subject, to=(user.email,))


def actionNotificationEmail(message, to, title=""):
    template = render_to_string(
        "emails/action_notification.html", {"message": message, "title": title}
    )
    

    s = SendEmail(template=template, subject="Action Notification", to=(to,))
