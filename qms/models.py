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


class PolicyDocumentation(models.Model):  
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="policy_documents",null=True, blank=True)
    title = models.CharField(max_length=50, blank=True, null=True,unique=True)
    text = models.TextField(blank=True, null=True)
    energy_policy = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename,max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
   
    def save(self, *args, **kwargs):
        self.clean()  
        super().save(*args, **kwargs)
    def save(self, *args, **kwargs):
        if not self.title or self.title.strip() == "":
            self.title = None

        self.clean()
        super().save(*args, **kwargs)

    

def generate_unique_filename_audit(instance, filename):
    
    unique_filename = f'{uuid.uuid4().hex}{os.path.splitext(filename)[1]}'
    return os.path.join('audit/', unique_filename)   



class Procedure(models.Model):
    document_type = models.CharField(
        max_length=255,blank = True, null =True,
        choices=[
            ('System', 'System'),
            ('Paper', 'Paper'),
            ('External','External'),
            ('Work Instruction','Work Instruction')
  
        ]
    )
    STATUS_CHOICES = [
    ('Pending for Review/Checking', 'Pending for Review/Checking'),
    ('Reviewed,Pending for Approval', 'Reviewed,Pending for Approval'),
    ('Pending for Publish','Pending for Publish'),
    ('Correction Requested','Correction Requested'),
    ('Published','Published'),
    ]

    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="procedure", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='procedure', null=True, blank=True) 
    no = models.CharField(max_length=50, blank=True, null=True)
    written_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="written_procedure"
    )
    approved_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, blank=True, null=True, related_name="approved_procedure"
    )
    checked_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="checked_procedure"
    )
    
    review_frequency_year = models.TextField(blank=True, null=True)
    review_frequency_month = models.TextField(blank=True, null=True)
    upload_attachment =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit,max_length=255, blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True,unique=True)
    rivision = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending for Review/Checking')
    written_at = models.DateTimeField(null=True, blank=True)
    checked_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    is_draft = models.BooleanField(default=False)
    send_notification_to_checked_by = models.BooleanField(default=False)
    send_email_to_checked_by = models.BooleanField(default=False)
    send_notification_to_approved_by = models.BooleanField(default=False)
    send_email_to_approved_by = models.BooleanField(default=False)
    send_notification = models.BooleanField(default=False)
    related_record_format =  models.CharField(max_length=50, blank=True, null=True)
    published_at = models.DateTimeField(null=True, blank=True)
    published_user = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True, related_name="published_procedure")

    def __str__(self):
       return self.title if self.title else f"Procedure #{self.id}"


class Manual(models.Model):
    document_type = models.CharField(
        max_length=255,blank = True, null =True,
        choices=[
            ('System', 'System'),
            ('Paper', 'Paper'),
            ('External','External'),
            ('Work Instruction','Work Instruction')
  
        ]
    )
    STATUS_CHOICES = [
    ('Pending for Review/Checking', 'Pending for Review/Checking'),
    ('Reviewed,Pending for Approval', 'Reviewed,Pending for Approval'),
    ('Pending for Publish','Pending for Publish'),
    ('Correction Requested','Correction Requested'),
    ('Published','Published'),
    ]

    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="manual", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='manual', null=True, blank=True) 
    no = models.CharField(max_length=50, blank=True, null=True)
    written_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="written_manual"
    )
    approved_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, blank=True, null=True, related_name="approved_manual"
    )
    checked_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="checked_manual"
    )
    
    review_frequency_year = models.TextField(blank=True, null=True)
    review_frequency_month = models.TextField(blank=True, null=True)
    upload_attachment =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit,max_length=255, blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    rivision = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending for Review/Checking')
    written_at = models.DateTimeField(null=True, blank=True)
    checked_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    is_draft = models.BooleanField(default=False)
    send_notification_to_checked_by = models.BooleanField(default=False)
    send_email_to_checked_by = models.BooleanField(default=False)
    send_notification_to_approved_by = models.BooleanField(default=False)
    send_email_to_approved_by = models.BooleanField(default=False)
    send_notification = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    published_user = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True, related_name="published_manual")
      

    def __str__(self):
       return self.title if self.title else f"Manual #{self.id}"

    
class RecordFormat(models.Model):
    document_type = models.CharField(
        max_length=255,blank = True, null =True,
        choices=[
            ('System', 'System'),
            ('Paper', 'Paper'),
            ('External','External'),
            ('Work Instruction','Work Instruction')
  
        ]
    )
    STATUS_CHOICES = [
    ('Pending for Review/Checking', 'Pending for Review/Checking'),
    ('Reviewed,Pending for Approval', 'Reviewed,Pending for Approval'),
    ('Pending for Publish','Pending for Publish'),
    ('Correction Requested','Correction Requested'),
    ('Published','Published'),
    ]

    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="record", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='record', null=True, blank=True) 
    no = models.CharField(max_length=50, blank=True, null=True)
    written_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="record_written_by"
    )
    approved_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, blank=True, null=True, related_name="record_approved_by"
    )
    checked_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="record_checked_by"
    )
    
    review_frequency_year = models.TextField(blank=True, null=True)
    review_frequency_month = models.TextField(blank=True, null=True)
    upload_attachment =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit,max_length=255, blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True,unique=True)
    rivision = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending for Review/Checking')
    written_at = models.DateTimeField(null=True, blank=True)
    checked_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    is_draft = models.BooleanField(default=False)
    send_notification_to_checked_by = models.BooleanField(default=False)
    send_email_to_checked_by = models.BooleanField(default=False)
    send_notification_to_approved_by = models.BooleanField(default=False)
    send_email_to_approved_by = models.BooleanField(default=False)
    send_notification = models.BooleanField(default=False)
    retention_period =  models.CharField(max_length=50, blank=True, null=True)
    published_at = models.DateTimeField(null=True, blank=True)
    published_user = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True, related_name="published_record")

   
    def __str__(self):
       return self.title if self.title else f"RecordFormat #{self.id}"
    
class NotificationQMS(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="notifications")
    manual = models.ForeignKey(Manual, on_delete=models.CASCADE, null=True, blank=True)
    title = models.TextField(blank=True,null=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.user.email} - {self.message}"

class NotificatioProcedure(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="notifications_procedure")
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, null=True, blank=True)
    title = models.TextField(blank=True,null=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.user.email} - {self.message}"

class NotificationRecord(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="recordFormat")
    record = models.ForeignKey(RecordFormat, on_delete=models.CASCADE, null=True, blank=True)
    title = models.TextField(blank=True,null=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.user.email} - {self.message}"
    
    
class CorrectionQMS(models.Model):
    manual = models.ForeignKey(Manual, on_delete=models.CASCADE, null=True, blank=True)
    to_user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="corrections_to", null=True, blank=True)
    from_user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="corrections_from", null=True, blank=True)
    correction = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Correction for {self.to_user.email}"


class CorrectionProcedure(models.Model):
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, null=True, blank=True)
    to_user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="corrections_to_procedure", null=True, blank=True)
    from_user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="corrections_from_procedure", null=True, blank=True)
    correction = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Correction for {self.to_user.email}"
    
class CorrectionRecord(models.Model):
    record = models.ForeignKey(RecordFormat, on_delete=models.CASCADE, null=True, blank=True)
    to_user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="recordformat", null=True, blank=True)
    from_user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="record_format", null=True, blank=True)
    correction = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Correction for {self.to_user.email}"
    
class Compliances(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="compliance", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='compliance', null=True, blank=True) 
    compliance_no = models.CharField(max_length=50,blank =True,null = True)
    compliance_type = models.CharField(
        max_length=255,blank = True, null =True,
        choices=[
            ('Legal', 'Legal'),
            ('Business', 'Business'),
            ('Client','Client'),
            ('Process/Specification','Process/Specification')
  
        ]
    )
    attach_document = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit,max_length=255,  blank=True, null=True) 
    compliance_remarks =  models.TextField(blank=True,null=True)
    rivision = models.CharField(max_length=50,blank =True,null = True)
    compliance_name =  models.CharField(max_length=50,blank =True,null = True)
    date = models.DateField(blank=True, null=True)
    relate_business_process = models.CharField(max_length=50,blank =True,null = True)
    relate_document =  models.TextField(blank=True,null=True)
    send_notification = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=False)
    

    def __str__(self):
        return self.compliance_name
    
class ComplianceNotification(models.Model):
    
    compliance = models.ForeignKey(Compliances, on_delete=models.CASCADE, null=True, blank=True)
    title = models.TextField(blank=True,null=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.title}"
    
    
class InterestedParty(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="interest", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='interested', null=True, blank=True) 
    CATEGORY_CHOICES = (
        ('Internal', 'Internal'),
        ('External', 'External'),
    ) 
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Internal')  
    special_requirements = models.TextField(blank=True, null=True)
    legal_requirements = models.CharField(  blank=True, null=True)
    custom_legal_requirements = models.TextField(blank=True, null=True)
    file = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename,max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    send_notification = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Interested Party"
        verbose_name_plural = "Interested Parties"
 
class Needs(models.Model):
    interested_party = models.ForeignKey(InterestedParty, on_delete=models.CASCADE, related_name='needs', null=True, blank=True) 
    needs = models.TextField(blank=True, null=True)
    expectation = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.needs
    

    
    

class NotificationInterest(models.Model):
    interest = models.ForeignKey(InterestedParty, on_delete=models.CASCADE, null=True, blank=True)
    title = models.TextField(blank=True,null=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.title}"
    
class Processes(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="Process", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='Process', null=True, blank=True) 
    CATEGORY_CHOICES = (
        ('Stratgic', 'Stratgic'),
        ('Core', 'Core'),
        ('Support', 'Support'),
        ('Monitoring/Measurment', 'Monitoring/Measurment'),
        ('Outsource', 'Outsource'),       
    )  
    name = models.CharField(max_length=255)
    no = models.CharField(max_length=50, blank=True, null=True)
    type = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Stratgic')
    legal_requirements = models.ManyToManyField('Procedure', related_name='processes', blank=True)
    custom_legal_requirements = models.TextField(blank=True, null=True)
    file = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename,max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    send_notification = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Processes"
        verbose_name_plural = "Processes"   


class NotificationProcess(models.Model):
    
    processes = models.ForeignKey(Processes, on_delete=models.CASCADE, null=True, blank=True)
    title = models.TextField(blank=True,null=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.title}"
    
    

class LegalRequirement(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="legal", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='legal', null=True, blank=True) 
    legal_no = models.CharField(max_length=50,blank =True,null = True)
    document_type = models.CharField(
        max_length=255,blank = True, null =True,
        choices=[
            ('System', 'System'),
            ('Paper', 'Paper'),
            ('External','External'),
            ('Work Instruction','Work Instruction')
  
        ]
    )
    attach_document = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit,max_length=255, blank=True, null=True)
    rivision = models.CharField(max_length=50,blank =True,null = True)
    legal_name =  models.CharField(max_length=50,blank =True,null = True)
    date = models.DateField(blank=True, null=True)
    related_record_format =  models.CharField(max_length=50,blank =True,null = True)
    send_notification = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=False)

    def __str__(self):
        return self.legal_name
    
class NotificationLegal(models.Model):
    
    legal = models.ForeignKey(LegalRequirement, on_delete=models.CASCADE, null=True, blank=True)
    title = models.TextField(blank=True,null=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.title}"
    
    
class Evaluation(models.Model):
    document_type = models.CharField(
        max_length=255,blank = True, null =True,
        choices=[
            ('Legal', 'Legal'),
            ('Business', 'Business'),
            ('Client','Client'),
            ('Process/Specification','Process/Specification')
  
        ]
    )
    STATUS_CHOICES = [
    ('Pending for Review/Checking', 'Pending for Review/Checking'),
    ('Reviewed,Pending for Approval', 'Reviewed,Pending for Approval'),
    ('Pending for Publish','Pending for Publish'),
    ('Correction Requested','Correction Requested'),
    ('Published','Published'),
    ]

    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="evaluation", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='evaluation', null=True, blank=True) 
    no = models.CharField(max_length=50, blank=True, null=True)
    written_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="written_evaluation"
    )
    approved_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, blank=True, null=True, related_name="approved_evaluation"
    )
    checked_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="checked_evaluation"
    )
    
    review_frequency_year = models.TextField(blank=True, null=True)
    review_frequency_month = models.TextField(blank=True, null=True)
    upload_attachment =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit,max_length=255, blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True,unique=True)
    rivision = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending for Review/Checking')
    written_at = models.DateTimeField(null=True, blank=True)
    checked_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    is_draft = models.BooleanField(default=False)
    send_notification_to_checked_by = models.BooleanField(default=False)
    send_email_to_checked_by = models.BooleanField(default=False)
    send_notification_to_approved_by = models.BooleanField(default=False)
    send_email_to_approved_by = models.BooleanField(default=False)
    send_notification = models.BooleanField(default=False)
    related_record_format =  models.CharField(max_length=50, blank=True, null=True)
    remarks =  models.CharField(max_length=50, blank=True, null=True)
    published_at = models.DateTimeField(null=True, blank=True)
    published_user = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True, related_name="published_evaluation")

    def __str__(self):
        return self.title


class CorrectionEvaluation(models.Model):
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, null=True, blank=True)
    to_user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="corrections_to_evaluation", null=True, blank=True)
    from_user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="corrections_from_evaluation", null=True, blank=True)
    correction = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Correction for {self.to_user.email}"
    

class NotificationEvaluations(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="evaluations", null=True, blank=True)   
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, null=True, blank=True)
    title = models.TextField(blank=True,null=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.title}"
    

class ManagementChanges(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="changes", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='changes', null=True, blank=True) 
    moc_no = models.CharField(max_length=50, blank=True, null=True)
    moc_type = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        choices=[
            ('Manual/Procedure', 'Manual/Procedure'),
            ('Guideline/Policy', 'Guideline/Policy'),
            ('Specification/Standards', 'Specification/Standards'),
            ('Facility/Equipment', 'Facility/Equipment'),
            ('System/Process', 'System/Process'),
        ]
    )

    attach_document = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit,max_length=255, blank=True, null=True)
    purpose_of_chnage = models.CharField(max_length=50, blank=True, null=True)
    potential_cosequences =models.CharField(max_length=50, blank=True, null=True)
    moc_remarks = models.CharField(max_length=50, blank=True, null=True)
    moc_title =models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    related_record_format = models.CharField(max_length=50, blank=True, null=True)
    resources_required = models.CharField(max_length=50, blank=True, null=True)
    impact_on_process = models.CharField(max_length=50, blank=True, null=True)
    rivision =models.CharField(max_length=50, blank=True, null=True)
    send_notification = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=False)

    def __str__(self):
        return self.moc_title
    
    
class NotificationChanges(models.Model):       
    changes = models.ForeignKey(ManagementChanges, on_delete=models.CASCADE, null=True, blank=True)
    title = models.TextField(blank=True,null=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.title}"
    
    
class Sustainabilities(models.Model):
    document_type = models.CharField(
        max_length=255,blank = True, null =True,
        choices=[
            ('Legal', 'Legal'),
            ('Business', 'Business'),
            ('Client','Client'),
            ('Process/Specification','Process/Specification')
  
        ]
    )
    STATUS_CHOICES = [
    ('Pending for Review/Checking', 'Pending for Review/Checking'),
    ('Reviewed,Pending for Approval', 'Reviewed,Pending for Approval'),
    ('Pending for Publish','Pending for Publish'),
    ('Correction Requested','Correction Requested'),
    ('Published','Published'),
    ]

    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="sustain", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sustain', null=True, blank=True) 
    no = models.CharField(max_length=50, blank=True, null=True)
    written_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="written_sustain"
    )
    approved_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, blank=True, null=True, related_name="approved_sustain"
    )
    checked_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="checked_sustain"
    )
    
    review_frequency_year = models.TextField(blank=True, null=True)
    review_frequency_month = models.TextField(blank=True, null=True)
    upload_attachment =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit,max_length=255, blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True,unique=True)
    rivision = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending for Review/Checking')
    written_at = models.DateTimeField(null=True, blank=True)
    checked_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    is_draft = models.BooleanField(default=False)
    send_notification_to_checked_by = models.BooleanField(default=False)
    send_email_to_checked_by = models.BooleanField(default=False)
    send_notification_to_approved_by = models.BooleanField(default=False)
    send_email_to_approved_by = models.BooleanField(default=False)
    send_notification = models.BooleanField(default=False)
    related_record_format =  models.CharField(max_length=50, blank=True, null=True)
    remarks =  models.CharField(max_length=50, blank=True, null=True)
    published_at = models.DateTimeField(null=True, blank=True)
    published_user = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True, related_name="published_ustainability")

    def __str__(self):
        return self.title
    
    
class CorrectionSustainability(models.Model):
    sustainability = models.ForeignKey(Sustainabilities, on_delete=models.CASCADE, null=True, blank=True)
    to_user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="corrections_to_sustainability", null=True, blank=True)
    from_user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="corrections_from_sustainability", null=True, blank=True)
    correction = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Correction for {self.to_user.email}"
    

class NotificationSustainability(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="sustainability", null=True, blank=True)   
    sustainability = models.ForeignKey(Sustainabilities, on_delete=models.CASCADE, null=True, blank=True)
    title = models.TextField(blank=True,null=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.title}"
    

def generate_unique_filename1(instance, filename):
    unique_filename = f'{uuid.uuid4().hex}{os.path.splitext(filename)[1]}'
    return os.path.join('awareness/', unique_filename)  


class AwarenessTraining(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="awareness", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='awareness', null=True, blank=True) 
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(
        max_length=255,
        choices=[
            ('YouTube video', 'YouTube video'),
            ('Presentation', 'Presentation'),
            ('Web Link','Web Link')
  
        ],blank=True, null=True
    )
    youtube_link = models.URLField(blank=True, null=True)
    upload_file = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename1,max_length=255, blank=True, null=True)
    web_link = models.CharField(max_length=100,blank=True, null=True)
    is_draft = models.BooleanField(default=False)
     
    
    def __str__(self):
        return self.title
    
def generate_unique_filename_training(instance, filename):
    unique_filename = f'{uuid.uuid4().hex}{os.path.splitext(filename)[1]}'
    return os.path.join('Training_attachments/', unique_filename)


class Training(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="training", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='training', null=True, blank=True) 
    STATUS_CHOICES = [
        ('Internal', 'Internal'),
        ('External', 'External'),
        ('Legal/Regulatory', 'Legal/Regulatory'),
         ('Client', 'Client'),
        ('Online', 'Online')
        
    ]
    TYPE_CHOICES = [
        ('Requested', 'Requested'),
        ('Completed', 'Completed'),
    ]
    training_title =  models.CharField(max_length=100,blank=True, null=True)
    expected_results = models.TextField(blank=True, null=True)
    actual_results = models.TextField(blank=True, null=True)
    type_of_training = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Internal',blank=True, null=True)
    training_attendees = models.ManyToManyField(Users, related_name='training_attendees', blank=True)
    status = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Requested',blank=True, null=True)
    requested_by = models.ForeignKey(Users, related_name='training_requested_by', on_delete=models.SET_NULL, null=True, blank=True)
    date_planned = models.DateField(blank=True, null=True)
    date_conducted = models.DateField(blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    venue = venue = models.CharField(max_length=255,blank=True, null=True)
    attachment = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_training,max_length=255, blank=True, null=True)
    training_evaluation = models.TextField(blank=True, null=True)
    evaluation_date = models.DateField(blank=True, null=True)
    evaluation_by = models.ForeignKey(Users, related_name='evaluation_by', on_delete=models.SET_NULL, null=True, blank=True)
    
    send_notification = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=False)
    
    def __str__(self):
        return self.training_title if self.training_title else "Untitled Training"
    
class TrainingNotification(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="trainingss", null=True, blank=True) 
    training = models.ForeignKey(Training, on_delete=models.CASCADE, null=True, blank=True)
    title = models.TextField(blank=True,null=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.title}"


class EmployeePerformance(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="performance", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='performance', null=True, blank=True) 
    evaluation_title = models.CharField(max_length=100,blank=True, null=True)
    valid_till = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_draft = models.BooleanField(default=False)
    
    def __str__(self):
        return self.evaluation_title
    
class PerformanceQuestions(models.Model):
    performance = models.ForeignKey(EmployeePerformance, on_delete=models.CASCADE, related_name="questions",blank=True, null=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="question", blank=True, null=True)
    question_text = models.TextField(blank=True, null=True)
    answer= models.CharField(blank=True, null=True)
    
   
    def __str__(self):
        if self.performance and self.performance.evaluation_title:
            return f"{self.performance.evaluation_title} - {self.question_text or 'Unnamed Question'}"
        return self.question_text or "Unnamed Question"
    
    
class EmployeeSurvey(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="survey", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='survey', null=True, blank=True) 
    survey_title = models.CharField(max_length=100,blank=True, null=True)
    valid_till = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_draft = models.BooleanField(default=False)
    
    def __str__(self):
        return self.survey_title
    
class SurveyQuestions(models.Model):
    survey = models.ForeignKey(EmployeeSurvey, on_delete=models.CASCADE, related_name="survey",blank=True, null=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="surveqsn", blank=True, null=True)
    question_text = models.TextField(blank=True, null=True)
    answer= models.CharField(blank=True, null=True)
    
   
    def __str__(self):
        if self.survey and self.survey.survey_title:
            return f"{self.survey.survey_title} - {self.question_text or 'Unnamed Question'}"
        return self.question_text or "Unnamed Question"
    
class Scope(models.Model):  
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="scope",null=True, blank=True)
    title = models.CharField(max_length=50, blank=True, null=True,unique=True)
    text = models.TextField(blank=True, null=True)
    energy_policy = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename,max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
   
    def save(self, *args, **kwargs):
        self.clean()  
        super().save(*args, **kwargs)
    def save(self, *args, **kwargs):
        if not self.title or self.title.strip() == "":
            self.title = None

        self.clean()
        super().save(*args, **kwargs)



class Agenda(models.Model):   
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='agenda', null=True, blank=True) 
    title = models.CharField(max_length=255,blank=True, null=True)
    
    def __str__(self):
        return self.title

class Meeting(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="user_meeting", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_meeting', null=True, blank=True) 
    TITLE_CHOICES = [
        ('Normal', 'Normal'),
        ('Specific', 'Specific'),
        
    ]
    agenda = models.ManyToManyField(Agenda, related_name='meeting_agenda', blank=True)
    title = models.CharField(max_length=255,blank=True, null=True )
    date = models.DateField(blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField (blank=True, null=True)
    meeting_type = models.CharField(max_length=50, choices=TITLE_CHOICES ,default ='Normal')
    venue = models.CharField(max_length=255,blank=True, null=True )
    attendees = models.ManyToManyField(Users, related_name='meeting_attendees', blank=True)
    called_by = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True )
    minutes = models.TextField(blank=True, null=True)
    file = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename,max_length=255, null=True, blank=True)
    send_notification = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=False)
    
    
    def __str__(self):
        return self.title


class MeetingNotification(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="meetingss", null=True, blank=True) 
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, null=True, blank=True)
    title = models.TextField(blank=True,null=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.title}"
    
    

    
class Message(models.Model):   
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='message', null=True, blank=True)
    from_user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='message_user', null=True, blank=True) 
    to_user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='to_user', null=True, blank=True) 
    file = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename,max_length=255, null=True, blank=True)
    message = models.TextField(blank=True, null=True)
    subject = models.CharField(max_length=255,blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return self.subject
    
class Audit(models.Model):
    TITLE_CHOICES = [
        ('Internal', 'Internal'),
        ('External', 'External'),
        
    ]
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="audit", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='audit_company', null=True, blank=True)
    title = models.CharField(max_length=50,blank =True,null = True)
    audit_from = models.CharField(max_length=50,blank =True,null = True)
    audit_from_internal =  models.ManyToManyField(Users, related_name='users' ,blank =True)
    area = models.CharField(max_length=50,blank =True,null = True)
    proposed_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True,null=True)
    certification_body  =  models.CharField(max_length=50,blank =True,null = True)
    audit_type =  models.CharField(max_length=50, choices=TITLE_CHOICES ,default ='Internal',blank=True, null=True)
    procedures = models.ManyToManyField('Procedure', related_name='procedures', blank=True,)   
    date_conducted = models.DateField(blank=True, null=True)
    upload_audit_report = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)
    upload_non_coformities_report =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)
    is_draft = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
class Inspection(models.Model):
    TITLE_CHOICES = [
        ('Internal', 'Internal'),
        ('External', 'External'),
        
    ]
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="inspention", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='inspention_company', null=True, blank=True)
    title = models.CharField(max_length=50,blank =True,null = True)
    inspector_from = models.CharField(max_length=50,blank =True,null = True)
    inspector_from_internal =  models.ManyToManyField(Users, related_name='inspector_users' ,blank =True)
    area = models.CharField(max_length=50,blank =True,null = True)
    proposed_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True,null=True)
    certification_body  =  models.CharField(max_length=50,blank =True,null = True)
    inspection_type = models.CharField(max_length=50, choices=TITLE_CHOICES ,default ='Internal',blank=True, null=True)
    procedures = models.ManyToManyField('Procedure', related_name='insprocedures', blank=True,)
        
    date_conducted = models.DateField(blank=True, null=True)
    upload_inspection_report = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)
    upload_non_coformities_report =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)
    is_draft = models.BooleanField(default=False)
    def __str__(self):
        return self.title
    
class Cause(models.Model):   
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='cause', null=True, blank=True) 
    title = models.CharField(max_length=255,blank=True, null=True)
    
    def __str__(self):
        return self.title
    
class RootCause(models.Model):   
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='rt', null=True, blank=True) 
    title = models.CharField(max_length=255,blank=True, null=True)
    
    def __str__(self):
        return self.title

class CarNumber(models.Model):   
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='carnumber', null=True, blank=True) 
    title = models.CharField(max_length=255, blank=True, null=True)
    source = models.CharField(
        max_length=255, blank=True, null=True,
        choices=[
            ('Audit', 'Audit'),
            ('Customer', 'Customer'),
            ('Internal', 'Internal'),
            ('Supplier', 'Supplier')
        ]
    )
    root_cause = models.ForeignKey(RootCause,on_delete=models.CASCADE, related_name='carroot', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    date_raised = models.DateField(blank=True, null=True)
    date_completed = models.DateField(blank=True, null=True)

    Status_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Deleted', 'Deleted')
    ]
    status = models.CharField(max_length=20, choices=Status_CHOICES, default='Pending')
    executor = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True)
    action_no = models.IntegerField(blank=True, null=True)
    action_or_corrections = models.TextField(blank=True, null=True)
    send_notification = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=False)
    send_notification = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
       
        if self.action_no is None and self.company:
            last_action = CarNumber.objects.filter(company=self.company).order_by('-action_no').first()
            self.action_no = 1 if not last_action or not last_action.action_no else last_action.action_no + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title or f"Action #{self.action_no}"


class CarNotification(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="car", null=True, blank=True) 
    carnumber = models.ForeignKey(CarNumber, on_delete=models.CASCADE, null=True, blank=True)
    title = models.TextField(blank=True,null=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.title}"

class InternalProblem(models.Model):
    ACTION_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]

    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="internal", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='internal_com', null=True, blank=True)
    cause = models.ForeignKey(Cause, on_delete=models.CASCADE, related_name="internal_cause", blank=True, null=True)
    problem = models.TextField(blank=True, null=True)
    immediate_action = models.TextField(blank=True, null=True)
    executor = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="internal_executor", blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    solve_after_action = models.CharField(max_length=20, choices=ACTION_CHOICES, default='Yes')
    corrective_action = models.CharField(max_length=20, choices=ACTION_CHOICES, default='Yes')
    correction = models.TextField(blank=True, null=True)
    car_no = models.ForeignKey(CarNumber, on_delete=models.CASCADE, related_name="internal_car", blank=True, null=True)
    is_draft = models.BooleanField(default=False)

    def __str__(self):
        return str(self.company) if self.company else "Internal Problem"


class Supplier(models.Model):
    
    ACTIVE_CHOICES = [
        ('active', 'active'),
        ('blocked', 'blocked'),        
    ] 
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="supplier", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='supplier_com', null=True, blank=True)
    company_name = models.CharField(max_length=50,blank =True,null = True)
    email = models.EmailField(blank =True,null = True) 
    address = models.TextField(blank=True,null=True)
    state = models.CharField(max_length=50,blank =True,null = True)
    country = models.CharField(max_length=50,blank =True,null = True)
    website = models.TextField(blank=True,null=True)
    city =  models.CharField(max_length=50,blank =True,null = True)
    postal_code = models.CharField(max_length=50,blank =True,null = True)
    phone = models.CharField(max_length=50,blank =True,null = True)
    alternate_phone =models.CharField(max_length=50,blank =True,null = True)
    fax =models.CharField(max_length=50,blank =True,null = True)
    contact_person = models.CharField(max_length=50,blank =True,null = True)
    qualified_to_supply = models.CharField(max_length=50,blank =True,null = True)
    notes = models.TextField(blank=True,null=True)
    analysis_needed = models.BooleanField(default=False)
    resolution = models.CharField(max_length=50,blank =True,null = True)
    active = models.CharField(max_length=20, choices=ACTIVE_CHOICES, default='active')
    approved_by = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="supplier_app", blank=True, null=True)
    selection_criteria = models.CharField(max_length=50,blank =True,null = True)
    STATUS_CHOICES = [
        ('Approved', 'Approved'),
        ('Provisional', 'Provisional'),
        ('Not Approved','Not Approved')       
    ] 
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Approved')
    approved_date =  models.DateField(blank=True, null=True)
    is_draft = models.BooleanField(default=False)
    pre_qualification = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit,max_length=255, blank=True, null=True)
    documents = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit,max_length=255, blank=True, null=True)
    

    def __str__(self):
        return self.company_name or "Unnamed Supplier"
    

class SupplierProblem(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="supplier_problem", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='supplier_com_problem', null=True, blank=True)
    TITLE_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
        
    ]
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="supplier_pr", blank=True, null=True)
    problem = models.TextField(blank=True,null=True)
    executor = models.ForeignKey(Users, on_delete=models.CASCADE, null=True )
    corrective_action_need = models.CharField(max_length=50, choices=TITLE_CHOICES ,default ='Yes')
    date =  models.DateField(blank=True, null=True)
    immediate_action = models.TextField(blank=True,null=True)
    solved = models.CharField(max_length=50, choices=TITLE_CHOICES ,default ='Yes')
    no_car = models.ForeignKey(CarNumber, on_delete=models.CASCADE,blank=True, null=True)
    corrections = models.CharField(max_length=50,blank =True,null = True)
    is_draft = models.BooleanField(default=False)

    def __str__(self):
        return self.problem or "No Problem Description"
    
    

class SupplierEvaluation(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="supp_eval", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='supp_eval_com', null=True, blank=True) 
    title = models.CharField(max_length=100,blank=True, null=True)
    valid_till = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_draft = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
class SupplierEvaluationQuestions(models.Model):
    supp_evaluation = models.ForeignKey(SupplierEvaluation, on_delete=models.CASCADE, related_name="supp_evlua",blank=True, null=True)
    Supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="surveqsn_supp", blank=True, null=True)
    question_text = models.TextField(blank=True, null=True)
    answer= models.CharField(blank=True, null=True)
    
   
    def __str__(self):
        if self.supp_evaluation and self.supp_evaluation.title:
            return f"{self.supp_evaluation.title} - {self.question_text or 'Unnamed Question'}"
        return self.question_text or "Unnamed Question"
    

class Customer(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="cus_problem", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='cuscom_problem', null=True, blank=True)
    name = models.CharField(max_length=100,blank =True,null = True)
    address =  models.TextField(blank=True,null=True)
    city = models.CharField(max_length=100,blank =True,null = True)
    state = models.CharField(max_length=100,blank =True,null = True)
    zipcode = models.CharField(max_length=100,blank =True,null = True)
    country = models.CharField(max_length=100,blank =True,null = True)
    email = models.EmailField(blank =True,null = True)
    contact_person = models.CharField(max_length=50,blank =True,null = True)
    phone = models.CharField(max_length=100, blank=True) 
    alternate_phone = models.CharField(max_length=100, blank=True)
    fax = models.CharField(max_length=100,blank =True,null = True)
    notes = models.TextField(blank=True,null=True)
    upload_attachment = models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit,max_length=255, blank=True, null=True)
    is_draft = models.BooleanField(default=False)
     
    def __str__(self):
        return self.name

   
class Category(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='category', null=True, blank=True) 
    title = models.CharField(max_length=255,blank=True, null=True)
    
    def __str__(self):
        return self.title


class Complaints(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="complaint", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='complaint_cus', null=True, blank=True)
    TITLE_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
        
    ] 
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True )
    details = models.TextField(blank=True,null=True)
    executor = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True )
    corrections = models.CharField(max_length=50,blank =True,null = True)
    solved_after_action =  models.CharField(max_length=50, choices=TITLE_CHOICES ,default ='Yes')
    category = models.ManyToManyField(Category, related_name='category' ,blank =True)
    immediate_action = models.TextField(blank=True,null=True)
    date = models.DateField(blank=True, null=True)
    corrective_action_need = models.CharField(max_length=50, choices=TITLE_CHOICES ,default ='Yes')
    no_car = models.ForeignKey(CarNumber, on_delete=models.CASCADE, null=True )
    upload_attachment =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)
    is_draft = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.customer.name)
    
    

    
    
class CustomerSatisfaction(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="cus_us", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='cus_comp', null=True, blank=True) 
    title = models.CharField(max_length=100,blank=True, null=True)
    valid_till = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_draft = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title


class CustomerQuestions(models.Model):
    customer = models.ForeignKey(CustomerSatisfaction, on_delete=models.CASCADE, related_name="supp_evlua",blank=True, null=True)
    customer_qsn= models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="us_user", blank=True, null=True)
    question_text = models.TextField(blank=True, null=True)
    answer= models.CharField(blank=True, null=True)
    
   
    def __str__(self):
        if self.customer and self.customer.name:
            return f"{self.customer.name} - {self.question_text or 'Unnamed Question'}"
        return self.question_text or "Unnamed Question"
    
    
class EmployeeTrainingEvaluation(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="aaaa", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='bbbbb', null=True, blank=True) 
    evaluation_title = models.CharField(max_length=100,blank=True, null=True)
    valid_till = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_draft = models.BooleanField(default=False)
    
    def __str__(self):
        return self.evaluation_title
    
class EmployeeTrainingEvaluationQuestions(models.Model):
    emp_training_eval = models.ForeignKey(EmployeeTrainingEvaluation, on_delete=models.CASCADE, related_name="ddd",blank=True, null=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="ccc", blank=True, null=True)
    question_text = models.TextField(blank=True, null=True)
    answer= models.CharField(blank=True, null=True)
    
   
    def __str__(self):
        if self.emp_training_eval and self.emp_training_eval.evaluation_title:
            return f"{self.emp_training_eval.evaluation_title} - {self.question_text or 'Unnamed Question'}"
        return self.question_text or "Unnamed Question"