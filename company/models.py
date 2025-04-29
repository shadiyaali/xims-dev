
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

    


    


    



class Question(models.Model):
    question_text = models.TextField(blank=True, null=True)
   

    def __str__(self):
        return self.question_text 
    
class CustomerSatisfaction(models.Model):
    title = models.CharField(max_length=50,blank =True,null = True)
    calid_till  = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True,null=True)
    questions = models.ForeignKey(Question, blank=True,null=True ,on_delete=models.SET_NULL,)
    answer = models.IntegerField(blank=True, null=True) 
    # customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True )
    

    def __str__(self):
        return self.title
    


    


class ProcessActivity(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.title if self.title else "No Title Provided"
    

class EnvironmentalAspect(models.Model):
    aspect_source = models.CharField(max_length=50, blank=True, null=True)
    aspect = models.CharField(max_length=50, blank=True, null=True)
    process_activity = models.ForeignKey(ProcessActivity, on_delete=models.SET_NULL, null=True )
    description =  models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    written_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="written_aspect"
    )
    approved_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_aspect"
    )
    checked_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="checked_aspect"
    )
    level_of_impact = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        choices=[
            ('Significant', 'Significant'),
            ('Non Significant', 'Non Significant'),
    
        ]
    )
    aspect_name = models.CharField(max_length=50, blank=True, null=True)
    legal_requirement = models.CharField(max_length=50, blank=True, null=True)
    action = models.CharField(max_length=50, blank=True, null=True)
    send_notification = models.BooleanField(default=False)
    
    def __str__(self):
        return self.aspect_name
    


class EnvironmentalImpact(models.Model):
    impact_assessment = models.CharField(max_length=50, blank=True, null=True)
    related_record = models.CharField(max_length=50, blank=True, null=True)   
    date = models.DateField(blank=True, null=True)
    written_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="written_impact"
    )
    approved_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_impact"
    )
    checked_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="checked_impact"
    )
  
    assessment_name = models.CharField(max_length=50, blank=True, null=True)
    rivision = models.CharField(max_length=50, blank=True, null=True)
    attach_document = models.FileField(
        storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True
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
    send_notification = models.BooleanField(default=False)
    public = models.BooleanField(default=False)

    def __str__(self):
        return self.impact_assessment
    


 
    

class EnvironmentalIncidents(models.Model):
    source = models.CharField(max_length=50, blank=True, null=True)
    incident = models.CharField(max_length=50, blank=True, null=True)
    # root_cause = models.ForeignKey(RootCause, on_delete=models.SET_NULL, null=True )
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
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_incidents"
    )
    action =  models.TextField(blank=True, null=True)
    date_completed = models.DateField(blank=True, null=True)
    send_notification = models.BooleanField(default=False)

    def __str__(self):
        return self.source  


class EnvironmentalWaste(models.Model):
    wmp = models.CharField(max_length=50, blank=True, null=True)
    written_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="written_waste"
    )
    approved_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_waste"
    )
    checked_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="checked_waste"
    )
    originator = models.CharField(max_length=50, blank=True, null=True)
    waste_type = models.CharField(max_length=50, blank=True, null=True)
    waste_quantity = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=50, blank=True, null=True)
    waste_handling = models.CharField(
        max_length=255,blank = True, null =True,
        choices=[
            ('Company', 'Company'),
            ('Client', 'Client'),
            ('Contractor','Contractor'),
            ('Third Party/Others','Third Party/Others')
  
        ]
    )
    waste_category = models.CharField(
        max_length=255,blank = True, null =True,
        choices=[
            ('Hazardous', 'Hazardous'),
            ('Non Hazardous', 'Non Hazardous'),  
        ]
    )
    waste_minimization = models.CharField(
        max_length=255,blank = True, null =True,
        choices=[
            ('Reuse', 'Reuse'),
            ('Recycle', 'Recycle'),
            ('Recovery','Recovery'),
            ('Disposal','Disposal'),
            ('Non Disposable','Non Disposable'),
        ]
    )
    responsible_party = models.CharField(max_length=50, blank=True, null=True)
    legal_requirement = models.CharField(max_length=50, blank=True, null=True)
    remark = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.wmp  
    
class ProcessHealth(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.title  
    
class HealthSafety(models.Model):
    hazard_source = models.CharField(max_length=50, blank=True, null=True)
    hazard = models.CharField(max_length=50, blank=True, null=True)
    process_activity = models.ForeignKey(ProcessHealth, on_delete=models.SET_NULL, null=True )
    description =  models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    written_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="written_hazard"
    )
    approved_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_hazard"
    )
    checked_by = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="checked_hazard"
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
    hazard_name = models.CharField(max_length=50, blank=True, null=True)
    legal_requirement = models.CharField(max_length=50, blank=True, null=True)
    action = models.CharField(max_length=50, blank=True, null=True)
    
    
    def __str__(self):
        return self.hazard_name
    
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
    

class ReviewType(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.title  

class EnergyReview(models.Model):
    review_no = models.CharField(max_length=50, blank=True, null=True)
    rivision = models.CharField(max_length=50, blank=True, null=True)
    review_type = models.ForeignKey(ReviewType, on_delete=models.SET_NULL, null=True )
    upload_attachment =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)    
    date  = models.DateField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    energy_name = models.CharField(max_length=50, blank=True, null=True) 
    relate_business_process = models.CharField(max_length=20, blank=True, null=True )
    relate_document_process = models.CharField(max_length=20, blank=True, null=True )
    publish = models.BooleanField(default=False)

    def __str__(self):
        return self.energy_name   
    
class BaselineReview(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.title or "No Title Provided"
    
class Baseline(models.Model):
    basline_title = models.CharField(max_length=50, blank=True, null=True)
    established_basline = models.CharField(max_length=50, blank=True, null=True)
    remarks =  models.TextField(blank=True, null=True)
    energy_review = models.ForeignKey(BaselineReview, on_delete=models.SET_NULL, null=True )
    date  = models.DateField(blank=True, null=True)
    responsible = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_baseline"
    )

    def __str__(self):
      return self.basline_title or "No Title Provided"


class Enpis(models.Model):
    enpi = models.CharField(max_length=50, blank=True, null=True)
    baseline = models.ForeignKey(
        Baseline, on_delete=models.CASCADE, null=True, related_name="enpis"
    )

    def __str__(self):
        return f"Additional enpi for {self.baseline.basline_title if self.baseline else 'No Baseline'}"



class EnergySource(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.title or "No Title Provided"
    
class SignificantEnergy(models.Model):
    significant = models.CharField(max_length=50, blank=True, null=True)
    source_type = models.ForeignKey(EnergySource, on_delete=models.SET_NULL, null=True )
    upload_attachment =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)    
    consumption =  models.CharField(max_length=50, blank=True, null=True)
    consequences =  models.CharField(max_length=50, blank=True, null=True)
    remarks =  models.TextField(blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    facility = models.CharField(max_length=50, blank=True, null=True)
    action = models.CharField(max_length=50, blank=True, null=True)
    impact = models.CharField(max_length=50, blank=True, null=True)
    rivision = models.CharField(max_length=50, blank=True, null=True)
    publish = models.BooleanField(default=False)


    def __str__(self):
        return self.significant or "No Title Provided"


class EnergyImprovement(models.Model):
    eio = models.CharField(max_length=50, blank=True, null=True)
    target = models.CharField(max_length=50, blank=True, null=True)
    results =  models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    STATUS_CHOICES = [
        ('On Going', 'On Going'),
        ('Achieved', 'Achieved'),
        ('Not Achieved', 'Not Achieved'),
        ('Modified', 'Modified'),       
    ] 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='On Going')
    eio_title = models.CharField(max_length=50, blank=True, null=True)
    associated_objective = models.CharField(max_length=50, blank=True, null=True)
    responsible = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_energy_improvements"
    )
    upload_attachment =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)

    def __str__(self):
        return self.eio or "No Title Provided"
    

class EnergyAction(models.Model):
    action_plan =  models.CharField(max_length=50, blank=True, null=True)
    associative_objective =  models.CharField(max_length=50, blank=True, null=True)
    legal_requirements =  models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    energy_improvements = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    upload_attachment =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)
    means = models.CharField(max_length=50, blank=True, null=True)
    responsible = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_energy_action_plan"
    )
    statement = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.action_plan or "No Title Provided"
    
class Program(models.Model):
    Program = models.CharField(max_length=50, blank=True, null=True)
    energy_action = models.ForeignKey(
    EnergyAction, on_delete=models.CASCADE, null=True, related_name="programs"
)

    def __str__(self):
        return f"Additional program for {self.energy_action.action_plan if self.energy_action else 'No Baseline'}"
    

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
    
class PreventiveAction(models.Model): 
    title =  models.CharField(max_length=255,blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    date_raised = models.DateField(blank=True, null=True)
    date_completed = models.DateField(blank=True, null=True)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed')
            
    ] 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    executor = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True )
    action =  models.TextField(blank=True, null=True)
    send_notification = models.BooleanField(default=False)

    def __str__(self):
        return self.title or "No Title Provided"


class Objectives(models.Model): 
    objective = models.CharField(max_length=255,blank=True, null=True)
    performance = models.TextField(blank=True, null=True)
    target_date = models.DateField(blank=True, null=True)
    reminder_date = models.DateField(blank=True, null=True)
    STATUS_CHOICES = [
        ('On Going', 'On Going'),
        ('Achieved', 'Achieved'),
        ('Not Achieved', 'Not Achieved'),
        ('Modified', 'Modified'),       
    ] 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='On Going')
    indicator = models.CharField(max_length=255,blank=True, null=True)
    responsible = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_planobjectives")
    

    def __str__(self):
        return self.objective or "No Title Provided"


class TargetsP(models.Model):
    target =  models.CharField(max_length=50, blank=True, null=True)
    associative_objective =  models.CharField(max_length=50, blank=True, null=True)
    target_date = models.DateField(blank=True, null=True)
    reminder_date = models.DateField(blank=True, null=True)
    STATUS_CHOICES = [
        ('On Going', 'On Going'),
        ('Achieved', 'Achieved'),
        ('Not Achieved', 'Not Achieved'),
        ('Modified', 'Modified'),       
    ] 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='On Going')
    results = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    upload_attachment =  models.FileField(storage=MediaStorage(), upload_to=generate_unique_filename_audit, blank=True, null=True)    
    responsible = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="approved_targets"
    )
    

    def __str__(self):
        return self.target or "No Title Provided"
    
class TProgram(models.Model):
    Program = models.CharField(max_length=50, blank=True, null=True)
    targets = models.ForeignKey(
    TargetsP, on_delete=models.CASCADE, null=True, related_name="programs"
)

    def __str__(self):
        return f"Additional program for {self.targets.target if self.targets else 'No Targets'}"


class ConformityCause(models.Model):   
    title = models.CharField(max_length=255,blank=True, null=True)
    
    def __str__(self):
        return self.title

class Conformity(models.Model):
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
    ncr = models.CharField(max_length=50, blank=True, null=True)
    root_cause = models.ForeignKey(ConformityCause, on_delete=models.SET_NULL, null=True )
    description = models.TextField(blank=True, null=True)
    date_raised = models.DateField(blank=True, null=True)
    date_completed = models.DateField(blank=True, null=True)
    Status_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Deleted','Deleted')
        
    ]
    status = models.CharField(max_length=20, choices=Status_CHOICES, default='Pending')
    title = models.CharField(max_length=50, blank=True, null=True)
    executor = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True )
    resolution = models.TextField(blank=True, null=True)
    send_notification = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
 