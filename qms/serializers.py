
from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password
from company.serializers import *
from django.conf import settings     
import json  





class DocumentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyDocumentation
        fields = '__all__'  


class ManualGetSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(write_only=True, required=True)
    approved_by = UserSerializer(read_only=True) 
    written_by = UserSerializer(read_only=True) 
    checked_by =UserSerializer(read_only=True) 
    
    
    class Meta:
        model = Manual
        fields = '__all__'
        
        

class ManualSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manual
        fields = '__all__'
    extra_kwargs = {
            'approved_by': {'required': False, 'allow_null': True},
        }   
    def validate_upload_attachment(self, value):
        if value and value.size > settings.MAX_UPLOAD_SIZE:
            raise serializers.ValidationError("File size should not exceed 10 MB.")
        return value

class ManualViewAllSerializer(serializers.ModelSerializer):
    written_by = UserSerializer()
    approved_by = UserSerializer()
    checked_by = UserSerializer()
    published_user = UserSerializer()

    class Meta:
        model = Manual
        fields = '__all__'       
 
       
class RecordFormatSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordFormat
        fields = '__all__'

        
class RecordFormatGetSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(write_only=True, required=True)
    approved_by = UserSerializer(read_only=True) 
    
    class Meta:
        model = RecordFormat
        fields = '__all__'

       
class NotificationSerializer(serializers.ModelSerializer):
    manual = ManualViewAllSerializer()  
    class Meta:
        model = NotificationQMS
        fields = "__all__"
        
class CorrectionQMSSerializer(serializers.ModelSerializer):
    to_user_email = serializers.EmailField(source='to_user.email', read_only=True)
    from_user_email = serializers.EmailField(source='from_user.email', read_only=True)
    manual_title = serializers.CharField(source='manual.title', read_only=True)

    class Meta:
        model = CorrectionQMS
        fields = [
            'id', 
            'manual', 
            'manual_title',
            'to_user', 
            'to_user_email',
            'from_user', 
            'from_user_email',
            'correction', 
            'created_at'
        ]
        


class CorrectionGetQMSSerializer(serializers.ModelSerializer):
    to_user = UserSerializer(read_only=True) 
    from_user= UserSerializer(read_only=True) 
    manual_title = serializers.CharField(source='manual.title', read_only=True)

    class Meta:
        model = CorrectionQMS
        fields = [
            'id', 
            'manual', 
            'manual_title',
            'to_user', 
            'to_user',
            'from_user', 
            'from_user',
            'correction', 
            'created_at'
        ]
        
class ManualUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manual
        fields = '__all__'
        extra_kwargs = {
          
            'written_at': {'read_only': True},
            'checked_at': {'read_only': True},
            'approved_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }
    

    def update(self, instance, validated_data):
      
        validated_data['status'] = 'Pending for Review/Checking'       
        return super().update(instance, validated_data)



class ProcedureSerializer(serializers.ModelSerializer):
 
    class Meta:
        model = Procedure
        fields = '__all__'
        
    

class ProcedureGetSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(write_only=True, required=True)
    approved_by = UserSerializer(read_only=True) 
    written_by = UserSerializer(read_only=True) 
    checked_by =UserSerializer(read_only=True) 
    
    
    class Meta:
        model = Procedure
        fields = '__all__'
        
class ProcedureUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procedure
        fields = '__all__'
        extra_kwargs = {
            'written_at': {'read_only': True},
            'checked_at': {'read_only': True},
            'approved_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }

    def update(self, instance, validated_data):
      
        validated_data['status'] = 'Pending for Review/Checking'       
        return super().update(instance, validated_data)
    
# class CorrectionProcedureSerializer(serializers.ModelSerializer):
#     to_user_email = serializers.EmailField(source='to_user.email', read_only=True)
#     from_user_email = serializers.EmailField(source='from_user.email', read_only=True)
#     procedure_title = serializers.CharField(source='procedure.title', read_only=True)

#     class Meta:
#         model = CorrectionProcedure
#         fields = [
#             'id', 
#             'procedure', 
#             'procedure_title',
#             'to_user', 
#             'to_user_email',
#             'from_user', 
#             'from_user_email',
#             'correction', 
#             'created_at'
#         ]



class CorrectionProcedureSerializer(serializers.ModelSerializer):
    to_user = UserSerializer(read_only=True)
    
    from_user = UserSerializer(read_only=True)
    
    procedure_title = serializers.CharField(source='procedure.title', read_only=True)

    class Meta:
        model = CorrectionProcedure
        fields = [
            'id', 
            'procedure', 
            
            'procedure_title',
            'to_user', 
         
            'from_user', 
          
            'correction', 
            'created_at'
        ]

class ProcedureViewAllSerializer(serializers.ModelSerializer):
    written_by = UserSerializer()
    approved_by = UserSerializer()
    checked_by = UserSerializer()
    published_user = UserSerializer()

    class Meta:
        model = Procedure
        fields = '__all__'  

class NotificationProcedureSerializer(serializers.ModelSerializer):
    procedure = ProcedureViewAllSerializer()  
    class Meta:
        model = NotificatioProcedure
        fields = "__all__"
        
        
class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordFormat
        fields = '__all__'
        
    def validate_upload_attachment(self, value):
        if value and value.size > settings.MAX_UPLOAD_SIZE:
            raise serializers.ValidationError("File size should not exceed 10 MB.")
        return value
    
class RecordGetSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(write_only=True, required=True)
    approved_by = UserSerializer(read_only=True) 
    written_by = UserSerializer(read_only=True) 
    checked_by =UserSerializer(read_only=True) 
    
    
    class Meta:
        model = RecordFormat
        fields = '__all__'


class RecordUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordFormat
        fields = '__all__'
        extra_kwargs = {
            'written_at': {'read_only': True},
            'checked_at': {'read_only': True},
            'approved_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }

    def update(self, instance, validated_data):
      
        validated_data['status'] = 'Pending for Review/Checking'       
        return super().update(instance, validated_data)
    
class CorrectionRecordSerializer(serializers.ModelSerializer):
    to_user = UserSerializer(read_only=True)
    
    from_user = UserSerializer(read_only=True)
    
    record_title = serializers.CharField(source='precord.title', read_only=True)

    class Meta:
        model = CorrectionRecord
        fields = [
            'id', 
            'record', 
            
            'record_title',
            'to_user', 
         
            'from_user', 
          
            'correction', 
            'created_at'
        ]


class RecordViewAllSerializer(serializers.ModelSerializer):
    written_by = UserSerializer()
    approved_by = UserSerializer()
    checked_by = UserSerializer()
    published_user = UserSerializer()

    class Meta:
        model = RecordFormat
        fields = '__all__'  

class NotificationRecordSerializer(serializers.ModelSerializer):
    record = RecordViewAllSerializer()  
    class Meta:
        model = NotificationRecord
        fields = "__all__"



class ComplianceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compliances
        fields = '__all__'


class NeedsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Needs
        fields = '__all__'        

        
        
class InterestedPartySerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestedParty
        fields = '__all__'
        
class CausePartySerializer(serializers.ModelSerializer):
    class Meta:
        model = CauseParty
        fields = '__all__'
        
class InterestedPartyGetSerializer(serializers.ModelSerializer):
    needs = NeedsSerializer(many=True, read_only=True)
    type = CausePartySerializer()
    user = UserSerializer()
    class Meta:
        model = InterestedParty
        fields = '__all__'


class ProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Processes
        fields = '__all__'
    
class ProcessManySerializer(serializers.ModelSerializer):
    # Add nested representation of legal requirements
    legal_requirement_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Processes
        fields = '__all__'
    
    def get_legal_requirement_details(self, instance):
        return [
            {
                'id': procedure.id,
                'title': procedure.title,
                'no': procedure.no,
                'document_type': procedure.document_type,
                'status': procedure.status
            }
            for procedure in instance.legal_requirements.all()
        ]

 

class LegalSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalRequirement
        fields = '__all__'
        
class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = '__all__'
        
        
class EvaluationGetSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(write_only=True, required=True)
    approved_by = UserSerializer(read_only=True) 
    written_by = UserSerializer(read_only=True) 
    checked_by =UserSerializer(read_only=True) 
    
    
    class Meta:
        model = Evaluation
        fields = '__all__'
        
class EvaluationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = '__all__'
        extra_kwargs = {
            'written_at': {'read_only': True},
            'checked_at': {'read_only': True},
            'approved_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }

    def update(self, instance, validated_data):
      
        validated_data['status'] = 'Pending for Review/Checking'       
        return super().update(instance, validated_data)
    

class CorrectionEvaluationSerializer(serializers.ModelSerializer):
    to_user = UserSerializer(read_only=True)
    
    from_user = UserSerializer(read_only=True)
    
    evaluation_title = serializers.CharField(source='evaluation.title', read_only=True)

    class Meta:
        model = CorrectionEvaluation
        fields = [
            'id', 
            'evaluation', 
            
            'evaluation_title',
            'to_user', 
         
            'from_user', 
          
            'correction', 
            'created_at'
        ]
        

class EvaluationViewAllSerializer(serializers.ModelSerializer):
    written_by = UserSerializer()
    approved_by = UserSerializer()
    checked_by = UserSerializer()
    published_user = UserSerializer()

    class Meta:
        model = Evaluation
        fields = '__all__'  

class NotificationEvaluationSerializer(serializers.ModelSerializer):
    procedure = EvaluationViewAllSerializer()  
    class Meta:
        model = NotificationEvaluations
        fields = "__all__"


class ChangesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagementChanges
        fields = '__all__'
        
        
class SustainabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Sustainabilities
        fields = '__all__'
        
        
        
class SustainabilityGetSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(write_only=True, required=True)
    approved_by = UserSerializer(read_only=True) 
    written_by = UserSerializer(read_only=True) 
    checked_by =UserSerializer(read_only=True) 
    
    
    class Meta:
        model = Sustainabilities
        fields = '__all__'

class SustainabilityUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sustainabilities
        fields = '__all__'
        extra_kwargs = {
            'written_at': {'read_only': True},
            'checked_at': {'read_only': True},
            'approved_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }

    def update(self, instance, validated_data):
      
        validated_data['status'] = 'Pending for Review/Checking'       
        return super().update(instance, validated_data)


class CorrectionSustainabilitySerializer(serializers.ModelSerializer):
    to_user = UserSerializer(read_only=True)
    
    from_user = UserSerializer(read_only=True)
    
    sustainability_title = serializers.CharField(source='sustainability.title', read_only=True)

    class Meta:
        model = CorrectionSustainability
        fields = [
            'id', 
            'sustainability', 
            
            'sustainability_title',
            'to_user', 
         
            'from_user', 
          
            'correction', 
            'created_at'
        ]
        


class SustainabilityViewAllSerializer(serializers.ModelSerializer):
    written_by = UserSerializer()
    approved_by = UserSerializer()
    checked_by = UserSerializer()
    published_user = UserSerializer()

    class Meta:
        model = Evaluation
        fields = '__all__' 
               
class NotificationSustainabilitySerializer(serializers.ModelSerializer):
    procedure = SustainabilityViewAllSerializer()  
    class Meta:
        model = NotificationSustainability
        fields = "__all__"


class AwarenessSerializer(serializers.ModelSerializer):
    class Meta:
        model = AwarenessTraining
        fields = '__all__'
        
        
class TrainingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Training
        fields = '__all__'  
        

class TrainingGetSerializer(serializers.ModelSerializer):
    requested_by = UserSerializer(read_only=True)
    evaluation_by = UserSerializer(read_only=True)
    training_attendees = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Training
        fields = '__all__'
        
class EmployeeEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeePerformance
        fields = '__all__'
        
        
class PerformanceQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceQuestions
        fields = ['id', 'performance', 'question_text', 'answer']
        
class EmployeeSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSurvey
        fields = '__all__'
        
class SurveyQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyQuestions
        fields = ['id', 'survey', 'question_text', 'answer']
        

class ScopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scope
        fields = '__all__'  


class AgendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agenda
        fields = '__all__'

class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = '__all__'


class MeetingGetSerializer(serializers.ModelSerializer):
 
    called_by = UserSerializer(read_only=True)
    attendees = UserSerializer(many=True, read_only=True)
    agenda = AgendaSerializer(many=True, read_only=True)

    class Meta:
        model = Meeting
        fields = '__all__'
        
class MessageSerializer(serializers.ModelSerializer):
    to_user = serializers.PrimaryKeyRelatedField(
        queryset=Users.objects.all(),
        many=True
    )

    class Meta:
        model = Message
        fields = '__all__'

    def create(self, validated_data):
        to_user = validated_data.pop('to_user', [])
        message = Message.objects.create(**validated_data)
        message.to_user.set(to_user)
        return message
    
    
class AuditSerializer(serializers.ModelSerializer):

    class Meta:
        model = Audit
        fields = '__all__' 


class AuditGetSerializer(serializers.ModelSerializer):
    procedures = serializers.SerializerMethodField()
    audit_from_internal = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Audit
        fields = '__all__'

    def get_procedures(self, instance):
        return [
            {
                'id': procedure.id,
                'title': procedure.title,
                'no': procedure.no,
                'document_type': procedure.document_type,
                'status': procedure.status
            }
            for procedure in instance.procedures.all()
        ]

    def get_audit_from_internal(self, instance):
        return [
            {
                'id': user.id,
                'name': user.first_name,   
                'email': user.email   
            }
            for user in instance.audit_from_internal.all()
        ]

class AuditFileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audit
        fields = ['upload_audit_report', 'upload_non_coformities_report']
        
class InspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inspection
        fields = '__all__'



class InspectionGetSerializer(serializers.ModelSerializer):
    procedures = serializers.SerializerMethodField()
    inspector_from_internal  = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Inspection
        fields = '__all__'

    def get_procedures(self, instance):
        return [
            {
                'id': procedure.id,
                'title': procedure.title,
                'no': procedure.no,
                'document_type': procedure.document_type,
                'status': procedure.status
            }
            for procedure in instance.procedures.all()
        ]

    def get_inspector_from_internal(self, instance):
        return [
            {
                'id': user.id,
                'name': user.first_name,   
                'email': user.email   
            }
            for user in instance.inspector_from_internal.all()
        ]
        
class InspectionFileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inspection
        fields = ['upload_inspection_report', 'upload_non_coformities_report']
        
        
class CauseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cause
        fields = '__all__'
        
class RootCauseSerializer(serializers.ModelSerializer):
    class Meta:
        model = RootCause
        fields = '__all__'
        
class CarNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarNumber
        fields = '__all__' 

   
 
 

class InternalProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalProblem
        fields = '__all__'

    def validate(self, data):
        corrective_action = data.get('corrective_action', self.instance.corrective_action if self.instance else 'Yes')
        
 
        if corrective_action == 'No':
            data['correction'] = None
            data['car_no'] = None
        
     
        elif corrective_action == 'Yes' and 'correction' in data and not data['correction']:
            raise serializers.ValidationError({
                'correction': 'Correction is required when corrective action is Yes'
            })
            
        return data


       
class InternalProblemGetSerializer(serializers.ModelSerializer):
    cause = CauseSerializer()
    car_no = CarNumberSerializer()
    executor = UserSerializer()
    class Meta:
        model = InternalProblem
        fields = '__all__'


     
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__' 
        
     
class SupplierGetSerializer(serializers.ModelSerializer):
    approved_by = UserSerializer()
    class Meta:
        model = Supplier
        fields = '__all__' 
               
 
        
class SupplierProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierProblem
        fields = '__all__'


class SupplierProblemGetSerializer(serializers.ModelSerializer):
    supplier = SupplierSerializer()
    no_car = CarNumberSerializer()
    executor =UserSerializer
    class Meta:
        model = SupplierProblem
        fields = '__all__'

class SupplierEvaluationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SupplierEvaluation
        fields = '__all__'
        
        
class SupEvalQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierEvaluationQuestions
        fields = ['id', 'supp_evaluation', 'question_text', 'answer']

     
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__' 


class CarNumberGetSerializer(serializers.ModelSerializer):
    executor = UserSerializer()
    root_cause = RootCauseSerializer()
    supplier = SupplierSerializer()
    
    class Meta:
        model = CarNumber
        fields = '__all__'    
        
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ComplaintsSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), 
        many=True,
        required=False   
    )

    class Meta:
        model = Complaints
        fields = '__all__'


class ComplaintGetSerializer(serializers.ModelSerializer):
    no_car = CarNumberSerializer()
    executor = UserSerializer()
    customer = CustomerSerializer()  
    category = CategorySerializer(many=True)
    user = UserSerializer()
    
    class Meta:
        model = Complaints
        fields = '__all__'




class CustomerQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerQuestions
        fields = '__all__' 
        
class CustomerSatisfactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomerSatisfaction
        fields = '__all__'


        
class TrainingEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeTrainingEvaluation
        fields = '__all__'
        
class TrainingEvaluationQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeTrainingEvaluationQuestions
        fields = ['id', 'emp_training_eval', 'question_text', 'answer']
        

class MessageListSerializer(serializers.ModelSerializer):
    from_user = UserSerializer()  
    to_user = UserSerializer(many=True)
    class Meta:
        model = Message
        fields = '__all__'
   
 
        
        
class PreventiveActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreventiveAction
        fields = '__all__'
        
        
class PreventiveActionGetSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    executor =UserSerializer()
    class Meta:
        model = PreventiveAction
        fields = '__all__'
        
        

class ObjectivesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Objectives
        fields = '__all__'



class ObjectivesGetSerializer(serializers.ModelSerializer):
    responsible = UserSerializer()
    class Meta:
        model = Objectives
        fields = '__all__'

 
class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Programs
        fields = ['title']


class TargetsGetSerializer(serializers.ModelSerializer):
    programs = ProgramSerializer(many=True, required=False)
    responsible = UserSerializer()
    user = UserSerializer()
    class Meta:
        model = Targets
        fields = '__all__'

class TargetSerializer(serializers.ModelSerializer):
    programs = ProgramSerializer(many=True, required=False)

    class Meta:
        model = Targets
        fields = [
            'id', 'user', 'company', 'target', 'associative_objective',
            'target_date', 'reminder_date', 'status', 'results',
            'title', 'upload_attachment', 'responsible', 'is_draft',
            'programs'
        ]

    def create(self, validated_data):
        programs_data = validated_data.pop('programs', [])
        target = Targets.objects.create(**validated_data)
        for program_data in programs_data:
            Programs.objects.create(target=target, **program_data)
        return target

    def update(self, instance, validated_data):
        programs_data = validated_data.pop('programs', None)

     
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

  
        if programs_data is not None:
            instance.programs.all().delete()  
            for program_data in programs_data:
                Programs.objects.create(target=instance, **program_data)

        return instance

 
class ConformityCauseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConformityCause
        fields = '__all__'
        
class ConformitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ConformityReport
        fields = '__all__' 
        
class ConformityGetSerializer(serializers.ModelSerializer):
    supplier = SupplierSerializer()
    user = UserSerializer()
    root_cause =ConformityCauseSerializer()
    executor = UserSerializer()
    
    
    class Meta:
        model = ConformityReport
        fields = '__all__' 
        
        
        
class ReviewTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewType
        fields = '__all__'
        
        
        
class EnergyReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyReview
        fields = '__all__'
        
class EnergyReviewGetSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    review_type =ReviewTypeSerializer()
    class Meta:
        model = EnergyReview
        fields = '__all__'
        
        
        
class BaselineReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaselineReview
        fields = '__all__'

class EnpisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enpis
        fields = ['id', 'enpi']  



class BaselineGetSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    responsible = UserSerializer()
    energy_review = BaselineReviewSerializer()
    enpis = EnpisSerializer(many=True, required=False)  
 
    
    class Meta:
        model = Baseline
        fields = '__all__'


class BaselineSerializer(serializers.ModelSerializer):
    enpis = EnpisSerializer(many=True, required=False)  
 

    class Meta:
        model = Baseline
        fields = '__all__'

    def create(self, validated_data):
        enpis_data = validated_data.pop('enpis', [])
        baseline = Baseline.objects.create(**validated_data)
        for enpi_data in enpis_data:
            Enpis.objects.create(baseline=baseline, **enpi_data)
        return baseline

    def update(self, instance, validated_data):
        enpis_data = validated_data.pop('enpis', [])
        instance.basline_title = validated_data.get('basline_title', instance.basline_title)
        instance.established_basline = validated_data.get('established_basline', instance.established_basline)
        instance.remarks = validated_data.get('remarks', instance.remarks)
        instance.energy_review = validated_data.get('energy_review', instance.energy_review)
        instance.date = validated_data.get('date', instance.date)
        instance.responsible = validated_data.get('responsible', instance.responsible)
        instance.is_draft = validated_data.get('is_draft', instance.is_draft)
        instance.save()

        
        existing_enpis = {enpi.id: enpi for enpi in instance.enpis.all()}
        updated_enpis_ids = []

        for enpi_data in enpis_data:
            enpi_value = enpi_data.get("enpi")
            enpi_id = enpi_data.get("id")  
            if enpi_id and enpi_id in existing_enpis:
                
                enpi = existing_enpis[enpi_id]
                enpi.enpi = enpi_value
                enpi.save()
                updated_enpis_ids.append(enpi_id)
            else:
                
                new_enpi = Enpis.objects.create(baseline=instance, **enpi_data)
                updated_enpis_ids.append(new_enpi.id)

     
        instance.enpis.exclude(id__in=updated_enpis_ids).delete()

        return instance
    
    
class EnergyImprovementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyImprovement
        fields = '__all__' 


 

    
class EnergyImprovementsGetSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    responsible = UserSerializer()
    class Meta:
        model = EnergyImprovement
        fields = '__all__' 

 


class ProgramActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramAction
        fields = ['id', 'Program']


class EnergyActionSerializer(serializers.ModelSerializer):
    programs = ProgramActionSerializer(many=True, required=False)

    class Meta:
        model = EnergyAction
        fields = '__all__'

    def create(self, validated_data):
        request = self.context.get('request')  

 
        raw_programs = request.data.get('programs')
        try:
            program_data = json.loads(raw_programs) if raw_programs else []
        except json.JSONDecodeError:
            program_data = []

        validated_data.pop('programs', None)  # Remove programs from validated_data

        # Create the EnergyAction instance
        energy_action = EnergyAction.objects.create(**validated_data)

        # Create related ProgramAction entries
        for program in program_data:
            ProgramAction.objects.create(energy_action=energy_action, **program)

        return energy_action

    def update(self, instance, validated_data):
        
        program_data = validated_data.pop('programs', [])
        
        
        instance.action_plan = validated_data.get('action_plan', instance.action_plan)
        instance.associative_objective = validated_data.get('associative_objective', instance.associative_objective)
        instance.legal_requirements = validated_data.get('legal_requirements', instance.legal_requirements)
        instance.date = validated_data.get('date', instance.date)
        instance.energy_improvements = validated_data.get('energy_improvements', instance.energy_improvements)
        instance.title = validated_data.get('title', instance.title)
        instance.upload_attachment = validated_data.get('upload_attachment', instance.upload_attachment)
        instance.means = validated_data.get('means', instance.means)
        instance.responsible = validated_data.get('responsible', instance.responsible)
        instance.statement = validated_data.get('statement', instance.statement)
        instance.is_draft = False
        instance.save()

     
        existing_programs = {program.id: program for program in instance.programs.all()}
        updated_program_ids = []

        for program_data in program_data:
            program_id = program_data.get("id")
            program_value = program_data.get("program")

            if program_id and program_id in existing_programs:
                
                program = existing_programs[program_id]
                program.program = program_value
                program.save()
                updated_program_ids.append(program_id)
            else:
                
                new_program = ProgramAction.objects.create(energy_action=instance, **program_data)
                updated_program_ids.append(new_program.id)

       
        instance.programs.exclude(id__in=updated_program_ids).delete()

        return instance


class EnergyActionGetSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    responsible = UserSerializer()
    programs = ProgramActionSerializer(many=True, read_only=True) 
    
    class Meta:
        model = EnergyAction
        fields = '__all__'
        
        
        

class EnergySourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergySource
        fields = '__all__'
        
        

class SignificantEnergySerializer(serializers.ModelSerializer):
    class Meta:
        model = SignificantEnergy
        fields = '__all__'


class SignificantEnergyGetSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    source_type = EnergySourceSerializer()
    
    class Meta:
        model = SignificantEnergy
        fields = '__all__'



class ProcessActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessActivity
        fields = '__all__' 

class EnvironmentalAspectSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnvironmentalAspect
        fields = '__all__'
        
        
class EnvironmentalAspectGetSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(write_only=True, required=True)
    approved_by = UserSerializer(read_only=True) 
    written_by = UserSerializer(read_only=True) 
    checked_by =UserSerializer(read_only=True) 
    process_activity = ProcessActivitySerializer()
    
    
    class Meta:
        model = EnvironmentalAspect
        fields = '__all__'
        
        
class EnvironmentalAspectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnvironmentalAspect
        fields = '__all__'
        extra_kwargs = {
          
            'written_at': {'read_only': True},
            'checked_at': {'read_only': True},
            'approved_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }
    

    def update(self, instance, validated_data):
      
        validated_data['status'] = 'Pending for Review/Checking'       
        return super().update(instance, validated_data)


class AspectViewAllSerializer(serializers.ModelSerializer):
    written_by = UserSerializer()
    approved_by = UserSerializer()
    checked_by = UserSerializer()
    published_user = UserSerializer()

    class Meta:
        model = EnvironmentalAspect
        fields = '__all__'       
 

class NotificationAspectSerializer(serializers.ModelSerializer):
    aspect = AspectViewAllSerializer()  
    class Meta:
        model = NotificationAspect
        fields = "__all__"   
    
class CorrectionAspectSerializer(serializers.ModelSerializer):
    to_user_email = serializers.EmailField(source='to_user.email', read_only=True)
    from_user_email = serializers.EmailField(source='from_user.email', read_only=True)
    aspect_correction_title = serializers.CharField(source='aspect_correction.title', read_only=True)

    class Meta:
        model = CorrectionAspect
        fields = [
            'id', 
            'aspect_correction', 
            'aspect_correction_title',
            'to_user', 
            'to_user_email',
            'from_user', 
            'from_user_email',
            'correction', 
            'created_at'
        ]
        


class CorrectionAspectGetSerializer(serializers.ModelSerializer):
    to_user = UserSerializer(read_only=True) 
    from_user= UserSerializer(read_only=True) 
    aspect_correction_title = serializers.CharField(source='aspect_correction.title', read_only=True)

    class Meta:
        model = CorrectionAspect
        fields = [
            'id', 
            'aspect_correction', 
            'aspect_correction_title',
            'to_user', 
            'to_user',
            'from_user', 
            'from_user',
            'correction', 
            'created_at'
        ]

class EnvironmentalImpactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnvironmentalImpact
        fields = '__all__'




class EnvironmentalImpactGetSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(write_only=True, required=True)
    approved_by = UserSerializer(read_only=True) 
    written_by = UserSerializer(read_only=True) 
    checked_by =UserSerializer(read_only=True) 
    
    
    class Meta:
        model = EnvironmentalImpact
        fields = '__all__'
        
        
        
class EnvironmentalImpacttUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnvironmentalImpact
        fields = '__all__'
        extra_kwargs = {
          
            'written_at': {'read_only': True},
            'checked_at': {'read_only': True},
            'approved_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }
    

    def update(self, instance, validated_data):
      
        validated_data['status'] = 'Pending for Review/Checking'       
        return super().update(instance, validated_data)
    
    
class CorrectionGetImpactSerializer(serializers.ModelSerializer):
    to_user = UserSerializer(read_only=True) 
    from_user= UserSerializer(read_only=True) 
    impact_correction_title = serializers.CharField(source='impact_correction.title', read_only=True)

    class Meta:
        model = CorrectionImpact
        fields = [
            'id', 
            'impact_correction',
             
            'impact_correction_title',
            'to_user', 
            'to_user',
            'from_user', 
            'from_user',
            'correction', 
            'created_at'
        ]
        

class ImpactViewAllSerializer(serializers.ModelSerializer):
    written_by = UserSerializer()
    approved_by = UserSerializer()
    checked_by = UserSerializer()
    published_user = UserSerializer()

    class Meta:
        model = EnvironmentalImpact
        fields = '__all__'  
       
class ImpactNotificationSerializer(serializers.ModelSerializer):
    impact = ImpactViewAllSerializer()  
    class Meta:
        model = NotificationImpact
        fields = "__all__"

class EnvironmentalIncidentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnvironmentalIncidents
        fields = '__all__'



class IncidentRootSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentRoot
        fields = '__all__' 
        
        
class EnvironmentalIncidentsGetSerializer(serializers.ModelSerializer):
    reported_by = UserSerializer()
    root_cause = IncidentRootSerializer()
    class Meta:
        model = EnvironmentalIncidents
        fields = '__all__'


class EnvironmentalWasteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnvironmentalWaste
        fields = '__all__'
        
        
        
class WasteGetSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(write_only=True, required=True)
    approved_by = UserSerializer(read_only=True) 
    written_by = UserSerializer(read_only=True) 
    checked_by =UserSerializer(read_only=True) 
    
    
    class Meta:
        model = EnvironmentalWaste
        fields = '__all__'

class WasteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnvironmentalWaste
        fields = '__all__'
        extra_kwargs = {
          
            'written_at': {'read_only': True},
            'checked_at': {'read_only': True},
            'approved_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }
    

    def update(self, instance, validated_data):
      
        validated_data['status'] = 'Pending for Review/Checking'       
        return super().update(instance, validated_data)
    
    
    
class CorrectionWasteSerializer(serializers.ModelSerializer):
    to_user_email = serializers.EmailField(source='to_user.email', read_only=True)
    from_user_email = serializers.EmailField(source='from_user.email', read_only=True)
    waste_correction_title = serializers.CharField(source='waste_correction.title', read_only=True)

    class Meta:
        model = CorrectionWaste
        fields = [
            'id', 
            'waste_correction', 
            'waste_correction_title',
            'to_user', 
            'to_user_email',
            'from_user', 
            'from_user_email',
            'correction', 
            'created_at'
        ]

class CorrectionWasteGetQMSSerializer(serializers.ModelSerializer):
    to_user = UserSerializer(read_only=True) 
    from_user= UserSerializer(read_only=True) 
    waste_correction_title = serializers.CharField(source='waste_correction.title', read_only=True)

    class Meta:
        model = CorrectionWaste
        fields = [
            'id', 
            'waste_correction', 
            'waste_correction_title',
            'to_user', 
            'to_user',
            'from_user', 
            'from_user',
            'correction', 
            'created_at'
        ]

class WasteViewAllSerializer(serializers.ModelSerializer):
    written_by = UserSerializer()
    approved_by = UserSerializer()
    checked_by = UserSerializer()
    published_user = UserSerializer()

    class Meta:
        model = EnvironmentalWaste
        fields = '__all__'       
 

class WasteNotificationSerializer(serializers.ModelSerializer):
     waste = WasteViewAllSerializer()  
     class Meta:
        model = NotificationWaste
        fields = "__all__"





class ProcessHealthSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessHealth
        fields = '__all__' 

class HealthSafetySerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthSafety
        fields = '__all__'
        


class HealthSafetyGetSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(write_only=True, required=True)
    approved_by = UserSerializer(read_only=True) 
    written_by = UserSerializer(read_only=True) 
    checked_by =UserSerializer(read_only=True) 
    
    
    class Meta:
        model = HealthSafety
        fields = '__all__'
        
class HealthSafetyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthSafety
        fields = '__all__'
        extra_kwargs = {
          
            'written_at': {'read_only': True},
            'checked_at': {'read_only': True},
            'approved_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }
    

    def update(self, instance, validated_data):
      
        validated_data['status'] = 'Pending for Review/Checking'       
        return super().update(instance, validated_data)
    
class CorrectionHealthSerializer(serializers.ModelSerializer):
    to_user_email = serializers.EmailField(source='to_user.email', read_only=True)
    from_user_email = serializers.EmailField(source='from_user.email', read_only=True)
    health_correction_title = serializers.CharField(source='health_correction.title', read_only=True)

    class Meta:
        model = CorrectionHealth
        fields = [
            'id', 
            'health_correction', 
            'health_correction_title',
            'to_user', 
            'to_user_email',
            'from_user', 
            'from_user_email',
            'correction', 
            'created_at'
        ]
        
class CorrectionHealthGetQMSSerializer(serializers.ModelSerializer):
    to_user = UserSerializer(read_only=True) 
    from_user= UserSerializer(read_only=True) 
    health_correction_title = serializers.CharField(source='health_correction.title', read_only=True)

    class Meta:
        model = CorrectionHealth
        fields = [
            'id', 
            'health_correction', 
            'health_correction_title',
            'to_user', 
            'to_user',
            'from_user', 
            'from_user',
            'correction', 
            'created_at'
        ]

class HealthViewAllSerializer(serializers.ModelSerializer):
    written_by = UserSerializer()
    approved_by = UserSerializer()
    checked_by = UserSerializer()
    published_user = UserSerializer()

    class Meta:
        model = HealthSafety
        fields = '__all__'    
        
class HealthNotificationSerializer(serializers.ModelSerializer):
     health = HealthViewAllSerializer()  
     class Meta:
        model = NotificationHealth
        fields = "__all__"
        
        
class RiskAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskAssessment
        fields = '__all__'
        
        

class RiskAssessmentGetSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(write_only=True, required=True)
    approved_by = UserSerializer(read_only=True) 
    written_by = UserSerializer(read_only=True) 
    checked_by =UserSerializer(read_only=True) 
    
    
    class Meta:
        model = RiskAssessment
        fields = '__all__'
        
        
class RiskAssessmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskAssessment
        fields = '__all__'
        extra_kwargs = {
          
            'written_at': {'read_only': True},
            'checked_at': {'read_only': True},
            'approved_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }
    

    def update(self, instance, validated_data):
      
        validated_data['status'] = 'Pending for Review/Checking'       
        return super().update(instance, validated_data)


class CorrectionAssessmentsSerializer(serializers.ModelSerializer):
    to_user_email = serializers.EmailField(source='to_user.email', read_only=True)
    from_user_email = serializers.EmailField(source='from_user.email', read_only=True)
    assessment_correction_title = serializers.CharField(source='assessment_correction.title', read_only=True)

    class Meta:
        model = CorrectionAssessments
        fields = [
            'id', 
            'assessment_correction', 
            'assessment_correction_title',
            'to_user', 
            'to_user',
            'from_user', 
            'from_user',
            'correction', 
            'created_at',
             'to_user_email',        
            'from_user_email'  
        ]


class CorrectionAssessmentGetQMSSerializer(serializers.ModelSerializer):
    to_user = UserSerializer(read_only=True) 
    from_user= UserSerializer(read_only=True) 
    assessment_correction_title = serializers.CharField(source='assessment_correction.title', read_only=True)

    class Meta:
        model = CorrectionAssessments
        fields = [
            'id', 
            'assessment_correction', 
            'assessment_correction_title',
            'to_user', 
            'to_user',
            'from_user', 
            'from_user',
            'correction', 
            'created_at'
        ]
        

class AssessmentGetSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(write_only=True, required=True)
    approved_by = UserSerializer(read_only=True) 
    written_by = UserSerializer(read_only=True) 
    checked_by =UserSerializer(read_only=True) 
    
    
    class Meta:
        model = RiskAssessment
        fields = '__all__'



class AssessmentViewAllSerializer(serializers.ModelSerializer):
    written_by = UserSerializer()
    approved_by = UserSerializer()
    checked_by = UserSerializer()
    published_user = UserSerializer()

    class Meta:
        model = RiskAssessment
        fields = '__all__'   
        
class AssessmentNotificationSerializer(serializers.ModelSerializer):
     assessment = AssessmentViewAllSerializer()  
     class Meta:
        model = NotificationAssessments
        fields = "__all__"


class SafetyRootCauseSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthRootCause
        fields = '__all__'

class HealthIncidentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthIncidents
        fields = '__all__'


class HealthIncidentsGetSerializer(serializers.ModelSerializer):
    reported_by = UserSerializer()
    root_cause = SafetyRootCauseSerializer()
    
    class Meta:
        model = HealthIncidents
        fields = '__all__'


class MessageGetSerializer(serializers.ModelSerializer):
    to_user = UserSerializer(many=True)
    from_user = UserSerializer()
    class Meta:
        model = Message
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    to_user = serializers.PrimaryKeyRelatedField(many=True, queryset=Users.objects.all())
    from_user = serializers.PrimaryKeyRelatedField(queryset=Users.objects.all())

    parent = serializers.PrimaryKeyRelatedField(queryset=Message.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Message
        fields = '__all__'
         

    def create(self, validated_data):
  
        to_users = validated_data.pop('to_user', [])
        parent = validated_data.get('parent', None)
        from_user = validated_data.get('from_user')

        message = Message.objects.create(**validated_data)

        if parent:
            message.thread_root = parent.thread_root or parent
            message.save()

        message.to_user.set(to_users)
        return message
