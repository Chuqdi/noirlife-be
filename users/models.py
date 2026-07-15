from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone







class UserManager(BaseUserManager):
    def create(self, email, full_name,phone_number, password):
        if  not email:
            raise ValueError("Please enter your  email")
        

        if  not full_name:
            raise ValueError("Please enter your full name")


        if password:
            raise ValueError("Please enter your password")

        user  = self.model(
            phone_number=phone_number, 
            full_name = full_name,
            email = self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    

    def  create_super_user(self, email, full_name,phone_number, password):
        user = self.create_user(email, full_name,phone_number, password)
        user.is_active=True
        user.is_superuser=True
        user.is_staff = True
        user.save(using=self._db)
        return user





class User(AbstractUser):
    username = models.CharField(null=True, blank=True,max_length=150)
    full_name = models.CharField(null=True, blank=True,max_length=150)
    profile_image = models.FileField(null=True, blank=True)
    company_name = models.CharField(null=True, blank=True,max_length=150)
    email  = models.EmailField(blank=False, null=False, unique=True,max_length=200, db_index=True)
    ref_code = models.CharField(null=True, blank=True, max_length=30)
    is_new = models.BooleanField(default=True)
    is_book_session_payment_completed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    ##USERS SAFEWORD
    safe_word = models.CharField(max_length=1000, null=True, blank=True)
    referalCode = models.CharField(max_length=100, null=True, blank=True)
    refered_by_code = models.CharField(max_length=100, null=True, blank=True)
    isReferalUsed = models.BooleanField(default=False)
    phone_number = models.CharField(null=False, blank=False, max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [ ]
    
    class Meta:
        ordering = ['-id']





    def __str__(self) -> str:
        return str(self.email)




class DeviceToken(models.Model):
    token = models.TextField()
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.user.email


class ReferalCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="referal_code")
    code = models.CharField(max_length=6, null=False, blank=False)

    def __str__(self):
        return self.user.email



class UserEmailActivationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, null=False, blank=False)
    date_created = models.DateTimeField(default = timezone.now)

    def __str__(self):
        return self.user.email
    



