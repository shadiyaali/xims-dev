
from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password


 
# class UserSerializer(serializers.ModelSerializer):
#     confirm_password = serializers.CharField(write_only=True)   
#     confirm_email = serializers.EmailField(write_only=True) 
#     company_id = serializers.IntegerField(write_only=True, required=True)

#     class Meta:
#         model = Users
#         fields = '__all__'  

#     def validate(self, data):
        
#         if data.get('password') != data.get('confirm_password'):
#             raise serializers.ValidationError("Passwords do not match.")

       
#         if data.get('email') != data.get('confirm_email'):
#             raise serializers.ValidationError("Email addresses do not match.")

        
#         data['password'] = make_password(data['password'])

        
#         data.pop('confirm_password', None)
#         data.pop('confirm_email', None)

#         return data
    
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Users, Company

class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)   
    confirm_email = serializers.EmailField(write_only=True) 
    company_id = serializers.IntegerField(write_only=True, required=True)
    permissions = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    

    class Meta:
        model = Users
        fields = '__all__'  

    def validate(self, data):
        
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError({"password": "Passwords do not match."})

        
        if data.get('email') != data.get('confirm_email'):
            raise serializers.ValidationError({"email": "Email addresses do not match."})

        email = data.get('email')
        username = data.get('username')

        
        if Users.objects.filter(email=email).exists() or Company.objects.filter(email_address=email).exists():
            raise serializers.ValidationError({"email": "This email is already in use."})

         
        if Users.objects.filter(username=username).exists() or Company.objects.filter(user_id=username).exists():
            raise serializers.ValidationError({"username": "This username is already in use."})

       
        data['password'] = make_password(data['password'])

        
        data.pop('confirm_password', None)
        data.pop('confirm_email', None)

        return data

    def create(self, validated_data):
        permissions_data = validated_data.pop('permissions', [])  
        user = Users.objects.create(**validated_data)  

        for permission_name in permissions_data:
            permission, created = Permission.objects.get_or_create(name=permission_name)
            user.permissions.add(permission)

        return user
    
    
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['name']

class UserDetailSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Users
        exclude = ['password']


class UserUpdateSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Users
        exclude = ['password']
    def validate_date_of_birth(self, value):
        if value in ['', None]:
            return None
        return value
    date_of_birth = serializers.DateField(required=False, allow_null=True)

    def update(self, instance, validated_data):
    
        permissions_data = self.initial_data.get('permissions', [])
        instance = super().update(instance, validated_data)

        instance.permissions.clear()
        for perm in permissions_data:
            perm_obj, _ = Permission.objects.get_or_create(name=perm.get('name'))
            instance.permissions.add(perm_obj)

        return instance


class UserGETSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)   
    confirm_email = serializers.EmailField(write_only=True) 
    company_id = serializers.IntegerField(write_only=True, required=True)
    permissions = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    
    
    permission_names = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = '__all__'  

    def get_permission_names(self, obj):
        return list(obj.permissions.values_list('name', flat=True))

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError({"password": "Passwords do not match."})

        if data.get('email') != data.get('confirm_email'):
            raise serializers.ValidationError({"email": "Email addresses do not match."})

        email = data.get('email')
        username = data.get('username')

        if Users.objects.filter(email=email).exists() or Company.objects.filter(email_address=email).exists():
            raise serializers.ValidationError({"email": "This email is already in use."})

        if Users.objects.filter(username=username).exists() or Company.objects.filter(user_id=username).exists():
            raise serializers.ValidationError({"username": "This username is already in use."})

        data['password'] = make_password(data['password'])

        data.pop('confirm_password', None)
        data.pop('confirm_email', None)

        return data

 



 
class ProcessActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessActivity
        fields = '__all__' 

class EnvironmentalAspectSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnvironmentalAspect
        fields = '__all__'
class EnvironmentalImpactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnvironmentalImpact
        fields = '__all__'

 

class EnvironmentalIncidentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnvironmentalIncidents
        fields = '__all__'

class EnvironmentalWasteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnvironmentalWaste
        fields = '__all__'

class ProcessHealthSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessHealth
        fields = '__all__' 

class HealthSafetySerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthSafety
        fields = '__all__'

 
class RiskAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskAssessment
        fields = '__all__'

class HealthRootCauseSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthRootCause
        fields = '__all__'

class HealthIncidentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthIncidents
        fields = '__all__'

class BusinessRiskSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessRisk
        fields = '__all__'

class ReviewTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewType
        fields = '__all__'

class EnergyReviewSerializer(serializers.ModelSerializer):
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


class BaselineSerializer(serializers.ModelSerializer):
    enpis = EnpisSerializer(many=True, required=False)   

    class Meta:
        model = Baseline
        fields = ['id', 'basline_title', 'established_basline', 'remarks', 'energy_review', 
                  'date', 'responsible', 'enpis']

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

class EnergySourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergySource
        fields = '__all__'

class SignificantEnergySerializer(serializers.ModelSerializer):
    class Meta:
        model = SignificantEnergy
        fields = '__all__'

class EnergyImprovementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyImprovement
        fields = '__all__' 




class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ['id', 'Program']


class EnergyActionSerializer(serializers.ModelSerializer):
    programs = ProgramSerializer(many=True, required=False)

    class Meta:
        model = EnergyAction
        fields = '__all__'

    def create(self, validated_data):
        
        program_data = validated_data.pop('programs', [])
        energy_action = EnergyAction.objects.create(**validated_data)
        
      
        for program_data in program_data:
            Program.objects.create(energy_action=energy_action, **program_data)
        
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
                
                new_program = Program.objects.create(energy_action=instance, **program_data)
                updated_program_ids.append(new_program.id)

       
        instance.programs.exclude(id__in=updated_program_ids).delete()

        return instance


class CorrectionCauseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorrectionCause
        fields = '__all__'

class CorrectiveActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorrectiveAction
        fields = '__all__'





 
 




 

class UserLogoSerializer(serializers.ModelSerializer):
    user_logo = serializers.ImageField(use_url=True)
    class Meta:
        model = Users
        fields = ['user_logo'] 
        
class UsersAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'
        
class UserAllListSerializer(serializers.ModelSerializer):
 
    permissions = serializers.ListField(child=serializers.CharField(), required=False)
    
  
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = '__all__'
    
    def get_permissions(self, obj):
       
        return list(obj.permissions.values_list('name', flat=True))
    
    
    
class ChangeUserPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data