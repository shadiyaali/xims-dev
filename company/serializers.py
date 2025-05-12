
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