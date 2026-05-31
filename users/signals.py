
import threading
from django.db.models.signals import post_save
from .models import User
from django.dispatch import receiver
from utils.tasks import send_email
from django.template.loader import render_to_string
from django.conf import settings
import time

