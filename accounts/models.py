from django.db import models
from django.utils.timezone import now
import os
import uuid
from datetime import timedelta
from django.utils import timezone
from storages.backends.s3boto3 import S3Boto3Storage
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password, check_password

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class MediaStorage(S3Boto3Storage):
    location = 'media'
def generate_profile_filename(instance, filename):
    unique_filename = f'{uuid.uuid4().hex}{os.path.splitext(filename)[1]}'
    return os.path.join('profile_photos/', unique_filename)


def generate_admin_filename(instance, filename):
    unique_filename = f'{uuid.uuid4().hex}{os.path.splitext(filename)[1]}'
    return os.path.join('profile_photos/', unique_filename)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    profile_photo = models.ImageField(storage=MediaStorage(), upload_to=generate_admin_filename, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    password = models.CharField(max_length=128, blank=True)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []



class MediaStorage(S3Boto3Storage):
    location = 'media'
def generate_unique_filename(instance, filename):
    unique_filename = f'{uuid.uuid4().hex}{os.path.splitext(filename)[1]}'
    return os.path.join('company_logos/', unique_filename)

class Company(models.Model):
    user_id = models.CharField(max_length=255, unique=True)
    company_name = models.CharField(max_length=255)
    company_admin_name = models.CharField(max_length=255)
    email_address = models.EmailField(unique=True)   
    password = models.CharField(max_length=255)  
    phone_no1 = models.CharField(max_length=15)
    phone_no2 = models.CharField(max_length=15, blank=True, null=True)   
    created_at = models.DateTimeField(default=timezone.now) 
    company_logo = models.ImageField(storage=MediaStorage(), upload_to=generate_unique_filename, null=True, blank=True)
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('blocked', 'Blocked'),
          
         
    ] 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    QMS = 'QMS'
    EMS = 'EMS'
    OHS = 'OHS'
    EnMS = 'EnMS'
    BMS = 'BMS'
    AMS = 'AMS'
    IMS = 'IMS'
    PERMISSION_CHOICES = [
        (QMS, 'QMS'),
        (EMS, 'EMS'),
        (OHS, 'OHS'),
        (EnMS, 'EnMS'),
        (BMS, 'BMS'),
        (AMS,'AMS'),
        (IMS,'IMS')

    ]
    permissions = models.ManyToManyField('Permission', blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    def set_password(self, raw_password):
        """Hash password before saving"""
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        """Check if a raw password matches the stored hashed password"""
        return check_password(raw_password, self.password)
    def __str__(self):
        return self.company_name

class Permission(models.Model):
    name = models.CharField(max_length=100, choices=Company.PERMISSION_CHOICES)
    
    def __str__(self):
        return self.get_name_display()
    
    
 
class Subscription(models.Model):
    subscription_name = models.CharField(max_length=255,default = True,null = True)
    validity =  models.IntegerField(blank = True,null=True)

    def __str__(self):
        return self.subscription_name
    
class Subscribers(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True) 
    plan = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('blocked', 'Blocked'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_date = models.DateField(null=True, blank=True)  
    expiry_date = models.DateField(null=True, blank=True)  

    def save(self, *args, **kwargs):
       
        if not self.start_date:   
            self.start_date = now().date()

        
        if self.plan and self.plan.validity and self.plan.validity > 0:
            duration = self.plan.validity  
            self.expiry_date = now().date() + timedelta(days=duration)

 
        else:
            self.expiry_date = None  # or set a default expiry date

        super().save(*args, **kwargs)
    
    def __str__(self):
        if self.company:
            return self.company.company_name
        return "No Company Assigned"