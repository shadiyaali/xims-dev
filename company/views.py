
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
from rest_framework import generics
from rest_framework.exceptions import NotFound
from django.contrib.auth.hashers import check_password
from django.conf import settings
logger = logging.getLogger(__name__) 
import jwt
from datetime import datetime, timedelta
from accounts.models import *
from django.core.mail import send_mail
from decouple import config  
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import get_authorization_header
from django.shortcuts import get_object_or_404
 


 

 
from django.contrib.auth.hashers import check_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
import jwt
from django.conf import settings
from .models import Company, Users

 

# class CompanyLoginView(APIView):
#     def post(self, request, *args, **kwargs):
#         username = request.data.get('username')   
#         password = request.data.get('password')

#         if not username or not password:
#             return Response({'error': 'Username and password must be provided'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             company = Company.objects.get(user_id=username)

#             # Check if the company is blocked
#             if company.status == 'blocked':
#                 return Response({'error': 'Your company is blocked. Please contact support.'}, status=status.HTTP_403_FORBIDDEN)

#             if not check_password(password, company.password):
#                 return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)

#             subscription = Subscribers.objects.filter(
#                 company=company, 
#                 status="active", 
#                 expiry_date__gte=now().date()
#             ).exists()

#             if not subscription:
#                 return Response({'error': 'Your subscription is inactive or expired. Please renew your plan.'}, status=status.HTTP_403_FORBIDDEN)

#             access_payload = {
#                 'id': company.id,
#                 'user_id': company.user_id,
#                 'username': company.user_id,
#                 'exp': datetime.utcnow() + timedelta(days=30),
#             }
#             refresh_payload = {
#                 'id': company.id,
#                 'user_id': company.user_id,
#                 'username': company.user_id,
#                 'exp': datetime.utcnow() + timedelta(days=365),
#             }

#             access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256')
#             refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')

#             return Response({
#                 'id': company.id,
#                 'user_id': company.user_id,
#                 'company_name': company.company_name,
#                 'company_admin_name': company.company_admin_name,
#                 'username': company.user_id,  
#                 'phone_no1': company.phone_no1,
#                 'phone_no2': company.phone_no2,
#                 'email_address':company.email_address,
#                 'created_at': company.created_at.strftime('%Y-%m-%d %H:%M:%S'),  
#                 'company_logo': company.company_logo.url if company.company_logo else None,
#                 'status': company.status,
#                 'permissions': [perm.name for perm in company.permissions.all()],  
#                 'date_joined': company.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
#                 'role': 'company', 
#                 'access': access_token,
#                 'refresh': refresh_token,
#             }, status=status.HTTP_200_OK)

#         except Company.DoesNotExist:
#             pass  

#         try:
#             user = Users.objects.get(username=username)

#             # Check if the user is in trash
#             if user.is_trash:
#                 return Response({'error': 'User account not found'}, status=status.HTTP_401_UNAUTHORIZED)
                
#             # Check if the user is blocked
#             if user.status == 'blocked':
#                 return Response({'error': 'Your account is blocked. Please contact support.'}, status=status.HTTP_403_FORBIDDEN)

#             # Check if the user's company is blocked
#             if user.company and user.company.status == 'blocked':
#                 return Response({'error': 'Your company is blocked. Please contact support.'}, status=status.HTTP_403_FORBIDDEN)

#             if not check_password(password, user.password):
#                 return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)

#             access_payload = {
#                 'id': user.id,
#                 'username': user.username,
#                 'company_id': user.company.id if user.company else None,
#                 'exp': datetime.utcnow() + timedelta(days=30),
#             }
#             refresh_payload = {
#                 'id': user.id,
#                 'username': user.username,
#                 'company_id': user.company.id if user.company else None,
#                 'exp': datetime.utcnow() + timedelta(days=365),
#             }

#             access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256')
#             refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')

#             return Response({
#                 'id': user.id,
#                 'username': user.username,
#                 'first_name': user.first_name,
#                 'last_name': user.last_name,
#                 'email': user.email,
#                 'phone': user.phone,
#                 'status': user.status,
#                 'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
#                 'company_id': user.company.id if user.company else None,
#                 'role': 'user',  
#                 'access': access_token,
#                 'refresh': refresh_token,
#             }, status=status.HTTP_200_OK)

#         except Users.DoesNotExist:
#             return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)



class CompanyLoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')   
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username and password must be provided'}, status=status.HTTP_400_BAD_REQUEST)

        # First try to authenticate as a user
        try:
            user = Users.objects.get(username=username)

            # Check if the user is in trash
            if user.is_trash:
                return Response({'error': 'User account not found'}, status=status.HTTP_401_UNAUTHORIZED)
                
            # Check if the user is blocked
            if user.status == 'blocked':
                return Response({'error': 'Your account is blocked. Please contact support.'}, status=status.HTTP_403_FORBIDDEN)

            # Check if the user's company is blocked
            if user.company and user.company.status == 'blocked':
                return Response({'error': 'Your company is blocked. Please contact support.'}, status=status.HTTP_403_FORBIDDEN)

            if not check_password(password, user.password):
                return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)

            access_payload = {
                'id': user.id,
                'username': user.username,
                'company_id': user.company.id if user.company else None,
                'exp': datetime.utcnow() + timedelta(days=30),
            }
            refresh_payload = {
                'id': user.id,
                'username': user.username,
                'company_id': user.company.id if user.company else None,
                'exp': datetime.utcnow() + timedelta(days=365),
            }

            access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256')
            refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')

            return Response({
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'phone': user.phone,
                'status': user.status,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'company_id': user.company.id if user.company else None,
                'role': 'user',  
                'access': access_token,
                'refresh': refresh_token,
            }, status=status.HTTP_200_OK)

        except Users.DoesNotExist:
            pass  # If user not found, try company login instead
            
        # If user authentication failed, try company authentication
        try:
            company = Company.objects.get(user_id=username)

            # Check if the company is blocked
            if company.status == 'blocked':
                return Response({'error': 'Your company is blocked. Please contact support.'}, status=status.HTTP_403_FORBIDDEN)

            if not check_password(password, company.password):
                return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)

            subscription = Subscribers.objects.filter(
                company=company, 
                status="active", 
                expiry_date__gte=now().date()
            ).exists()

            if not subscription:
                return Response({'error': 'Your subscription is inactive or expired. Please renew your plan.'}, status=status.HTTP_403_FORBIDDEN)

            access_payload = {
                'id': company.id,
                'user_id': company.user_id,
                'username': company.user_id,
                'exp': datetime.utcnow() + timedelta(days=30),
            }
            refresh_payload = {
                'id': company.id,
                'user_id': company.user_id,
                'username': company.user_id,
                'exp': datetime.utcnow() + timedelta(days=365),
            }

            access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256')
            refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')

            return Response({
                'id': company.id,
                'user_id': company.user_id,
                'company_name': company.company_name,
                'company_admin_name': company.company_admin_name,
                'username': company.user_id,  
                'phone_no1': company.phone_no1,
                'phone_no2': company.phone_no2,
                'email_address':company.email_address,
                'created_at': company.created_at.strftime('%Y-%m-%d %H:%M:%S'),  
                'company_logo': company.company_logo.url if company.company_logo else None,
                'status': company.status,
                'permissions': [perm.name for perm in company.permissions.all()],  
                'date_joined': company.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
                'role': 'company', 
                'access': access_token,
                'refresh': refresh_token,
            }, status=status.HTTP_200_OK)

        except Company.DoesNotExist:
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)

class UserCreate(APIView):

    def post(self, request):
        company_id = request.data.get("company_id")  

        if not company_id:
            return Response({"error": "Company ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({"error": "Invalid Company ID"}, status=status.HTTP_400_BAD_REQUEST)

        user_data = request.data.copy()
        user_data["company"] = company.id  

        serializer = UserSerializer(data=user_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserList(APIView):
    def get(self, request, company_id):
        try:
            company = Company.objects.get(id=company_id)
            print(f"Found company with ID: {company_id}")
            
            # Check all users in the system
            all_users = Users.objects.all()
            print(f"Total users in system: {all_users.count()}")
            
            # Check users associated with this company, regardless of is_trash
            company_users = Users.objects.filter(company=company)
            print(f"Users with company ID {company_id}: {company_users.count()}")
            
            # Now apply the is_trash filter
            users = Users.objects.filter(company=company, is_trash=False)
            print(f"Non-trash users with company ID {company_id}: {users.count()}")
            
            serializer = UserGETSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)


class ActriveUserList(APIView):
    def get(self, request, company_id):
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

       
        users = Users.objects.filter(company=company, is_trash=False, status='active')
        serializer = UserGETSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


from rest_framework.generics import RetrieveAPIView

class UserDetailView(RetrieveAPIView):
    queryset = Users.objects.all()
    serializer_class = UserDetailSerializer


from rest_framework.generics import UpdateAPIView 


class UserUpdateView(UpdateAPIView):
    queryset = Users.objects.all()
    serializer_class = UserUpdateSerializer

    def update(self, request, *args, **kwargs):
        print("Request Data:", request.data)

        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # 🛠️ Preprocess data: convert "" to None for nullable fields
        data = request.data.copy()
        if data.get('date_of_birth') == '':
            data['date_of_birth'] = None
        if data.get('gender') == '':
            data['gender'] = None

        serializer = self.get_serializer(instance, data=data, partial=partial)

        if not serializer.is_valid():
            print("Validation Errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)
        return Response(serializer.data)

    
    
class UserDelete(APIView):
    def delete(self, request, pk):
        try:
            user = Users.objects.get(pk=pk)
        except Users.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
 
 
class UserDelete(APIView):
    def delete(self, request, pk):
        try:
            user = Users.objects.get(pk=pk)
        except Users.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

      
        user.username = f"{user.username}_deleted_{user.id}"
        if user.email:
            local_part, _, domain = user.email.partition('@')
            user.email = f"{local_part}_deleted_{user.id}@{domain}" if domain else f"{local_part}_deleted_{user.id}@deleted.com"

        
        user.is_trash = True
        user.save()

        return Response({"message": "User moved to trash and username/email updated"}, status=status.HTTP_200_OK)


 
 



 

 
 
    
 
    


 
    
    

    
    
 
    
 


 
    



 


 
    
 
    
class QuestionView(APIView):
    def get(self, request):
        agendas = Question.objects.all()
        serializer = QuestionSerializer(agendas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
 
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuestionDetailView(APIView):
    def get_object(self, pk):
        try:
            return Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return None

    def get(self, request, pk):
        agenda = self.get_object(pk)
        if not agenda:
            return Response({"error": "Agenda not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = QuestionSerializer(agenda)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        agenda = self.get_object(pk)
        if not agenda:
            return Response({"error": "Agenda not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = QuestionSerializer(agenda, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        agenda = self.get_object(pk)
        if not agenda:
            return Response({"error": "Agenda not found."}, status=status.HTTP_404_NOT_FOUND)
        agenda.delete()
        return Response({"message": "Agenda deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    


# class CustomerSatisfactionView(APIView):
#     def get(self, request):
#         agendas = CustomerSatisfaction.objects.all()
#         serializer = CustomerSatisfactionSerializer(agendas, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def post(self, request):
       
#         serializer = CustomerSatisfactionSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class CustomerSatisfactionDetailView(APIView):
#     def get_object(self, pk):
#         try:
#             return CustomerSatisfaction.objects.get(pk=pk)
#         except CustomerSatisfaction.DoesNotExist:
#             return None

#     def get(self, request, pk):
#         agenda = self.get_object(pk)
#         if not agenda:
#             return Response({"error": "  not found."}, status=status.HTTP_404_NOT_FOUND)
#         serializer = CustomerSatisfactionSerializer(agenda)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def put(self, request, pk):
#         print(request.data)
#         agenda = self.get_object(pk)
#         if not agenda:
#             return Response({"error": " not found."}, status=status.HTTP_404_NOT_FOUND)
#         serializer = CustomerSatisfactionSerializer(agenda, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         agenda = self.get_object(pk)
#         if not agenda:
#             return Response({"error": "  not found."}, status=status.HTTP_404_NOT_FOUND)
#         agenda.delete()
#         return Response({"message": " deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    

    


    
 
 
 
 
 


class ProcessActivityListCreate(APIView):
  
    def get(self, request):
        process_activities = ProcessActivity.objects.all()
        serializer = ProcessActivitySerializer(process_activities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

  
    def post(self, request):
        serializer = ProcessActivitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProcessActivityDetail(APIView):
   
    def get(self, request, pk):
        try:
            process_activity = ProcessActivity.objects.get(pk=pk)
        except ProcessActivity.DoesNotExist:
            raise NotFound("ProcessActivity record not found.")
        
        serializer = ProcessActivitySerializer(process_activity)
        return Response(serializer.data, status=status.HTTP_200_OK)

   
    def put(self, request, pk):
        try:
            process_activity = ProcessActivity.objects.get(pk=pk)
        except ProcessActivity.DoesNotExist:
            raise NotFound("ProcessActivity record not found.")
        
        serializer = ProcessActivitySerializer(process_activity, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request, pk):
        try:
            process_activity = ProcessActivity.objects.get(pk=pk)
        except ProcessActivity.DoesNotExist:
            raise NotFound("ProcessActivity record not found.")
        
        process_activity.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


 
class EnvironmentalAspectView(APIView):
    def get(self, request):
 
        aspects = EnvironmentalAspect.objects.all()
        serializer = EnvironmentalAspectSerializer(aspects, many=True)
        return Response(serializer.data)

    def post(self, request):
 
        serializer = EnvironmentalAspectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


 
class EnvironmentalAspectDetailView(APIView):
    def get(self, request, pk):
        try:
            aspect = EnvironmentalAspect.objects.get(pk=pk)
        except EnvironmentalAspect.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = EnvironmentalAspectSerializer(aspect)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            aspect = EnvironmentalAspect.objects.get(pk=pk)
        except EnvironmentalAspect.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EnvironmentalAspectSerializer(aspect, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            aspect = EnvironmentalAspect.objects.get(pk=pk)
        except EnvironmentalAspect.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        aspect.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

 
class EnvironmentalImpactView(APIView):
    def get(self, request):
   
        impacts = EnvironmentalImpact.objects.all()
        serializer = EnvironmentalImpactSerializer(impacts, many=True)
        return Response(serializer.data)

    def post(self, request):
      
        serializer = EnvironmentalImpactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class EnvironmentalImpactDetailView(APIView):
    def get(self, request, pk):
        try:
            impact = EnvironmentalImpact.objects.get(pk=pk)
        except EnvironmentalImpact.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = EnvironmentalImpactSerializer(impact)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            impact = EnvironmentalImpact.objects.get(pk=pk)
        except EnvironmentalImpact.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EnvironmentalImpactSerializer(impact, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            impact = EnvironmentalImpact.objects.get(pk=pk)
        except EnvironmentalImpact.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        impact.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


 

 
 

 
class EnvironmentalIncidentsView(APIView):
    def get(self, request):
    
        incidents = EnvironmentalIncidents.objects.all()
        serializer = EnvironmentalIncidentsSerializer(incidents, many=True)
        return Response(serializer.data)

    def post(self, request):
 
        serializer = EnvironmentalIncidentsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class EnvironmentalIncidentDetailView(APIView):
    def get(self, request, pk):
        try:
            incident = EnvironmentalIncidents.objects.get(pk=pk)
        except EnvironmentalIncidents.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = EnvironmentalIncidentsSerializer(incident)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            incident = EnvironmentalIncidents.objects.get(pk=pk)
        except EnvironmentalIncidents.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = EnvironmentalIncidentsSerializer(incident, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            incident = EnvironmentalIncidents.objects.get(pk=pk)
        except EnvironmentalIncidents.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        incident.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

 
class EnvironmentalWasteView(APIView):
    def get(self, request):
       
        wastes = EnvironmentalWaste.objects.all()
        serializer = EnvironmentalWasteSerializer(wastes, many=True)
        return Response(serializer.data)

    def post(self, request):
 
        serializer = EnvironmentalWasteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class EnvironmentalWasteDetailView(APIView):
    def get(self, request, pk):
        try:
            waste = EnvironmentalWaste.objects.get(pk=pk)
        except EnvironmentalWaste.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = EnvironmentalWasteSerializer(waste)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            waste = EnvironmentalWaste.objects.get(pk=pk)
        except EnvironmentalWaste.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = EnvironmentalWasteSerializer(waste, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            waste = EnvironmentalWaste.objects.get(pk=pk)
        except EnvironmentalWaste.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        waste.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProcessHealthListCreate(APIView):
  
    def get(self, request):
        process_activities = ProcessHealth.objects.all()
        serializer = ProcessHealthSerializer(process_activities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

  
    def post(self, request):
        serializer = ProcessHealthSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProcessHealthDetail(APIView):
   
    def get(self, request, pk):
        try:
            process_activity = ProcessHealth.objects.get(pk=pk)
        except ProcessHealth.DoesNotExist:
            raise NotFound("ProcessActivity record not found.")
        
        serializer = ProcessHealthSerializer(process_activity)
        return Response(serializer.data, status=status.HTTP_200_OK)

   
    def put(self, request, pk):
        try:
            process_activity = ProcessHealth.objects.get(pk=pk)
        except ProcessHealth.DoesNotExist:
            raise NotFound("ProcessActivity record not found.")
        
        serializer = ProcessHealthSerializer(process_activity, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request, pk):
        try:
            process_activity = ProcessHealth.objects.get(pk=pk)
        except ProcessHealth.DoesNotExist:
            raise NotFound("ProcessActivity record not found.")
        
        process_activity.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
 
class HealthSafetyView(APIView):
    def get(self, request):
       
        hazards = HealthSafety.objects.all()
        serializer = HealthSafetySerializer(hazards, many=True)
        return Response(serializer.data)

    def post(self, request):
       
        serializer = HealthSafetySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class HealthSafetyDetailView(APIView):
    def get(self, request, pk):
        try:
            hazard = HealthSafety.objects.get(pk=pk)
        except HealthSafety.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = HealthSafetySerializer(hazard)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            hazard = HealthSafety.objects.get(pk=pk)
        except HealthSafety.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = HealthSafetySerializer(hazard, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            hazard = HealthSafety.objects.get(pk=pk)
        except HealthSafety.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        hazard.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


 
class RiskAssessmentView(APIView):
    def get(self, request):
      
        assessments = RiskAssessment.objects.all()
        serializer = RiskAssessmentSerializer(assessments, many=True)
        return Response(serializer.data)

    def post(self, request):
       
        serializer = RiskAssessmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class RiskAssessmentDetailView(APIView):
    def get(self, request, pk):
        try:
            assessment = RiskAssessment.objects.get(pk=pk)
        except RiskAssessment.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = RiskAssessmentSerializer(assessment)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            assessment = RiskAssessment.objects.get(pk=pk)
        except RiskAssessment.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RiskAssessmentSerializer(assessment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            assessment = RiskAssessment.objects.get(pk=pk)
        except RiskAssessment.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        assessment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class HealthRootCauseView(APIView):
    def get(self, request):
 
        root_causes = HealthRootCause.objects.all()
        serializer = HealthRootCauseSerializer(root_causes, many=True)
        return Response(serializer.data)

    def post(self, request):
  
        serializer = HealthRootCauseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class HealthRootCauseDetailView(APIView):
    def get(self, request, pk):
        try:
            root_cause = HealthRootCause.objects.get(pk=pk)
        except HealthRootCause.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = HealthRootCauseSerializer(root_cause)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            root_cause = HealthRootCause.objects.get(pk=pk)
        except HealthRootCause.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = HealthRootCauseSerializer(root_cause, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            root_cause = HealthRootCause.objects.get(pk=pk)
        except HealthRootCause.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        root_cause.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

 
class HealthIncidentsView(APIView):
    def get(self, request):
    
        incidents = HealthIncidents.objects.all()
        serializer = HealthIncidentsSerializer(incidents, many=True)
        return Response(serializer.data)

    def post(self, request):
       
        serializer = HealthIncidentsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class HealthIncidentsDetailView(APIView):
    def get(self, request, pk):
        try:
            incident = HealthIncidents.objects.get(pk=pk)
        except HealthIncidents.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = HealthIncidentsSerializer(incident)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            incident = HealthIncidents.objects.get(pk=pk)
        except HealthIncidents.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = HealthIncidentsSerializer(incident, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            incident = HealthIncidents.objects.get(pk=pk)
        except HealthIncidents.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        incident.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


 
class BusinessRiskView(APIView):
    def get(self, request):
        
        risks = BusinessRisk.objects.all()
        serializer = BusinessRiskSerializer(risks, many=True)
        return Response(serializer.data)

    def post(self, request):
      
        serializer = BusinessRiskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class BusinessRiskDetailView(APIView):
    def get(self, request, pk):
        try:
            risk = BusinessRisk.objects.get(pk=pk)
        except BusinessRisk.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = BusinessRiskSerializer(risk)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            risk = BusinessRisk.objects.get(pk=pk)
        except BusinessRisk.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BusinessRiskSerializer(risk, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            risk = BusinessRisk.objects.get(pk=pk)
        except BusinessRisk.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        risk.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class ReviewTypeView(APIView):
    def get(self, request):
 
        root_causes = ReviewType.objects.all()
        serializer = ReviewTypeSerializer(root_causes, many=True)
        return Response(serializer.data)

    def post(self, request):
  
        serializer = ReviewTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class ReviewTypeDetailView(APIView):
    def get(self, request, pk):
        try:
            root_cause = ReviewType.objects.get(pk=pk)
        except ReviewType.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ReviewTypeSerializer(root_cause)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            root_cause = ReviewType.objects.get(pk=pk)
        except ReviewType.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ReviewTypeSerializer(root_cause, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            root_cause = ReviewType.objects.get(pk=pk)
        except ReviewType.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        root_cause.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
 
class EnergyReviewView(APIView):
    def get(self, request):
     
        reviews = EnergyReview.objects.all()
        serializer = EnergyReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request):
 
        serializer = EnergyReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class EnergyReviewDetailView(APIView):
    def get(self, request, pk):
        try:
            review = EnergyReview.objects.get(pk=pk)
        except EnergyReview.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = EnergyReviewSerializer(review)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            review = EnergyReview.objects.get(pk=pk)
        except EnergyReview.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = EnergyReviewSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            review = EnergyReview.objects.get(pk=pk)
        except EnergyReview.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class BaselineReviewView(APIView):
    def get(self, request):
 
        root_causes = BaselineReview.objects.all()
        serializer = BaselineReviewSerializer(root_causes, many=True)
        return Response(serializer.data)

    def post(self, request):
  
        serializer = BaselineReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class BaselineReviewDetailView(APIView):
    def get(self, request, pk):
        try:
            root_cause = BaselineReview.objects.get(pk=pk)
        except BaselineReview.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = BaselineReviewSerializer(root_cause)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            root_cause = BaselineReview.objects.get(pk=pk)
        except BaselineReview.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BaselineReviewSerializer(root_cause, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            root_cause = BaselineReview.objects.get(pk=pk)
        except BaselineReview.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        root_cause.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
 

class BaselineView(APIView):
    def get(self, request):
        baselines = Baseline.objects.prefetch_related('enpis').all()
        serializer = BaselineSerializer(baselines, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BaselineSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BaselineDetailView(APIView):
    def get(self, request, pk):
        try:
            baseline = Baseline.objects.prefetch_related('enpis').get(pk=pk)
        except Baseline.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = BaselineSerializer(baseline)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            baseline = Baseline.objects.get(pk=pk)
        except Baseline.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BaselineSerializer(baseline, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            baseline = Baseline.objects.get(pk=pk)
        except Baseline.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        baseline.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class EnergySourceView(APIView):
    def get(self, request):
     
        reviews = EnergySource.objects.all()
        serializer = EnergySourceSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EnergySourceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class EnergySourceDetailView(APIView):
    def get(self, request, pk):
        try:
            root_cause = EnergySource.objects.get(pk=pk)
        except EnergySource.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = EnergySourceSerializer(root_cause)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            root_cause = EnergySource.objects.get(pk=pk)
        except EnergySource.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EnergySourceSerializer(root_cause, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            root_cause = EnergySource.objects.get(pk=pk)
        except EnergySource.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        root_cause.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
 
class SignificantEnergyListView(APIView):
    def get(self, request):
       
        significant_energies = SignificantEnergy.objects.all()
        serializer = SignificantEnergySerializer(significant_energies, many=True)
        return Response(serializer.data)

    def post(self, request):
      
        serializer = SignificantEnergySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


 
class SignificantEnergyDetailView(APIView):
    def get_object(self, pk):
        try:
            return SignificantEnergy.objects.get(pk=pk)
        except SignificantEnergy.DoesNotExist:
            return None

    def get(self, request, pk):
     
        significant_energy = self.get_object(pk)
        if significant_energy is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = SignificantEnergySerializer(significant_energy)
        return Response(serializer.data)

    def put(self, request, pk):      
        significant_energy = self.get_object(pk)
        if significant_energy is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = SignificantEnergySerializer(significant_energy, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):        
        significant_energy = self.get_object(pk)
        if significant_energy is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        significant_energy.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

 

class EnergyImprovementsListCreateAPIView(APIView):
     
    def get(self, request):
        
        energy_improvements = EnergyImprovement.objects.all()
        serializer = EnergyImprovementsSerializer(energy_improvements, many=True)
        return Response(serializer.data)

    def post(self, request):
  
        serializer = EnergyImprovementsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EnergyImprovementsDetailAPIView(APIView):
  
    def get(self, request, pk):
        try:
            energy_improvement = EnergyImprovement.objects.get(pk=pk)
        except EnergyImprovement.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = EnergyImprovementsSerializer(energy_improvement)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            energy_improvement = EnergyImprovement.objects.get(pk=pk)
        except EnergyImprovement.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = EnergyImprovementsSerializer(energy_improvement, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            energy_improvement = EnergyImprovement.objects.get(pk=pk)
        except EnergyImprovement.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        energy_improvement.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EnergyActionView(APIView):
    def get(self, request):
        baselines = EnergyAction.objects.prefetch_related('programs').all()
        serializer = EnergyActionSerializer(baselines, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer =EnergyActionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EnergyActionDetailView(APIView):
    def get(self, request, pk):
        try:
            baseline = EnergyAction.objects.prefetch_related('programs').get(pk=pk)
        except EnergyAction.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = EnergyActionSerializer(baseline)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            baseline = EnergyAction.objects.get(pk=pk)
        except EnergyAction.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = EnergyActionSerializer(baseline, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            baseline = EnergyAction.objects.get(pk=pk)
        except EnergyAction.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        baseline.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class CorrectionCauseView(APIView):
    def get(self, request):
     
        reviews = CorrectionCause.objects.all()
        serializer = CorrectionCauseSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CorrectionCauseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CorrectionCauseDetailView(APIView):
    def get(self, request, pk):
        try:
            review = CorrectionCause.objects.get(pk=pk)
        except CorrectionCause.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CorrectionCauseSerializer(review)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            review = CorrectionCause.objects.get(pk=pk)
        except CorrectionCause.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CorrectionCauseSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            review = CorrectionCause.objects.get(pk=pk)
        except CorrectionCause.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class CorrectiveActionListView(APIView):
 
    def get(self, request):
        corrective_actions = CorrectiveAction.objects.all()
        serializer = CorrectiveActionSerializer(corrective_actions, many=True)
        return Response(serializer.data)

   
    def post(self, request):
        serializer = CorrectiveActionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CorrectiveActionDetailView(APIView):
   
    def get(self, request, pk):
        try:
            corrective_action = CorrectiveAction.objects.get(pk=pk)
        except CorrectiveAction.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CorrectiveActionSerializer(corrective_action)
        return Response(serializer.data)

  
    def put(self, request, pk):
        try:
            corrective_action = CorrectiveAction.objects.get(pk=pk)
        except CorrectiveAction.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CorrectiveActionSerializer(corrective_action, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
    def delete(self, request, pk):
        try:
            corrective_action = CorrectiveAction.objects.get(pk=pk)
        except CorrectiveAction.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        corrective_action.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PreventiveActionListCreateView(APIView):
    
    def get(self, request):
        actions = PreventiveAction.objects.all()
        serializer = PreventiveActionSerializer(actions, many=True)
        return Response(serializer.data)

   
    def post(self, request):
        serializer = PreventiveActionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PreventiveActionDetailView(APIView):
    
    def get(self, request, pk):
        try:
            action = PreventiveAction.objects.get(pk=pk)
        except PreventiveAction.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PreventiveActionSerializer(action)
        return Response(serializer.data)

    
    def put(self, request, pk):
        try:
            action = PreventiveAction.objects.get(pk=pk)
        except PreventiveAction.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PreventiveActionSerializer(action, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request, pk):
        try:
            action = PreventiveAction.objects.get(pk=pk)
        except PreventiveAction.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        action.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class ObjectivesListCreateView(APIView):
     
    def get(self, request):
        objectives = Objectives.objects.all()
        serializer = ObjectivesSerializer(objectives, many=True)
        return Response(serializer.data)

    
    def post(self, request):
        serializer = ObjectivesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ObjectivesDetailView(APIView):
    
    def get(self, request, pk):
        try:
            objective = Objectives.objects.get(pk=pk)
        except Objectives.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ObjectivesSerializer(objective)
        return Response(serializer.data)

    
    def put(self, request, pk):
        try:
            objective = Objectives.objects.get(pk=pk)
        except Objectives.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ObjectivesSerializer(objective, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
    def delete(self, request, pk):
        try:
            objective = Objectives.objects.get(pk=pk)
        except Objectives.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        objective.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TargetsPView(APIView):
    def get(self, request):
     
        targets = TargetsP.objects.prefetch_related('programs').all()
        serializer = TargetPSerializer(targets, many=True)
        return Response(serializer.data)

    def post(self, request):
      
        serializer = TargetPSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TargetsPDetailView(APIView):
    def get(self, request, pk):
        try:
 
            target = TargetsP.objects.prefetch_related('programs').get(pk=pk)
        except TargetsP.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
 
        serializer = TargetPSerializer(target)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
  
            target = TargetsP.objects.get(pk=pk)
        except TargetsP.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    
        serializer = TargetPSerializer(target, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            
            target = TargetsP.objects.get(pk=pk)
        except TargetsP.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        
        target.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


 

class ConformityCauseView(APIView):
   
    def get(self, request):
        conformity_causes = ConformityCause.objects.all()
        serializer = ConformityCauseSerializer(conformity_causes, many=True)
        return Response(serializer.data)

 
    def post(self, request):
        serializer = ConformityCauseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConformityCauseDetailView(APIView):
 
    def get(self, request, pk):
        try:
            conformity_cause = ConformityCause.objects.get(pk=pk)
        except ConformityCause.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ConformityCauseSerializer(conformity_cause)
        return Response(serializer.data)

  
    def put(self, request, pk):
        try:
            conformity_cause = ConformityCause.objects.get(pk=pk)
        except ConformityCause.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ConformityCauseSerializer(conformity_cause, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

   
    def delete(self, request, pk):
        try:
            conformity_cause = ConformityCause.objects.get(pk=pk)
        except ConformityCause.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        conformity_cause.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

 
class ConformityView(APIView):
   
    def get(self, request):
        conformities = Conformity.objects.all()
        serializer = ConformitySerializer(conformities, many=True)
        return Response(serializer.data)

 
    def post(self, request):
        serializer = ConformitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConformityDetailView(APIView):
 
    def get(self, request, pk):
        try:
            conformity = Conformity.objects.get(pk=pk)
        except Conformity.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ConformitySerializer(conformity)
        return Response(serializer.data)

    
    def put(self, request, pk):
        try:
            conformity = Conformity.objects.get(pk=pk)
        except Conformity.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ConformitySerializer(conformity, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
    def delete(self, request, pk):
        try:
            conformity = Conformity.objects.get(pk=pk)
        except Conformity.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        conformity.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

 
 










 

 

 


class UserChangePasswordView(generics.UpdateAPIView):

    def update(self, request, *args, **kwargs):
        print("request...", request.data)
        user_id = kwargs.get('id')
        user = get_object_or_404(Users, id=user_id)

        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        if not current_password or not new_password:
            return Response({"error": "Both current and new passwords are required."}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(current_password):
            return Response({"error": "Current password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

   
        user.set_password(new_password)
        user.save() 

        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)


 
  
class EditUserLogoAPIView(APIView):

    def put(self, request, user_id, *args, **kwargs):
        print("request data...", request.data)
        print("request files...", request.FILES)

        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

 
        data = request.data.copy()

        if "logo" in request.FILES:   
            data["user_logo"] = request.FILES["logo"]

        serializer = UserLogoSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            user.refresh_from_db()
            return Response(
                {"message": "User logo updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ValidateEmailView(APIView):
    def get(self, request):
        email = request.GET.get('email', '')       
        if not email:
            return Response({'status': 400, 'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)        
        if Users.objects.filter(email=email).exists():
            return Response({'status': 200, 'exists': True}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 200, 'exists': False}, status=status.HTTP_200_OK)

class ValidateEmailEditView(APIView):
    def get(self, request):
        email = request.GET.get('email', '')
        id = request.GET.get('id')  

        if not email:
            return Response({'status': 400, 'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        
        query = Users.objects.filter(email=email)
        
        
        if id:
            try:
                id = int(id) 
                query = query.exclude(id=id)
            except (ValueError, TypeError):
                
                print(f"Invalid company_id format: {id}")
                pass

 
        exists = query.exists()
        
        return Response({'status': 200, 'exists': exists}, status=status.HTTP_200_OK)

class ValidatuseridView(APIView):

    def get(self, request):
        username = request.GET.get('username', '')        
        if not username:
            return Response({'status': 400, 'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)        
        if Users.objects.filter(username=username).exists():
            return Response({'status': 200, 'exists': True}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 200, 'exists': False}, status=status.HTTP_200_OK)
    
class ValidateUsernameEditView(APIView):
    def get(self, request):
        username = request.GET.get('username', '')
        id = request.GET.get('id')
        
        if not username:
            return Response({'status': 400, 'error': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        query = Users.objects.filter(username=username)
        
        if id:
            try:
                id = int(id)
                query = query.exclude(id=id)
            except (ValueError, TypeError):
                print(f"Invalid user id format: {id}")
                pass
        
        exists = query.exists()
        
        return Response({'status': 200, 'exists': exists}, status=status.HTTP_200_OK)

    
class ChangeUserStatusView(APIView):
    def post(self, request, id):
        try:
            user = Users.objects.get(id=id)
        except Users.DoesNotExist:
            raise NotFound("User not found")

        action = request.data.get('action')   
        
        if action == 'block':
            user.status = 'blocked'
            user.save()
            return Response({"message": "User has been blocked successfully."}, status=status.HTTP_200_OK)
        
        elif action == 'active':
            user.status = 'active'
            user.save()
            return Response({"message": "User has been activated successfully."}, status=status.HTTP_200_OK)
        
        return Response({"error": "Invalid action. Use 'block' or 'active'."}, status=status.HTTP_400_BAD_REQUEST)


class UserPermissionsAPIView(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
            permissions = list(user.permissions.values_list('name', flat=True))
            return Response({'permissions': permissions}, status=status.HTTP_200_OK)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
        