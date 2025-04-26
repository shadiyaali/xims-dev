
from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password
from company.serializers import *



class PolicyEnvSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyEnv
        fields = '__all__'  
        

class ManualEnvGetSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(write_only=True, required=True)
    approved_by = UserSerializer(read_only=True) 
    class Meta:
        model = ManualEnv
        fields = '__all__'
        
class ManualEnvSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = ManualEnv
        fields = '__all__'