
from django.db import models
import os
import uuid
from storages.backends.s3boto3 import S3Boto3Storage
from accounts.models import Company 
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError

class MediaStorage(S3Boto3Storage):
    location = 'media'
def generate_profile_filename(instance, filename):
    unique_filename = f'{uuid.uuid4().hex}{os.path.splitext(filename)[1]}'
    return os.path.join('user_logos/', unique_filename)


class Users(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='usercomp', null=True, blank=True)  
    username = models.CharField(max_length=255, unique=True, default =True ) 
    first_name = models.CharField(max_length=255, default =True  )
    last_name = models.CharField(max_length=255, default =True  )
    password = models.CharField(max_length=255, default =True  )   
    gender = models.CharField(
        max_length=255,
        choices=[
            ('Male', 'Male'),
            ('Female', 'Female'),  
        ],null=True, blank=True
    )
    date_of_birth = models.DateField(null=True,blank=True)
    address =  models.TextField(null=True,blank=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    zip_po_box = models.CharField(max_length=20, blank=True, null=True)
    province_state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=50, default =True  )
    department_division = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True, default =True  ) 
    phone = models.CharField(max_length=15, default =True  )
    office_phone = models.CharField(max_length=15, blank=True, null=True)
    mobile_phone = models.CharField(max_length=15, blank=True, null=True)
    fax = models.CharField(max_length=15, blank=True, null=True)
    secret_question = models.CharField(max_length=100,null=True,blank=True)
    answer = models.CharField(max_length=100,null=True,blank=True)
    user_logo = models.ImageField(storage=MediaStorage(), upload_to=generate_profile_filename, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    is_trash = models.BooleanField(default=False)
    STATUS_CHOICES = [
        ('active', 'active'),
        ('blocked', 'blocked'),
          
         
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
    created_at = models.DateTimeField(auto_now_add=True)
    
    def set_password(self, raw_password):
        """Hash password before saving"""
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        """Check if a raw password matches the stored hashed password"""
        return check_password(raw_password, self.password)
    
    
    def __str__(self):
       
        return self.username

    
class Permission(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class MediaStorage(S3Boto3Storage):
    location = 'media'
def generate_unique_filename(instance, filename):
    unique_filename = f'{uuid.uuid4().hex}{os.path.splitext(filename)[1]}'
    return os.path.join('policy_documents/', unique_filename)


def generate_unique_filename1(instance, filename):
    unique_filename = f'{uuid.uuid4().hex}{os.path.splitext(filename)[1]}'
    return os.path.join('policy_documents/', unique_filename)


def generate_unique_filename_training(instance, filename):
    unique_filename = f'{uuid.uuid4().hex}{os.path.splitext(filename)[1]}'
    return os.path.join('Training_attachments/', unique_filename)
    

    

 


def generate_unique_filename_minute(instance, filename):
    
    unique_filename = f'{uuid.uuid4().hex}{os.path.splitext(filename)[1]}'
    return os.path.join('minutes_attached/', unique_filename)     
 


 






 


def generate_unique_filename_audit(instance, filename):
    
    unique_filename = f'{uuid.uuid4().hex}{os.path.splitext(filename)[1]}'
    return os.path.join('audit/', unique_filename)     

    




    

    
class RiskAssessment(models.Model):
    assessment_no = models.CharField(max_length=50, blank=True, null=True)
    related_record_format = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    written_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="written_assessment"
    )
    approved_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_assessment"
    )
    checked_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="checked_assessment"
    )
    document_type = models.CharField(
        max_length=255,blank = True, null =True,
        choices=[
            ('System', 'System'),
            ('Paper', 'Paper'),
            ('External','External'),
            ('Work Instruction','Work Instruction')
  
        ]
    )
    assessment_name = models.CharField(max_length=50, blank=True, null=True)
    upload_attachment =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)   
    rivision = models.CharField(max_length=50, blank=True, null=True)
    send_notification = models.BooleanField(default=False)
    public = models.BooleanField(default=False)
    
    def __str__(self):
        return self.assessment_name

class HealthRootCause(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.title  
    
class HealthIncidents(models.Model):
    source = models.CharField(max_length=50, blank=True, null=True)
    incident = models.CharField(max_length=50, blank=True, null=True)
    root_cause = models.ForeignKey(HealthRootCause, on_delete=models.SET_NULL, null=True )
    description = models.TextField(blank=True, null=True)
    date_raised = models.DateField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Deleted', 'Deleted')        
    ] 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    reported_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_health_incidents"
    )
    action =  models.TextField(blank=True, null=True)
    date_completed = models.DateField(blank=True, null=True)
    send_notification = models.BooleanField(default=False)

    def __str__(self):
        return self.source  
    

class BusinessRisk(models.Model):
    risk_no = models.CharField(max_length=50, blank=True, null=True)
    business_process = models.CharField(max_length=50, blank=True, null=True)
 
    remark =  models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    written_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="written_risk"
    )
    approved_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_risk"
    )
    checked_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="checked_risk"
    )
    document_type = models.CharField(
        max_length=255,blank = True, null =True,
        choices=[
            ('System', 'System'),
            ('Paper', 'Paper'),
            ('External','External'),
            ('Work Instruction','Work Instruction')
  
        ]
    )
    level_of_risk = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        choices=[
            ('High', 'High'),
            ('Medium', 'Medium'),
            ('Low','Low')
    
        ]
    )
    business_name = models.CharField(max_length=50, blank=True, null=True)
    rivision = models.CharField(max_length=50, blank=True, null=True)
    upload_attachment =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)   
    send_notification = models.BooleanField(default=False)
    public = models.BooleanField(default=False)
    
    def __str__(self):
        return self.business_name
    









    


    

class CorrectionCause(models.Model):   
    title = models.CharField(max_length=255,blank=True, null=True)
    
    def __str__(self):
        return self.title or "No Title Provided"

class CorrectiveAction(models.Model): 
    source = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        choices=[
            ('Audit', 'Audit'),
            ('Customer', 'Customer'),
            ('Internal','Internal'),
            ('Supplier','Supplier')  
        ]
    )
    action = models.CharField(max_length=255,blank=True, null=True)
    root_cause = models.ForeignKey(CorrectionCause, on_delete=models.SET_NULL, null=True )
    description = models.TextField(blank=True, null=True)
    date_raised = models.DateField(blank=True, null=True)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Deleted', 'Deleted')        
    ] 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    title = models.CharField(max_length=255,blank=True, null=True)
    executor = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True )
    action_corrections =  models.TextField(blank=True, null=True)
    date_completed = models.DateField(blank=True, null=True)
    send_notification = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title or "No Title Provided"
    







    




    
 