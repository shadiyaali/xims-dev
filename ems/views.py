import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from django.conf import settings
logger = logging.getLogger(__name__)  
from accounts.models import *
from company.models import *
from django.db import transaction
from django.core.mail import send_mail
from decouple import config  
 
from django.shortcuts import get_object_or_404


class PolicyEnvCreateView(APIView):
    def post(self, request):
        serializer = PolicyEnvSerializer(data=request.data)
        if serializer.is_valid():
       
            serializer.save()   
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class PolicyEnvAllList(APIView):
    def get(self, request, company_id):
        try:
            
            if not Company.objects.filter(id=company_id).exists():
                return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

 
            users_in_company = Users.objects.filter(company_id=company_id).values_list('id', flat=True)

 
            company_policies = PolicyEnv.objects.filter(company_id=company_id)

      
            user_policies = PolicyEnv.objects.filter(user_id__in=users_in_company)

       
            all_policies = company_policies | user_policies

        
            serializer = PolicyEnvSerializer(all_policies, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class PolicyEnvDeleteView(APIView):
    def delete(self, request, pk, format=None):
        policy_env = get_object_or_404(PolicyEnv, pk=pk)
        policy_env.delete()
        return Response({"message": "Policy document deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
class ManualView(APIView):
  
    def post(self, request):
        logger.info("Received manual creation request.")
        serializer = ManualEnv(data=request.data)

        if serializer.is_valid():
            manual = serializer.save()

    
            if manual.written_by and manual.written_by.email:
                logger.info(f"Manual created by {manual.written_by.email}, attempting to send email.")
                self.send_email_notification(manual)
            else:
                logger.warning("Manual created, but no associated user email found.")

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.error(f"Manual creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_email_notification(self, manual):
        recipient_email = manual.written_by.email if manual.written_by else None

        if recipient_email:
            try:
                send_mail(
                    subject=f"Manual Created: {manual.title}",
                    message=(
                        f"Dear {manual.written_by.first_name},\n\n"
                        f"Your manual titled '{manual.title}' has been successfully created.\n\n"
                        f"Review Frequency (Years): {manual.review_frequency_year or 'N/A'}\n"
                        f"Review Frequency (Months): {manual.review_frequency_month or 'N/A'}\n"
                        f"Document Type: {manual.document_type}\n\n"
                        f"Best regards,\nDocumentation Team"
                    ),
                    from_email=config('EMAIL_HOST_USER'),
                    recipient_list=[recipient_email],
                    fail_silently=False,
                )
                logger.info(f"Email successfully sent to {recipient_email}")
            except Exception as e:
                logger.error(f"Failed to send email: {str(e)}")
                
class ManualAllList(APIView):
    def get(self, request, company_id):
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

        manuals = ManualEnv.objects.filter(company=company)
        serializer = ManualEnvGetSerializer(manuals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    