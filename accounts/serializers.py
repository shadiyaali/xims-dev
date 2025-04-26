 


from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import *
from  company.models import Users

class CompanySerializer(serializers.ModelSerializer):
    permissions = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)

    class Meta:
        model = Company
        fields = [
            'id', 
            'company_name', 
            'company_admin_name', 
            'user_id',   
            'email_address',  
            'password', 
            'phone_no1', 
            'phone_no2', 
            'company_logo',
            'permissions'
        ]

     


    def create(self, validated_data):
        permissions_data = validated_data.pop('permissions', []) 
        password = validated_data.get('password')
        
        if password:
            validated_data['password'] = make_password(password)
        
        company = Company.objects.create(**validated_data)

        
        for permission_name in permissions_data:
            permission, created = Permission.objects.get_or_create(name=permission_name)
            company.permissions.add(permission)

        return company

    
class CompanyGetSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = '__all__'

    def get_permissions(self, obj):
        return [perm.name for perm in obj.permissions.all()]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.company_logo:
            representation['company_logo'] = instance.company_logo.url  
        return representation

        
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['name']   

class CompanySingleSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = '__all__'

    def get_permissions(self, obj):
        return list(obj.permissions.values_list('name', flat=True)) 

from django.contrib.auth.hashers import check_password, make_password
import json

class CompanyUpdateSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            'id', 'company_name', 'company_admin_name', 'user_id', 
            'email_address', 'password', 'phone_no1', 'phone_no2', 
            'company_logo', 'permissions'
        ]
        extra_kwargs = {
            'password': {'write_only': True},  
        }

    def get_permissions(self, obj):
        """Retrieve permission names instead of IDs"""
        return list(obj.permissions.values_list('name', flat=True)) 

    def update(self, instance, validated_data):
        permission_names = validated_data.pop('permissions', None)

        # Convert stringified JSON to a list if necessary
        if isinstance(permission_names, str):
            try:
                permission_names = json.loads(permission_names)   
            except json.JSONDecodeError:
                raise serializers.ValidationError({"permissions": "Invalid format for permissions."})

        if permission_names:
            permissions = Permission.objects.filter(name__in=permission_names)
            instance.permissions.set(permissions)

        return super().update(instance, validated_data)


    
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['name']

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__' 


class SubscriberSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.company_name')
    plan_name = serializers.ReadOnlyField(source='plan.subscription_name')

    class Meta:
        model = Subscribers
        fields = ['id', 'company', 'company_name', 'plan', 'plan_name', 'expiry_date', 'status']



class SubscriberSerializerss(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.company_name')
    plan_name = serializers.ReadOnlyField(source='plan.subscription_name')

    class Meta:
        model = Subscribers
        fields = ['id', 'company', 'company_name', 'plan', 'plan_name', 'expiry_date', 'status']

    def update(self, instance, validated_data):
        plan = validated_data.get('plan', instance.plan)
        if plan != instance.plan:
            instance.plan = plan
            duration = plan.validity if plan else 0
            instance.expiry_date = (timezone.now() + timedelta(days=duration)).date() if plan else None
        return super().update(instance, validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'date_joined','profile_photo', 'is_staff', 'is_superuser']
        


class CompanyAllListSerializer(serializers.ModelSerializer):
 
    permissions = serializers.ListField(child=serializers.CharField(), required=False)
    
  
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = [
            'id', 
            'company_name', 
            'company_admin_name',
            'user_id', 
            'email_address', 
            'password',
            'phone_no1',
            'phone_no2',
            'company_logo',
            'permissions'
        ]
    
    def get_permissions(self, obj):
       
        return list(obj.permissions.values_list('name', flat=True))
    

class CompanyLogoSerializer(serializers.ModelSerializer):
    company_logo = serializers.ImageField(use_url=True)
    class Meta:
        model = Company
        fields = ['company_logo'] 
        
class ProfilePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile_photo']