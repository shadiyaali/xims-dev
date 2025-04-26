
from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password
from company.serializers import *





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
        
        
from django.conf import settings       
class ManualSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manual
        fields = '__all__'
        
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
        
        
class InterestedPartySerializer(serializers.ModelSerializer):
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
    class Meta:
        model = Message
        fields = '__all__'
        
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
        
from rest_framework import serializers
from .models import InternalProblem

class InternalProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalProblem
        fields = '__all__'

    def validate(self, data):
        corrective_action = data.get('corrective_action', self.instance.corrective_action if self.instance else 'Yes')
        
        # If corrective_action is No, set both correction and car_no to None
        if corrective_action == 'No':
            data['correction'] = None
            data['car_no'] = None
        
        # If corrective_action is Yes, ensure correction is provided
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
        
        
 
        
class SupplierProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierProblem
        fields = '__all__'
