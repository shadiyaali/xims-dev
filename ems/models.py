from django.db import models
import os
import uuid
from storages.backends.s3boto3 import S3Boto3Storage
from accounts.models import Company 
from company.models import Users
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError

class MediaStorage(S3Boto3Storage):
    location = 'media'

def generate_unique_filename(instance, filename):
    unique_filename = f'{uuid.uuid4().hex}{os.path.splitext(filename)[1]}'
    return os.path.join('policy_documents/', unique_filename)


def generate_unique_filename_audit(instance, filename):
    
    unique_filename = f'{uuid.uuid4().hex}{os.path.splitext(filename)[1]}'
    return os.path.join('audit/', unique_filename)   



class PolicyEnv(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="policy_documentsf",null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="policy_documentsf",null=True, blank=True)
    text = models.TextField(blank=True, null=True)
    energy_policy = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
   
    def clean(self):
        
        if self.user and self.company:
            raise ValidationError("You can only assign this document to either a user or a company, not both.")
        if not self.user and not self.company:
            raise ValidationError("You must assign this document to either a user or a company.")

    def save(self, *args, **kwargs):
        self.clean()  
        super().save(*args, **kwargs)
    def __str__(self):
        return self.text
    
    
class ManualEnv(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='manualenv', null=True, blank=True) 
    no = models.CharField(max_length=50, blank=True, null=True)
    written_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="written_manualenv"
    )
    approved_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_manualenv"
    )
    checked_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="checked_manualenv"
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
    review_frequency_year = models.TextField(blank=True, null=True)
    review_frequency_month = models.TextField(blank=True, null=True)
    upload_attachment =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    rivision = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    send_notification = models.BooleanField(default=False)
    publish = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    

 


class ProcedureEnv(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='procedureenv', null=True, blank=True) 
    no = models.CharField(max_length=50, blank=True, null=True)
    written_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="written_procedureenv"
    )
    approved_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_procedureenv"
    )
    checked_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="checked_procedureenv"
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
    review_frequency_year = models.TextField(blank=True, null=True)
    review_frequency_month = models.TextField(blank=True, null=True)
    relate_format = models.CharField(max_length=50, blank=True, null=True)
    upload_attachment =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    rivision = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    send_notification = models.BooleanField(default=False)
    publish = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
class RecordFormatEnv(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='recordenv', null=True, blank=True) 
    no = models.CharField(max_length=50, blank=True, null=True)
    written_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="written_recordenv"
    )
    approved_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_recordenv"
    )
    checked_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="checkedrecordenv"
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
    review_frequency_year = models.TextField(blank=True, null=True)
    review_frequency_month = models.TextField(blank=True, null=True)
    retention = models.CharField(max_length=50, blank=True, null=True)
    upload_attachment =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    rivision = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    send_notification = models.BooleanField(default=False)
    publish = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class NotificationEnv(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="notificationsenv")
    manual = models.ForeignKey(ManualEnv, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.email} - {self.message}"