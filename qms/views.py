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
from django.utils.timezone import now
from django.http import HttpResponse, JsonResponse
from django.views import View
from botocore.exceptions import ClientError
import boto3
import logging
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.generics import RetrieveDestroyAPIView






 
class PolicyDocumentationCreateView(APIView):
    def post(self, request):
        serializer = DocumentationSerializer(data=request.data)
        if serializer.is_valid():
       
            serializer.save()   
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class PolicyAllList(APIView):
    def get(self, request, company_id):
        try:
        
            if not Company.objects.filter(id=company_id).exists():
                return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

           
            company_policies = PolicyDocumentation.objects.filter(company_id=company_id)

           
            serializer = DocumentationSerializer(company_policies, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PolicyDocumentationDetailView(APIView):
    def get(self, request, id):
        policy = get_object_or_404(PolicyDocumentation, id=id)
        serializer = DocumentationSerializer(policy)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PolicyDocumentationUpdateView(APIView):
    def put(self, request, pk):
        try:
            documentation = PolicyDocumentation.objects.get(pk=pk)
        except PolicyDocumentation.DoesNotExist:
            return Response({"error": "Documentation not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = DocumentationSerializer(documentation, data=request.data)
        if serializer.is_valid():
            serializer.save()   
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            documentation = PolicyDocumentation.objects.get(pk=pk)
        except PolicyDocumentation.DoesNotExist:
            return Response({"error": "Documentation not found"}, status=status.HTTP_404_NOT_FOUND)
        
        documentation.delete()   
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ManualView(APIView):
  
    def post(self, request):
        logger.info("Received manual creation request.")
        serializer = ManualSerializer(data=request.data)

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

      
        manuals = Manual.objects.filter(company=company, is_draft=False)
        serializer = ManualGetSerializer(manuals, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class ManualDetailView(APIView):
    def get(self, request, pk):
        try:
            manual = Manual.objects.get(pk=pk)
        except Manual.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ManualGetSerializer(manual)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            manual = Manual.objects.get(pk=pk)
        except Manual.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ManualSerializer(manual, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            manual = Manual.objects.get(pk=pk)
        except Manual.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        manual.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




 

 
logger = logging.getLogger(__name__)

def parse_bool(value):
    return str(value).strip().lower() in ['yes', 'true', '1']

class ManualCreateView(APIView):
    def post(self, request):
        logger.info("Received manual creation request.")
        serializer = ManualSerializer(data=request.data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    manual = serializer.save()
                    manual.written_at = now()
                    manual.is_draft = False

                    manual.send_notification_to_checked_by = parse_bool(
                        request.data.get('send_notification_to_checked_by')
                    )
                    manual.send_email_to_checked_by = parse_bool(
                        request.data.get('send_email_to_checked_by')
                    )
                 

                    manual.save()
                    logger.info(f"Manual created successfully with ID: {manual.id}")

                    if manual.checked_by:
                        if manual.send_notification_to_checked_by:
                            try:
                                NotificationQMS.objects.create(
                                    user=manual.checked_by,
                                    manual=manual,
                                    title="Notification for Checking/Review",
                                    message="A manual has been created for your review."
                                )
                                logger.info(f"Notification created for checked_by user {manual.checked_by.id}")
                            except Exception as e:
                                logger.error(f"Error creating notification for checked_by: {str(e)}")

                        if manual.send_email_to_checked_by and manual.checked_by.email:
                            self.send_email_notification(manual, manual.checked_by, "review")
                        else:
                            logger.warning("Email to checked_by skipped: flag disabled or email missing.")
                    else:
                        logger.warning("No checked_by user assigned.")

                    return Response(
                        {"message": "Manual created successfully", "id": manual.id},
                        status=status.HTTP_201_CREATED
                    )

            except Exception as e:
                logger.error(f"Error during manual creation: {str(e)}")
                return Response(
                    {"error": "An unexpected error occurred."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        logger.error(f"Manual creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_email_notification(self, manual, recipient, action_type):
        recipient_email = recipient.email if recipient else None

        if recipient_email:
            try:
                if action_type == "review":
                    subject = f"Manual Ready for Review: {manual.title}"

                    from django.template.loader import render_to_string
                    from django.utils.html import strip_tags

                    context = {
                        'recipient_name': recipient.first_name,
                        'title': manual.title,
                        'document_number': manual.no or 'N/A',
                        'review_frequency_year': manual.review_frequency_year or 0,
                        'review_frequency_month': manual.review_frequency_month or 0,
                        'document_type': manual.document_type,
                        'section_number': manual.no,
                        'revision': manual.rivision,
                        "written_by": manual.written_by,
                        "checked_by": manual.checked_by,
                        "approved_by": manual.approved_by,
                        'date': manual.date,
                        'document_url': manual.upload_attachment.url if manual.upload_attachment else None,
                        'document_name': manual.upload_attachment.name.rsplit('/', 1)[-1] if manual.upload_attachment else None,
                    }

                    html_message = render_to_string('qms/manual/manual_to_checked_by.html', context)
                    plain_message = strip_tags(html_message)

                    send_mail(
                        subject=subject,
                        message=plain_message,
                        from_email=config("EMAIL_HOST_USER"),
                        recipient_list=[recipient_email],
                        fail_silently=False,
                        html_message=html_message,
                    )
                    logger.info(f"HTML Email successfully sent to {recipient_email} for action: {action_type}")
                else:
                    logger.warning("Unknown action type provided for email.")
                    return
            except Exception as e:
                logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        else:
            logger.warning("Recipient email is None. Skipping email send.")



 
                
 
    
class RecordFormatPostView(APIView):

    def post(self, request):
        serializer = RecordFormatSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class RecordFormatView(APIView):
    def get(self, request, company_id):
        records = RecordFormat.objects.filter(company_id=company_id)
        
        if not records.exists():
            return Response({"error": "No records found for this company"}, status=status.HTTP_404_NOT_FOUND)

        serializer = RecordFormatGetSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class RecordFormatDetailView(APIView):
   
    def get(self, request, pk):
        try:
            record_format = RecordFormat.objects.get(pk=pk)
        except RecordFormat.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RecordFormatSerializer(record_format)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            record_format = RecordFormat.objects.get(pk=pk)
        except RecordFormat.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RecordFormatSerializer(record_format, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            record_format = RecordFormat.objects.get(pk=pk)
        except RecordFormat.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        record_format.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class NotificationView(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(Users, id=user_id)
        notifications = NotificationQMS.objects.filter(user=user ).order_by("-created_at")
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, user_id):
        user = get_object_or_404(Users, id=user_id)
        NotificationQMS.objects.filter(user=user, is_read=False).update(is_read=True)
        return Response({"message": "Notifications marked as read"}, status=status.HTTP_200_OK)
    
 
 



class SubmitCorrectionView(APIView):
    def post(self, request):
        try:
            manual_id = request.data.get('manual_id')
            correction_text = request.data.get('correction')
            from_user_id = request.data.get('from_user')

            if not all([manual_id, correction_text, from_user_id]):
                return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                manual = Manual.objects.get(id=manual_id)
            except Manual.DoesNotExist:
                return Response({'error': 'Manual not found'}, status=status.HTTP_404_NOT_FOUND)

            try:
                from_user = Users.objects.get(id=from_user_id)
            except Users.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

         
            if from_user == manual.checked_by:
                to_user = manual.written_by
            elif from_user == manual.approved_by:
                to_user = manual.checked_by
            else:
                return Response({'error': 'Invalid user role for correction'}, status=status.HTTP_400_BAD_REQUEST)

     
            

     
            correction = CorrectionQMS.objects.create(
                manual=manual,
                to_user=to_user,
                from_user=from_user,
                correction=correction_text
            )

         
            manual.status = 'Correction Requested'
            manual.save()

  
            self.create_correction_notification(correction)
            self.send_correction_email_notification(correction)

            serializer = CorrectionQMSSerializer(correction)
            return Response(
                {'message': 'Correction submitted successfully', 'correction': serializer.data},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create_correction_notification(self, correction):
        try:
            manual = correction.manual
            to_user = correction.to_user
            from_user = correction.from_user

            if from_user == manual.approved_by and to_user == manual.checked_by:
                should_send = manual.send_notification_to_checked_by
            elif from_user == manual.checked_by and to_user == manual.written_by:
                should_send = True
            else:
                should_send = False

            if should_send:
                message = (
                    f"Correction Request from {from_user.first_name} "
                    f"to {to_user.first_name} for Manual: {manual.title}"
                )
                notification = NotificationQMS.objects.create(
                    user=to_user,
                    manual=manual,
                    message=message
                )
                print(f"Correction Notification created successfully: {notification.id}")
            else:
                print("Notification not sent due to permission flags or invalid role flow.")
        except Exception as e:
            print(f"Failed to create correction notification: {str(e)}")

    def send_correction_email_notification(self, correction):
        manual    = correction.manual
        from_user = correction.from_user
        to_user   = correction.to_user
        recipient_email = to_user.email if to_user else None

       
        if from_user == manual.checked_by and to_user == manual.written_by:
           
            template_name = 'qms/manual/manual_correction_to_writer.html'
            subject = f"Correction Requested on '{manual.title}'"
           
            should_send = True
        elif from_user == manual.approved_by and to_user == manual.checked_by:
        
            template_name = 'qms/manual/manual_correction_to_checker.html'
            subject = f"Correction Requested on '{manual.title}'"
            should_send = manual.send_email_to_checked_by
        else:
     
            return

        if not recipient_email or not should_send:
            return

  
        context = {
                        'recipient_name': to_user.first_name,
                        'title': manual.title,
                        'document_number': manual.no or 'N/A',
                        'review_frequency_year': manual.review_frequency_year or 0,
                        'review_frequency_month': manual.review_frequency_month or 0,
                        'document_type': manual.document_type,
                        'section_number': manual.no,
                        'revision': manual.rivision,
                        "written_by": manual.written_by,
                        "checked_by": manual.checked_by,
                        "approved_by": manual.approved_by,
                        'date': manual.date,
                        'document_url': manual.upload_attachment.url if manual.upload_attachment else None,
                        'document_name': manual.upload_attachment.name.rsplit('/', 1)[-1] if manual.upload_attachment else None,
                    }

        # Render and send
        html_message  = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[recipient_email],
            fail_silently=False,
            html_message=html_message,
        )




class ManualCorrectionsListView(generics.ListAPIView):
    serializer_class = CorrectionGetQMSSerializer

    def get_queryset(self):
        manual_id = self.kwargs.get("manual_id")
        return CorrectionQMS.objects.filter(manual_id=manual_id)
    
    


from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

class ManualReviewView(APIView):
    def post(self, request):
        logger.info("Received request for manual review process.")
        
        try:
            manual_id = request.data.get('manual_id')
            current_user_id = request.data.get('current_user_id')

            if not all([manual_id, current_user_id]):
                return Response({'error': 'Missing required parameters'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                manual = Manual.objects.get(id=manual_id)
                current_user = Users.objects.get(id=current_user_id)
            except (Manual.DoesNotExist, Users.DoesNotExist):
                return Response({'error': 'Invalid manual or user'}, status=status.HTTP_404_NOT_FOUND)

            with transaction.atomic():
                if current_user == manual.written_by and not manual.written_at:
                    manual.written_at = now()
                    manual.save()

                current_status = manual.status

                # Case 1: Checked_by reviews
                if current_status == 'Pending for Review/Checking' and current_user == manual.checked_by:
                    manual.status = 'Reviewed,Pending for Approval'
                    manual.checked_at = now()
                    manual.save()

                    if manual.send_notification_to_approved_by:
                        NotificationQMS.objects.create(
                            user=manual.approved_by,
                            manual=manual,
                            message=f"Manual '{manual.title}' is ready for approval."
                        )

                    if manual.send_email_to_approved_by:
                        self.send_email_notification(
                            manual=manual,
                            recipients=[manual.approved_by],  # list of one
                            action_type="review"
                        )

                # Case 2: Approved_by approves
                elif current_status == 'Reviewed,Pending for Approval' and current_user == manual.approved_by:
                    manual.status = 'Pending for Publish'
                    manual.approved_at = now()
                    manual.save()

                    # Send notifications
                    for user in [manual.written_by, manual.checked_by, manual.approved_by]:
                        if user:
                            NotificationQMS.objects.create(
                                user=user,
                                manual=manual,
                                message=f"Manual '{manual.title}' has been approved and is pending for publish."
                            )

                    # Send emails
                    self.send_email_notification(
                        manual=manual,
                        recipients=[u for u in [manual.written_by, manual.checked_by, manual.approved_by] if u],
                        action_type="approved"
                    )

                # Correction Requested Case
                elif current_status == 'Correction Requested' and current_user == manual.written_by:
                    manual.status = 'Pending for Review/Checking'
                    manual.save()

                else:
                    return Response({
                        'message': 'No action taken. User not authorized for current manual status.'
                    }, status=status.HTTP_200_OK)

            return Response({
                'status': 'success',
                'message': 'Manual processed successfully',
                'manual_status': manual.status
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in manual review process: {str(e)}")
            return Response({
                'error': 'An unexpected error occurred',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def send_email_notification(self, manual, recipients, action_type):
        from decouple import config   

        for recipient in recipients:
            recipient_email = recipient.email if recipient else None

            if recipient_email:
                try:
                    if action_type == "review":
                        subject = f"Manual Submitted for Approval: {manual.title}"
                        context = {
                        'recipient_name': recipient.first_name,
                        'title': manual.title,
                        'document_number': manual.no or 'N/A',
                        'review_frequency_year': manual.review_frequency_year or 0,
                        'review_frequency_month': manual.review_frequency_month or 0,
                        'document_type': manual.document_type,
                        'section_number': manual.no,
                        'revision': manual.rivision,
                        "written_by": manual.written_by,
                        "checked_by": manual.checked_by,
                        "approved_by": manual.approved_by,
                        'date': manual.date,
                        'document_url': manual.upload_attachment.url if manual.upload_attachment else None,
                        'document_name': manual.upload_attachment.name.rsplit('/', 1)[-1] if manual.upload_attachment else None,
                    }
                        html_message = render_to_string('qms/manual/manual_to_approved_by.html', context)
                        plain_message = strip_tags(html_message)

                    elif action_type == "approved":
                        subject = f"Manual Approved: {manual.title}"
                        context = {
                            'recipient_name': recipient.first_name,
                            'title': manual.title,
                            'document_number': manual.no or 'N/A',
                            'document_type': manual.document_type,
                            'revision': manual.rivision,
                            'date': manual.date,
                            'document_url': manual.upload_attachment.url if manual.upload_attachment else None,
                            'document_name': manual.upload_attachment.name.rsplit('/', 1)[-1] if manual.upload_attachment else None,
                        }
                        html_message = render_to_string('qms/manual/manual_publish.html', context)
                        plain_message = strip_tags(html_message)

                    else:
                        logger.warning(f"Unknown action type '{action_type}' for email notification.")
                        continue

                    send_mail(
                        subject=subject,
                        message=plain_message,
                        from_email=config('EMAIL_HOST_USER'),
                        recipient_list=[recipient_email],
                        fail_silently=False,
                        html_message=html_message,
                    )
                    logger.info(f"Email successfully sent to {recipient_email} for action: {action_type}")

                except Exception as e:
                    logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
            else:
                logger.warning("Recipient email is None. Skipping email send.")



 

class NotificationsQMS(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        
        notifications = NotificationQMS.objects.filter(user=user).order_by('-created_at')

        serializer = NotificationSerializer(notifications, many=True)

        return Response({
            "notifications": serializer.data
        }, status=status.HTTP_200_OK)


class NotificationsProcedure(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(Users, id=user_id)
        notifications = NotificatioProcedure.objects.filter(user=user ).order_by("-created_at")
        serializer = NotificationProcedureSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, user_id):
        user = get_object_or_404(Users, id=user_id)
        NotificatioProcedure.objects.filter(user=user, is_read=False).update(is_read=True)
        return Response({"message": "Notifications marked as read"}, status=status.HTTP_200_OK)
 


class ManualUpdateView(APIView):
    def put(self, request, pk):
        print("Request data:", request.data)
        try:
            with transaction.atomic():
                manual = Manual.objects.get(pk=pk)

                serializer = ManualUpdateSerializer(manual, data=request.data, partial=True)

                if serializer.is_valid():
                    updated_manual = serializer.save()

                    updated_manual.written_at = now()
                    updated_manual.is_draft = False
                    updated_manual.status = 'Pending for Review/Checking'

                    updated_manual.send_notification_to_checked_by = parse_bool(request.data.get('send_system_checked'))
                    updated_manual.send_email_to_checked_by = parse_bool(request.data.get('send_email_checked'))

                    updated_manual.save()

                    # Handle notification/email to checked_by
                    if updated_manual.checked_by:
                        if updated_manual.send_notification_to_checked_by:
                            try:
                                NotificationQMS.objects.create(
                                    user=updated_manual.checked_by,
                                    manual=updated_manual,
                                    title="Manual Updated - Review Required",
                                    message=f"Manual '{updated_manual.title}' has been updated and requires your review."
                                )
                            except Exception as e:
                                logger.error(f"Notification error for checked_by: {str(e)}")

                        if updated_manual.send_email_to_checked_by and updated_manual.checked_by.email:
                            self.send_email_notification(updated_manual, updated_manual.checked_by, "review")

                    return Response({"message": "Manual updated successfully"}, status=status.HTTP_200_OK)

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Manual.DoesNotExist:
            return Response({"error": "Manual not found"}, status=status.HTTP_404_NOT_FOUND)

  

    def send_email_notification(self, manual, recipient, action_type):
        recipient_email = recipient.email if recipient else None

        if recipient_email:
            try:
                if action_type == "review":
                    subject = f"Manual Corrections Updated: {manual.title}"

                    from django.template.loader import render_to_string
                    from django.utils.html import strip_tags

                    context = {
                        'recipient_name': recipient.first_name,
                        'title': manual.title,
                        'document_number': manual.no or 'N/A',
                        'review_frequency_year': manual.review_frequency_year or 0,
                        'review_frequency_month': manual.review_frequency_month or 0,
                        'document_type': manual.document_type,
                        'section_number': manual.no,
                        'revision': manual.rivision,
                        "written_by": manual.written_by,
                        "checked_by": manual.checked_by,
                        "approved_by": manual.approved_by,
                        'date': manual.date,
                        'document_url': manual.upload_attachment.url if manual.upload_attachment else None,
                        'document_name': manual.upload_attachment.name.rsplit('/', 1)[-1] if manual.upload_attachment else None,
                    }

                    html_message = render_to_string('qms/manual/manual_update_to_checked_by.html', context)
                    plain_message = strip_tags(html_message)

                    send_mail(
                        subject=subject,
                        message=plain_message,
                        from_email=config("EMAIL_HOST_USER"),
                        recipient_list=[recipient_email],
                        fail_silently=False,
                        html_message=html_message,
                    )
                    logger.info(f"HTML Email successfully sent to {recipient_email} for action: {action_type}")
                else:
                    logger.warning("Unknown action type provided for email.")
                    return
            except Exception as e:
                logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        else:
            logger.warning("Recipient email is None. Skipping email send.")




        
class ManualDraftAPIView(APIView):
    def post(self, request, *args, **kwargs):
      
        data = {}
    
        for key in request.data:
            if key != 'upload_attachment':
                data[key] = request.data[key]

        data['is_draft'] = True
        
  
        file_obj = request.FILES.get('upload_attachment')
        
        serializer = ManualSerializer(data=data)
        if serializer.is_valid():
            manual = serializer.save()
            
 
            if file_obj:
                manual.upload_attachment = file_obj
                manual.save()
                
            return Response({"message": "Manual saved as draft", "data": serializer.data}, 
                           status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class ManualDraftAllList(APIView):
    def get(self, request, company_id):
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

      
        manuals = Manual.objects.filter(company=company, is_draft=True)
        serializer = ManualGetSerializer(manuals, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UnreadNotificationsAPIView(APIView):
    def get(self, request, user_id):
        try:
            unread_count = NotificationQMS.objects.filter(user_id=user_id, is_read=False).count()
            return Response({"unread_count": unread_count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class MarkNotificationReadAPIView(APIView):
    
    def patch(self, request, notification_id):
        try:
            notification = get_object_or_404(NotificationQMS, id=notification_id)          
            notification.is_read = True
            notification.save()
            serializer = NotificationSerializer(notification)
            return Response(serializer.data, status=status.HTTP_200_OK)        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class ManualDraftAllList(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        manuals = Manual.objects.filter(user=user, is_draft=True)
        serializer = ManualGetSerializer(manuals, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class DraftManualcountAPIView(APIView):
 
    def get(self, request, user_id):
        # Change filter to find manuals where user_id matches and is_draft is True
        draft_manuals = Manual.objects.filter(is_draft=True, user_id=user_id)
        
        serializer = ManualSerializer(draft_manuals, many=True)
        
        return Response({
            "count": draft_manuals.count(),
            "draft_manuals": serializer.data
        }, status=status.HTTP_200_OK)
        
 
 
logger = logging.getLogger(__name__)

class ManualPublishNotificationView(APIView):
    """
    Endpoint to handle publishing a manual and sending notifications to company users.
    """

    def post(self, request, manual_id):
        try:
          
            manual = Manual.objects.get(id=manual_id)
            company_id = request.data.get('company_id')
            published_by = request.data.get('published_by')  
            send_notification = request.data.get('send_notification', False)
            
            if not company_id:
                return Response(
                    {"error": "Company ID is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            company = Company.objects.get(id=company_id)

            with transaction.atomic():
                # Update manual status and published information
                manual.status = 'Published'
                manual.published_at = now()
                
                # Set the published_user if the ID was provided
                if published_by:
                    try:
                        publishing_user = Users.objects.get(id=published_by)
                        manual.published_user = publishing_user
                    except Users.DoesNotExist:
                        logger.warning(f"Publisher user ID {published_by} not found")
                
                # Only send notifications if requested
                manual.send_notification = send_notification
                manual.save()

                # Only proceed with notifications if send_notification is True
                if send_notification:
                    # Get all users in the company
                    company_users = Users.objects.filter(company=company)

                    # Create notifications for each user
                    notifications = [
                        NotificationQMS(
                            user=user,
                            manual=manual,
                            title=f"Manual Published: {manual.title}",
                            message=f"A new manual '{manual.title}' has been published."
                        )
                        for user in company_users
                    ]

                    # Bulk create all notifications
                    if notifications:
                        NotificationQMS.objects.bulk_create(notifications)
                        logger.info(f"Created {len(notifications)} notifications for manual {manual_id}")

                    # Send emails
                    for user in company_users:
                        if user.email:
                            try:
                                self._send_publish_email(manual, user)
                            except Exception as e:
                                logger.error(f"Failed to send email to {user.email}: {str(e)}")

            return Response(
                {
                    "message": "Manual published successfully",
                    "notification_sent": send_notification,
                    "publisher_set": published_by is not None
                },
                status=status.HTTP_200_OK
            )

        except Manual.DoesNotExist:
            return Response(
                {"error": "Manual not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Company.DoesNotExist:
            return Response(
                {"error": "Company not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error in publish notification: {str(e)}")
            return Response(
                {"error": f"Failed to publish manual: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    from django.template.loader import render_to_string
    from django.utils.html import strip_tags

    def _send_publish_email(self, manual, recipient):
        """Helper method to send email notifications with template"""
        publisher_name = "N/A"
        if manual.published_user:
            publisher_name = f"{manual.published_user.first_name} {manual.published_user.last_name}"
        elif manual.approved_by:
            publisher_name = f"{manual.approved_by.first_name} {manual.approved_by.last_name}"

        subject = f"New Manual Published: {manual.title}"

        # Context for the email template
        context = {
                        'recipient_name': recipient.first_name,
                        'title': manual.title,
                        'document_number': manual.no or 'N/A',
                        'review_frequency_year': manual.review_frequency_year or 0,
                        'review_frequency_month': manual.review_frequency_month or 0,
                        'document_type': manual.document_type,
                        'section_number': manual.no,
                        'revision': manual.rivision,
                        "written_by": manual.written_by,
                        "checked_by": manual.checked_by,
                        "approved_by": manual.approved_by,
                        'date': manual.date,
                        'document_url': manual.upload_attachment.url if manual.upload_attachment else None,
                        'document_name': manual.upload_attachment.name.rsplit('/', 1)[-1] if manual.upload_attachment else None,
                    }

        # Render the HTML email
        html_message = render_to_string('qms/manual/manual_published_notification.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=config("EMAIL_HOST_USER"),
            recipient_list=[recipient.email],
            fail_silently=False,
            html_message=html_message,
        )
        logger.info(f"HTML Email sent to {recipient.email}")

 

 

class PolicyFileDownloadView(View):
    """View to handle policy file downloads from S3 storage"""
    
    def get(self, request, policy_id):
        try:
            # Get the policy object or return 404
            policy = get_object_or_404(PolicyDocumentation, id=policy_id)
            
            # Check if the policy has an attached file
            if not policy.energy_policy or not policy.energy_policy.name:
                return JsonResponse({"error": "No file attached to this policy"}, status=404)

            # Get bucket name from settings
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            if not bucket_name:
                bucket_name = "hoztox-test"  # fallback

            # Get file key and make sure it includes the 'media/' prefix
            file_key = policy.energy_policy.name
            if not file_key.startswith("media/"):
                file_key = f"media/{file_key}"

            print(f"Generating download URL for file: {file_key} in bucket: {bucket_name}")
            
            # Create the S3 client
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME or 'ap-south-1'
            )
            
            # Generate a presigned URL
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': file_key,
                    'ResponseContentDisposition': f'attachment; filename="{os.path.basename(file_key)}"'
                },
                ExpiresIn=3600  # 1 hour
            )

            print(f"Generated presigned URL: {url}")
            return JsonResponse({"download_url": url})

        except ClientError as e:
            print(f"S3 client error: {e}")
            return JsonResponse({"error": f"S3 error: {str(e)}"}, status=500)

        except Exception as e:
            print(f"Unexpected error: {e}")
            return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)



def parse_bool(value):
    return str(value).strip().lower() in ['yes', 'true', '1']

class ProcedureCreateView(APIView):
 
    def post(self, request):
        logger.info("Received Procedure creation request.")
        serializer = ProcedureSerializer(data=request.data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    procedure = serializer.save()
                    procedure.written_at = now()
                    procedure.is_draft = False

                    procedure.send_notification_to_checked_by = parse_bool(
                        request.data.get('send_notification_to_checked_by')
                    )
                    procedure.send_email_to_checked_by = parse_bool(
                        request.data.get('send_email_to_checked_by')
                    )
                 

                    procedure.save()
                    logger.info(f"Procedure created successfully with ID: {procedure.id}")

                    if procedure.checked_by:
                        if procedure.send_notification_to_checked_by:
                            try:
                                NotificatioProcedure.objects.create(
                                    user=procedure.checked_by,
                                    procedure=procedure,
                                    title="Notification for Checking/Review",
                                    message="A Procedure has been created for your review."
                                )
                                logger.info(f"Notification created for checked_by user {procedure.checked_by.id}")
                            except Exception as e:
                                logger.error(f"Error creating notification for checked_by: {str(e)}")

                        if procedure.send_email_to_checked_by and procedure.checked_by.email:
                            self.send_email_notification(procedure, procedure.checked_by, "review")
                        else:
                            logger.warning("Email to checked_by skipped: flag disabled or email missing.")
                    else:
                        logger.warning("No checked_by user assigned.")

                    return Response(
                        {"message": "procedure created successfully", "id": procedure.id},
                        status=status.HTTP_201_CREATED
                    )

            except Exception as e:
                logger.error(f"Error during procedure creation: {str(e)}")
                return Response(
                    {"error": "An unexpected error occurred."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        logger.error(f"procedure creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_email_notification(self, procedure, recipient, action_type):
        recipient_email = recipient.email if recipient else None

        if recipient_email:
            try:
                if action_type == "review":
                    subject = f"procedure Ready for Review: {procedure.title}"
                    message = (
                        f"Dear {recipient.first_name},\n\n"
                        f"A procedure titled '{procedure.title}' requires your review.\n\n"
                        f"Document Number: {procedure.no or 'N/A'}\n"
                        f"Review Frequency: {procedure.review_frequency_year or 0} year(s), "
                        f"{procedure.review_frequency_month or 0} month(s)\n"
                        f"Document Type: {procedure.document_type}\n\n"
                        f"Please login to the system to review.\n\n"
                        f"Best regards,\nDocumentation Team"
                    )
                else:
                    logger.warning("Unknown action type provided for email.")
                    return

                send_mail(
                    subject=subject,
                    message=message,
                    from_email=config("EMAIL_HOST_USER"),
                    recipient_list=[recipient_email],
                    fail_silently=False,
                )
                logger.info(f"Email successfully sent to {recipient_email} for action: {action_type}")

            except Exception as e:
                logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        else:
            logger.warning("Recipient email is None. Skipping email send.")


class ProcedureAllList(APIView):
    def get(self, request, company_id):
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

      
        procedures = Procedure.objects.filter(company=company, is_draft=False)
        serializer = ProcedureGetSerializer(procedures, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ProcedureDetailView(APIView):
    def get(self, request, pk):
        try:
            procedure = Procedure.objects.get(pk=pk)
        except Procedure.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProcedureGetSerializer(procedure)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            procedure = Procedure.objects.get(pk=pk)
        except Procedure.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProcedureSerializer(procedure, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            procedure = Procedure.objects.get(pk=pk)
        except Procedure.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        procedure.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ProcedureUpdateView(APIView):
    def put(self, request, pk):
        print("fsddf",request.data)
        try:
            with transaction.atomic():
                procedure = Procedure.objects.get(pk=pk)

                serializer = ProcedureUpdateSerializer(procedure, data=request.data, partial=True)

                if serializer.is_valid():
                    updated_procedure = serializer.save()

                 
                    updated_procedure.written_at = now()
                    updated_procedure.is_draft = False
                    updated_procedure.status = 'Pending for Review/Checking'
 
                    updated_procedure.send_notification_to_checked_by = parse_bool(request.data.get('send_system_checked'))
                    updated_procedure.send_email_to_checked_by = parse_bool(request.data.get('send_email_checked'))
                    updated_procedure.send_notification_to_approved_by = parse_bool(request.data.get('send_system_approved'))
                    updated_procedure.send_email_to_approved_by = parse_bool(request.data.get('send_email_approved'))



                    updated_procedure.save()

                 
                    if updated_procedure.checked_by:
                        if updated_procedure.send_notification_to_checked_by:
                            try:
                                NotificatioProcedure.objects.create(
                                    user=updated_procedure.checked_by,
                                    procedure=updated_procedure,
                                    title="procedure Updated - Review Required",
                                    message=f"Procedure '{updated_procedure.title}' has been updated and requires your review."
                                )
                            except Exception as e:
                                logger.error(f"Notification error for checked_by: {str(e)}")

                        if updated_procedure.send_email_to_checked_by and updated_procedure.checked_by.email:
                            self.send_email_notification(updated_procedure, updated_procedure.checked_by, "review")

                    
                    if updated_procedure.approved_by:
                        if updated_procedure.send_notification_to_approved_by:
                            try:
                                NotificatioProcedure.objects.create(
                                    user=updated_procedure.approved_by,
                                    procedure=updated_procedure,
                                    title="procedure Updated - Approval Required",
                                    message=f"procedure '{updated_procedure.title}' has been updated and is ready for your approval."
                                )
                            except Exception as e:
                                logger.error(f"Notification error for approved_by: {str(e)}")

                        if updated_procedure.send_email_to_approved_by and updated_procedure.approved_by.email:
                            self.send_email_notification(updated_procedure, updated_procedure.approved_by, "approval")

                    return Response(serializer.data, status=status.HTTP_200_OK)

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Manual.DoesNotExist:
            return Response({"error": "procedure not found"}, status=status.HTTP_404_NOT_FOUND)

    def send_email_notification(self, procedure, recipient, action_type):
        recipient_email = recipient.email if recipient else None

        if recipient_email:
            try:
                if action_type == "review":
                    subject = f"procedure Ready for Review: {procedure.title}"
                    message = (
                        f"Dear {recipient.first_name},\n\n"
                        f"The procedure '{procedure.title}' has been updated and requires your review.\n\n"
                        f"Document Number: {procedure.no or 'N/A'}\n"
                        f"Review Frequency: {procedure.review_frequency_year or 0} year(s), "
                        f"{procedure.review_frequency_month or 0} month(s)\n"
                        f"Document Type: {procedure.document_type}\n\n"
                        f"Please login to the system to review.\n\n"
                        f"Best regards,\nDocumentation Team"
                    )
                elif action_type == "approval":
                    subject = f"procedure Pending Approval: {procedure.title}"
                    message = (
                        f"Dear {recipient.first_name},\n\n"
                        f"The procedure '{procedure.title}' has been updated and is ready for your approval.\n\n"
                        f"Document Number: {procedure.no or 'N/A'}\n"
                        f"Review Frequency: {procedure.review_frequency_year or 0} year(s), "
                        f"{procedure.review_frequency_month or 0} month(s)\n"
                        f"Document Type: {procedure.document_type}\n\n"
                        f"Please login to the system to approve.\n\n"
                        f"Best regards,\nDocumentation Team"
                    )
                else:
                    logger.warning("Unknown action type for email notification.")
                    return

                send_mail(
                    subject=subject,
                    message=message,
                    from_email=config("EMAIL_HOST_USER"),
                    recipient_list=[recipient_email],
                    fail_silently=False,
                )
                logger.info(f"Email sent to {recipient_email} for action: {action_type}")

            except Exception as e:
                logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        else:
            logger.warning("Recipient email is missing, skipping email.")


class SubmitCorrectionProcedureView(APIView):
    def post(self, request):
        try:
            procedure_id = request.data.get('manual_id')
            correction_text = request.data.get('correction')
            from_user_id = request.data.get('from_user')

            if not all([procedure_id, correction_text, from_user_id]):
                return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                procedure = Procedure.objects.get(id=procedure_id)
            except Procedure.DoesNotExist:
                return Response({'error': 'procedure not found'}, status=status.HTTP_404_NOT_FOUND)

            try:
                from_user = Users.objects.get(id=from_user_id)
            except Users.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Determine to_user based on from_user
            if from_user == procedure.checked_by:
                to_user = procedure.written_by
            elif from_user == procedure.approved_by:
                to_user = procedure.checked_by
            else:
                return Response({'error': 'Invalid user role for correction'}, status=status.HTTP_400_BAD_REQUEST)

            # Delete old correction
            

            # Create new correction
            correction = CorrectionProcedure.objects.create(
                procedure=procedure,
                to_user=to_user,
                from_user=from_user,
                correction=correction_text
            )

            # Update status
            procedure.status = 'Correction Requested'
            procedure.save()

            # Send notification and email
            self.create_correction_notification(correction)
            self.send_correction_email_notification(correction)

            serializer = CorrectionProcedureSerializer(correction)
            return Response(
                {'message': 'Correction submitted successfully', 'correction': serializer.data},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create_correction_notification(self, correction):
        try:
            procedure = correction.procedure
            to_user = correction.to_user
            from_user = correction.from_user

            if from_user == procedure.approved_by and to_user == procedure.checked_by:
                should_send = procedure.send_notification_to_checked_by
            elif from_user == procedure.checked_by and to_user == procedure.written_by:
                should_send = True
            else:
                should_send = False

            if should_send:
                message = (
                    f"Correction Request from {from_user.first_name} "
                    f"to {to_user.first_name} for procedure: {procedure.title}"
                )
                notification = NotificatioProcedure.objects.create(
                    user=to_user,
                    procedure=procedure,
                    message=message
                )
                print(f"Correction Notification created successfully: {notification.id}")
            else:
                print("Notification not sent due to permission flags or invalid role flow.")
        except Exception as e:
            print(f"Failed to create correction notification: {str(e)}")

    def send_correction_email_notification(self, correction):
        try:
            procedure = correction.procedure
            to_user = correction.to_user
            from_user = correction.from_user
            recipient_email = to_user.email if to_user else None

            if from_user == procedure.approved_by and to_user == procedure.checked_by:
                should_send = procedure.send_email_to_checked_by
            elif from_user == procedure.checked_by and to_user == procedure.written_by:
                should_send = True
            else:
                should_send = False

            if recipient_email and should_send:
                send_mail(
                    subject=f"Correction Request: {procedure.title}",
                    message=(
                        f"Dear {to_user.first_name},\n\n"
                        f"A correction has been requested by {from_user.first_name} for the procedure '{procedure.title}'.\n\n"
                        f"Correction details:\n"
                        f"{correction.correction}\n\n"
                        f"Please review and take necessary actions.\n\n"
                        f"Best regards,\nDocumentation Team"
                    ),
                    from_email=config("EMAIL_HOST_USER"),
                    recipient_list=[recipient_email],
                    fail_silently=False,
                )
                print(f"Correction email successfully sent to {recipient_email}")
            else:
                print("Email not sent due to permission flags, invalid roles, or missing email.")
        except Exception as e:
            print(f"Failed to send correction email: {str(e)}")
            
            
class CorrectionProcedureList(generics.ListAPIView):
    serializer_class = CorrectionProcedureSerializer

    def get_queryset(self):
        procedure_id = self.kwargs.get("procedure_id")
        return CorrectionProcedure.objects.filter(procedure_id=procedure_id)
    

class ProcedureReviewView(APIView):
    
    def post(self, request):
        logger.info("Received request for Procedure review process.")
        
        try:
            procedure_id = request.data.get('procedure_id')
            current_user_id = request.data.get('current_user_id')

            if not all([procedure_id, current_user_id]):
                return Response({'error': 'Missing required parameters'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                procedure = Procedure.objects.get(id=procedure_id)
                current_user = Users.objects.get(id=current_user_id)
            except (Procedure.DoesNotExist, Users.DoesNotExist):
                return Response({'error': 'Invalid procedure or user'}, status=status.HTTP_404_NOT_FOUND)

            with transaction.atomic():
                # Written by - First Submission
                if current_user == procedure.written_by and not procedure.written_at:
                    procedure.written_at = now()


                current_status = procedure.status
                
                # 1. If status is "Pending for Review/Checking" and user is checked_by
             
                # Review process
                if current_status == 'Pending for Review/Checking' and current_user == procedure.checked_by:
                    procedure.status = 'Reviewed,Pending for Approval'
                    procedure.checked_at = now()
                    procedure.save()

                    # Notification to approved_by (only if flag is True)
                    if procedure.send_notification_to_approved_by:
                        NotificatioProcedure.objects.create(
                            user=procedure.approved_by,
                            procedure=procedure,
                            message=f"procedure '{procedure.title}' is ready for approval."
                        )

                    # Email to approved_by (only if flag is True)
                    if procedure.send_email_to_approved_by:
                        self.send_email_notification(
                            recipient=procedure.approved_by,
                            subject=f"procedure {procedure.title} - Pending Approval",
                            message=f"The procedure '{procedure.title}' has been reviewed and is pending your approval."
                        )

                # Approval process
                elif current_user == procedure.approved_by:
                    procedure.status = 'Pending for Publish'
                    procedure.approved_at = now()
                    procedure.save()

                    # Notification to approved_by (only if flag is True)
                    # if manual.send_notification_to_checked_by:
                    #     NotificationQMS.objects.create(
                    #         user=manual.written_by,
                    #         manual=manual,
                    #         message=f"Manual '{manual.title}' has been approved."
                    #     )

                    # Email to approved_by (only if flag is True)
                    # if manual.send_email_to_checked_by:
                    #     self.send_email_notification(
                    #         recipient=manual.written_by,
                    #         subject=f"Manual {manual.title} - Approved",
                    #         message=f"Your manual '{manual.title}' has been approved."
                    #     )

                # Resubmission after correction
                elif current_status == 'Reviewed,Pending for Approval' and current_user == procedure.approved_by:
                    procedure.status = 'Pending for Review/Checking'
                    procedure.save()

                else:
                    return Response({
                        'message': 'No action taken. User not authorized for this Procedure.'
                    }, status=status.HTTP_200_OK)

            return Response({
                'status': 'success',
                'message': 'procedure processed successfully',
                'procedure_status': procedure.status
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in procedure review process: {str(e)}")
            return Response({
                'error': 'An unexpected error occurred',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def send_email_notification(self, recipient, subject, message):
        if recipient and recipient.email:
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=config("EMAIL_HOST_USER"),
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )
                logger.info(f"Email sent to {recipient.email}")
            except Exception as e:
                logger.error(f"Failed to send email: {str(e)}")


class ProcedureDraftAPIView(APIView):
    def post(self, request, *args, **kwargs):
  
        data = {}      
        for key in request.data:
            if key != 'upload_attachment':
                data[key] = request.data[key]      
        data['is_draft'] = True      
        file_obj = request.FILES.get('upload_attachment')
        
        serializer = ProcedureSerializer(data=data)
        if serializer.is_valid():
            procedure = serializer.save()
                     
            if file_obj:
                procedure.upload_attachment = file_obj
                procedure.save()
                
            return Response({"message": "Procedure saved as draft", "data": serializer.data}, 
                           status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProcedureDraftAllList(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        procedure = Procedure.objects.filter(user=user, is_draft=True)
        serializer = ProcedureGetSerializer(procedure, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class DrafProcedurecountAPIView(APIView):
 
    def get(self, request, user_id):
   
        draft_procedures = Procedure.objects.filter(is_draft=True, user_id=user_id)
        
        serializer = ProcedureSerializer(draft_procedures, many=True)
        
        return Response({
            "count": draft_procedures.count(),
            "draft_procedures": serializer.data
        }, status=status.HTTP_200_OK)
        
class UnreadProcedureNotificationsAPIView(APIView):
    def get(self, request, user_id):
        try:
            unread_count = NotificatioProcedure.objects.filter(user_id=user_id, is_read=False).count()
            return Response({"unread_count": unread_count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class MarkProcedureNotificationReadAPIView(APIView):
    
    def patch(self, request, notification_id):
        try:
            notification = get_object_or_404(NotificatioProcedure, id=notification_id)          
            notification.is_read = True
            notification.save()
            serializer = NotificationProcedureSerializer(notification)
            return Response(serializer.data, status=status.HTTP_200_OK)        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            
            
class NotificationsLastProcedure(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        
        notifications = NotificatioProcedure.objects.filter(user=user).order_by('-created_at')

        serializer = NotificationProcedureSerializer(notifications, many=True)

        return Response({
            "notifications": serializer.data
        }, status=status.HTTP_200_OK)
        
        
        
def parse_bool(value):
    return str(value).strip().lower() in ['yes', 'true', '1']

class RecordCreateView(APIView):
  
    def post(self, request):
        logger.info("Received Record creation request.")
        serializer = RecordSerializer(data=request.data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    record = serializer.save()
                    record.written_at = now()
                    record.is_draft = False

                    record.send_notification_to_checked_by = parse_bool(
                        request.data.get('send_notification_to_checked_by')
                    )
                    record.send_email_to_checked_by = parse_bool(
                        request.data.get('send_email_to_checked_by')
                    )
                 

                    record.save()
                    logger.info(f"record created successfully with ID: {record.id}")

                    if record.checked_by:
                        if record.send_notification_to_checked_by:
                            try:
                                NotificationRecord.objects.create(
                                    user=record.checked_by,
                                    record=record,
                                    title="Notification for Checking/Review",
                                    message="A record has been created for your review."
                                )
                                logger.info(f"Notification created for checked_by user {record.checked_by.id}")
                            except Exception as e:
                                logger.error(f"Error creating notification for checked_by: {str(e)}")

                        if record.send_email_to_checked_by and record.checked_by.email:
                            self.send_email_notification(record, record.checked_by, "review")
                        else:
                            logger.warning("Email to checked_by skipped: flag disabled or email missing.")
                    else:
                        logger.warning("No checked_by user assigned.")

                    return Response(
                        {"message": "record created successfully", "id": record.id},
                        status=status.HTTP_201_CREATED
                    )

            except Exception as e:
                logger.error(f"Error during record creation: {str(e)}")
                return Response(
                    {"error": "An unexpected error occurred."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        logger.error(f"record creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_email_notification(self, record, recipient, action_type):
        recipient_email = recipient.email if recipient else None

        if recipient_email:
            try:
                if action_type == "review":
                    subject = f"record Ready for Review: {record.title}"
                    message = (
                        f"Dear {recipient.first_name},\n\n"
                        f"A record titled '{record.title}' requires your review.\n\n"
                        f"Document Number: {record.no or 'N/A'}\n"
                        f"Review Frequency: {record.review_frequency_year or 0} year(s), "
                        f"{record.review_frequency_month or 0} month(s)\n"
                        f"Document Type: {record.document_type}\n\n"
                        f"Please login to the system to review.\n\n"
                        f"Best regards,\nDocumentation Team"
                    )
                else:
                    logger.warning("Unknown action type provided for email.")
                    return

                send_mail(
                    subject=subject,
                    message=message,
                    from_email=config("EMAIL_HOST_USER"),
                    recipient_list=[recipient_email],
                    fail_silently=False,
                )
                logger.info(f"Email successfully sent to {recipient_email} for action: {action_type}")

            except Exception as e:
                logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        else:
            logger.warning("Recipient email is None. Skipping email send.")

            
class RecordAllList(APIView):
    def get(self, request, company_id):
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

      
        procedures = RecordFormat.objects.filter(company=company, is_draft=False)
        serializer = RecordGetSerializer(procedures, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class RecordDetailView(APIView):
    def get(self, request, pk):
        try:
            record = RecordFormat.objects.get(pk=pk)
        except RecordFormat.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RecordGetSerializer(record)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            record = RecordFormat.objects.get(pk=pk)
        except RecordFormat.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RecordSerializer(record, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            record = RecordFormat.objects.get(pk=pk)
        except RecordFormat.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ComplainceView(APIView):
 
    def get(self, request, user_id):
   
        draft_records = Compliances.objects.filter(is_draft=True, user_id=user_id)
        
        serializer = ComplianceSerializer(draft_records, many=True)
        
        return Response({
            "count": draft_records.count(),
            "draft_records": serializer.data
        }, status=status.HTTP_200_OK)
        
    
class RecordUpdateView(APIView):
    def put(self, request, pk):
        print("fsddf",request.data)
        try:
            with transaction.atomic():
                record = RecordFormat.objects.get(pk=pk)

                serializer = RecordUpdateSerializer(record, data=request.data, partial=True)

                if serializer.is_valid():
                    updated_record = serializer.save()

                 
                    updated_record.written_at = now()
                    updated_record.is_draft = False
                    updated_record.status = 'Pending for Review/Checking'
 
                    updated_record.send_notification_to_checked_by = parse_bool(request.data.get('send_system_checked'))
                    updated_record.send_email_to_checked_by = parse_bool(request.data.get('send_email_checked'))
                    updated_record.send_notification_to_approved_by = parse_bool(request.data.get('send_system_approved'))
                    updated_record.send_email_to_approved_by = parse_bool(request.data.get('send_email_approved'))



                    updated_record.save()

                 
                    if updated_record.checked_by:
                        if updated_record.send_notification_to_checked_by:
                            try:
                                NotificationRecord.objects.create(
                                    user=updated_record.checked_by,
                                    record=updated_record,
                                    title="Record Updated - Review Required",
                                    message=f"Record '{updated_record.title}' has been updated and requires your review."
                                )
                            except Exception as e:
                                logger.error(f"Notification error for checked_by: {str(e)}")

                        if updated_record.send_email_to_checked_by and updated_record.checked_by.email:
                            self.send_email_notification(updated_record, updated_record.checked_by, "review")

                    
                    if updated_record.approved_by:
                        if updated_record.send_notification_to_approved_by:
                            try:
                                NotificationRecord.objects.create(
                                    user=updated_record.approved_by,
                                    record=updated_record,
                                    title="Record Updated - Approval Required",
                                    message=f"Record '{updated_record.title}' has been updated and is ready for your approval."
                                )
                            except Exception as e:
                                logger.error(f"Notification error for approved_by: {str(e)}")

                        if updated_record.send_email_to_approved_by and updated_record.approved_by.email:
                            self.send_email_notification(updated_record, updated_record.approved_by, "approval")

                    return Response(serializer.data, status=status.HTTP_200_OK)

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except RecordFormat.DoesNotExist:
            return Response({"error": "Record not found"}, status=status.HTTP_404_NOT_FOUND)

    def send_email_notification(self, record, recipient, action_type):
        recipient_email = recipient.email if recipient else None

        if recipient_email:
            try:
                if action_type == "review":
                    subject = f"Record Ready for Review: {record.title}"
                    message = (
                        f"Dear {recipient.first_name},\n\n"
                        f"The Record '{record.title}' has been updated and requires your review.\n\n"
                        f"Document Number: {record.no or 'N/A'}\n"
                        f"Review Frequency: {record.review_frequency_year or 0} year(s), "
                        f"{record.review_frequency_month or 0} month(s)\n"
                        f"Document Type: {record.document_type}\n\n"
                        f"Please login to the system to review.\n\n"
                        f"Best regards,\nDocumentation Team"
                    )
                elif action_type == "approval":
                    subject = f"procedure Pending Approval: {record.title}"
                    message = (
                        f"Dear {recipient.first_name},\n\n"
                        f"The record '{record.title}' has been updated and is ready for your approval.\n\n"
                        f"Document Number: {record.no or 'N/A'}\n"
                        f"Review Frequency: {record.review_frequency_year or 0} year(s), "
                        f"{record.review_frequency_month or 0} month(s)\n"
                        f"Document Type: {record.document_type}\n\n"
                        f"Please login to the system to approve.\n\n"
                        f"Best regards,\nDocumentation Team"
                    )
                else:
                    logger.warning("Unknown action type for email notification.")
                    return

                send_mail(
                    subject=subject,
                    message=message,
                     from_email=config("EMAIL_HOST_USER"),
                    recipient_list=[recipient_email],
                    fail_silently=False,
                )
                logger.info(f"Email sent to {recipient_email} for action: {action_type}")

            except Exception as e:
                logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        else:
            logger.warning("Recipient email is missing, skipping email.")
            

class SubmitCorrectionRecordView(APIView):
    def post(self, request):
        try:
            record_id = request.data.get('manual_id')
            correction_text = request.data.get('correction')
            from_user_id = request.data.get('from_user')

            if not all([record_id, correction_text, from_user_id]):
                return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                record = RecordFormat.objects.get(id=record_id)
            except RecordFormat.DoesNotExist:
                return Response({'error': 'RecordFormat not found'}, status=status.HTTP_404_NOT_FOUND)

            try:
                from_user = Users.objects.get(id=from_user_id)
            except Users.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Determine to_user based on from_user
            if from_user == record.checked_by:
                to_user = record.written_by
            elif from_user == record.approved_by:
                to_user = record.checked_by
            else:
                return Response({'error': 'Invalid user role for correction'}, status=status.HTTP_400_BAD_REQUEST)

            # Delete old correction
            

            # Create new correction
            correction = CorrectionRecord.objects.create(
                record=record,
                to_user=to_user,
                from_user=from_user,
                correction=correction_text
            )

            # Update status
            record.status = 'Correction Requested'
            record.save()

            # Send notification and email
            self.create_correction_notification(correction)
            self.send_correction_email_notification(correction)

            serializer = CorrectionRecordSerializer(correction)
            return Response(
                {'message': 'Correction submitted successfully', 'correction': serializer.data},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create_correction_notification(self, correction):
        try:
            record = correction.record
            to_user = correction.to_user
            from_user = correction.from_user

            if from_user == record.approved_by and to_user == record.checked_by:
                should_send = record.send_notification_to_checked_by
            elif from_user == record.checked_by and to_user == record.written_by:
                should_send = True
            else:
                should_send = False

            if should_send:
                message = (
                    f"Correction Request from {from_user.first_name} "
                    f"to {to_user.first_name} for record: {record.title}"
                )
                notification = NotificationRecord.objects.create(
                    user=to_user,
                    record=record,
                    message=message
                )
                print(f"Correction Notification created successfully: {notification.id}")
            else:
                print("Notification not sent due to permission flags or invalid role flow.")
        except Exception as e:
            print(f"Failed to create correction notification: {str(e)}")

    def send_correction_email_notification(self, correction):
        try:
            record = correction.record
            to_user = correction.to_user
            from_user = correction.from_user
            recipient_email = to_user.email if to_user else None

            if from_user == record.approved_by and to_user == record.checked_by:
                should_send = record.send_email_to_checked_by
            elif from_user == record.checked_by and to_user == record.written_by:
                should_send = True
            else:
                should_send = False

            if recipient_email and should_send:
                send_mail(
                    subject=f"Correction Request: {record.title}",
                    message=(
                        f"Dear {to_user.first_name},\n\n"
                        f"A correction has been requested by {from_user.first_name} for the record '{record.title}'.\n\n"
                        f"Correction details:\n"
                        f"{correction.correction}\n\n"
                        f"Please review and take necessary actions.\n\n"
                        f"Best regards,\nDocumentation Team"
                    ),
                    from_email=config("EMAIL_HOST_USER"),
                    recipient_list=[recipient_email],
                    fail_silently=False,
                )
                print(f"Correction email successfully sent to {recipient_email}")
            else:
                print("Email not sent due to permission flags, invalid roles, or missing email.")
        except Exception as e:
            print(f"Failed to send correction email: {str(e)}")

class CorrectionRecordList(generics.ListAPIView):
    serializer_class = CorrectionRecordSerializer

    def get_queryset(self):
        record_id = self.kwargs.get("record_id")
        return CorrectionRecord.objects.filter(record_id=record_id)
    
class RecordReviewView(APIView):
    def post(self, request):
        logger.info("Received request for record review process.")
        
        try:
            record_id = request.data.get('record_id')
            current_user_id = request.data.get('current_user_id')

            if not all([record_id, current_user_id]):
                return Response({'error': 'Missing required parameters'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                record = RecordFormat.objects.get(id=record_id)
                current_user = Users.objects.get(id=current_user_id)
            except (RecordFormat.DoesNotExist, Users.DoesNotExist):
                return Response({'error': 'Invalid record or user'}, status=status.HTTP_404_NOT_FOUND)

            with transaction.atomic():
                # Written by - First Submission
                if current_user == record.written_by and not record.written_at:
                    record.written_at = now()

                # Review process
                current_status = record.status
                if current_status == 'Pending for Review/Checking' and current_user == record.checked_by:
                    record.status = 'Reviewed,Pending for Approval'
                    record.checked_at = now()
                    record.save()

                    # Notification to approved_by (only if flag is True)
                    if record.send_notification_to_approved_by:
                        NotificationRecord.objects.create(
                            user=record.approved_by,
                            record=record,
                            message=f"Record '{record.title}' is ready for approval."
                        )

                    # Email to approved_by (only if flag is True)
                    if record.send_email_to_approved_by:
                        self.send_email_notification(
                            recipient=record.approved_by,
                            subject=f"Record {record.title} - Pending Approval",
                            message=f"The Record '{record.title}' has been reviewed and is pending your approval."
                        )

                # Approval process
                elif current_user == record.approved_by:
                    record.status = 'Pending for Publish'
                    record.approved_at = now()
                    record.save()

                    # Notification to approved_by (only if flag is True)
                    if record.send_notification_to_checked_by:
                        NotificationRecord.objects.create(
                            user=record.written_by,
                            record=record,
                            message=f"record '{record.title}' has been approved."
                        )

                    # Email to approved_by (only if flag is True)
                    if record.send_email_to_checked_by:
                        self.send_email_notification(
                            recipient=record.written_by,
                            subject=f"Record {record.title} - Approved",
                            message=f"Your Record '{record.title}' has been approved."
                        )

                # Resubmission after correction
                elif current_status == 'Reviewed,Pending for Approval' and current_user == record.approved_by:
                    record.status = 'Pending for Review/Checking'
                    record.save()

                else:
                    return Response({
                        'message': 'No action taken. User not authorized for this record.'
                    }, status=status.HTTP_200_OK)

            return Response({
                'status': 'success',
                'message': 'Record processed successfully',
                'record_status': record.status
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in record review process: {str(e)}")
            return Response({
                'error': 'An unexpected error occurred',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def send_email_notification(self, recipient, subject, message):
        if recipient and recipient.email:
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=config("EMAIL_HOST_USER"),
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )
                logger.info(f"Email sent to {recipient.email}")
            except Exception as e:
                logger.error(f"Failed to send email: {str(e)}")
                
                
class RecordPublishNotificationView(APIView):
 
    """
    Endpoint to handle publishing a manual and sending notifications to company users.
    """

    def post(self, request, record_id):
        try:
          
            record = RecordFormat.objects.get(id=record_id)
            company_id = request.data.get('company_id')
            published_by = request.data.get('published_by')  
            send_notification = request.data.get('send_notification', False)
            
            if not company_id:
                return Response(
                    {"error": "Company ID is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            company = Company.objects.get(id=company_id)

            with transaction.atomic():
                # Update manual status and published information
                record.status = 'Published'
                record.published_at = now()
                
                # Set the published_user if the ID was provided
                if published_by:
                    try:
                        publishing_user = Users.objects.get(id=published_by)
                        record.published_user = publishing_user
                    except Users.DoesNotExist:
                        logger.warning(f"Publisher user ID {published_by} not found")
                
                # Only send notifications if requested
                record.send_notification = send_notification
                record.save()

                # Only proceed with notifications if send_notification is True
                if send_notification:
                    # Get all users in the company
                    company_users = Users.objects.filter(company=company)

                    # Create notifications for each user
                    notifications = [
                        NotificationRecord(
                            user=user,
                            record=record,
                            title=f"record Published: {record.title}",
                            message=f"A new record '{record.title}' has been published."
                        )
                        for user in company_users
                    ]

                    # Bulk create all notifications
                    if notifications:
                        NotificationRecord.objects.bulk_create(notifications)
                        logger.info(f"Created {len(notifications)} notifications for record {record_id}")

                    # Send emails
                    for user in company_users:
                        if user.email:
                            try:
                                self._send_publish_email(record, user)
                            except Exception as e:
                                logger.error(f"Failed to send email to {user.email}: {str(e)}")

            return Response(
                {
                    "message": "record published successfully",
                    "notification_sent": send_notification,
                    "publisher_set": published_by is not None
                },
                status=status.HTTP_200_OK
            )

        except RecordFormat.DoesNotExist:
            return Response(
                {"error": "record not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Company.DoesNotExist:
            return Response(
                {"error": "Company not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error in publish notification: {str(e)}")
            return Response(
                {"error": f"Failed to publish manual: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _send_publish_email(self, record, recipient):
        """Helper method to send email notifications"""
        # Get publisher name
        publisher_name = "N/A"
        if record.published_user:
            publisher_name = f"{record.published_user.first_name} {record.published_user.last_name}"
        elif record.approved_by:
            publisher_name = f"{record.approved_by.first_name} {record.approved_by.last_name}"
            
        subject = f"New record Published: {record.title}"
        message = (
            f"Dear {recipient.first_name},\n\n"
            f"A new record titled '{record.title}' has been published.\n\n"
            f"record Details:\n"
            f"- Document Number: {record.no or 'N/A'}\n"
            f"- Document Type: {record.document_type}\n"
            f"- Published By: {publisher_name}\n\n"
            f"Please login to view this document.\n\n"
            f"Best regards,\nDocumentation Team"
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=config("EMAIL_HOST_USER"),
            recipient_list=[recipient.email],
            fail_silently=False,
        )
        logger.info(f"Email sent to {recipient.email}")
 
class RecordDraftAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Don't copy the entire request.data, just extract what we need
        data = {}
        
        # Copy over simple data fields 
        for key in request.data:
            if key != 'upload_attachment':
                data[key] = request.data[key]
        
        # Set is_draft flag
        data['is_draft'] = True
        
        # Handle file separately
        file_obj = request.FILES.get('upload_attachment')
        
        serializer = RecordSerializer(data=data)
        if serializer.is_valid():
            record = serializer.save()
            
            # Assign file if provided
            if file_obj:
                record.upload_attachment = file_obj
                record.save()
                
            return Response({"message": "Record saved as draft", "data": serializer.data}, 
                           status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class RecordDraftAllList(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        record = RecordFormat.objects.filter(user=user, is_draft=True)
        serializer =RecordGetSerializer(record, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class DrafRecordcountAPIView(APIView):
 
    def get(self, request, user_id):
   
        draft_records = RecordFormat.objects.filter(is_draft=True, user_id=user_id)
        
        serializer = RecordSerializer(draft_records, many=True)
        
        return Response({
            "count": draft_records.count(),
            "draft_records": serializer.data
        }, status=status.HTTP_200_OK)
        

class NotificationsRecord(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(Users, id=user_id)
        notifications = NotificationRecord.objects.filter(user=user ).order_by("-created_at")
        serializer = NotificationRecordSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, user_id):
        user = get_object_or_404(Users, id=user_id)
        NotificationRecord.objects.filter(user=user, is_read=False).update(is_read=True)
        return Response({"message": "Notifications marked as read"}, status=status.HTTP_200_OK)
    
    
class NotificationsLastRecord(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        
        notifications = NotificationRecord.objects.filter(user=user).order_by('-created_at')

        serializer = NotificationRecordSerializer(notifications, many=True)

        return Response({
            "notifications": serializer.data
        }, status=status.HTTP_200_OK)
        
class UnreadRecordNotificationsAPIView(APIView):
    def get(self, request, user_id):
        try:
            unread_count = NotificationRecord.objects.filter(user_id=user_id, is_read=False).count()
            return Response({"unread_count": unread_count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class MarkRecordNotificationReadAPIView(APIView):
    
    def patch(self, request, notification_id):
        try:
            notification = get_object_or_404(NotificationRecord, id=notification_id)          
            notification.is_read = True
            notification.save()
            serializer = NotificationRecordSerializer(notification)
            return Response(serializer.data, status=status.HTTP_200_OK)        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

 
 
class ComplianceDetailView(RetrieveDestroyAPIView):
    queryset = Compliances.objects.all()
    serializer_class = ComplianceSerializer
    
    
class ProcedurePublishNotificationView(APIView):

 
    """
    Endpoint to handle publishing a manual and sending notifications to company users.
    """

    def post(self, request, procedure_id):
        try:
          
            procedure = Procedure.objects.get(id=procedure_id)
            company_id = request.data.get('company_id')
            published_by = request.data.get('published_by')  
            send_notification = request.data.get('send_notification', False)
            
            if not company_id:
                return Response(
                    {"error": "Company ID is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            company = Company.objects.get(id=company_id)

            with transaction.atomic():
                # Update manual status and published information
                procedure.status = 'Published'
                procedure.published_at = now()
                
                # Set the published_user if the ID was provided
                if published_by:
                    try:
                        publishing_user = Users.objects.get(id=published_by)
                        procedure.published_user = publishing_user
                    except Users.DoesNotExist:
                        logger.warning(f"Publisher user ID {published_by} not found")
                
                # Only send notifications if requested
                procedure.send_notification = send_notification
                procedure.save()

                # Only proceed with notifications if send_notification is True
                if send_notification:
                    # Get all users in the company
                    company_users = Users.objects.filter(company=company)

                    # Create notifications for each user
                    notifications = [
                        NotificatioProcedure(
                            user=user,
                            procedure=procedure,
                            title=f"procedure Published: {procedure.title}",
                            message=f"A new procedure '{procedure.title}' has been published."
                        )
                        for user in company_users
                    ]

                    # Bulk create all notifications
                    if notifications:
                        NotificatioProcedure.objects.bulk_create(notifications)
                        logger.info(f"Created {len(notifications)} notifications for procedure {procedure_id}")

                    # Send emails
                    for user in company_users:
                        if user.email:
                            try:
                                self._send_publish_email(procedure, user)
                            except Exception as e:
                                logger.error(f"Failed to send email to {user.email}: {str(e)}")

            return Response(
                {
                    "message": "procedure published successfully",
                    "notification_sent": send_notification,
                    "publisher_set": published_by is not None
                },
                status=status.HTTP_200_OK
            )

        except Procedure.DoesNotExist:
            return Response(
                {"error": "procedure not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Company.DoesNotExist:
            return Response(
                {"error": "Company not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error in publish notification: {str(e)}")
            return Response(
                {"error": f"Failed to publish procedure: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _send_publish_email(self, procedure, recipient):
        """Helper method to send email notifications"""
        # Get publisher name
        publisher_name = "N/A"
        if procedure.published_user:
            publisher_name = f"{procedure.published_user.first_name} {procedure.published_user.last_name}"
        elif procedure.approved_by:
            publisher_name = f"{procedure.approved_by.first_name} {procedure.approved_by.last_name}"
            
        subject = f"New procedure Published: {procedure.title}"
        message = (
            f"Dear {recipient.first_name},\n\n"
            f"A new procedure titled '{procedure.title}' has been published.\n\n"
            f"procedure Details:\n"
            f"- Document Number: {procedure.no or 'N/A'}\n"
            f"- Document Type: {procedure.document_type}\n"
            f"- Published By: {publisher_name}\n\n"
            f"Please login to view this document.\n\n"
            f"Best regards,\nDocumentation Team"
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=config("EMAIL_HOST_USER"),
            recipient_list=[recipient.email],
            fail_silently=False,
        )
        logger.info(f"Email sent to {recipient.email}")
        
        


class ComplianecesList(APIView):
    def get(self, request, company_id):
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

      
        cpmpliance = Compliances.objects.filter(company=company,is_draft=False)
        serializer = ComplianceSerializer(cpmpliance, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

 

class InterestedPartyCreateView(APIView):
    """
    Endpoint to handle creation of Interested Party, Needs, Expectations, and optionally send notifications.
    """
    def post(self, request):
        print("Received Data:", request.data)  
        try:
            company_id = request.data.get('company')
            send_notification = request.data.get('send_notification', 'false') == 'true'  
            needs_data = request.data.get('needs', [])   
            expectations_data = request.data.get('expectations', [])  

            if not company_id:
                return Response(
                    {"error": "Company ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            company = Company.objects.get(id=company_id)
            serializer = InterestedPartySerializer(data=request.data)

            if serializer.is_valid():
                with transaction.atomic():
 
                    interested_party = serializer.save()
                    logger.info(f"Interested Party created: {interested_party.name}")

                  
                    if needs_data:
                        needs_instances = [
                            Needs(interested_party=interested_party, title=need['title']) 
                            for need in needs_data
                        ]
                        Needs.objects.bulk_create(needs_instances)
                        logger.info(f"Created {len(needs_instances)} Needs for Interested Party {interested_party.id}")

         
                    if expectations_data:
                        expectations_instances = [
                            Expectations(interested_party=interested_party, title=expectation['title']) 
                            for expectation in expectations_data
                        ]
                        Expectations.objects.bulk_create(expectations_instances)
                        logger.info(f"Created {len(expectations_instances)} Expectations for Interested Party {interested_party.id}")

     
                    interested_party.send_notification = send_notification
                    interested_party.save()

    
                    if send_notification:
                        company_users = Users.objects.filter(company=company)
                        notifications = [
                            NotificationInterest(
                                interest=interested_party,
                                title=f"New Interested Party: {interested_party.name}",
                                message=f"A new interested party '{interested_party.name}' has been added."
                            )
                            for user in company_users
                        ]

                
                        if notifications:
                            NotificationInterest.objects.bulk_create(notifications)
                            logger.info(f"Created {len(notifications)} notifications for Interested Party {interested_party.id}")

                 
                        for user in company_users:
                            if user.email:
                                try:
                                    self._send_notification_email(interested_party, user)
                                except Exception as e:
                                    logger.error(f"Failed to send email to {user.email}: {str(e)}")

                return Response(
                    {
                        "message": "Interested Party created successfully",
                        "notification_sent": send_notification
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                logger.warning(f"Validation error: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


        except Company.DoesNotExist:
            return Response(
                {"error": "Company not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error creating Interested Party: {str(e)}")
            return Response(
                {"error": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _send_notification_email(self, interested_party, recipient):
        """
        Helper method to send email notifications about a new Interested Party.
        """
        subject = f"New Interested Party Created: {interested_party.name}"
        message = (
            f"Dear {recipient.first_name},\n\n"
            f"A new interested party '{interested_party.name}' has been created.\n\n"
            f"Details:\n"
            f"- Category: {interested_party.category}\n"
            f"- Needs: {interested_party.needs}\n"
            f"- Expectations: {interested_party.expectations}\n"
            f"- Special Requirements: {interested_party.special_requirements}\n"
            f"- Legal Requirements: {interested_party.legal_requirements}\n"
            f"- Custom Legal Requirements: {interested_party.custom_legal_requirements}\n\n"
            f"Please log in to view more details.\n\n"
            f"Best regards,\nYour Company Team"
        )
        
        send_mail(
            subject=subject,
            message=message,
            from_email=config("EMAIL_HOST_USER"),
            recipient_list=[recipient.email],
            fail_silently=False,
        )
        logger.info(f"Email sent to {recipient.email}")



    
class InterestedPartyList(APIView):
    def get(self, request, company_id):
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

      
        cpmpliance = InterestedParty.objects.filter(company=company,is_draft=False)
        serializer = InterestedPartyGetSerializer(cpmpliance, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

 
class InterestedPartyDetailView(APIView):
    def get_object(self, pk):
        try:
            return InterestedParty.objects.get(pk=pk)
        except InterestedParty.DoesNotExist:
            return None

    def get(self, request, pk, *args, **kwargs):
        party = self.get_object(pk)
        if not party:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = InterestedPartyGetSerializer(party)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        party = self.get_object(pk)
        if not party:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = InterestedPartySerializer(party, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        party = self.get_object(pk)
        if not party:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = InterestedPartySerializer(party, data=request.data, partial=True)
        if serializer.is_valid():
            updated_party = serializer.save()
            send_notification = request.data.get('send_notification', 'false') == 'true'

            # Check if notification should be sent
            if send_notification:
                self._send_update_notifications(updated_party)

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _send_update_notifications(self, updated_party):
        """
        Send notifications to all users about the updated Interested Party.
        """
        company_users = Users.objects.filter(company=updated_party.company)
        notifications = [
            NotificationInterest(
                interest=updated_party,
                title=f"Updated Interested Party: {updated_party.name}",
                message=f"The interested party '{updated_party.name}' has been updated."
            )
            for user in company_users
        ]

        # Bulk create notifications
        if notifications:
            NotificationInterest.objects.bulk_create(notifications)
            logger.info(f"Created {len(notifications)} notifications for updated interested party {updated_party.id}")

        # Send email notifications
        for user in company_users:
            if user.email:
                try:
                    self._send_notification_email(updated_party, user)
                except Exception as e:
                    logger.error(f"Failed to send email to {user.email}: {str(e)}")

    def _send_notification_email(self, updated_party, recipient):
        """
        Helper method to send email notifications about an updated Interested Party.
        """
        subject = f"Interested Party Updated: {updated_party.name}"
        message = (
            f"Dear {recipient.first_name},\n\n"
            f"The interested party '{updated_party.name}' has been updated.\n\n"
            f"Updated Details:\n"
            f"- Category: {updated_party.category}\n"
            f"- Needs: {updated_party.needs}\n"
            f"- Expectations: {updated_party.expectations}\n"
            f"- Special Requirements: {updated_party.special_requirements}\n"
            f"- Legal Requirements: {updated_party.legal_requirements}\n"
            f"- Custom Legal Requirements: {updated_party.custom_legal_requirements}\n\n"
            f"Please log in to view more details.\n\n"
            f"Best regards,\nYour Company Team"
        )
        
        send_mail(
            subject=subject,
            message=message,
            from_email=config("EMAIL_HOST_USER"),
            recipient_list=[recipient.email],
            fail_silently=False,
        )
        logger.info(f"Email sent to {recipient.email}")


    def delete(self, request, pk, *args, **kwargs):
        party = self.get_object(pk)
        if not party:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        party.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class InterestDraftAPIView(APIView):
    def post(self, request, *args, **kwargs):
        data = {key: request.data[key] for key in request.data if key != 'upload_attachment'}
        data['is_draft'] = True

        file_obj = request.FILES.get('upload_attachment')

        serializer = InterestedPartySerializer(data=data)
        if serializer.is_valid():
            interest = serializer.save()
 
            if file_obj:
                interest.upload_attachment = file_obj
                interest.save()

      
            needs_data = request.data.get('needs', [])
            for need in needs_data:
                Needs.objects.create(interested_party=interest, title=need.get('title'))

            expectations_data = request.data.get('expectations', [])
            for expectation in expectations_data:
                Expectations.objects.create(interested_party=interest, title=expectation.get('title'))

            return Response({"message": "Interest saved as draft", "data": serializer.data}, 
                             status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    
class InterstDraftAllList(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        record = InterestedParty.objects.filter(user=user, is_draft=True)
        serializer =InterestedPartySerializer(record, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    
class EditInterestedParty(APIView):
    def put(self, request, pk):
        interested_party = get_object_or_404(InterestedParty, pk=pk)
        send_notification = request.data.get('send_notification', 'false') == 'true'

        # Extract Needs and Expectations separately
        needs_data = request.data.pop('needs', [])
        expectations_data = request.data.pop('expectation', [])

        serializer = InterestedPartySerializer(interested_party, data=request.data, partial=True)

        if serializer.is_valid():
            instance = serializer.save(is_draft=False)

            # Update Needs
            if needs_data:
                instance.needs.all().delete()  # Clear old needs
                needs_objs = [Needs(interested_party=instance, title=need.get('title', '')) for need in needs_data]
                Needs.objects.bulk_create(needs_objs)

            # Update Expectations
            if expectations_data:
                instance.expectation.all().delete()  # Clear old expectations
                expectations_objs = [Expectations(interested_party=instance, title=exp.get('title', '')) for exp in expectations_data]
                Expectations.objects.bulk_create(expectations_objs)

            # Send notification if requested
            if send_notification:
                company = instance.company
                company_users = Users.objects.filter(company=company)

                notifications = [
                    NotificationInterest(
                        interest=instance,
                        title=f"Updated Interested Party: {instance.name}",
                        message=f"The interested party '{instance.name}' has been updated."
                    )
                    for user in company_users
                ]
                if notifications:
                    NotificationInterest.objects.bulk_create(notifications)
                    logger.info(f"Created {len(notifications)} notifications for interested party {instance.id}")

                for user in company_users:
                    if user.email:
                        try:
                            self._send_notification_email(instance, user)
                        except Exception as e:
                            logger.error(f"Failed to send email to {user.email}: {str(e)}")

            return Response(InterestedPartyGetSerializer(instance).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _send_notification_email(self, interested_party, recipient):
        subject = f"Interested Party Updated: {interested_party.name}"
        needs_list = "\n".join([f"- {need.title}" for need in interested_party.needs.all()])
        expectations_list = "\n".join([f"- {exp.title}" for exp in interested_party.expectation.all()])

        message = (
            f"Dear {recipient.first_name},\n\n"
            f"The interested party '{interested_party.name}' has been updated.\n\n"
            f"Details:\n"
            f"- Category: {interested_party.category}\n"
            f"- Needs:\n{needs_list}\n"
            f"- Expectations:\n{expectations_list}\n"
            f"- Special Requirements: {interested_party.special_requirements}\n"
            f"- Legal Requirements: {interested_party.legal_requirements}\n"
            f"- Custom Legal Requirements: {interested_party.custom_legal_requirements}\n\n"
            f"Please log in to view more details.\n\n"
            f"Best regards,\nYour Company Team"
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=config("EMAIL_HOST_USER"),
            recipient_list=[recipient.email],
            fail_silently=False,
        )
        logger.info(f"Email sent to {recipient.email}")




class DrafInterstAPIView(APIView):
 
    def get(self, request, user_id):
   
        draft_records = InterestedParty.objects.filter(is_draft=True, user_id=user_id)
        
        serializer = InterestedPartySerializer(draft_records, many=True)
        
        return Response({
            "count": draft_records.count(),
            "draft_records": serializer.data
        }, status=status.HTTP_200_OK)
        
        


class ProcessList(APIView):
    def get(self, request, company_id):
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

        # Get all non-draft processes for the company
        processes = Processes.objects.filter(company=company, is_draft=False)
        
        # Use select_related to optimize database queries for foreign keys
        # Use prefetch_related to optimize queries for many-to-many relationships
        processes = processes.prefetch_related('legal_requirements')
        
        serializer = ProcessManySerializer(processes, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ProcessDetailView(APIView):
    def get_object(self, pk):
        try:
            return Processes.objects.get(pk=pk)
        except Processes.DoesNotExist:
            return None

    def get(self, request, pk, *args, **kwargs):
        process = self.get_object(pk)
        if not process:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Use select_related to optimize queries
        process = Processes.objects.prefetch_related('legal_requirements').get(pk=pk)
        serializer = ProcessManySerializer(process)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        process = self.get_object(pk)
        if not process:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Extract legal_requirements IDs from request data
        legal_requirements_ids = []
        for key in request.data.keys():
            if key.startswith('legal_requirements[') and key.endswith(']'):
                legal_requirements_ids.append(request.data.get(key))
        
        # Create a mutable copy of the data
        data = request.data.copy()
        
        # Remove the legal_requirements entries from data
        for key in list(data.keys()):
            if key.startswith('legal_requirements[') and key.endswith(']'):
                data.pop(key)
        
        # Process the update with a transaction to ensure consistency
        with transaction.atomic():
            serializer = ProcessSerializer(process, data=data)
            if serializer.is_valid():
                updated_process = serializer.save()
                
                # Update many-to-many relationships
                process.legal_requirements.clear()
                for procedure_id in legal_requirements_ids:
                    try:
                        procedure = Procedure.objects.get(id=procedure_id)
                        process.legal_requirements.add(procedure)
                    except (Procedure.DoesNotExist, ValueError) as e:
                        logger.warning(f"Failed to add procedure {procedure_id}: {str(e)}")
                
                # Refresh the serializer to include updated relationships
                serializer = ProcessSerializer(updated_process)
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, *args, **kwargs):
        process = self.get_object(pk)
        if not process:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Extract legal_requirements IDs from request data
        legal_requirements_ids = []
        legal_requirements_updated = False
        
        for key in request.data.keys():
            if key.startswith('legal_requirements[') and key.endswith(']'):
                legal_requirements_ids.append(request.data.get(key))
                legal_requirements_updated = True
        
        # Create a mutable copy of the data
        data = request.data.copy()
        
        # Remove the legal_requirements entries from data
        for key in list(data.keys()):
            if key.startswith('legal_requirements[') and key.endswith(']'):
                data.pop(key)
        
        # Process the partial update with a transaction
        with transaction.atomic():
            serializer = ProcessSerializer(process, data=data, partial=True)
            if serializer.is_valid():
                updated_process = serializer.save()
                
                # Update many-to-many relationships only if legal_requirements were included in the request
                if legal_requirements_updated:
                    process.legal_requirements.clear()
                    for procedure_id in legal_requirements_ids:
                        try:
                            procedure = Procedure.objects.get(id=procedure_id)
                            process.legal_requirements.add(procedure)
                        except (Procedure.DoesNotExist, ValueError) as e:
                            logger.warning(f"Failed to add procedure {procedure_id}: {str(e)}")
                
                send_notification = request.data.get('send_notification', 'false') == 'true'
                
                if send_notification:
                    self._send_update_notifications(updated_process)
                
                # Refresh the serializer to include updated relationships
                serializer = ProcessSerializer(updated_process)
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _send_update_notifications(self, updated_process):
        """
        Send notifications to all users about the updated Process.
        """
        company_users = Users.objects.filter(company=updated_process.company)
        notifications = [
            NotificationProcess(
                processes=updated_process,
                title=f"Updated Process: {updated_process.name}",
                message=f"The process '{updated_process.name}' has been updated."
            )
            for user in company_users
        ]

        # Bulk create notifications
        if notifications:
            NotificationProcess.objects.bulk_create(notifications)
            logger.info(f"Created {len(notifications)} notifications for updated process {updated_process.id}")

        # Send email notifications
        for user in company_users:
            if user.email:
                try:
                    self._send_notification_email(updated_process, user)
                except Exception as e:
                    logger.error(f"Failed to send email to {user.email}: {str(e)}")

    def _send_notification_email(self, process, recipient):
        """
        Helper method to send email notifications about an updated Process.
        """
        # Get the legal requirements titles for email content
        legal_requirements_titles = ", ".join([proc.title for proc in process.legal_requirements.all()])
        
        subject = f"Process Updated: {process.name}"
        message = (
            f"Dear {recipient.first_name},\n\n"
            f"The process '{process.name}' has been updated.\n\n"
            f"Updated Details:\n"
            f"- Type: {process.type}\n"  # Changed from category to type
            f"- Legal Requirements: {legal_requirements_titles or 'None'}\n"
            f"- Custom Legal Requirements: {process.custom_legal_requirements or 'None'}\n\n"
            f"Please log in to view more details.\n\n"
            f"Best regards,\nYour Company Team"
        )
        
        send_mail(
            subject=subject,
            message=message,
            from_email=config("EMAIL_HOST_USER"),
            recipient_list=[recipient.email],
            fail_silently=False,
        )
        logger.info(f"Email sent to {recipient.email}")

    def delete(self, request, pk, *args, **kwargs):
        process = self.get_object(pk)
        if not process:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        process.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class ProcessCreateView(APIView):
    """
    Endpoint to handle creation of process and optionally send notifications.
    """
    def post(self, request):
        print("Received Data:", request.data)   
        try:
            company_id = request.data.get('company')
            send_notification = request.data.get('send_notification', 'false') == 'true'  # Handle as boolean

            if not company_id:
                return Response(
                    {"error": "Company ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            company = Company.objects.get(id=company_id)
            
            # Extract legal_requirements IDs from request data
            legal_requirements_ids = []
            for key in request.data.keys():
                if key.startswith('legal_requirements[') and key.endswith(']'):
                    legal_requirements_ids.append(request.data.get(key))
            
            # Create a mutable copy of the data
            data = request.data.copy()
            
            # Remove the legal_requirements entries from the data before validation
            # since they're handled separately after the initial save
            for key in list(data.keys()):
                if key.startswith('legal_requirements[') and key.endswith(']'):
                    data.pop(key)

            serializer = ProcessSerializer(data=data) 

            if serializer.is_valid():
                with transaction.atomic():
                    process = serializer.save()
                    logger.info(f"Processes created: {process.name}")

                    # Update and save send_notification flag
                    process.send_notification = send_notification
                    
                    # Add legal requirements relationships
                    if legal_requirements_ids:
                        for procedure_id in legal_requirements_ids:
                            try:
                                procedure = Procedure.objects.get(id=procedure_id)
                                process.legal_requirements.add(procedure)
                            except (Procedure.DoesNotExist, ValueError) as e:
                                logger.warning(f"Failed to add procedure {procedure_id}: {str(e)}")
                    
                    process.save()

                    # Send notifications only if requested
                    if send_notification:
                        company_users = Users.objects.filter(company=company)
                        notifications = [
                            NotificationProcess(
                                processes=process,
                                title=f"New process Party: {process.name}",
                                message=f"A new process party '{process.name}' has been added."
                            )
                            for user in company_users  # Still iterating for sending emails below
                        ]

                        # Bulk create notifications
                        if notifications:
                            NotificationProcess.objects.bulk_create(notifications)
                            logger.info(f"Created {len(notifications)} notifications for process party {process.id}")

                        # Send email to each user
                        for user in company_users:
                            if user.email:
                                try:
                                    self._send_notification_email(process, user)
                                except Exception as e:
                                    logger.error(f"Failed to send email to {user.email}: {str(e)}")

                return Response(
                    {
                        "message": "process Party created successfully",
                        "notification_sent": send_notification
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                logger.warning(f"Validation error: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Company.DoesNotExist:
            return Response(
                {"error": "Company not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error creating process Party: {str(e)}")
            return Response(
                {"error": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _send_notification_email(self, process, recipient):
        """
        Helper method to send email notifications about a new process Party.
        """
    
        legal_requirements_titles = ", ".join([proc.title for proc in process.legal_requirements.all()])
        
        subject = f"New process Party Created: {process.name}"
        message = (
            f"Dear {recipient.first_name},\n\n"
            f"A new process party '{process.name}' has been created.\n\n"
            f"Details:\n"
            f"- Category: {process.type}\n"   
            f"- Legal Requirements: {legal_requirements_titles or 'None'}\n"
            f"- Custom Legal Requirements: {process.custom_legal_requirements or 'None'}\n\n"
            f"Please log in to view more details.\n\n"
            f"Best regards,\nYour Company Team"
        )
        
        send_mail(
            subject=subject,
            message=message,
            from_email=config("EMAIL_HOST_USER"),
            recipient_list=[recipient.email],
            fail_silently=False,
        )
        logger.info(f"Email sent to {recipient.email}")

class ProcessAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Create a copy of request.data to modify
        data = {}

        # Copy over simple data fields, excluding 'upload_attachment'
        for key in request.data:
            if key != 'upload_attachment':
                data[key] = request.data[key]
        
        # Set the is_draft flag
        data['is_draft'] = True
        
        # Handle file separately if any
        file_obj = request.FILES.get('upload_attachment')

        # Assuming you have a serializer for the Process model
        serializer = ProcessSerializer(data=data)
        if serializer.is_valid():
            process = serializer.save()
            
            # Assign file if provided
            if file_obj:
                process.upload_attachment = file_obj
                process.save()

            return Response({
                "message": "Process saved as draft",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProcessAllList(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        record = Processes.objects.filter(user=user, is_draft=True)
        serializer =ProcessSerializer(record, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class EditProcess(APIView):
    def put(self, request, pk):
        process = get_object_or_404(Processes, pk=pk)
      
        print("Request data:", request.data)
        print("Legal requirements data:", request.data.getlist('legal_requirements'))
        print("Custom legal requirements:", request.data.get('custom_legal_requirements', ''))
        
     
        data = request.data.copy()
        
 
        has_custom_text = 'custom_legal_requirements' in request.data and request.data.get('custom_legal_requirements', '').strip()
        
 
        serializer = ProcessManySerializer(process, data=data, partial=True)
        if serializer.is_valid():
 
            instance = serializer.save(is_draft=False)
            
           
            if has_custom_text:
         
                instance.legal_requirements.clear()
                print("N/A selected - cleared all legal requirements")
            else:
     
                legal_req_data = request.data.getlist('legal_requirements')
                if legal_req_data:
           
                    req_ids = [int(req_id) for req_id in legal_req_data if req_id and req_id.isdigit()]
              
                    instance.legal_requirements.set(req_ids)
                    print(f"Set legal requirements to: {req_ids}")
                else:
            
                    instance.legal_requirements.clear()
                    print("No legal requirements provided - cleared all")
            
 
            return Response(ProcessManySerializer(instance).data, status=status.HTTP_200_OK)
        
        print("Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 

class ProcessDraftAPIView(APIView):
    def post(self, request, *args, **kwargs):
        data = {}

      
        for key in request.data:
            if key not in ['upload_attachment', 'legal_requirements']:
                data[key] = request.data[key]

  
        legal_requirements_ids = request.data.getlist('legal_requirements') if hasattr(request.data, 'getlist') else request.data.get('legal_requirements', [])
        data['legal_requirements'] = legal_requirements_ids
 
        data['is_draft'] = True

     
        file_obj = request.FILES.get('upload_attachment')

        # Serialize and validate
        serializer = ProcessSerializer(data=data)
        if serializer.is_valid():
            process = serializer.save()

        
            if file_obj:
                process.upload_attachment = file_obj
                process.save()

            # Save many-to-many separately if not handled by serializer
            if legal_requirements_ids:
                process.legal_requirements.set(legal_requirements_ids)

            return Response({"message": "Process saved as draft", "data": serializer.data}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProcessAPIView(APIView):
 
    def get(self, request, user_id):
   
        draft_records = Processes.objects.filter(is_draft=True, user_id=user_id)
        
        serializer = ProcessSerializer(draft_records, many=True)
        
        return Response({
            "count": draft_records.count(),
            "draft_records": serializer.data
        }, status=status.HTTP_200_OK)
        
    
class ProcessesDraftAllList(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        record = Processes.objects.filter(user=user, is_draft=True)
        serializer =ProcessSerializer(record, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

 
 
import threading   
class ComplianceCreateAPIView(APIView):
    """
    Endpoint to handle creation of Interested Party and optionally send notifications.
    """

    def post(self, request):
        print("Received Data:", request.data)
        try:
            company_id = request.data.get('company')
            send_notification = request.data.get('send_notification', 'false') == 'true'

            if not company_id:
                return Response(
                    {"error": "Company ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            company = Company.objects.get(id=company_id)
            serializer = ComplianceSerializer(data=request.data)

            if serializer.is_valid():
                with transaction.atomic():
                    compliance = serializer.save()
                    logger.info(f"Interested Party created: {compliance.compliance_name}")

                    compliance.send_notification = send_notification
                    compliance.save()

                    if send_notification:
                        company_users = Users.objects.filter(company=company)
                        notifications = [
                            ComplianceNotification(
                                compliance=compliance,
                                title=f"New Interested Party: {compliance.compliance_name}",
                                message=f"A new interested party '{compliance.compliance_name}' has been added."
                            )
                            for user in company_users
                        ]

                        if notifications:
                            ComplianceNotification.objects.bulk_create(notifications)
                            logger.info(f"Created {len(notifications)} notifications for compliance {compliance.id}")

                        # Send email asynchronously to each user
                        for user in company_users:
                            if user.email:
                                self._send_email_async(compliance, user)

                return Response(
                    {
                        "message": "Compliance created successfully",
                        "notification_sent": send_notification
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                logger.warning(f"Validation error: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Company.DoesNotExist:
            return Response(
                {"error": "Company not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error creating compliance: {str(e)}")
            return Response(
                {"error": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _send_email_async(self, compliance, recipient):
        """
        Sends email in a separate thread to avoid blocking file upload response.
        """
        threading.Thread(target=self._send_notification_email, args=(compliance, recipient)).start()

    def _send_notification_email(self, compliance, recipient):
        """
        Send HTML-formatted email notification about a new compliance.
        """
        subject = f"New Compliance Created: {compliance.compliance_name}"
        recipient_email = recipient.email

        context = {
            'compliance_name': compliance.compliance_name,
            'compliance_type': compliance.compliance_type,
            'compliance_no': compliance.compliance_no,
            'compliance_remarks': compliance.compliance_remarks,
            'rivision': compliance.rivision,
            'date': compliance.date,
            'relate_business_process': compliance.relate_business_process,
            'relate_document': compliance.relate_document,
            'created_by': compliance.user,
        }

        html_message = render_to_string('qms/compliance/compliance_add_template.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=config("EMAIL_HOST_USER"),
            recipient_list=[recipient_email],
            fail_silently=False,
            html_message=html_message,
        )
        logger.info(f"Email sent to {recipient_email}")



class ComplianceDraftAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Don't copy the entire request.data, just extract what we need
        data = {}
        
        # Copy over simple data fields 
        for key in request.data:
            if key != 'upload_attachment':
                data[key] = request.data[key]
        
        # Set is_draft flag
        data['is_draft'] = True
        
        # Handle file separately
        file_obj = request.FILES.get('upload_attachment')
        
        serializer = ComplianceSerializer(data=data)
        if serializer.is_valid():
            compliance = serializer.save()
            
            # Assign file if provided
            if file_obj:
                compliance.upload_attachment = file_obj
                compliance.save()
                
            return Response({"message": "Compliance saved as draft", "data": serializer.data}, 
                           status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
 

 
class EditsCompliance(APIView):
    def put(self, request, pk):
        print("requestfdcxgvdxgds",request.data)
        compliance = get_object_or_404(Compliances, pk=pk)
        mutable_data = request.data.copy()

        
        if 'attach_document' in mutable_data and not request.FILES.get('attach_document'):
            print("Removing attach_document from request because it's not a file")
            mutable_data.pop('attach_document')
        
        serializer = ComplianceSerializer(compliance, data=request.data, partial=True)
        
        if serializer.is_valid():
            instance = serializer.save(is_draft=False)

       
            if instance.send_notification:
                company = instance.company

         
                company_users = Users.objects.filter(company=company)

             
                notifications = [
                    ComplianceNotification(
                        compliance=instance,
                        title=f"Updated Compliance: {instance.compliance_name}",
                        message=f"The compliance '{instance.compliance_name}' has been updated."
                    )
                    for user in company_users
                ]

                if notifications:
                    ComplianceNotification.objects.bulk_create(notifications)
                    logger.info(f"Created {len(notifications)} notifications for compliance {instance.id}")

          
                for user in company_users:
                    if user.email:
                        try:
                            self._send_notification_email(instance, user)
                        except Exception as e:
                            logger.error(f"Failed to send email to {user.email}: {str(e)}")

            return Response(ComplianceSerializer(instance).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _send_notification_email(self, compliance, recipient):
        subject = f"Compliance Updated: {compliance.compliance_name}"
        message = (
            f"Dear {recipient.first_name},\n\n"
            f"The compliance '{compliance.compliance_name}' has been updated.\n\n"
            f"Details:\n"
            f"- Category: {compliance.compliance_type}\n"
            f"- Remarks: {compliance.compliance_remarks}\n"
            f"- Revision: {compliance.rivision}\n"
            f"- Date: {compliance.date}\n"
            f"- Related Document: {compliance.relate_document}\n"
            f"- Special Requirements: {compliance.special_requirements if hasattr(compliance, 'special_requirements') else ''}\n"
            f"- Legal Requirements: {compliance.legal_requirements if hasattr(compliance, 'legal_requirements') else ''}\n\n"
            f"Please log in to view more details.\n\n"
            f"Best regards,\nYour Company Team"
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=config("EMAIL_HOST_USER"),
            recipient_list=[recipient.email],
            fail_silently=False,
        )
        logger.info(f"Email sent to {recipient.email}")


class ComplianceDraftAllList(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        record = Compliances.objects.filter(user=user, is_draft=True)
        serializer =ComplianceSerializer(record, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class LegalList(APIView):
    def get(self, request, company_id):
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

      
        cpmpliance = LegalRequirement.objects.filter(company=company,is_draft=False)
        serializer = LegalSerializer(cpmpliance, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class LegalDetailView(RetrieveDestroyAPIView):
    queryset = LegalRequirement.objects.all()
    serializer_class = LegalSerializer
    
    
class LegalCreateAPIView(APIView):
    """
    Endpoint to handle creation of Legal and optionally send notifications.
    """
    def post(self, request):
        print("Received Data:", request.data) 
        try:
            company_id = request.data.get('company')
            send_notification = request.data.get('send_notification', 'false') == 'true'   

            if not company_id:
                return Response(
                    {"error": "Company ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            company = Company.objects.get(id=company_id)
            serializer = LegalSerializer(data=request.data)

            if serializer.is_valid():
                with transaction.atomic():
                    legal = serializer.save()
                    logger.info(f"Legal created: {legal.legal_name}")

                    # Update and save send_notification flag
                    legal.send_notification = send_notification
                    legal.save()

                    # Send notifications only if requested
                    if send_notification:
                        company_users = Users.objects.filter(company=company)
                        notifications = [
                            NotificationLegal(
                                legal=legal,
                                title=f"New legal : {legal.legal_name}",
                                message=f"A new legal'{legal.legal_name}' has been added."
                            )
                            for user in company_users  # Still iterating for sending emails below
                        ]

                        # Bulk create notifications
                        if notifications:
                            NotificationLegal.objects.bulk_create(notifications)
                            logger.info(f"Created {len(notifications)} notifications for compllaince party {legal.id}")

                        # Send email to each user
                        for user in company_users:
                            if user.email:
                                try:
                                    self._send_notification_email(legal, user)
                                except Exception as e:
                                    logger.error(f"Failed to send email to {user.email}: {str(e)}")

                return Response(
                    {
                        "message": "legal Party created successfully",
                        "notification_sent": send_notification
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                logger.warning(f"Validation error: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Company.DoesNotExist:
            return Response(
                {"error": "Company not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error creating compllaince Party: {str(e)}")
            return Response(
                {"error": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _send_notification_email(self, legal, recipient):
        """
        Helper method to send email notifications about a new Interested Party.
        """
        subject = f"New Legal Requirement Created: {legal.legal_name}"
        message = (
                f"Dear {recipient.first_name},\n\n"
                f"A new legal requirement '{legal.legal_name}' has been Updated.\n\n"
                f"Details:\n"
                f"- Document Type: {legal.document_type}\n"
                f"- Revision: {legal.rivision}\n"
                f"- Date: {legal.date}\n"
                f"- Related Record Format: {legal.related_record_format}\n\n"
                f"Please log in to view more details.\n\n"
                f"Best regards,\nYour Company Team"
            )

        
        send_mail(
            subject=subject,
            message=message,
            from_email=config("EMAIL_HOST_USER"),
            recipient_list=[recipient.email],
            fail_silently=False,
        )
        logger.info(f"Email sent to {recipient.email}")


class LegalDraftAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Create a copy of request.data to modify
        data = {}
        
        # Copy over simple data fields
        for key in request.data:
            if key != 'upload_attachment':
                data[key] = request.data[key]
        
        # Set is_draft flag
        data['is_draft'] = True
        
        # Handle file separately if any
        file_obj = request.FILES.get('upload_attachment')

        # Assuming you have a serializer for the Legal model
        serializer = LegalSerializer(data=data)
        if serializer.is_valid():
            legal = serializer.save()
            
            # Assign file if provided
            if file_obj:
                legal.upload_attachment = file_obj
                legal.save()

            return Response({"message": "Legal Requirements saved as draft", "data": serializer.data}, 
                             status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EditsLegal(APIView):
    def put(self, request, pk):
        legal = get_object_or_404(LegalRequirement, pk=pk)
        
        mutable_data = request.data.copy()

        
        if 'attach_document' in mutable_data and not request.FILES.get('attach_document'):
            print("Removing attach_document from request because it's not a file")
            mutable_data.pop('attach_document')
        serializer = LegalSerializer(legal, data=mutable_data, partial=True)


        
        if serializer.is_valid():
            instance = serializer.save(is_draft=False)

       
            if instance.send_notification:
                company = instance.company

         
                company_users = Users.objects.filter(company=company)

             
                notifications = [
                    NotificationLegal(
                        legal=instance,
                        title=f"Updated legal: {instance.legal_name}",
                        message=f"The legal '{instance.legal_name}' has been updated."
                    )
                    for user in company_users
                ]

                if notifications:
                    NotificationLegal.objects.bulk_create(notifications)
                    logger.info(f"Created {len(notifications)} notifications for legal {instance.id}")

          
                for user in company_users:
                    if user.email:
                        try:
                            self._send_notification_email(instance, user)
                        except Exception as e:
                            logger.error(f"Failed to send email to {user.email}: {str(e)}")

            return Response(LegalSerializer(instance).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _send_notification_email(self, legal, recipient):
        subject = f"legal Updated: {legal.legal_name}"
        message = (
                f"Dear {recipient.first_name},\n\n"
                f"A new legal requirement '{legal.legal_name}' has been updated.\n\n"
                f"Details:\n"
                f"- Document Type: {legal.document_type}\n"
                f"- Revision: {legal.rivision}\n"
                f"- Date: {legal.date}\n"
                f"- Related Record Format: {legal.related_record_format}\n\n"
                f"Please log in to view more details.\n\n"
                f"Best regards,\nYour Company Team"
            )

        send_mail(
            subject=subject,
            message=message,
            from_email=config("EMAIL_HOST_USER"),
            recipient_list=[recipient.email],
            fail_silently=False,
        )
        logger.info(f"Email sent to {recipient.email}")
        
class LegalDraftAllList(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        record = LegalRequirement.objects.filter(user=user, is_draft=True)
        serializer =LegalSerializer(record, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class LegalView(APIView):
 
    def get(self, request, user_id):
   
        draft_records = LegalRequirement.objects.filter(is_draft=True, user_id=user_id)
        
        serializer = LegalSerializer(draft_records, many=True)
        
        return Response({
            "count": draft_records.count(),
            "draft_records": serializer.data
        }, status=status.HTTP_200_OK)
        

class EvaluationCreateView(APIView):
 
    def post(self, request):
        logger.info("Received evaluation creation request.")
        serializer = EvaluationSerializer(data=request.data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    evaluation = serializer.save()
                    evaluation.written_at = now()
                    evaluation.is_draft = False

                    evaluation.send_notification_to_checked_by = parse_bool(
                        request.data.get('send_notification_to_checked_by')
                    )
                    evaluation.send_email_to_checked_by = parse_bool(
                        request.data.get('send_email_to_checked_by')
                    )
                 

                    evaluation.save()
                    logger.info(f"evaluation created successfully with ID: {evaluation.id}")

                    if evaluation.checked_by:
                        if evaluation.send_notification_to_checked_by:
                            try:
                                NotificationEvaluations.objects.create(
                                    user=evaluation.checked_by,
                                    evaluation=evaluation,
                                    title="Notification for Checking/Review",
                                    message="A evaluation has been created for your review."
                                )
                                logger.info(f"Notification created for checked_by user {evaluation.checked_by.id}")
                            except Exception as e:
                                logger.error(f"Error creating notification for checked_by: {str(e)}")

                        if evaluation.send_email_to_checked_by and evaluation.checked_by.email:
                            self.send_email_notification(evaluation, evaluation.checked_by, "review")
                        else:
                            logger.warning("Email to checked_by skipped: flag disabled or email missing.")
                    else:
                        logger.warning("No checked_by user assigned.")

                    return Response(
                        {"message": "evaluation created successfully", "id": evaluation.id},
                        status=status.HTTP_201_CREATED
                    )

            except Exception as e:
                logger.error(f"Error during evaluation creation: {str(e)}")
                return Response(
                    {"error": "An unexpected error occurred."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        logger.error(f"evaluation creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_email_notification(self, evaluation, recipient, action_type):
        recipient_email = recipient.email if recipient else None

        if recipient_email:
            try:
                if action_type == "review":
                    subject = f"evaluation Ready for Review: {evaluation.title}"
                    message = (
                        f"Dear {recipient.first_name},\n\n"
                        f"A evaluation titled '{evaluation.title}' requires your review.\n\n"
                        f"Document Number: {evaluation.no or 'N/A'}\n"
                        f"Review Frequency: {evaluation.review_frequency_year or 0} year(s), "
                        f"{evaluation.review_frequency_month or 0} month(s)\n"
                        f"Document Type: {evaluation.document_type}\n\n"
                        f"Please login to the system to review.\n\n"
                        f"Best regards,\nDocumentation Team"
                    )
                else:
                    logger.warning("Unknown action type provided for email.")
                    return

                send_mail(
                    subject=subject,
                    message=message,
                    from_email=config("EMAIL_HOST_USER"),
                    recipient_list=[recipient_email],
                    fail_silently=False,
                )
                logger.info(f"Email successfully sent to {recipient_email} for action: {action_type}")

            except Exception as e:
                logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        else:
            logger.warning("Recipient email is None. Skipping email send.")


class EvaluationAllList(APIView):
    def get(self, request, company_id):
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

      
        procedures = Evaluation.objects.filter(company=company, is_draft=False)
        serializer = EvaluationGetSerializer(procedures, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class EvaluationDetailView(APIView):
    def get(self, request, pk):
        try:
            evaluation = Evaluation.objects.get(pk=pk)
        except Evaluation.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = EvaluationGetSerializer(evaluation)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            procedure = Evaluation.objects.get(pk=pk)
        except Evaluation.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = EvaluationSerializer(procedure, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            evaluation = Evaluation.objects.get(pk=pk)
        except Evaluation.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        evaluation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class EvaluationUpdateView(APIView):
    def put(self, request, pk):
        print("fsddf",request.data)
        try:
            with transaction.atomic():
                evaluation = Evaluation.objects.get(pk=pk)

                serializer = EvaluationUpdateSerializer(evaluation, data=request.data, partial=True)

                if serializer.is_valid():
                    updated_procedure = serializer.save()

                 
                    updated_procedure.written_at = now()
                    updated_procedure.is_draft = False
                    updated_procedure.status = 'Pending for Review/Checking'
 
                    updated_procedure.send_notification_to_checked_by = parse_bool(request.data.get('send_system_checked'))
                    updated_procedure.send_email_to_checked_by = parse_bool(request.data.get('send_email_checked'))
                    updated_procedure.send_notification_to_approved_by = parse_bool(request.data.get('send_system_approved'))
                    updated_procedure.send_email_to_approved_by = parse_bool(request.data.get('send_email_approved'))



                    updated_procedure.save()

                 
                    if updated_procedure.checked_by:
                        if updated_procedure.send_notification_to_checked_by:
                            try:
                                NotificationEvaluations.objects.create(
                                    user=updated_procedure.checked_by,
                                    evaluation=updated_procedure,
                                    title="evaluation Updated - Review Required",
                                    message=f"evaluation '{updated_procedure.title}' has been updated and requires your review."
                                )
                            except Exception as e:
                                logger.error(f"Notification error for checked_by: {str(e)}")

                        if updated_procedure.send_email_to_checked_by and updated_procedure.checked_by.email:
                            self.send_email_notification(updated_procedure, updated_procedure.checked_by, "review")

                    
                    if updated_procedure.approved_by:
                        if updated_procedure.send_notification_to_approved_by:
                            try:
                                NotificationEvaluations.objects.create(
                                    user=updated_procedure.approved_by,
                                    evaluation=updated_procedure,
                                    title="evaluation Updated - Approval Required",
                                    message=f"evaluation '{updated_procedure.title}' has been updated and is ready for your approval."
                                )
                            except Exception as e:
                                logger.error(f"Notification error for approved_by: {str(e)}")

                        if updated_procedure.send_email_to_approved_by and updated_procedure.approved_by.email:
                            self.send_email_notification(updated_procedure, updated_procedure.approved_by, "approval")

                    return Response(serializer.data, status=status.HTTP_200_OK)

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Evaluation.DoesNotExist:
            return Response({"error": "procedure not found"}, status=status.HTTP_404_NOT_FOUND)

    def send_email_notification(self, evaluation, recipient, action_type):
        recipient_email = recipient.email if recipient else None

        if recipient_email:
            try:
                if action_type == "review":
                    subject = f"evaluation Ready for Review: {evaluation.title}"
                    message = (
                        f"Dear {recipient.first_name},\n\n"
                        f"The evaluation '{evaluation.title}' has been updated and requires your review.\n\n"
                        f"Document Number: {evaluation.no or 'N/A'}\n"
                        f"Review Frequency: {evaluation.review_frequency_year or 0} year(s), "
                        f"{evaluation.review_frequency_month or 0} month(s)\n"
                        f"Document Type: {evaluation.document_type}\n\n"
                        f"Please login to the system to review.\n\n"
                        f"Best regards,\nDocumentation Team"
                    )
                elif action_type == "approval":
                    subject = f"evaluation Pending Approval: {evaluation.title}"
                    message = (
                        f"Dear {recipient.first_name},\n\n"
                        f"The evaluation '{evaluation.title}' has been updated and is ready for your approval.\n\n"
                        f"Document Number: {evaluation.no or 'N/A'}\n"
                        f"Review Frequency: {evaluation.review_frequency_year or 0} year(s), "
                        f"{evaluation.review_frequency_month or 0} month(s)\n"
                        f"Document Type: {evaluation.document_type}\n\n"
                        f"Please login to the system to approve.\n\n"
                        f"Best regards,\nDocumentation Team"
                    )
                else:
                    logger.warning("Unknown action type for email notification.")
                    return

                send_mail(
                    subject=subject,
                    message=message,
                    from_email=config("EMAIL_HOST_USER"),
                    recipient_list=[recipient_email],
                    fail_silently=False,
                )
                logger.info(f"Email sent to {recipient_email} for action: {action_type}")

            except Exception as e:
                logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        else:
            logger.warning("Recipient email is missing, skipping email.")


class SubmitCorrectionEvaluationView(APIView):
    def post(self, request):
        try:
            evaluation_id = request.data.get('evaluation_id')
            correction_text = request.data.get('correction')
            from_user_id = request.data.get('from_user')

            if not all([evaluation_id, correction_text, from_user_id]):
                return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                evaluation = Evaluation.objects.get(id=evaluation_id)
            except Evaluation.DoesNotExist:
                return Response({'error': 'evaluation not found'}, status=status.HTTP_404_NOT_FOUND)

            try:
                from_user = Users.objects.get(id=from_user_id)
            except Users.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Determine to_user based on from_user
            if from_user == evaluation.checked_by:
                to_user = evaluation.written_by
            elif from_user == evaluation.approved_by:
                to_user = evaluation.checked_by
            else:
                return Response({'error': 'Invalid user role for correction'}, status=status.HTTP_400_BAD_REQUEST)

            # Delete old correction
            

            # Create new correction
            correction = CorrectionEvaluation.objects.create(
                evaluation=evaluation,
                to_user=to_user,
                from_user=from_user,
                correction=correction_text
            )

            # Update status
            evaluation.status = 'Correction Requested'
            evaluation.save()

            # Send notification and email
            self.create_correction_notification(correction)
            self.send_correction_email_notification(correction)

            serializer = CorrectionEvaluationSerializer(correction)
            return Response(
                {'message': 'Correction submitted successfully', 'correction': serializer.data},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create_correction_notification(self, correction):
        try:
            evaluation = correction.evaluation
            to_user = correction.to_user
            from_user = correction.from_user

            if from_user == evaluation.approved_by and to_user == evaluation.checked_by:
                should_send = evaluation.send_notification_to_checked_by
            elif from_user == evaluation.checked_by and to_user == evaluation.written_by:
                should_send = True
            else:
                should_send = False

            if should_send:
                message = (
                    f"Correction Request from {from_user.first_name} "
                    f"to {to_user.first_name} for evaluation: {evaluation.title}"
                )
                notification = NotificationEvaluations.objects.create(
                    user=to_user,
                    evaluation=evaluation,
                    message=message
                )
                print(f"Correction Notification created successfully: {notification.id}")
            else:
                print("Notification not sent due to permission flags or invalid role flow.")
        except Exception as e:
            print(f"Failed to create correction notification: {str(e)}")

    def send_correction_email_notification(self, correction):
        try:
            evaluation = correction.evaluation
            to_user = correction.to_user
            from_user = correction.from_user
            recipient_email = to_user.email if to_user else None

            if from_user == evaluation.approved_by and to_user == evaluation.checked_by:
                should_send = evaluation.send_email_to_checked_by
            elif from_user == evaluation.checked_by and to_user == evaluation.written_by:
                should_send = True
            else:
                should_send = False

            if recipient_email and should_send:
                send_mail(
                    subject=f"Correction Request: {evaluation.title}",
                    message=(
                        f"Dear {to_user.first_name},\n\n"
                        f"A correction has been requested by {from_user.first_name} for the evaluation '{evaluation.title}'.\n\n"
                        f"Correction details:\n"
                        f"{correction.correction}\n\n"
                        f"Please review and take necessary actions.\n\n"
                        f"Best regards,\nDocumentation Team"
                    ),
                    from_email=config("EMAIL_HOST_USER"),
                    recipient_list=[recipient_email],
                    fail_silently=False,
                )
                print(f"Correction email successfully sent to {recipient_email}")
            else:
                print("Email not sent due to permission flags, invalid roles, or missing email.")
        except Exception as e:
            print(f"Failed to send correction email: {str(e)}")
            
class CorrectionEvaluationList(generics.ListAPIView):
    serializer_class = CorrectionEvaluationSerializer

    def get_queryset(self):
        evaluation_id = self.kwargs.get("evaluation_id")
        return CorrectionEvaluation.objects.filter(evaluation_id=evaluation_id)
    
    
class EvaluationReviewView(APIView):
    
    def post(self, request):
        logger.info("Received request for Evaluation review process.")
        
        try:
            evaluation_id = request.data.get('evaluation_id')
            current_user_id = request.data.get('current_user_id')

            if not all([evaluation_id, current_user_id]):
                return Response({'error': 'Missing required parameters'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                evaluation = Evaluation.objects.get(id=evaluation_id)
                current_user = Users.objects.get(id=current_user_id)
            except (Evaluation.DoesNotExist, Users.DoesNotExist):
                return Response({'error': 'Invalid Evaluation or user'}, status=status.HTTP_404_NOT_FOUND)

            with transaction.atomic():
                # Written by - First Submission
                if current_user == evaluation.written_by and not evaluation.written_at:
                    evaluation.written_at = now()

                # Review process
                if evaluation.status == 'Pending for Review/Checking' and current_user == evaluation.checked_by:
                    evaluation.status = 'Reviewed,Pending for Approval'
                    evaluation.checked_at = now()
                    evaluation.save()

                    # Notification to approved_by (only if flag is True)
                    if evaluation.send_notification_to_approved_by:
                        NotificationEvaluations.objects.create(
                            user=evaluation.approved_by,
                            evaluation=evaluation,
                            message=f"evaluation '{evaluation.title}' is ready for approval."
                        )

                    # Email to approved_by (only if flag is True)
                    if evaluation.send_email_to_approved_by:
                        self.send_email_notification(
                            recipient=evaluation.approved_by,
                            subject=f"evaluation {evaluation.title} - Pending Approval",
                            message=f"The evaluation '{evaluation.title}' has been reviewed and is pending your approval."
                        )

                # Approval process
                elif evaluation.status == 'Reviewed,Pending for Approval' and current_user == evaluation.approved_by:
                    evaluation.status = 'Pending for Publish'
                    evaluation.approved_at = now()
                    evaluation.save()
 
                elif current_user == evaluation.written_by and evaluation.status == 'Correction Requested':
                    evaluation.status = 'Pending for Review/Checking'
                    evaluation.save()

                else:
                    return Response({
                        'message': 'No action taken. User not authorized for this Procedure.'
                    }, status=status.HTTP_200_OK)

            return Response({
                'status': 'success',
                'message': 'evaluation processed successfully',
                'evaluation_status': evaluation.status
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in procedure review process: {str(e)}")
            return Response({
                'error': 'An unexpected error occurred',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def send_email_notification(self, recipient, subject, message):
        if recipient and recipient.email:
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=config("EMAIL_HOST_USER"),
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )
                logger.info(f"Email sent to {recipient.email}")
            except Exception as e:
                logger.error(f"Failed to send email: {str(e)}")



class EvaluationPublishNotificationView(APIView):

 
    """
    Endpoint to handle publishing a manual and sending notifications to company users.
    """

    def post(self, request, evaluation_id):
        try:
          
            evaluation = Evaluation.objects.get(id=evaluation_id)
            company_id = request.data.get('company_id')
            published_by = request.data.get('published_by')  
            send_notification = request.data.get('send_notification', False)
            
            if not company_id:
                return Response(
                    {"error": "Company ID is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            company = Company.objects.get(id=company_id)

            with transaction.atomic():
                
                evaluation.status = 'Published'
                evaluation.published_at = now()
                
 
                if published_by:
                    try:
                        publishing_user = Users.objects.get(id=published_by)
                        evaluation.published_user = publishing_user
                    except Users.DoesNotExist:
                        logger.warning(f"Publisher user ID {published_by} not found")
                
      
                evaluation.send_notification = send_notification
                evaluation.save()

      
                if send_notification:
             
                    company_users = Users.objects.filter(company=company)

       
                    notifications = [
                        NotificationEvaluations(
                            user=user,
                            evaluation=evaluation,
                            title=f"procedure Published: {evaluation.title}",
                            message=f"A new evaluation '{evaluation.title}' has been published."
                        )
                        for user in company_users
                    ]

                    # Bulk create all notifications
                    if notifications:
                        NotificationEvaluations.objects.bulk_create(notifications)
                        logger.info(f"Created {len(notifications)} notifications for evaluation {evaluation_id}")

                    # Send emails
                    for user in company_users:
                        if user.email:
                            try:
                                self._send_publish_email(evaluation, user)
                            except Exception as e:
                                logger.error(f"Failed to send email to {user.email}: {str(e)}")

            return Response(
                {
                    "message": "evaluation published successfully",
                    "notification_sent": send_notification,
                    "publisher_set": published_by is not None
                },
                status=status.HTTP_200_OK
            )

        except Evaluation.DoesNotExist:
            return Response(
                {"error": "evaluation not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Company.DoesNotExist:
            return Response(
                {"error": "Company not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error in publish notification: {str(e)}")
            return Response(
                {"error": f"Failed to publish evaluation: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _send_publish_email(self, evaluation, recipient):
        """Helper method to send email notifications"""
        # Get publisher name
        publisher_name = "N/A"
        if evaluation.published_user:
            publisher_name = f"{evaluation.published_user.first_name} {evaluation.published_user.last_name}"
        elif evaluation.approved_by:
            publisher_name = f"{evaluation.approved_by.first_name} {evaluation.approved_by.last_name}"
            
        subject = f"New evaluation Published: {evaluation.title}"
        message = (
            f"Dear {recipient.first_name},\n\n"
            f"A new evaluation titled '{evaluation.title}' has been published.\n\n"
            f"evaluation Details:\n"
            f"- Document Number: {evaluation.no or 'N/A'}\n"
            f"- Document Type: {evaluation.document_type}\n"
            f"- Published By: {publisher_name}\n\n"
            f"Please login to view this document.\n\n"
            f"Best regards,\nDocumentation Team"
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=config("EMAIL_HOST_USER"),
            recipient_list=[recipient.email],
            fail_silently=False,
        )
        logger.info(f"Email sent to {recipient.email}")
        

class PEvaluationDraftAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Create a copy of request.data to modify
        data = {}
        
        # Copy over simple data fields
        for key in request.data:
            if key != 'upload_attachment':
                data[key] = request.data[key]
        
        # Set is_draft flag
        data['is_draft'] = True
        
        # Handle file separately if any
        file_obj = request.FILES.get('upload_attachment')

        # Assuming you have a serializer for the Evaluation model
        serializer = EvaluationSerializer(data=data)
        if serializer.is_valid():
            evaluation = serializer.save()
            
            # Assign file if provided
            if file_obj:
                evaluation.upload_attachment = file_obj
                evaluation.save()

            return Response({"message": "Evaluation saved as draft", "data": serializer.data}, 
                             status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class EvaluationDraftAllList(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        procedure = Evaluation.objects.filter(user=user, is_draft=True)
        serializer = EvaluationGetSerializer(procedure, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class DrafEvaluationcountAPIView(APIView):
 
    def get(self, request, user_id):
   
        draft_procedures = Evaluation.objects.filter(is_draft=True, user_id=user_id)
        
        serializer = EvaluationSerializer(draft_procedures, many=True)
        
        return Response({
            "count": draft_procedures.count(),
            "draft_procedures": serializer.data
        }, status=status.HTTP_200_OK)
        
class NotificationEvaluation(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(Users, id=user_id)
        notifications = NotificationEvaluations.objects.filter(user=user ).order_by("-created_at")
        serializer = NotificationEvaluationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, user_id):
        user = get_object_or_404(Users, id=user_id)
        NotificationEvaluations.objects.filter(user=user, is_read=False).update(is_read=True)
        return Response({"message": "Notifications marked as read"}, status=status.HTTP_200_OK)
    
    
class NotificationsLastEvaluation(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        
        notifications = NotificationEvaluations.objects.filter(user=user).order_by('-created_at')

        serializer = NotificationEvaluationSerializer(notifications, many=True)

        return Response({
            "notifications": serializer.data
        }, status=status.HTTP_200_OK)
        
class UnreadEvaluationNotificationsAPIView(APIView):
    def get(self, request, user_id):
        try:
            unread_count = NotificationEvaluations.objects.filter(user_id=user_id, is_read=False).count()
            return Response({"unread_count": unread_count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class MarkEvaluationNotificationReadAPIView(APIView):
    
    def patch(self, request, notification_id):
        try:
            notification = get_object_or_404(NotificationEvaluations, id=notification_id)          
            notification.is_read = True
            notification.save()
            serializer = NotificationEvaluationSerializer(notification)
            return Response(serializer.data, status=status.HTTP_200_OK)        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ChangesList(APIView):
    def get(self, request, company_id):
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

      
        cpmpliance = ManagementChanges.objects.filter(company=company,is_draft=False)
        serializer = ChangesSerializer(cpmpliance, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class ChangesDetailView(RetrieveDestroyAPIView):
    queryset = ManagementChanges.objects.all()
    serializer_class = ChangesSerializer
    
    
class ChangesCreateAPIView(APIView):
    """
    Endpoint to handle creation of ManagementChanges and optionally send notifications.
    """

    def post(self, request):
        print("Received Data:", request.data)
        try:
            company_id = request.data.get('company')
            send_notification = request.data.get('send_notification', 'false') == 'true'

            if not company_id:
                return Response(
                    {"error": "Company ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            company = Company.objects.get(id=company_id)
            serializer = ChangesSerializer(data=request.data)

            if serializer.is_valid():
                with transaction.atomic():
                    changes = serializer.save()
                    logger.info(f"ManagementChanges created: {changes.moc_title}")

                    changes.send_notification = send_notification
                    changes.save()

                    if send_notification:
                        company_users = Users.objects.filter(company=company)

                        notifications = [
                            NotificationChanges(
                                changes=changes,
                                title=f"New Change: {changes.moc_title}",
                                message=f"A new management change '{changes.moc_title}' has been added."
                            )
                            for user in company_users  # used for email below
                        ]

                        if notifications:
                            NotificationChanges.objects.bulk_create(notifications)
                            logger.info(f"Created {len(notifications)} notifications for change ID {changes.id}")

                        for user in company_users:
                            if user.email:
                                try:
                                    self._send_notification_email(changes, user)
                                except Exception as e:
                                    logger.error(f"Failed to send email to {user.email}: {str(e)}")

                return Response(
                    {
                        "message": "Management Change created successfully",
                        "notification_sent": send_notification
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                logger.warning(f"Validation error: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Company.DoesNotExist:
            return Response(
                {"error": "Company not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error creating Management Change: {str(e)}")
            return Response(
                {"error": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _send_notification_email(self, changes, recipient):
        """
        Helper method to send email notifications about a new Management Change.
        """
        subject = f"New Management Change: {changes.moc_title}"
        message = (
            f"Dear {recipient.first_name},\n\n"
            f"A new management change '{changes.moc_title}' has been created.\n\n"
            f"Details:\n"
            f"- MOC No: {changes.moc_no}\n"
            f"- Type: {changes.moc_type}\n"
            f"- Date: {changes.date}\n"
            f"- Revision: {changes.rivision}\n"
            f"- Related Record Format: {changes.related_record_format}\n\n"
            f"Please log in to view more details.\n\n"
            f"Best regards,\nYour Company Team"
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=config("EMAIL_HOST_USER"),
            recipient_list=[recipient.email],
            fail_silently=False,
        )
        logger.info(f"Email sent to {recipient.email}")




class ChangesDraftAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Create a copy of request.data to modify
        data = {}
        
        # Copy over simple data fields
        for key in request.data:
            if key != 'upload_attachment':
                data[key] = request.data[key]
        
        # Set is_draft flag
        data['is_draft'] = True
        
        # Handle file separately if any
        file_obj = request.FILES.get('upload_attachment')

        # Assuming you have a serializer for the Changes model
        serializer = ChangesSerializer(data=data)
        if serializer.is_valid():
            changes = serializer.save()
            
            # Assign file if provided
            if file_obj:
                changes.upload_attachment = file_obj
                changes.save()

            return Response({"message": "Changes Requirements saved as draft", "data": serializer.data}, 
                             status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class EditsChanges(APIView):
    def put(self, request, pk):
        change_instance = get_object_or_404(ManagementChanges, pk=pk)

        mutable_data = request.data.copy()

        # If attach_document is in the data but no file uploaded, remove it
        if 'attach_document' in mutable_data and not request.FILES.get('attach_document'):
            print("Removing attach_document from request because it's not a file")
            mutable_data.pop('attach_document')

        serializer = ChangesSerializer(change_instance, data=mutable_data, partial=True)

        if serializer.is_valid():
            instance = serializer.save(is_draft=False)

            # If send_notification is True, trigger notifications
            if instance.send_notification and instance.company:
                company_users = Users.objects.filter(company=instance.company)

                notifications = [
                    NotificationChanges(
                        changes=instance,
                        title=f"Updated MOC: {instance.moc_title}",
                        message=f"The MOC '{instance.moc_title}' has been updated."
                    )
                    for user in company_users
                ]

                if notifications:
                    NotificationChanges.objects.bulk_create(notifications)
                    logger.info(f"Created {len(notifications)} notifications for MOC {instance.id}")

                for user in company_users:
                    if user.email:
                        try:
                            self._send_notification_email(instance, user)
                        except Exception as e:
                            logger.error(f"Failed to send email to {user.email}: {str(e)}")

            return Response(ChangesSerializer(instance).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _send_notification_email(self, changes, recipient):
        subject = f"MOC Updated: {changes.moc_title}"
        message = (
            f"Dear {recipient.first_name},\n\n"
            f"A management of change (MOC) titled '{changes.moc_title}' has been updated.\n\n"
            f"Details:\n"
            f"- MOC Type: {changes.moc_type}\n"
            f"- Revision: {changes.rivision}\n"
            f"- Date: {changes.date}\n"
            f"- Related Record Format: {changes.related_record_format}\n\n"
            f"Please log in to view more details.\n\n"
            f"Best regards,\nYour Company Team"
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=config("EMAIL_HOST_USER"),
            recipient_list=[recipient.email],
            fail_silently=False,
        )
        logger.info(f"Email sent to {recipient.email}")


class ChangesDraftAllList(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        record = ManagementChanges.objects.filter(user=user, is_draft=True)
        serializer =ChangesSerializer(record, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class ChangesView(APIView):
 
    def get(self, request, user_id):
   
        draft_records = ManagementChanges.objects.filter(is_draft=True, user_id=user_id)
        
        serializer = ChangesSerializer(draft_records, many=True)
        
        return Response({
            "count": draft_records.count(),
            "draft_records": serializer.data
        }, status=status.HTTP_200_OK)
        
        
class LegalAPIView(APIView):
 
    def get(self, request, user_id):
   
        draft_records = LegalRequirement.objects.filter(is_draft=True, user_id=user_id)
        
        serializer = LegalSerializer(draft_records, many=True)
        
        return Response({
            "count": draft_records.count(),
            "draft_records": serializer.data
        }, status=status.HTTP_200_OK)
        
class ChangesAPIView(APIView):
 
    def get(self, request, user_id):
   
        draft_records = ManagementChanges.objects.filter(is_draft=True, user_id=user_id)
        
        serializer = ChangesSerializer(draft_records, many=True)
        
        return Response({
            "count": draft_records.count(),
            "draft_records": serializer.data
        }, status=status.HTTP_200_OK)
        
        
        
class SustainabilityCreateView(APIView):

    def post(self, request):
        logger.info("Received sustainability creation request.")
        serializer = SustainabilitySerializer(data=request.data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    sustainability = serializer.save()
                    sustainability.written_at = now()
                    sustainability.is_draft = False

                    # Parse boolean flags from request
                    sustainability.send_notification_to_checked_by = parse_bool(
                        request.data.get('send_notification_to_checked_by')
                    )
                    sustainability.send_email_to_checked_by = parse_bool(
                        request.data.get('send_email_to_checked_by')
                    )

                    sustainability.save()
                    logger.info(f"Sustainability created successfully with ID: {sustainability.id}")

                    # Handle notification/email for checked_by user
                    if sustainability.checked_by:
                        if sustainability.send_notification_to_checked_by:
                            try:
                                NotificationSustainability.objects.create(
                                    user=sustainability.checked_by,
                                    sustainability=sustainability,
                                    title="Notification for Checking/Review",
                                    message="A sustainability document has been created for your review."
                                )
                                logger.info(f"Notification created for checked_by user {sustainability.checked_by.id}")
                            except Exception as e:
                                logger.error(f"Error creating notification for checked_by: {str(e)}")

                        if sustainability.send_email_to_checked_by and sustainability.checked_by.email:
                            self.send_email_notification(sustainability, sustainability.checked_by, "review")
                        else:
                            logger.warning("Email to checked_by skipped: flag disabled or email missing.")
                    else:
                        logger.warning("No checked_by user assigned.")

                    return Response(
                        {"message": "Sustainability created successfully", "id": sustainability.id},
                        status=status.HTTP_201_CREATED
                    )

            except Exception as e:
                logger.error(f"Error during sustainability creation: {str(e)}")
                return Response(
                    {"error": "An unexpected error occurred."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        logger.error(f"Sustainability creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def send_email_notification(self, sustainability, recipient, action_type):
    #     recipient_email = recipient.email if recipient else None

    #     if recipient_email:
    #         try:
    #             if action_type == "review":
    #                 subject = f"Sustainability Document Ready for Review: {sustainability.title}"
    #                 message = (
    #                     f"Dear {recipient.first_name},\n\n"
    #                     f"A sustainability document titled '{sustainability.title}' requires your review.\n\n"
    #                     f"Document Number: {sustainability.no or 'N/A'}\n"
    #                     f"Review Frequency: {sustainability.review_frequency_year or 0} year(s), "
    #                     f"{sustainability.review_frequency_month or 0} month(s)\n"
    #                     f"Document Type: {sustainability.document_type}\n\n"
    #                     f"Please login to the system to review.\n\n"
    #                     f"Best regards,\nDocumentation Team"
    #                 )
    #             else:
    #                 logger.warning("Unknown action type provided for email.")
    #                 return

    #             send_mail(
    #                 subject=subject,
    #                 message=message,
    #                 from_email=config("EMAIL_HOST_USER"),
    #                 recipient_list=[recipient_email],
    #                 fail_silently=False,
    #             )
    #             logger.info(f"Email successfully sent to {recipient_email} for action: {action_type}")

    #         except Exception as e:
    #             logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
    #     else:
    #         logger.warning("Recipient email is None. Skipping email send.")

    def send_email_notification(self, sustainability, recipient, action_type):
        recipient_email = recipient.email if recipient else None

        if recipient_email:
            try:
                if action_type == "review":
                    subject = f"Sustainability Document Ready for Review: {sustainability.title}"

                    from django.template.loader import render_to_string
                    from django.utils.html import strip_tags

                    context = {
                        'recipient_name': recipient.first_name,
                        'title': sustainability.title,
                        'document_number': sustainability.no or 'N/A',
                        'review_frequency_year': sustainability.review_frequency_year or 0,
                        'review_frequency_month': sustainability.review_frequency_month or 0,
                        'document_type': sustainability.document_type,
                        'section_number': sustainability.no,
                        'revision': sustainability.rivision,
                         "written_by": sustainability.written_by,
                         "checked_by": sustainability.checked_by,
                         "approved_by": sustainability.approved_by,
                        'date': sustainability.date,
                    }

                
                    html_message = render_to_string('qms/sustainability/template.html', context)
                    plain_message = strip_tags(html_message)

                    send_mail(
                        subject=subject,
                        message=plain_message,
                        from_email=config("EMAIL_HOST_USER"),
                        recipient_list=[recipient_email],
                        fail_silently=False,
                        html_message=html_message,
                    )
                    logger.info(f"HTML Email successfully sent to {recipient_email} for action: {action_type}")
                else:
                    logger.warning("Unknown action type provided for email.")
                    return
            except Exception as e:
                logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        else:
            logger.warning("Recipient email is None. Skipping email send.")

            
            
class SustainabilityAllList(APIView):
    def get(self, request, company_id):
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

        documents = Sustainabilities.objects.filter(company=company, is_draft=False)
        serializer = SustainabilityGetSerializer(documents, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
 

class SustainabilityDetailView(APIView):
    def get(self, request, pk):
        try:
            sustainability = Sustainabilities.objects.get(pk=pk)
        except Sustainabilities.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SustainabilityGetSerializer(sustainability)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            sustainability = Sustainabilities.objects.get(pk=pk)
        except Sustainabilities.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SustainabilitySerializer(sustainability, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            sustainability = Sustainabilities.objects.get(pk=pk)
        except Sustainabilities.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        sustainability.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



 

class SustainabilityUpdateView(APIView):
    def put(self, request, pk):
        try:
            with transaction.atomic():
                sustainability = Sustainabilities.objects.get(pk=pk)

                serializer = SustainabilityUpdateSerializer(sustainability, data=request.data, partial=True)

                if serializer.is_valid():
                    updated_instance = serializer.save()

                    updated_instance.written_at = now()
                    updated_instance.is_draft = False
                    updated_instance.status = 'Pending for Review/Checking'

                    updated_instance.send_notification_to_checked_by = parse_bool(request.data.get('send_system_checked'))
                    updated_instance.send_email_to_checked_by = parse_bool(request.data.get('send_email_checked'))
                    updated_instance.send_notification_to_approved_by = parse_bool(request.data.get('send_system_approved'))
                    updated_instance.send_email_to_approved_by = parse_bool(request.data.get('send_email_approved'))

                    updated_instance.save()

                    # Notifications and emails to checked_by
                    if updated_instance.checked_by:
                        if updated_instance.send_notification_to_checked_by:
                            try:
                                NotificationSustainability.objects.create(
                                    user=updated_instance.checked_by,
                                    sustainability=updated_instance,
                                    title="Sustainability Updated - Review Required",
                                    message=f"Sustainability '{updated_instance.title}' has been updated and requires your review."
                                )
                            except Exception as e:
                                logger.error(f"Notification error for checked_by: {str(e)}")

                        if updated_instance.send_email_to_checked_by and updated_instance.checked_by.email:
                            self.send_email_notification(updated_instance, updated_instance.checked_by, "review")

                    # Notifications and emails to approved_by
                    if updated_instance.approved_by:
                        if updated_instance.send_notification_to_approved_by:
                            try:
                                NotificationSustainability.objects.create(
                                    user=updated_instance.approved_by,
                                    sustainability=updated_instance,
                                    title="Sustainability Updated - Approval Required",
                                    message=f"Sustainability '{updated_instance.title}' has been updated and is ready for your approval."
                                )
                            except Exception as e:
                                logger.error(f"Notification error for approved_by: {str(e)}")

                        if updated_instance.send_email_to_approved_by and updated_instance.approved_by.email:
                            self.send_email_notification(updated_instance, updated_instance.approved_by, "approval")

                    return Response(serializer.data, status=status.HTTP_200_OK)

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Sustainabilities.DoesNotExist:
            return Response({"error": "Sustainability record not found"}, status=status.HTTP_404_NOT_FOUND)

    def send_email_notification(self, instance, recipient, action_type):
        recipient_email = recipient.email if recipient else None

        if recipient_email:
            try:
                if action_type == "review":
                    subject = f"Sustainability Ready for Review: {instance.title}"
                    message = (
                        f"Dear {recipient.first_name},\n\n"
                        f"The sustainability entry '{instance.title}' has been updated and requires your review.\n\n"
                        f"Document Number: {instance.no or 'N/A'}\n"
                        f"Review Frequency: {instance.review_frequency_year or 0} year(s), "
                        f"{instance.review_frequency_month or 0} month(s)\n"
                        f"Document Type: {instance.document_type}\n\n"
                        f"Please login to the system to review.\n\n"
                        f"Best regards,\nDocumentation Team"
                    )
                elif action_type == "approval":
                    subject = f"Sustainability Pending Approval: {instance.title}"
                    message = (
                        f"Dear {recipient.first_name},\n\n"
                        f"The sustainability entry '{instance.title}' has been updated and is ready for your approval.\n\n"
                        f"Document Number: {instance.no or 'N/A'}\n"
                        f"Review Frequency: {instance.review_frequency_year or 0} year(s), "
                        f"{instance.review_frequency_month or 0} month(s)\n"
                        f"Document Type: {instance.document_type}\n\n"
                        f"Please login to the system to approve.\n\n"
                        f"Best regards,\nDocumentation Team"
                    )
                else:
                    logger.warning("Unknown action type for email notification.")
                    return

                send_mail(
                    subject=subject,
                    message=message,
                     from_email=config("EMAIL_HOST_USER"),
                    recipient_list=[recipient_email],
                    fail_silently=False,
                )
                logger.info(f"Email sent to {recipient_email} for action: {action_type}")

            except Exception as e:
                logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        else:
            logger.warning("Recipient email is missing, skipping email.")




class SubmitCorrectionSustainabilityView(APIView):
    def post(self, request):
        try:
            sustainability_id = request.data.get('sustainability_id')
            correction_text = request.data.get('correction')
            from_user_id = request.data.get('from_user')

            if not all([sustainability_id, correction_text, from_user_id]):
                return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                sustainability = Sustainabilities.objects.get(id=sustainability_id)
            except Sustainabilities.DoesNotExist:
                return Response({'error': 'Sustainability record not found'}, status=status.HTTP_404_NOT_FOUND)

            try:
                from_user = Users.objects.get(id=from_user_id)
            except Users.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Determine to_user based on from_user
            if from_user == sustainability.checked_by:
                to_user = sustainability.written_by
            elif from_user == sustainability.approved_by:
                to_user = sustainability.checked_by
            else:
                return Response({'error': 'Invalid user role for correction'}, status=status.HTTP_400_BAD_REQUEST)

            # Delete old correction for same sustainability and from_user (optional)
            CorrectionSustainability.objects.filter(sustainability=sustainability, from_user=from_user).delete()

            # Create new correction
            correction = CorrectionSustainability.objects.create(
                sustainability=sustainability,
                to_user=to_user,
                from_user=from_user,
                correction=correction_text
            )

            # Update status
            sustainability.status = 'Correction Requested'
            sustainability.save()

            # Send notification and email
            self.create_correction_notification(correction)
            self.send_correction_email_notification(correction)

            serializer = CorrectionSustainabilitySerializer(correction)
            return Response(
                {'message': 'Correction submitted successfully', 'correction': serializer.data},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create_correction_notification(self, correction):
        try:
            sustainability = correction.sustainability
            to_user = correction.to_user
            from_user = correction.from_user

            if from_user == sustainability.approved_by and to_user == sustainability.checked_by:
                should_send = sustainability.send_notification_to_checked_by
            elif from_user == sustainability.checked_by and to_user == sustainability.written_by:
                should_send = True
            else:
                should_send = False

            if should_send:
                message = (
                    f"Correction Request from {from_user.first_name} "
                    f"to {to_user.first_name} for document: {sustainability.title}"
                )
                notification = NotificationSustainability.objects.create(
                    user=to_user,
                    sustainability=sustainability,
                    title=sustainability.title,
                    message=message
                )
                print(f"Correction Notification created successfully: {notification.id}")
            else:
                print("Notification not sent due to permission flags or invalid role flow.")
        except Exception as e:
            print(f"Failed to create correction notification: {str(e)}")

    def send_correction_email_notification(self, correction):
        try:
            sustainability = correction.sustainability
            to_user = correction.to_user
            from_user = correction.from_user
            recipient_email = to_user.email if to_user else None

            if from_user == sustainability.approved_by and to_user == sustainability.checked_by:
                should_send = sustainability.send_email_to_checked_by
            elif from_user == sustainability.checked_by and to_user == sustainability.written_by:
                should_send = True
            else:
                should_send = False

            if recipient_email and should_send:
                send_mail(
                    subject=f"Correction Request: {sustainability.title}",
                    message=(
                        f"Dear {to_user.first_name},\n\n"
                        f"A correction has been requested by {from_user.first_name} for the document '{sustainability.title}'.\n\n"
                        f"Correction details:\n"
                        f"{correction.correction}\n\n"
                        f"Please review and take necessary actions.\n\n"
                        f"Best regards,\nDocumentation Team"
                    ),
                    from_email=config("EMAIL_HOST_USER"),
                    recipient_list=[recipient_email],
                    fail_silently=False,
                )
                print(f"Correction email successfully sent to {recipient_email}")
            else:
                print("Email not sent due to permission flags, invalid roles, or missing email.")
        except Exception as e:
            print(f"Failed to send correction email: {str(e)}")


class CorrectionSustainabilityList(generics.ListAPIView):
    serializer_class = CorrectionSustainabilitySerializer

    def get_queryset(self):
        sustainability_id = self.kwargs.get("sustainability_id")
        return CorrectionSustainability.objects.filter(sustainability_id=sustainability_id)
    
 

 

class SustainabilityReviewView(APIView):
    
    def post(self, request):
        logger.info("Received request for Sustainability review process.")
        
        try:
            sustainability_id = request.data.get('sustainability_id')
            current_user_id = request.data.get('current_user_id')

            if not all([sustainability_id, current_user_id]):
                return Response({'error': 'Missing required parameters'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                sustainability = Sustainabilities.objects.get(id=sustainability_id)
                current_user = Users.objects.get(id=current_user_id)
            except (Sustainabilities.DoesNotExist, Users.DoesNotExist):
                return Response({'error': 'Invalid Sustainability or user'}, status=status.HTTP_404_NOT_FOUND)

            with transaction.atomic():
                # Written by - First Submission
                if current_user == sustainability.written_by and not sustainability.written_at:
                    sustainability.written_at = now()

                # Review process
                if sustainability.status == 'Pending for Review/Checking' and current_user == sustainability.checked_by:
                    sustainability.status = 'Reviewed,Pending for Approval'
                    sustainability.checked_at = now()
                    sustainability.save()

                    # Notification to approved_by (only if flag is True)
                    if sustainability.send_notification_to_approved_by:
                        NotificationSustainability.objects.create(
                            user=sustainability.approved_by,
                            sustainability=sustainability,
                            message=f"Sustainability document '{sustainability.title}' is ready for approval."
                        )

                    # Email to approved_by (only if flag is True)
                    if sustainability.send_email_to_approved_by:
                        self.send_email_notification(
                            recipient=sustainability.approved_by,
                            subject=f"Sustainability {sustainability.title} - Pending Approval",
                            message=f"The sustainability document '{sustainability.title}' has been reviewed and is pending your approval."
                        )

                # Approval process
                elif sustainability.status == 'Reviewed,Pending for Approval' and current_user == sustainability.approved_by:
                    sustainability.status = 'Pending for Publish'
                    sustainability.approved_at = now()
                    sustainability.save()
 
                elif current_user == sustainability.written_by and sustainability.status == 'Correction Requested':
                    sustainability.status = 'Pending for Review/Checking'
                    sustainability.save()

                else:
                    return Response({
                        'message': 'No action taken. User not authorized for this Procedure.'
                    }, status=status.HTTP_200_OK)

            return Response({
                'status': 'success',
                'message': 'Sustainability document processed successfully',
                'sustainability_status': sustainability.status
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in procedure review process: {str(e)}")
            return Response({
                'error': 'An unexpected error occurred',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def send_email_notification(self, recipient, subject, message):
        if recipient and recipient.email:
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=config("EMAIL_HOST_USER"),
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )
                logger.info(f"Email sent to {recipient.email}")
            except Exception as e:
                logger.error(f"Failed to send email: {str(e)}")



 

class SustainabilityPublishNotificationView(APIView):
    """
    Endpoint to handle publishing a sustainability document and sending notifications to company users.
    """

    def post(self, request, sustainability_id):
        try:
            sustainability = Sustainabilities.objects.get(id=sustainability_id)
            company_id = request.data.get('company_id')
            published_by = request.data.get('published_by')  
            send_notification = request.data.get('send_notification', False)
            
            if not company_id:
                return Response(
                    {"error": "Company ID is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            company = Company.objects.get(id=company_id)

            with transaction.atomic():
                # Update sustainability status and published_at timestamp
                sustainability.status = 'Published'
                sustainability.published_at = now()

                # Set the publishing user if provided
                if published_by:
                    try:
                        publishing_user = Users.objects.get(id=published_by)
                        sustainability.published_user = publishing_user
                    except Users.DoesNotExist:
                        logger.warning(f"Publisher user ID {published_by} not found")

                sustainability.send_notification = send_notification
                sustainability.save()

                # If notification should be sent, create notifications and send emails
                if send_notification:
                    company_users = Users.objects.filter(company=company)

                    notifications = [
                        NotificationSustainability(
                            user=user,
                            sustainability=sustainability,
                            title=f"Sustainability Document Published: {sustainability.title}",
                            message=f"A new sustainability document '{sustainability.title}' has been published."
                        )
                        for user in company_users
                    ]

                    # Bulk create all notifications
                    if notifications:
                        NotificationSustainability.objects.bulk_create(notifications)
                        logger.info(f"Created {len(notifications)} notifications for sustainability {sustainability_id}")

                    # Send emails to company users
                    for user in company_users:
                        if user.email:
                            try:
                                self._send_publish_email(sustainability, user)
                            except Exception as e:
                                logger.error(f"Failed to send email to {user.email}: {str(e)}")

            return Response(
                {
                    "message": "Sustainability document published successfully",
                    "notification_sent": send_notification,
                    "publisher_set": published_by is not None
                },
                status=status.HTTP_200_OK
            )

        except Sustainabilities.DoesNotExist:
            return Response(
                {"error": "Sustainability document not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Company.DoesNotExist:
            return Response(
                {"error": "Company not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error in publish notification: {str(e)}")
            return Response(
                {"error": f"Failed to publish sustainability document: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _send_publish_email(self, sustainability, recipient):
        """Helper method to send email notifications"""
        # Get publisher name
        publisher_name = "N/A"
        if sustainability.published_user:
            publisher_name = f"{sustainability.published_user.first_name} {sustainability.published_user.last_name}"
        elif sustainability.approved_by:
            publisher_name = f"{sustainability.approved_by.first_name} {sustainability.approved_by.last_name}"
            
        subject = f"New Sustainability Document Published: {sustainability.title}"
        message = (
            f"Dear {recipient.first_name},\n\n"
            f"A new sustainability document titled '{sustainability.title}' has been published.\n\n"
            f"Sustainability Document Details:\n"
            f"- Document Number: {sustainability.no or 'N/A'}\n"
            f"- Document Type: {sustainability.document_type}\n"
            f"- Published By: {publisher_name}\n\n"
            f"Please login to view this document.\n\n"
            f"Best regards,\nSustainability Team"
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=config("EMAIL_HOST_USER"),
            recipient_list=[recipient.email],
            fail_silently=False,
        )
        logger.info(f"Email sent to {recipient.email}")


class SustainabilityDraftAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Create a copy of request.data to modify
        data = {}
        
        # Copy over simple data fields
        for key in request.data:
            if key != 'upload_attachment':
                data[key] = request.data[key]
        
        # Set is_draft flag
        data['is_draft'] = True
        
        # Handle file separately if any
        file_obj = request.FILES.get('upload_attachment')

        # Assuming you have a serializer for the Sustainability model
        serializer = SustainabilitySerializer(data=data)
        if serializer.is_valid():
            sustainability = serializer.save()
            
            # Assign file if provided
            if file_obj:
                sustainability.upload_attachment = file_obj
                sustainability.save()

            return Response({
                "message": "Sustainability document saved as draft",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class SustainabilityDraftAllList(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
 
        sustainability_documents = Sustainabilities.objects.filter(user=user, is_draft=True)
        serializer = SustainabilityGetSerializer(sustainability_documents, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class DraftSustainabilityCountAPIView(APIView):
    def get(self, request, user_id):
    
        draft_sustainabilities = Sustainabilities.objects.filter(is_draft=True, user_id=user_id)
        
  
        serializer = SustainabilitySerializer(draft_sustainabilities, many=True)
        
 
        return Response({
            "count": draft_sustainabilities.count(),
            "draft_sustainabilities": serializer.data
        }, status=status.HTTP_200_OK)
        
        
class NotificationSustainabilityView(APIView):
    
    def get(self, request, user_id):
        user = get_object_or_404(Users, id=user_id)
        notifications = NotificationSustainability.objects.filter(user=user).order_by("-created_at")
        serializer = NotificationSustainabilitySerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, user_id):
        user = get_object_or_404(Users, id=user_id)
        NotificationSustainability.objects.filter(user=user, is_read=False).update(is_read=True)
        return Response({"message": "Notifications marked as read"}, status=status.HTTP_200_OK)
    
    
class NotificationsLastSustainability(APIView):
    
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        notifications = NotificationSustainability.objects.filter(user=user).order_by('-created_at')
        serializer = NotificationSustainabilitySerializer(notifications, many=True)

        return Response({
            "notifications": serializer.data
        }, status=status.HTTP_200_OK)
        
        
class UnreadSustainabilityNotificationsAPIView(APIView):
    def get(self, request, user_id):
        try:
            unread_count = NotificationSustainability.objects.filter(user_id=user_id, is_read=False).count()
            return Response({"unread_count": unread_count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class MarkSustainabilityNotificationReadAPIView(APIView):
    
    def patch(self, request, notification_id):
        try:
            notification = get_object_or_404(NotificationSustainability, id=notification_id)          
            notification.is_read = True
            notification.save()
            serializer = NotificationSustainabilitySerializer(notification)
            return Response(serializer.data, status=status.HTTP_200_OK)        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            
class AwarenessTrainingCreateView(APIView):
    def post(self, request):
        serializer = AwarenessSerializer(data=request.data)
        if serializer.is_valid():
       
            serializer.save()   
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AwarenessAllList(APIView):
    def get(self, request, company_id):
        try:
        
            if not Company.objects.filter(id=company_id).exists():
                return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

           
            company_policies = AwarenessTraining.objects.filter(company_id=company_id ,is_draft=False)

           
            serializer = AwarenessSerializer(company_policies, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AwarenessUpdateView(APIView):
    def put(self, request, pk):
        try:
            documentation = AwarenessTraining.objects.get(pk=pk)
        except AwarenessTraining.DoesNotExist:
            return Response({"error": "AwarenessTraining not found"}, status=status.HTTP_404_NOT_FOUND)

 
        data = request.data.copy()
        
      
        data['is_draft'] = False

 
        serializer = AwarenessSerializer(documentation, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            documentation = AwarenessTraining.objects.get(pk=pk)
        except AwarenessTraining.DoesNotExist:
            return Response({"error": "AwarenessTraining not found"}, status=status.HTTP_404_NOT_FOUND)
        
        documentation.delete()   
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class AwarenessDetailView(APIView):
    def get(self, request, id):
        policy = get_object_or_404(AwarenessTraining, id=id)
        serializer = AwarenessSerializer(policy)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class AwarenessDraftAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Create a copy of request.data to modify
        data = {}
        
        # Copy over simple data fields
        for key in request.data:
            if key != 'upload_attachment':
                data[key] = request.data[key]
        
        # Set is_draft flag
        data['is_draft'] = True
        
        # Handle file separately if any
        file_obj = request.FILES.get('upload_attachment')

        # Assuming you have a serializer for the Awareness model
        serializer = AwarenessSerializer(data=data)
        if serializer.is_valid():
            awareness = serializer.save()
            
            # Assign file if provided
            if file_obj:
                awareness.upload_attachment = file_obj
                awareness.save()

            return Response({
                "message": "Awareness Training saved as draft",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AwarenessDraftAllList(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        record = AwarenessTraining.objects.filter(user=user, is_draft=True)
        serializer =AwarenessSerializer(record, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class AwarenessView(APIView):
 
    def get(self, request, user_id):
   
        draft_records = AwarenessTraining.objects.filter(is_draft=True, user_id=user_id)
        
        serializer = AwarenessSerializer(draft_records, many=True)
        
        return Response({
            "count": draft_records.count(),
            "draft_records": serializer.data
        }, status=status.HTTP_200_OK)


 

class TrainingCreateAPIView(APIView):
    """
    Endpoint to handle creation of a new training and optionally send notifications.
    """
    def post(self, request):
        print("Received Data:", request.data)
        try:
            company_id = request.data.get('company')
            send_notification = request.data.get('send_notification', 'false') == 'true'

            if not company_id:
                return Response(
                    {"error": "Company ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            company = Company.objects.get(id=company_id)
            serializer = TrainingSerializer(data=request.data)

            if serializer.is_valid():
                with transaction.atomic():
                    training = serializer.save()
                    logger.info(f"Training created: {training.training_title}")

                
                    if send_notification:
                        attendees = training.training_attendees.all()
                        users_to_notify = [training.evaluation_by, training.requested_by] + list(attendees)
                        
                     
                        notifications = [
                            TrainingNotification(
                                training=training,
                                title=f"New Training: {training.training_title}",
                                message=f"A new training '{training.training_title}' has been scheduled."
                            )
                            for user in users_to_notify if user
                        ]

                        if notifications:
                            TrainingNotification.objects.bulk_create(notifications)
                            logger.info(f"Created {len(notifications)} notifications for training {training.id}")
 
                        for user in users_to_notify:
                            if user and user.email:
                                self._send_email_async(training, user)

                return Response(
                    {
                        "message": "Training created successfully",
                        "notification_sent": send_notification
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                logger.warning(f"Validation error: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Company.DoesNotExist:
            return Response(
                {"error": "Company not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error creating training: {str(e)}")
            return Response(
                {"error": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _send_email_async(self, training, recipient):
        """
        Sends email in a separate thread to avoid blocking the response.
        """
        threading.Thread(target=self._send_notification_email, args=(training, recipient)).start()

    def _send_notification_email(self, training, recipient):
        """
        Send HTML-formatted email notification about the new training.
        """
        subject = f"New Training Scheduled: {training.training_title}"
        recipient_email = recipient.email

        context = {
            'training_title': training.training_title,
            'expected_results': training.expected_results,
            'type_of_training': training.type_of_training,
            'actual_results': training.actual_results,
            'status': training.status,
            'training_evaluation': training.training_evaluation,
            'training_attendees': training.training_attendees.all(),
            'date_planned': training.date_planned,
            'date_conducted': training.date_conducted,
            'start_time': training.start_time,
            'end_time': training.end_time,
            'venue': training.venue,
            'requested_by': training.requested_by,
            'evaluation_by': training.evaluation_by,
        }

        html_message = render_to_string('qms/training/training_add.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=config("EMAIL_HOST_USER"),
            recipient_list=[recipient_email],
            fail_silently=False,
            html_message=html_message,
        )
        logger.info(f"Email sent to {recipient_email}")



class TrainingList(APIView):
    def get(self, request, company_id):
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

      
        cpmpliance = Training.objects.filter(company=company,is_draft=False)
        serializer = TrainingSerializer(cpmpliance, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class TrainingDetailView(RetrieveDestroyAPIView):
    queryset = Training.objects.all()
    serializer_class = TrainingGetSerializer
    
    
class TrainingUpdateAPIView(APIView):
    """
    Endpoint to update an existing training and optionally send notifications.
    """

    def put(self, request, pk):
        print("request.vfdsgvsd",request.data)
        try:
            training = Training.objects.get(pk=pk)
            send_notification = request.data.get('send_notification', 'false') == 'true'

            serializer = TrainingSerializer(training, data=request.data, partial=True)

            if serializer.is_valid():
                with transaction.atomic():
                    training = serializer.save()
                    logger.info(f"Training updated: {training.training_title}")

                    if send_notification:
                        attendees = training.training_attendees.all()
                        users_to_notify = [training.evaluation_by, training.requested_by] + list(attendees)

                        # Save notifications
                        notifications = [
                            TrainingNotification(
                                training=training,
                                title=f"Updated Training: {training.training_title}",
                                message=f"The training '{training.training_title}' has been updated."
                            )
                            for user in users_to_notify if user
                        ]
                        if notifications:
                            TrainingNotification.objects.bulk_create(notifications)
                            logger.info(f"Created {len(notifications)} notifications for training {training.id}")

                        # Send emails
                        for user in users_to_notify:
                            if user and user.email:
                                self._send_email_async(training, user)

                return Response(
                    {
                        "message": "Training updated successfully",
                        "notification_sent": send_notification
                    },
                    status=status.HTTP_200_OK
                )

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Training.DoesNotExist:
            return Response({"error": "Training not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error updating training: {str(e)}")
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _send_email_async(self, training, recipient):
        threading.Thread(target=self._send_notification_email, args=(training, recipient)).start()

    def _send_notification_email(self, training, recipient):
        subject = f"Training Updated: {training.training_title}"
        recipient_email = recipient.email

        context = {
            'training_title': training.training_title,
            'expected_results': training.expected_results,
            'type_of_training': training.type_of_training,
            'actual_results': training.actual_results,
            'status': training.status,
            'training_evaluation': training.training_evaluation,
            'training_attendees': training.training_attendees.all(),
            'date_planned': training.date_planned,
            'date_conducted': training.date_conducted,
            'start_time': training.start_time,
            'end_time': training.end_time,
            'venue': training.venue,
            'requested_by': training.requested_by,
            'evaluation_by': training.evaluation_by,
        }

        html_message = render_to_string('qms/training/training_update.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=config("EMAIL_HOST_USER"),
            recipient_list=[recipient_email],
            fail_silently=False,
            html_message=html_message,
        )
        logger.info(f"Email sent to {recipient_email}")
        

 

class TrainingCompleteAndNotifyView(APIView):
    def post(self, request, training_id):
        try:
            training = Training.objects.get(id=training_id)
            company = training.company
            send_notification = training.send_notification

            # Set send_notification to True if it's False
            if not send_notification:
                training.send_notification = True
                training.save(update_fields=['send_notification'])
                print(f"send_notification updated to True for training {training_id}")
            
            print(f"Training: {training}")
            print(f"Company: {company}")
            print(f"Send Notification: {training.send_notification}")

            if not company:
                return Response(
                    {"error": "Associated company not found for this training."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            with transaction.atomic():
                training.status = 'Completed'
                training.save(update_fields=['status'])

                logger.info(f"Training '{training.training_title}' marked as Completed")

                if training.send_notification:
                    company_users = Users.objects.filter(company=company)
                    print(f"Company Users: {company_users}")

                    notifications = [
                        TrainingNotification(
                            user=user,
                            training=training,
                            title=f"Training Completed: {training.training_title}",
                            message=f"The training '{training.training_title}' has been completed."
                        )
                        for user in company_users
                    ]

                    if notifications:
                        TrainingNotification.objects.bulk_create(notifications)
                        logger.info(f"{len(notifications)} notifications created for training {training_id}")

                    for user in company_users:
                        if user.email:
                            print(f"Sending email to {user.email}")
                            try:
                                self._send_email(training, user)
                            except Exception as e:
                                logger.error(f"Failed to send email to {user.email}: {str(e)}")

            return Response(
                {"message": "Training marked as completed successfully."},
                status=status.HTTP_200_OK
            )

        except Training.DoesNotExist:
            return Response(
                {"error": "Training not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            logger.error(f"Error in TrainingCompleteAndNotifyView: {str(e)}")
            return Response(
                {"error": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    def _send_email(self, training, recipient):
        subject = f"Training Completed: {training.training_title}"
        context = {
            'training_title': training.training_title,
            'expected_results': training.expected_results,
            'type_of_training': training.type_of_training,
            'actual_results': training.actual_results,
            'status': training.status,
            'training_evaluation': training.training_evaluation,
            'training_attendees': training.training_attendees.all(),
            'date_planned': training.date_planned,
            'date_conducted': training.date_conducted,
            'start_time': training.start_time,
            'end_time': training.end_time,
            'venue': training.venue,
            'requested_by': training.requested_by,
            'evaluation_by': training.evaluation_by,
        }

        print(f"Email Context: {context}")
        logger.info(f"Email Context: {context}")

        try:
            html_message = render_to_string('qms/training/training_completed.html', context)
        except Exception as e:
            logger.warning(f"Template render failed: {str(e)}")
            html_message = f"<p>Training {training.training_title} completed.</p>"

        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=config("EMAIL_HOST_USER"),
            recipient_list=[recipient.email],
            html_message=html_message,
            fail_silently=False
        )
        logger.info(f"Email sent to {recipient.email}")
        print(f"Email sent to {recipient.email}")


class TrainingDraftAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Print request data for debugging (optional)
        print("Request Data:", request.data)
        
        # Create a copy of request.data to modify
        data = {}
        
        # Copy over simple data fields, excluding 'upload_attachment'
        for key in request.data:
            if key != 'upload_attachment':
                data[key] = request.data[key]
        
        # Set the is_draft flag
        data['is_draft'] = True
        
        # Handle file separately if any
        file_obj = request.FILES.get('upload_attachment')

        # Assuming you have a serializer for the Training model
        serializer = TrainingSerializer(data=data)
        if serializer.is_valid():
            training = serializer.save()
            
            # Assign file if provided
            if file_obj:
                training.upload_attachment = file_obj
                training.save()

            return Response({
                "message": "Training saved as draft",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TrainingDraftAllList(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        record = Training.objects.filter(user=user, is_draft=True)
        serializer =TrainingSerializer(record, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TrainingView(APIView):
 
    def get(self, request, user_id):
   
        draft_records = Training.objects.filter(is_draft=True, user_id=user_id)
        
        serializer = TrainingSerializer(draft_records, many=True)
        
        return Response({
            "count": draft_records.count(),
            "draft_records": serializer.data
        }, status=status.HTTP_200_OK)
        
        
class TrainingsByAttendeeAPIView(APIView):
    def get(self, request, user_id, *args, **kwargs):
        trainings = Training.objects.filter(training_attendees__id=user_id).distinct()
        serializer = TrainingSerializer(trainings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TrainingsEvaluatedByUserAPIView(APIView):
    def get(self, request, user_id, *args, **kwargs):
        trainings = Training.objects.filter(evaluation_by__id=user_id).distinct()
        serializer = TrainingSerializer(trainings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class PerformanceCreateView(APIView):
    def post(self, request):
        serializer = EmployeeEvaluationSerializer(data=request.data)
        if serializer.is_valid():
       
            serializer.save()   
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class PerformanceDraftAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Create a copy of request.data to modify
        data = {}

        # Copy over simple data fields, excluding 'upload_attachment'
        for key in request.data:
            if key != 'upload_attachment':
                data[key] = request.data[key]
        
        # Set the is_draft flag
        data['is_draft'] = True
        
        # Handle file separately if any
        file_obj = request.FILES.get('upload_attachment')

        # Assuming you have a serializer for the Employee Evaluation model
        serializer = EmployeeEvaluationSerializer(data=data)
        if serializer.is_valid():
            evaluation = serializer.save()
            
            # Assign file if provided
            if file_obj:
                evaluation.upload_attachment = file_obj
                evaluation.save()

            return Response({
                "message": "Employee Evaluation saved as draft",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class PerformanceAllList(APIView):
    def get(self, request, company_id):
        try:
        
            if not Company.objects.filter(id=company_id).exists():
                return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

           
            company_policies = EmployeePerformance.objects.filter(company_id=company_id ,is_draft=False)

           
            serializer = EmployeeEvaluationSerializer(company_policies, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class PerformanceDetailView(APIView):
    def get(self, request, id):
        policy = get_object_or_404(EmployeePerformance, id=id)
        serializer = EmployeeEvaluationSerializer(policy)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class  PerformanceUpdateView(APIView):
    def put(self, request, pk):
        try:
            documentation = EmployeePerformance.objects.get(pk=pk)
        except EmployeeEvaluationSerializer.DoesNotExist:
            return Response({"error": "EmployeePerformance not found"}, status=status.HTTP_404_NOT_FOUND) 
        data = request.data.copy()      
        data['is_draft'] = False
        serializer = EmployeeEvaluationSerializer(documentation, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            documentation = EmployeePerformance.objects.get(pk=pk)
        except EmployeePerformance.DoesNotExist:
            return Response({"error": "EmployeePerformance not found"}, status=status.HTTP_404_NOT_FOUND)
        
        documentation.delete()   
        return Response(status=status.HTTP_204_NO_CONTENT)


class PerformanceDraftAllList(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        record = EmployeePerformance.objects.filter(user=user, is_draft=True)
        serializer =EmployeeEvaluationSerializer(record, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class PerformanceView(APIView):
 
    def get(self, request, user_id):
   
        draft_records = EmployeePerformance.objects.filter(is_draft=True, user_id=user_id)
        
        serializer = EmployeeEvaluationSerializer(draft_records, many=True)
        
        return Response({
            "count": draft_records.count(),
            "draft_records": serializer.data
        }, status=status.HTTP_200_OK)


class AddPerformanceQuestionAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PerformanceQuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class PerformanceQuestionsByEvaluationAPIView(APIView):
    def get(self, request, performance_id, *args, **kwargs):
        questions = PerformanceQuestions.objects.filter(performance_id=performance_id)
        serializer = PerformanceQuestionSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)   

class DeletePerformanceQuestionAPIView(APIView):
    def delete(self, request, question_id, *args, **kwargs):
        try:
            question = PerformanceQuestions.objects.get(id=question_id)
            question.delete()
            return Response({"message": "Question deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except PerformanceQuestions.DoesNotExist:
            return Response({"error": "Question not found."}, status=status.HTTP_404_NOT_FOUND)
        
class AddAnswerToQuestionAPIView(APIView):
    def patch(self, request, question_id, *args, **kwargs):
        try:
            question = PerformanceQuestions.objects.get(id=question_id)
            answer = request.data.get('answer')
            user_id = request.data.get('user_id')

            if not answer:
                return Response({"error": "Answer is required."}, status=status.HTTP_400_BAD_REQUEST)

            if not user_id:
                return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            question.answer = answer
            question.user_id = user_id  
            question.save()

            return Response({"message": "Answer and user updated successfully."}, status=status.HTTP_200_OK)

        except PerformanceQuestions.DoesNotExist:
            return Response({"error": "Question not found."}, status=status.HTTP_404_NOT_FOUND)
        
        
 

class UsersNotSubmittedAnswersView(APIView):
    def get(self, request, company_id, evaluation_id):
        try:
  
            try:
                company = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                return Response(
                    {"error": "Company not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
          
            try:
                performance = EmployeePerformance.objects.get(id=evaluation_id, company=company)
            except EmployeePerformance.DoesNotExist:
                return Response(
                    {"error": "Evaluation not found or does not belong to the specified company."},
                    status=status.HTTP_404_NOT_FOUND
                )
           
            company_users = Users.objects.filter(company=company, is_trash=False)
           
            submitted_user_ids = PerformanceQuestions.objects.filter(
                performance=performance,
                user__isnull=False
            ).values_list('user_id', flat=True).distinct()
            
            not_submitted_users = company_users.exclude(id__in=submitted_user_ids)
      
            user_data = [
                {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "status": user.status
                }
                for user in not_submitted_users
            ]

            return Response(user_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
class SurveyCreateView(APIView):
    def post(self, request):
        serializer = EmployeeSurveySerializer(data=request.data)
        if serializer.is_valid():
       
            serializer.save()   
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SurveyAllList(APIView):
    def get(self, request, company_id):
        try:
        
            if not Company.objects.filter(id=company_id).exists():
                return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

           
            company_policies = EmployeeSurvey.objects.filter(company_id=company_id ,is_draft=False)

           
            serializer = EmployeeSurveySerializer(company_policies, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class  SurveyUpdateView(APIView):
    def put(self, request, pk):
        try:
            documentation = EmployeeSurvey.objects.get(pk=pk)
        except EmployeeSurveySerializer.DoesNotExist:
            return Response({"error": "Employee Survey not found"}, status=status.HTTP_404_NOT_FOUND) 
        data = request.data.copy()      
        data['is_draft'] = False
        serializer = EmployeeSurveySerializer(documentation, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            documentation = EmployeeSurvey.objects.get(pk=pk)
        except EmployeeSurvey.DoesNotExist:
            return Response({"error": "Employee Survey not found"}, status=status.HTTP_404_NOT_FOUND)
        
        documentation.delete()   
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class SurveyDetailView(APIView):
    def get(self, request, id):
        policy = get_object_or_404(EmployeeSurvey, id=id)
        serializer = EmployeeSurveySerializer(policy)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class SurveyDraftAPIView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data.copy()  
        data['is_draft'] = True  

        serializer =EmployeeSurveySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Employee Survey   saved as draft", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SurveyDraftAllList(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        record = EmployeeSurvey.objects.filter(user=user, is_draft=True)
        serializer =EmployeeSurveySerializer(record, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class SurveyView(APIView):
 
    def get(self, request, user_id):
   
        draft_records = EmployeeSurvey.objects.filter(is_draft=True, user_id=user_id)
        
        serializer = EmployeeSurveySerializer(draft_records, many=True)
        
        return Response({
            "count": draft_records.count(),
            "draft_records": serializer.data
        }, status=status.HTTP_200_OK)


class AddSurveyQuestionAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SurveyQuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
class SurveyQuestionsByEvaluationAPIView(APIView):
    def get(self, request, survey_id, *args, **kwargs):
        questions = SurveyQuestions.objects.filter(survey_id=survey_id)
        serializer = SurveyQuestionSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)   


class DeleteSurveyQuestionAPIView(APIView):
    def delete(self, request, question_id, *args, **kwargs):
        try:
            question = SurveyQuestions.objects.get(id=question_id)
            question.delete()
            return Response({"message": "Question deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except SurveyQuestions.DoesNotExist:
            return Response({"error": "Question not found."}, status=status.HTTP_404_NOT_FOUND)
        
class AddSurveyAnswerToQuestionAPIView(APIView):
    def patch(self, request, question_id, *args, **kwargs):
        try:
            question = SurveyQuestions.objects.get(id=question_id)
            answer = request.data.get('answer')
            user_id = request.data.get('user_id')

            if not answer:
                return Response({"error": "Answer is required."}, status=status.HTTP_400_BAD_REQUEST)

            if not user_id:
                return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            question.answer = answer
            question.user_id = user_id  
            question.save()

            return Response({"message": "Answer and user updated successfully."}, status=status.HTTP_200_OK)

        except PerformanceQuestions.DoesNotExist:
            return Response({"error": "Question not found."}, status=status.HTTP_404_NOT_FOUND)


class UserSurveysAnswersView(APIView):
    def get(self, request, company_id, survey_id):
        try:
  
            try:
                company = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                return Response(
                    {"error": "Company not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
          
            try:
                survey = EmployeeSurvey.objects.get(id=survey_id, company=company)
            except EmployeeSurvey.DoesNotExist:
                return Response(
                    {"error": "Survey not found or does not belong to the specified company."},
                    status=status.HTTP_404_NOT_FOUND
                )
           
            company_users = Users.objects.filter(company=company, is_trash=False)
           
            submitted_user_ids = SurveyQuestions.objects.filter(
                survey=survey,
                user__isnull=False
            ).values_list('user_id', flat=True).distinct()
            
            not_submitted_users = company_users.exclude(id__in=submitted_user_ids)
      
            user_data = [
                {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "status": user.status
                }
                for user in not_submitted_users
            ]

            return Response(user_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
class ScopeCreateView(APIView):
    def post(self, request):
        serializer = ScopeSerializer(data=request.data)
        if serializer.is_valid():
       
            serializer.save()   
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ScopeAllList(APIView):
    def get(self, request, company_id):
        try:
        
            if not Company.objects.filter(id=company_id).exists():
                return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

           
            company_policies = Scope.objects.filter(company_id=company_id)

           
            serializer = ScopeSerializer(company_policies, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ScopeUpdateView(APIView):
    def put(self, request, pk):
        try:
            documentation = Scope.objects.get(pk=pk)
        except Scope.DoesNotExist:
            return Response({"error": "Scope not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ScopeSerializer(documentation, data=request.data)
        if serializer.is_valid():
            serializer.save()   
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            documentation = Scope.objects.get(pk=pk)
        except Scope.DoesNotExist:
            return Response({"error": "Scope not found"}, status=status.HTTP_404_NOT_FOUND)
        
        documentation.delete()   
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ScopeDetailView(APIView):
    def get(self, request, id):
        policy = get_object_or_404(Scope, id=id)
        serializer = ScopeSerializer(policy)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class ScopeFileDownloadView(View):
    """View to handle policy file downloads from S3 storage"""
    
    def get(self, request, policy_id):
        try:
            # Get the policy object or return 404
            policy = get_object_or_404(Scope, id=policy_id)
            
            # Check if the policy has an attached file
            if not policy.energy_policy or not policy.energy_policy.name:
                return JsonResponse({"error": "No file attached to this policy"}, status=404)

            # Get bucket name from settings
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            if not bucket_name:
                bucket_name = "hoztox-test"  # fallback

            # Get file key and make sure it includes the 'media/' prefix
            file_key = policy.energy_policy.name
            if not file_key.startswith("media/"):
                file_key = f"media/{file_key}"

            print(f"Generating download URL for file: {file_key} in bucket: {bucket_name}")
            
            # Create the S3 client
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME or 'ap-south-1'
            )
            
            # Generate a presigned URL
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': file_key,
                    'ResponseContentDisposition': f'attachment; filename="{os.path.basename(file_key)}"'
                },
                ExpiresIn=3600  # 1 hour
            )

            print(f"Generated presigned URL: {url}")
            return JsonResponse({"download_url": url})

        except ClientError as e:
            print(f"S3 client error: {e}")
            return JsonResponse({"error": f"S3 error: {str(e)}"}, status=500)

        except Exception as e:
            print(f"Unexpected error: {e}")
            return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)


class ProcedurePublishedList(APIView):
    def get(self, request, company_id):
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

        procedures = Procedure.objects.filter(
            company=company,
            is_draft=False,
            status='Published'
        )
        serializer = ProcedureGetSerializer(procedures, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AgendaListCreateView(APIView):
    def post(self, request):
        serializer = AgendaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CompanyAgendaView(APIView):
    def get(self, request, company_id):
        agendas = Agenda.objects.filter(company_id=company_id)
        serializer = AgendaSerializer(agendas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

 
   
class AgendaDetailView(APIView):
 
    def get_object(self, pk):
        try:
            return Agenda.objects.get(pk=pk)
        except Agenda.DoesNotExist:
            return None


    def delete(self, request, pk):
        agenda = self.get_object(pk)
        if not agenda:
            return Response({"error": "Agenda not found."}, status=status.HTTP_404_NOT_FOUND)
        agenda.delete()
        return Response({"message": "Agenda deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
class MeetingListCreateView(APIView):
  
    def get(self, request):
        meetings = Meeting.objects.all()
        serializer = MeetingSerializer(meetings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = MeetingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeetingDetailView(APIView):
    
    def get_object(self, pk):
        try:
            return Meeting.objects.get(pk=pk)
        except Meeting.DoesNotExist:
            return None

    def get(self, request, pk):
        meeting = self.get_object(pk)
        if not meeting:
            return Response({"error": "Meeting not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = MeetingSerializer(meeting)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        meeting = self.get_object(pk)
        if not meeting:
            return Response({"error": "Meeting not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = MeetingSerializer(meeting, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        meeting = self.get_object(pk)
        if not meeting:
            return Response({"error": "Meeting not found."}, status=status.HTTP_404_NOT_FOUND)
        meeting.delete()
        return Response({"message": "Meeting deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
    
 

 

class MeetingCreateView(APIView):
    def post(self, request):
        print("✅ Received Data:", request.data)
        try:
            company_id = request.data.get('company')
            # Convert the boolean value properly - this is likely the issue
            send_notification = request.data.get('send_notification', False)
            
            # If send_notification comes as a string (like 'true' or 'false'), convert it
            if isinstance(send_notification, str):
                send_notification = send_notification.lower() == 'true'
                
            print("🔔 Send Notification Flag:", send_notification)  # Debug the value
            
            if not company_id:
                return Response(
                    {"error": "Company ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            company = Company.objects.get(id=company_id)
            
            # Your existing serializer validation code
            serializer = MeetingSerializer(data=request.data)
            
            if serializer.is_valid():
                with transaction.atomic():
                    meeting = serializer.save()
                    print(f"📅 Meeting created: {meeting.title}")
                    
                    # Ensure the send_notification flag is properly set
                    meeting.send_notification = send_notification
                    meeting.save()
                    
                    # Process attendees if they're sent separately
                    attendees_ids = request.data.get('attendees', [])
                    if attendees_ids:
                        for attendee_id in attendees_ids:
                            try:
                                attendee = Users.objects.get(id=attendee_id)
                                meeting.attendees.add(attendee)
                            except Users.DoesNotExist:
                                pass
                    
                    # Process agenda items if they're sent separately
                    agenda_ids = request.data.get('agenda', [])
                    if agenda_ids:
                        for agenda_id in agenda_ids:
                            try:
                                agenda = Agenda.objects.get(id=agenda_id)
                                meeting.agenda.add(agenda)
                            except Agenda.DoesNotExist:
                                pass
                    
                    # Send notifications only if requested
                    if send_notification:
                        # Create notifications for attendees
                        notifications = []
                        for attendee in meeting.attendees.all():
                            notification = MeetingNotification(
                                user=attendee,
                                meeting=meeting,
                                title=f"Meeting Invitation: {meeting.title}",
                                message=f"You have been invited to a meeting on {meeting.date} at {meeting.start_time}."
                            )
                            notifications.append(notification)
                        
                        # Bulk create notifications
                        if notifications:
                            MeetingNotification.objects.bulk_create(notifications)
                            print(f"Created {len(notifications)} notifications for meeting {meeting.id}")
                        
                        # Send email to each attendee
                        for attendee in meeting.attendees.all():
                            if attendee.email:
                                try:
                                    self._send_notification_email(meeting, attendee)
                                except Exception as e:
                                    print(f"Failed to send email to {attendee.email}: {str(e)}")
                
                return Response(
                    {
                        "message": "Meeting created successfully",
                        "notification_sent": send_notification
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Company.DoesNotExist:
            return Response(
                {"error": "Company not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error creating meeting: {str(e)}")
            return Response(
                {"error": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _send_notification_email(self, meeting, recipient):
        subject = f"Meeting Invitation: {meeting.title}"
        recipient_email = recipient.email

        context = {
            'title': meeting.title,
            'date': meeting.date,
            'start_time': meeting.start_time,
            'end_time': meeting.end_time,
            'venue': meeting.venue or 'Not specified',
            'meeting_type': meeting.meeting_type,
            'called_by': f"{meeting.called_by.first_name} {meeting.called_by.last_name}" if meeting.called_by else "Unknown",
            'agenda_item': meeting.agenda.all(),
            'attendees': meeting.attendees.all(),
            'recipient_name': recipient.first_name,
        }

        html_message = render_to_string('qms/meeting/meeting_add.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=config("EMAIL_HOST_USER"),
            recipient_list=[recipient_email],
            fail_silently=False,
            html_message=html_message,
        )
        print(f"📧 Email sent to {recipient_email}")



class MeetingAllList(APIView):
    def get(self, request, company_id):
        try:
        
            if not Company.objects.filter(id=company_id).exists():
                return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

           
            company_policies = Meeting.objects.filter(company_id=company_id,is_draft=False)

           
            serializer = MeetingGetSerializer(company_policies, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MeetingDetailView(RetrieveDestroyAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingGetSerializer
    
    
 
logger = logging.getLogger(__name__)


class MeetingUpdateAPIView(APIView):
    """
    Endpoint to update an existing meeting and optionally send notifications.
    """

    def put(self, request, pk):
        print("Request Data:", request.data)
        try:
            meeting = Meeting.objects.get(pk=pk)
            send_notification = str(request.data.get('send_notification', 'false')).lower() == 'true'

            serializer = MeetingSerializer(meeting, data=request.data, partial=True)

            if serializer.is_valid():
                with transaction.atomic():
                    meeting = serializer.save()
                    logger.info(f"Meeting updated: {meeting.title}")

                    if send_notification:
                        attendees = meeting.attendees.all()
                        users_to_notify = [meeting.called_by] + list(attendees)

                        # Save notifications
                        notifications = [
                            MeetingNotification(
                                user=user,
                                meeting=meeting,
                                title=f"Updated Meeting: {meeting.title}",
                                message=f"The meeting '{meeting.title}' has been updated."
                            )
                            for user in users_to_notify if user
                        ]
                        if notifications:
                            MeetingNotification.objects.bulk_create(notifications)
                            logger.info(f"Created {len(notifications)} notifications for meeting {meeting.id}")

                        # Send emails
                        for user in users_to_notify:
                            if user and user.email:
                                self._send_email_async(meeting, user)

                return Response(
                    {
                        "message": "Meeting updated successfully",
                        "notification_sent": send_notification
                    },
                    status=status.HTTP_200_OK
                )

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Meeting.DoesNotExist:
            return Response({"error": "Meeting not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error updating meeting: {str(e)}", exc_info=True)
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _send_email_async(self, meeting, recipient):
   
        threading.Thread(target=self._send_notification_email, args=(meeting, recipient)).start()

    def _send_notification_email(self, meeting, recipient):
        subject = f"Meeting Updated: {meeting.title}"
        recipient_email = recipient.email

        context = {
            'title': meeting.title,
            'date': meeting.date,
            'start_time': meeting.start_time,
            'end_time': meeting.end_time,
            'venue': meeting.venue or 'Not specified',
            'meeting_type': meeting.meeting_type,
            'called_by': f"{meeting.called_by.first_name} {meeting.called_by.last_name}" if meeting.called_by else "Unknown",
            'agenda_item': meeting.agenda.all(),
            'attendees': meeting.attendees.all(),
            'recipient_name': recipient.first_name,
        }

        try:
            html_message = render_to_string('qms/meeting/meeting_update.html', context)
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=config("EMAIL_HOST_USER"),
                recipient_list=[recipient_email],
                fail_silently=False,
                html_message=html_message,
            )
            logger.info(f"Email sent to {recipient_email}")
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}: {str(e)}", exc_info=True)

        
class MeetingDraftAPIView(APIView):
    def post(self, request, *args, **kwargs):
 
        print("Request Data:", request.data)
        
   
        data = {}
        
      
        for key in request.data:
            if key != 'upload_attachment':
                data[key] = request.data[key]
        
        # Set the is_draft flag
        data['is_draft'] = True
        
      
        file_obj = request.FILES.get('upload_attachment')

     
        serializer = MeetingSerializer(data=data)
        if serializer.is_valid():
            training = serializer.save()
            
     
            if file_obj:
                training.upload_attachment = file_obj
                training.save()

            return Response({
                "message": "Training saved as draft",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class MeetingDraftAllList(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        record = Meeting.objects.filter(user=user, is_draft=True)
        serializer =MeetingGetSerializer(record, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class MessageCreateAPIView(APIView):
    def post(self, request, format=None):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    
 

 

class AuditCreateAPIView(APIView):
    def post(self, request, format=None):
        q = request.data   

      
        data = {
            k: q.get(k)
            for k in q.keys()
            if k not in ('procedures', 'audit_from_internal')
        }   
        procedure_ids = q.getlist('procedures')           
        auditor_ids   = q.getlist('audit_from_internal')  

        print("Scalar data:", data)
        print("Procedures:", procedure_ids)
        print("Auditors:", auditor_ids)       
        serializer = AuditSerializer(data=data)
        if not serializer.is_valid():
            print("Serializer Errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        audit = serializer.save()

       
        procs = Procedure.objects.filter(id__in=procedure_ids)
        if procs.count() != len(procedure_ids):
            return Response(
                {"error": "One or more selected procedures do not exist."},
                status=status.HTTP_400_BAD_REQUEST
            )

  
        audit.procedures.set(procs)
        audit.audit_from_internal.set(auditor_ids)

        return Response(AuditSerializer(audit).data, status=status.HTTP_201_CREATED)





class CompanyAuditView(APIView):
    def get(self, request, company_id):
        agendas = Audit.objects.filter(company_id=company_id,is_draft=False)
        serializer = AuditSerializer(agendas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AuditDetailView(APIView):
    def get_object(self, pk):
        try:
            return Audit.objects.get(pk=pk)
        except Audit.DoesNotExist:
            return None

    def get(self, request, pk):
        audit = self.get_object(pk)
        if not audit:
            return Response({"error": "Audit not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = AuditSerializer(audit)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        audit = self.get_object(pk)
        if not audit:
            return Response({"error": "Audit not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = AuditSerializer(audit, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        audit = self.get_object(pk)
        if not audit:
            return Response({"error": "Audit not found."}, status=status.HTTP_404_NOT_FOUND)
        audit.delete()
        return Response({"message": "Audit deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


 
class AuditDraftAPIView(APIView): 

    def post(self, request, *args, **kwargs):
        q = request.data  

     
        data = {
            k: q.get(k)
            for k in q.keys()
            if k not in ('upload_attachment', 'procedures', 'audit_from_internal')
        }
        data['is_draft'] = True

    
        procedure_ids = q.getlist('procedures')               
        auditor_ids   = q.getlist('audit_from_internal')    

    
        file_obj = request.FILES.get('upload_attachment')

    
        serializer = AuditSerializer(data=data)
        if not serializer.is_valid():
            print("Serializer Errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        audit = serializer.save()

    
        if file_obj:
            audit.upload_audit_report = file_obj
            audit.save()

     
        if procedure_ids:
            existing = Procedure.objects.filter(id__in=procedure_ids)
            if existing.count() != len(procedure_ids):
                return Response(
                    {"error": "One or more selected procedures do not exist."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            audit.procedures.set(existing)

        if auditor_ids:
 
            audit.audit_from_internal.set(auditor_ids)

        return Response(
            {"message": "Audit saved as draft", "data": AuditSerializer(audit).data},
            status=status.HTTP_201_CREATED
        )


    
class AuditDraftAllList(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        record = Audit.objects.filter(user=user, is_draft=True)
        serializer =AuditSerializer(record, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class AuditDetailAPIView(APIView):

    def get(self, request, pk, format=None):
        audit = get_object_or_404(Audit, pk=pk)
        serializer = AuditGetSerializer(audit)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        print("Request data:", request.data)
        audit = get_object_or_404(Audit, pk=pk)
        serializer = AuditSerializer(audit, data=request.data)

        if serializer.is_valid():
            # Save the basic audit information
            audit = serializer.save()

            # Handle procedures
            procedure_ids = request.data.getlist('procedures', [])
            if procedure_ids:
                existing_procedures = Procedure.objects.filter(id__in=procedure_ids)
                if len(existing_procedures) != len(procedure_ids):
                    return Response(
                        {"error": "One or more selected procedures do not exist."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                audit.procedures.set(existing_procedures)
            else:
                # Clear procedures if none provided
                audit.procedures.clear()

            # Check if audit_from is provided (External auditor)
            if 'audit_from' in request.data and request.data.get('audit_from').strip():
                # This is an external audit, clear internal auditors
                audit.audit_from_internal.clear()
                audit.audit_from = request.data.get('audit_from')
                audit.save()
            
            # Check if audit_from_internal is provided (Internal auditor)
            elif 'audit_from_internal' in request.data and request.data.getlist('audit_from_internal'):
                internal_ids = request.data.getlist('audit_from_internal', [])
                valid_users = Users.objects.filter(id__in=internal_ids)
                
                if len(valid_users) != len(internal_ids):
                    return Response(
                        {"error": "One or more selected users in 'audit_from_internal' do not exist."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Set internal auditors and clear external audit_from
                audit.audit_from_internal.set(valid_users)
                audit.audit_from = ""  # Clear external auditor field
                audit.save()
            
            # If neither is provided, clear both
            else:
                audit.audit_from_internal.clear()
                audit.audit_from = ""
                audit.save()

            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        audit = get_object_or_404(Audit, pk=pk)
        audit.delete()
        return Response({"message": "Audit deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class AuditReportUploadView(APIView):
 

    def post(self, request, audit_id):
        print("rrrrrrrr",request.data)
        try:
            audit = Audit.objects.get(id=audit_id)
        except Audit.DoesNotExist:
            return Response({"error": "Audit not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AuditFileUploadSerializer(audit, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Files uploaded successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class GetAuditReportView(APIView):
    def get(self, request, audit_id):
        try:
            audit = Audit.objects.get(id=audit_id)
        except Audit.DoesNotExist:
            return Response({"error": "Audit not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AuditFileUploadSerializer(audit)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)
    


class InspectionCreateAPIView(APIView):
    def post(self, request, format=None):
        q = request.data   

      
        data = {
            k: q.get(k)
            for k in q.keys()
            if k not in ('procedures', 'inspector_from_internal')
        }   
        procedure_ids = q.getlist('procedures')           
        auditor_ids   = q.getlist('inspector_from_internal')  

        print("Scalar data:", data)
        print("Procedures:", procedure_ids)
        print("inspectiros:", auditor_ids)       
        serializer = InspectionSerializer(data=data)
        if not serializer.is_valid():
            print("Serializer Errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        audit = serializer.save()

       
        procs = Procedure.objects.filter(id__in=procedure_ids)
        if procs.count() != len(procedure_ids):
            return Response(
                {"error": "One or more selected procedures do not exist."},
                status=status.HTTP_400_BAD_REQUEST
            )

  
        audit.procedures.set(procs)
        audit.inspector_from_internal.set(auditor_ids)

        return Response(InspectionSerializer(audit).data, status=status.HTTP_201_CREATED)


   
class CompanyinspectionView(APIView):
    def get(self, request, company_id):
        agendas = Inspection.objects.filter(company_id=company_id,is_draft=False)
        serializer = InspectionSerializer(agendas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class InspectionDetailView(APIView):
    def get_object(self, pk):
        try:
            return Inspection.objects.get(pk=pk)
        except Inspection.DoesNotExist:
            return None

    def get(self, request, pk):
        audit = self.get_object(pk)
        if not audit:
            return Response({"error": "Inspection not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = InspectionSerializer(audit)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        audit = self.get_object(pk)
        if not audit:
            return Response({"error": "Inspection not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = InspectionSerializer(audit, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        audit = self.get_object(pk)
        if not audit:
            return Response({"error": "Inspection not found."}, status=status.HTTP_404_NOT_FOUND)
        audit.delete()
        return Response({"message": "Inspection deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


 
    
class InspesctionDraftAPIView(APIView):

    def post(self, request, *args, **kwargs):
        q = request.data  

     
        data = {
            k: q.get(k)
            for k in q.keys()
            if k not in ('upload_attachment', 'procedures', 'inspector_from_internal')
        }
        data['is_draft'] = True

    
        procedure_ids = q.getlist('procedures')               
        auditor_ids   = q.getlist('inspector_from_internal')    

    
        file_obj = request.FILES.get('upload_attachment')

    
        serializer = InspectionSerializer(data=data)
        if not serializer.is_valid():
            print("Serializer Errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        audit = serializer.save()

    
        if file_obj:
            audit.upload_audit_report = file_obj
            audit.save()

     
        if procedure_ids:
            existing = Procedure.objects.filter(id__in=procedure_ids)
            if existing.count() != len(procedure_ids):
                return Response(
                    {"error": "One or more selected procedures do not exist."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            audit.procedures.set(existing)

        if auditor_ids:
 
            audit.inspector_from_internal.set(auditor_ids)

        return Response(
            {"message": "Internal saved as draft", "data": InspectionSerializer(audit).data},
            status=status.HTTP_201_CREATED
        )


    
class InspectionDraftAllList(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        record = Inspection.objects.filter(user=user, is_draft=True)
        serializer =InspectionSerializer(record, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class InspectionDetailAPIView(APIView):

    def get(self, request, pk, format=None):
        audit = get_object_or_404(Inspection, pk=pk)
        serializer = InspectionGetSerializer(audit)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        print("Request data:", request.data)
        audit = get_object_or_404(Inspection, pk=pk)
        serializer = InspectionSerializer(audit, data=request.data)

        if serializer.is_valid():
            # Save the basic audit information
            audit = serializer.save()

            # Handle procedures
            procedure_ids = request.data.getlist('procedures', [])
            if procedure_ids:
                existing_procedures = Procedure.objects.filter(id__in=procedure_ids)
                if len(existing_procedures) != len(procedure_ids):
                    return Response(
                        {"error": "One or more selected procedures do not exist."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                audit.procedures.set(existing_procedures)
            else:
                # Clear procedures if none provided
                audit.procedures.clear()

            # Check if inspector_from is provided (External inspector)
            if 'inspector_from' in request.data and request.data.get('inspector_from').strip():
                # This is an external inspection, clear internal inspectors
                audit.inspector_from_internal.clear()
                audit.inspector_from = request.data.get('inspector_from')
                audit.save()
            
            # Check if inspector_from_internal is provided (Internal inspector)
            elif 'inspector_from_internal' in request.data and request.data.getlist('inspector_from_internal'):
                internal_ids = request.data.getlist('inspector_from_internal', [])
                valid_users = Users.objects.filter(id__in=internal_ids)
                
                if len(valid_users) != len(internal_ids):
                    return Response(
                        {"error": "One or more selected users in 'inspector_from_internal' do not exist."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Set internal inspectors and clear external inspector_from
                audit.inspector_from_internal.set(valid_users)
                audit.inspector_from = ""  # Clear external inspector field
                audit.save()
            
            # If neither is provided, clear both
            else:
                audit.inspector_from_internal.clear()
                audit.inspector_from = ""
                audit.save()

            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        audit = get_object_or_404(Inspection, pk=pk)
        audit.delete()
        return Response({"message": "Audit deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
    
class InspectionReportUploadView(APIView):
 

    def post(self, request, audit_id):
        print("rrrrrrrr",request.data)
        try:
            audit = Inspection.objects.get(id=audit_id)
        except Inspection.DoesNotExist:
            return Response({"error": "Inspection not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = InspectionFileUploadSerializer(audit, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Files uploaded successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class GetInspectionReportView(APIView):
    def get(self, request, audit_id):
        try:
            audit = Inspection.objects.get(id=audit_id)
        except Inspection.DoesNotExist:
            return Response({"error": "Audit not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = InspectionFileUploadSerializer(audit)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)
    
    
class CauseListCreateView(APIView):
    def post(self, request):
        serializer = CauseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CompanyCauseView(APIView):
    def get(self, request, company_id):
        agendas = Cause.objects.filter(company_id=company_id)
        serializer = CauseSerializer(agendas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
 
class CauseDetailView(APIView):
 
    def get_object(self, pk):
        try:
            return Cause.objects.get(pk=pk)
        except Cause.DoesNotExist:
            return None


    def delete(self, request, pk):
        agenda = self.get_object(pk)
        if not agenda:
            return Response({"error": "Cause not found."}, status=status.HTTP_404_NOT_FOUND)
        agenda.delete()
        return Response({"message": "Cause deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    

class RootCauseListCreateView(APIView):
    def post(self, request):
        serializer = RootCauseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RootCompanyCauseView(APIView):
    def get(self, request, company_id):
        agendas = RootCause.objects.filter(company_id=company_id)
        serializer = RootCauseSerializer(agendas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
 
class RootCauseDetailView(APIView):
 
    def get_object(self, pk):
        try:
            return RootCause.objects.get(pk=pk)
        except RootCause.DoesNotExist:
            return None


    def delete(self, request, pk):
        agenda = self.get_object(pk)
        if not agenda:
            return Response({"error": "RootCause not found."}, status=status.HTTP_404_NOT_FOUND)
        agenda.delete()
        return Response({"message": "RootCause deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    

   
class CarNumberCreateAPIView(APIView):
    """
    Endpoint to handle creation of Corrective Action Record and send notifications.
    """

    def post(self, request):
        print("Received Data:", request.data)
        try:
            company_id = request.data.get('company')
            send_notification = request.data.get('send_notification', False)
            executor_id = request.data.get('executor')

            if not company_id:
                return Response(
                    {"error": "Company ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            company = Company.objects.get(id=company_id)
            serializer = CarNumberSerializer(data=request.data)

            if serializer.is_valid():
                with transaction.atomic():
                    car_number = serializer.save()
                    logger.info(f"Corrective Action created: {car_number.title}")

                    # If send_notification is true and executor exists
                    if send_notification and executor_id:
                        try:
                            executor = Users.objects.get(id=executor_id)
                            
                            # Create notification for the executor
                            notification = CarNotification(
                                user=executor,
                                carnumber=car_number,
                                title=f"New Corrective Action: {car_number.title}",
                                message=f"You have been assigned as executor for corrective action '{car_number.title}'"
                            )
                            notification.save()
                            logger.info(f"Created notification for executor {executor.id} for CAR {car_number.id}")
                            
                            # Send email to executor
                            if executor.email:
                                self._send_email_async(car_number, executor)

                        except Users.DoesNotExist:
                            logger.warning(f"Executor with ID {executor_id} not found")

                return Response(
                    {
                        "message": "Corrective Action created successfully",
                        "notification_sent": send_notification and executor_id is not None
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                logger.warning(f"Validation error: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Company.DoesNotExist:
            return Response(
                {"error": "Company not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error creating CAR: {str(e)}")
            return Response(
                {"error": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _send_email_async(self, car_number, recipient):
        """
        Sends email in a separate thread to avoid blocking response.
        """
        threading.Thread(target=self._send_notification_email, args=(car_number, recipient)).start()

    def _send_notification_email(self, car_number, recipient):
        """
        Send HTML-formatted email notification about a new CAR assignment.
        """
        subject = f"CAR Assignment: {car_number.title}"
        recipient_email = recipient.email

        context = {
            'title': car_number.title,
            'action_no': car_number.action_no,
            'source': car_number.source,
            'description': car_number.description,
            'date_raised': car_number.date_raised,
            'date_completed': car_number.date_completed,
            'action_or_corrections': car_number.action_or_corrections,
            'status': car_number.status,
            'root_cause': car_number.root_cause.title if car_number.root_cause else "N/A",
        }

        html_message = render_to_string('qms/car/car_add_template.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=config("EMAIL_HOST_USER"),
            recipient_list=[recipient_email],
            fail_silently=False,
            html_message=html_message,
        )
        logger.info(f"Email sent to {recipient_email}")


class CarNumberDetailView(APIView):
   
    def get_object(self, pk):
        try:
            return CarNumber.objects.get(pk=pk)
        except CarNumber.DoesNotExist:
            return None

    def get(self, request, pk):
        car_number = self.get_object(pk)
        if not car_number:
            return Response({"error": "CarNumber not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CarNumberSerializer(car_number)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        car_number = self.get_object(pk)
        if not car_number:
            return Response({"error": "CarNumber not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CarNumberSerializer(car_number, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        car_number = self.get_object(pk)
        if not car_number:
            return Response({"error": "CarNumber not found."}, status=status.HTTP_404_NOT_FOUND)
        car_number.delete()
        return Response({"message": "CarNumber deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
class CarDraftAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Don't copy the entire request.data, just extract what we need
        data = {}
        
        # Copy over simple data fields 
        for key in request.data:
            if key != 'upload_attachment':
                data[key] = request.data[key]
        
        # Set is_draft flag
        data['is_draft'] = True
        
        # Handle file separately
        file_obj = request.FILES.get('upload_attachment')
        
        serializer = CarNumberSerializer(data=data)
        if serializer.is_valid():
            manual = serializer.save()
            
            # Assign file if provided
            if file_obj:
                manual.upload_attachment = file_obj
                manual.save()
                
            return Response({"message": "CarNumber saved as draft", "data": serializer.data}, 
                           status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CarNCompanyCauseView(APIView):
    def get(self, request, company_id):
        agendas = CarNumber.objects.filter(company_id=company_id)
        serializer = CarNumberSerializer(agendas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetNextActionNumberView(APIView):
    def get(self, request, company_id):
        try:
            company = Company.objects.get(id=company_id)
            last_car = CarNumber.objects.filter(company=company).order_by('-action_no').first()
            next_action_no = 1 if not last_car or not last_car.action_no else last_car.action_no + 1
            return Response({'next_action_no': next_action_no}, status=status.HTTP_200_OK)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        
class InternalProblemCreateView(generics.CreateAPIView):
    queryset = InternalProblem.objects.all()
    serializer_class = InternalProblemSerializer
    
class InternalProblemView(APIView):
    def get(self, request, company_id):
        agendas = InternalProblem.objects.filter(company_id=company_id,is_draft=False)
        serializer = InternalProblemGetSerializer(agendas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class InternalDetailView(APIView):
   
    def get_object(self, pk):
        try:
            return InternalProblem.objects.get(pk=pk)
        except InternalProblem.DoesNotExist:
            return None

    def get(self, request, pk):
        internal_problem = self.get_object(pk)  # Renamed from car_number to internal_problem for clarity
        if not internal_problem:
            return Response({"error": "InternalProblem not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = InternalProblemGetSerializer(internal_problem)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        print("rrrrr", request.data)
        internal_problem = self.get_object(pk)
        if not internal_problem:
            return Response({"error": "InternalProblem not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = InternalProblemSerializer(internal_problem, data=request.data)
        if serializer.is_valid():
            # Ensure car_no is None if corrective_action is No
            if serializer.validated_data.get('corrective_action') == 'No':
                serializer.validated_data['car_no'] = None
            
            # Save with is_draft set to False
            serializer.save(is_draft=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        print("sssssss", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk):
        car_number = self.get_object(pk)
        if not car_number:
            return Response({"error": "InternalProblem not found."}, status=status.HTTP_404_NOT_FOUND)
        car_number.delete()
        return Response({"message": "InternalProblem deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
    
class SupplierAPIView(APIView):
   
    def post(self, request):
        serializer = SupplierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SupplierView(APIView):
    def get(self, request, company_id):
        agendas = Supplier.objects.filter(company_id=company_id,is_draft=False)
        serializer = SupplierGetSerializer(agendas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SupplierDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Supplier.objects.get(pk=pk)
        except Supplier.DoesNotExist:
            return None

 
    def get(self, request, pk):
        supplier = self.get_object(pk)
        if not supplier:
            return Response({"error": "Supplier not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = SupplierGetSerializer(supplier)
        return Response(serializer.data, status=status.HTTP_200_OK)

   
    def put(self, request, pk):
        supplier = self.get_object(pk)
        if not supplier:
            return Response({"error": "Supplier not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = SupplierSerializer(supplier, data=request.data)
        if serializer.is_valid():
            serializer.save(is_draft=False)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request, pk):
        supplier = self.get_object(pk)
        if not supplier:
            return Response({"error": "Supplier not found."}, status=status.HTTP_404_NOT_FOUND)
        supplier.delete()
        return Response({"message": "Supplier deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
    
class InternalDraftAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Don't copy the entire request.data, just extract what we need
        data = {}
        
        # Copy over simple data fields 
        for key in request.data:
            if key != 'upload_attachment':
                data[key] = request.data[key]
        
        # Set is_draft flag
        data['is_draft'] = True
        
        # Handle file separately
        file_obj = request.FILES.get('upload_attachment')
        
        serializer = InternalProblemSerializer(data=data)
        if serializer.is_valid():
            manual = serializer.save()
            
            # Assign file if provided
            if file_obj:
                manual.upload_attachment = file_obj
                manual.save()
                
            return Response({"message": "CarNumber saved as draft", "data": serializer.data}, 
                           status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class IternalDraftAllList(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        record = InternalProblem.objects.filter(user=user, is_draft=True)
        serializer =InternalProblemGetSerializer(record, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class SupplierDraftAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Don't copy the entire request.data, just extract what we need
        data = {}
        
        # Copy over simple data fields 
        for key in request.data:
            if key != 'upload_attachment':
                data[key] = request.data[key]
        
        # Set is_draft flag
        data['is_draft'] = True
        
        # Handle file separately
        file_obj = request.FILES.get('upload_attachment')
        
        serializer = SupplierSerializer(data=data)
        if serializer.is_valid():
            manual = serializer.save()
            
            # Assign file if provided
            if file_obj:
                manual.upload_attachment = file_obj
                manual.save()
                
            return Response({"message": "CarNumber saved as draft", "data": serializer.data}, 
                           status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SupplierDraftAllList(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        record = Supplier.objects.filter(user=user, is_draft=True)
        serializer =SupplierSerializer(record, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class SupplierProblemAPIView(APIView):
    def post(self, request):
        serializer = SupplierProblemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
 


class SupplierProblemDetailAPIView(APIView):
   
    def get_object(self, pk):
        try:
            return SupplierProblem.objects.get(pk=pk)
        except SupplierProblem.DoesNotExist:
            return None

 
    def get(self, request, pk):
        supplier_problem = self.get_object(pk)
        if supplier_problem is None:
            return Response({"error": "SupplierProblem not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = SupplierProblemSerializer(supplier_problem)
        return Response(serializer.data, status=status.HTTP_200_OK)

 
    def put(self, request, pk):
        supplier_problem = self.get_object(pk)
        if supplier_problem is None:
            return Response({"error": "SupplierProblem not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = SupplierProblemSerializer(supplier_problem, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  
    def delete(self, request, pk):
        supplier_problem = self.get_object(pk)
        if supplier_problem is None:
            return Response({"error": "SupplierProblem not found"}, status=status.HTTP_404_NOT_FOUND)
        supplier_problem.delete()
        return Response({"message": "SupplierProblem deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
    
class SupplierProblemView(APIView):
    def get(self, request, company_id):
     
        agendas = SupplierProblem.objects.filter(ompany_id=company_id,is_draft=False)
        serializer = SupplierProblemSerializer(agendas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    
class ManualDraftEditView(APIView):
    def put(self, request, id):
        logger.info("Received manual edit request.")

        try:
            # Try to get the manual by ID
            manual = Manual.objects.get(id=id)
            
            # Create a serializer instance for updating the manual
            serializer = ManualSerializer(manual, data=request.data, partial=True)
            
            if serializer.is_valid():
                try:
                    with transaction.atomic():
                        # Save the changes to the manual
                        manual = serializer.save()

                        # Set `is_draft` to False when the manual is edited
                        manual.is_draft = False  # This is crucial for your requirement

                        # Apply the changes to the manual
                        manual.save()

                        logger.info(f"Manual updated successfully with ID: {manual.id}")

                        # Send notifications and emails like in manual creation
                        if manual.checked_by:
                            if manual.send_notification_to_checked_by:
                                self._send_notifications(manual)

                            if manual.send_email_to_checked_by and manual.checked_by.email:
                                self.send_email_notification(manual, manual.checked_by, "review")

                        return Response(
                            {"message": "Manual updated successfully", "id": manual.id},
                            status=status.HTTP_200_OK
                        )

                except Exception as e:
                    logger.error(f"Error during manual update: {str(e)}")
                    return Response(
                        {"error": "An unexpected error occurred."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Manual.DoesNotExist:
            return Response({"error": "Manual not found."}, status=status.HTTP_404_NOT_FOUND)

    def _send_notifications(self, manual):
        # Your notification sending logic (same as in the creation view)
        if manual.checked_by:
            try:
                NotificationQMS.objects.create(
                    user=manual.checked_by,
                    manual=manual,
                    title="Notification for Checking/Review",
                    message="A manual has been created/updated for your review."
                )
                logger.info(f"Notification created for checked_by user {manual.checked_by.id}")
            except Exception as e:
                logger.error(f"Error creating notification for checked_by: {str(e)}")

    def send_email_notification(self, manual, recipient, action_type):
        # Same email logic as in the creation view
        recipient_email = recipient.email if recipient else None
        if recipient_email:
            try:
                if action_type == "review":
                    subject = f"Manual Ready for Review: {manual.title}"
                    from django.template.loader import render_to_string
                    from django.utils.html import strip_tags

                    context = {
                        'recipient_name': recipient.first_name,
                        'title': manual.title,
                        'document_number': manual.no or 'N/A',
                        'review_frequency_year': manual.review_frequency_year or 0,
                        'review_frequency_month': manual.review_frequency_month or 0,
                        'document_type': manual.document_type,
                        'section_number': manual.no,
                        'revision': manual.rivision,
                        "written_by": manual.written_by,
                        "checked_by": manual.checked_by,
                        "approved_by": manual.approved_by,
                        'date': manual.date,
                        'document_url': manual.upload_attachment.url if manual.upload_attachment else None,
                        'document_name': manual.upload_attachment.name.rsplit('/', 1)[-1] if manual.upload_attachment else None,
                    }

                    html_message = render_to_string('qms/manual/manual_to_checked_by.html', context)
                    plain_message = strip_tags(html_message)

                    send_mail(
                        subject=subject,
                        message=plain_message,
                        from_email=config("EMAIL_HOST_USER"),
                        recipient_list=[recipient_email],
                        fail_silently=False,
                        html_message=html_message,
                    )
                    logger.info(f"HTML Email successfully sent to {recipient_email} for action: {action_type}")
                else:
                    logger.warning("Unknown action type provided for email.")
                    return
            except Exception as e:
                logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        else:
            logger.warning("Recipient email is None. Skipping email send.")
