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
from django.core.mail import EmailMultiAlternatives
from rest_framework.exceptions import NotFound
from ximspro.utils.email_backend import CertifiEmailBackend



 
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
                    from_email=config('DEFAULT_FROM_EMAIL'),
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

                    context = {
                        'recipient_name': recipient.first_name,
                        'title': manual.title,
                        'document_number': manual.no or 'N/A',
                        'review_frequency_year': manual.review_frequency_year or 0,
                        'review_frequency_month': manual.review_frequency_month or 0,
                        'document_type': manual.document_type,
                        'section_number': manual.no,
                        'rivision': getattr(manual, 'rivision', ''),
                        'written_by': manual.written_by,
                        'checked_by': manual.checked_by,
                        'approved_by': manual.approved_by,
                        'date': manual.date,
                    }

                    html_message = render_to_string('qms/manual/manual_to_checked_by.html', context)
                    plain_message = strip_tags(html_message)

                    # Create email message
                    email = EmailMultiAlternatives(
                        subject=subject,
                        body=plain_message,
                        from_email=config("DEFAULT_FROM_EMAIL"),
                        to=[recipient_email]
                    )
                    email.attach_alternative(html_message, "text/html")

                    # Attach document if available
                    if manual.upload_attachment:
                        try:
                            file_name = manual.upload_attachment.name.rsplit('/', 1)[-1]
                            file_content = manual.upload_attachment.read()
                            email.attach(file_name, file_content)
                            logger.info(f"Attached manual document {file_name} to email")
                        except Exception as attachment_error:
                            logger.error(f"Error attaching manual file: {str(attachment_error)}")

                    # Optional: Use custom backend
                    connection = CertifiEmailBackend(
                        host=config('EMAIL_HOST'),
                        port=config('EMAIL_PORT'),
                        username=config('EMAIL_HOST_USER'),
                        password=config('EMAIL_HOST_PASSWORD'),
                        use_tls=True
                    )

                    email.connection = connection
                    email.send(fail_silently=False)

                    logger.info(f"Email with attachment successfully sent to {recipient_email} for action: {action_type}")
                else:
                    logger.warning("Unknown action type provided for email.")
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
            # Extract data from request
            manual_id = request.data.get('manual_id')
            correction_text = request.data.get('correction')
            from_user_id = request.data.get('from_user')

            # Check if all required fields are provided
            if not all([manual_id, correction_text, from_user_id]):
                return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

            # Get manual object
            try:
                manual = Manual.objects.get(id=manual_id)
            except Manual.DoesNotExist:
                return Response({'error': 'Manual not found'}, status=status.HTTP_404_NOT_FOUND)

            # Get user object
            try:
                from_user = Users.objects.get(id=from_user_id)
            except Users.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Validate user role and determine the recipient of the correction
            if from_user == manual.checked_by:
                to_user = manual.written_by
            elif from_user == manual.approved_by:
                to_user = manual.checked_by
            else:
                return Response({'error': 'Invalid user role for correction'}, status=status.HTTP_400_BAD_REQUEST)

            # Create correction
            correction = CorrectionQMS.objects.create(
                manual=manual,
                to_user=to_user,
                from_user=from_user,
                correction=correction_text
            )

            # Update manual status
            manual.status = 'Correction Requested'
            manual.save()

            # Create notification and send email
            self.create_correction_notification(correction)
            self.send_correction_email_notification(correction)

            # Serialize and return response
            serializer = CorrectionQMSSerializer(correction)
            return Response(
                {'message': 'Correction submitted successfully', 'correction': serializer.data},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            print(f"Error occurred in submit correction: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create_correction_notification(self, correction):
        try:
            manual = correction.manual
            to_user = correction.to_user
            from_user = correction.from_user

            # Determine if notification should be sent based on user roles
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
        try:
            manual = correction.manual
            from_user = correction.from_user
            to_user = correction.to_user
            recipient_email = to_user.email if to_user else None

            # Define template and subject based on user roles
            if from_user == manual.checked_by and to_user == manual.written_by:
                template_name = 'qms/manual/manual_correction_to_writer.html'
                subject = f"Correction Requested on '{manual.title}'"
                should_send = True
            elif from_user == manual.approved_by and to_user == manual.checked_by:
                template_name = 'qms/manual/manual_correction_to_checker.html'
                subject = f"Correction Requested on '{manual.title}'"
                should_send = manual.send_email_to_checked_by
            else:
                return  # Not a valid correction flow

            # Check if email sending is enabled and recipient is valid
            if not recipient_email or not should_send:
                return

            # Prepare email context
            context = {
                'recipient_name': to_user.first_name,
                'title': manual.title,
                'document_number': manual.no or 'N/A',
                'review_frequency_year': manual.review_frequency_year or 0,
                'review_frequency_month': manual.review_frequency_month or 0,
                'document_type': manual.document_type,
                'section_number': manual.no,
                'rivision': getattr(manual, 'rivision', ''),
                'written_by': manual.written_by,
                'checked_by': manual.checked_by,
                'approved_by': manual.approved_by,
                'date': manual.date,
            }

            # Render email message
            html_message = render_to_string(template_name, context)
            plain_message = strip_tags(html_message)

            # Send email
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=config("DEFAULT_FROM_EMAIL"),
                to=[recipient_email]
            )
            email.attach_alternative(html_message, "text/html")

            # Attach manual file if exists
            if manual.upload_attachment:
                try:
                    file_name = manual.upload_attachment.name.rsplit('/', 1)[-1]
                    file_content = manual.upload_attachment.read()
                    email.attach(file_name, file_content)
                    print(f"Attached file {file_name} to correction email.")
                except Exception as attachment_error:
                    print(f"Failed to attach file: {str(attachment_error)}")

            # Use custom email backend
            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )
            email.connection = connection
            email.send(fail_silently=False)

            print(f"Correction email successfully sent to {recipient_email}")

        except Exception as e:
            print(f"Error sending correction email: {str(e)}")





class ManualCorrectionsListView(generics.ListAPIView):
    serializer_class = CorrectionGetQMSSerializer

    def get_queryset(self):
        manual_id = self.kwargs.get("manual_id")
        return CorrectionQMS.objects.filter(manual_id=manual_id)
    
    


 

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
        from django.core.mail import EmailMultiAlternatives

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
                            'rivision': manual.rivision,
                            'written_by': manual.written_by,
                            'checked_by': manual.checked_by,
                            'approved_by': manual.approved_by,
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
                            'review_frequency_year': manual.review_frequency_year or 0,
                            'review_frequency_month': manual.review_frequency_month or 0,
                            'document_type': manual.document_type,
                            'section_number': manual.no,
                            'rivision': manual.rivision,
                            'written_by': manual.written_by,
                            'checked_by': manual.checked_by,
                            'approved_by': manual.approved_by,
                            'date': manual.date,
                            'document_url': manual.upload_attachment.url if manual.upload_attachment else None,
                            'document_name': manual.upload_attachment.name.rsplit('/', 1)[-1] if manual.upload_attachment else None,
                        }
                        html_message = render_to_string('qms/manual/manual_publish.html', context)
                        plain_message = strip_tags(html_message)

                    else:
                        logger.warning(f"Unknown action type '{action_type}' for email notification.")
                        continue

                    # Create email
                    email = EmailMultiAlternatives(
                        subject=subject,
                        body=plain_message,
                        from_email=config('DEFAULT_FROM_EMAIL'),
                        to=[recipient_email]
                    )
                    email.attach_alternative(html_message, "text/html")

                    # Attach the manual document if it exists
                    if manual.upload_attachment:
                        try:
                            file_name = manual.upload_attachment.name.rsplit('/', 1)[-1]
                            file_content = manual.upload_attachment.read()
                            email.attach(file_name, file_content)
                            logger.info(f"Attached manual file {file_name} to email")
                        except Exception as attachment_error:
                            logger.error(f"Error attaching file: {str(attachment_error)}")

                    # Use custom backend (optional)
                    connection = CertifiEmailBackend(
                        host=config('EMAIL_HOST'),
                        port=config('EMAIL_PORT'),
                        username=config('EMAIL_HOST_USER'),
                        password=config('EMAIL_HOST_PASSWORD'),
                        use_tls=True
                    )
                    email.connection = connection
                    email.send(fail_silently=False)

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
                        'rivision': getattr(manual, 'rivision', ''),
                        'written_by': manual.written_by,
                        'checked_by': manual.checked_by,
                        'approved_by': manual.approved_by,
                        'date': manual.date,
                    }

                    html_message = render_to_string('qms/manual/manual_update_to_checked_by.html', context)
                    plain_message = strip_tags(html_message)

                    email = EmailMultiAlternatives(
                        subject=subject,
                        body=plain_message,
                        from_email=config("DEFAULT_FROM_EMAIL"),
                        to=[recipient_email]
                    )
                    email.attach_alternative(html_message, "text/html")

                    # Attach the manual file if available
                    if manual.upload_attachment:
                        try:
                            file_name = manual.upload_attachment.name.rsplit('/', 1)[-1]
                            file_content = manual.upload_attachment.read()
                            email.attach(file_name, file_content)
                            logger.info(f"Attached manual file {file_name} to email")
                        except Exception as attachment_error:
                            logger.error(f"Error attaching file: {str(attachment_error)}")

                    # Use custom email backend (optional, can be removed if not needed)
                    connection = CertifiEmailBackend(
                        host=config('EMAIL_HOST'),
                        port=config('EMAIL_PORT'),
                        username=config('EMAIL_HOST_USER'),
                        password=config('EMAIL_HOST_PASSWORD'),
                        use_tls=True
                    )
                    email.connection = connection
                    email.send(fail_silently=False)

                    logger.info(f"Email with attachment successfully sent to {recipient_email} for action: {action_type}")
                else:
                    logger.warning("Unknown action type provided for email.")
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
        """Helper method to send email notifications with template and attach manual document"""
        from decouple import config
      
        from django.utils.html import strip_tags
        from django.template.loader import render_to_string

        publisher_name = "N/A"
        if manual.published_user:
            publisher_name = f"{manual.published_user.first_name} {manual.published_user.last_name}"
        elif manual.approved_by:
            publisher_name = f"{manual.approved_by.first_name} {manual.approved_by.last_name}"

        subject = f"New Manual Published: {manual.title}"

        context = {
            'recipient_name': recipient.first_name,
            'title': manual.title,
            'document_number': manual.no or 'N/A',
            'review_frequency_year': manual.review_frequency_year or 0,
            'review_frequency_month': manual.review_frequency_month or 0,
            'document_type': manual.document_type,
            'section_number': manual.no,
            'rivision': manual.rivision,
            "written_by": manual.written_by,
            "checked_by": manual.checked_by,
            "approved_by": manual.approved_by,
            'date': manual.date,
            'document_url': manual.upload_attachment.url if manual.upload_attachment else None,
            'document_name': manual.upload_attachment.name.rsplit('/', 1)[-1] if manual.upload_attachment else None,
        }

        html_message = render_to_string('qms/manual/manual_published_notification.html', context)
        plain_message = strip_tags(html_message)

        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=config("DEFAULT_FROM_EMAIL"),
            to=[recipient.email]
        )
        email.attach_alternative(html_message, "text/html")

        if manual.upload_attachment:
            try:
                file_name = manual.upload_attachment.name.rsplit('/', 1)[-1]
                file_content = manual.upload_attachment.read()
                email.attach(file_name, file_content)
                logger.info(f"Attached manual file {file_name} to email")
            except Exception as attachment_error:
                logger.error(f"Error attaching file: {str(attachment_error)}")

        # Use custom backend if needed
        try:
            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )
            email.connection = connection
            email.send(fail_silently=False)
            logger.info(f"HTML Email sent to {recipient.email}")
        except Exception as e:
            logger.error(f"Failed to send email to {recipient.email}: {str(e)}")


 

 

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
                    subject = f"Procedure Ready for Review: {procedure.title}"

                    context = {
                        'recipient_name': recipient.first_name,
                        'title': procedure.title,
                        'document_number': procedure.no or 'N/A',
                        'review_frequency_year': procedure.review_frequency_year or 0,
                        'review_frequency_month': procedure.review_frequency_month or 0,
                        'document_type': procedure.document_type,
                        'section_number': procedure.no,
                        'rivision': getattr(procedure, 'rivision', ''),
                        'written_by': procedure.written_by,
                        'checked_by': procedure.checked_by,
                        'approved_by': procedure.approved_by,
                        'date': procedure.date,
                    }

                    html_message = render_to_string('qms/procedure/procedure_to_checked_by.html', context)
                    plain_message = strip_tags(html_message)

                    email = EmailMultiAlternatives(
                        subject=subject,
                        body=plain_message,
                        from_email=config("DEFAULT_FROM_EMAIL"),
                        to=[recipient_email]
                    )
                    email.attach_alternative(html_message, "text/html")

                    # Attach document if available
                    if procedure.upload_attachment:
                        try:
                            file_name = procedure.upload_attachment.name.rsplit('/', 1)[-1]
                            file_content = procedure.upload_attachment.read()
                            email.attach(file_name, file_content)
                            logger.info(f"Attached procedure document {file_name} to email")
                        except Exception as attachment_error:
                            logger.error(f"Error attaching procedure file: {str(attachment_error)}")

                    # Optional: Use custom backend
                    connection = CertifiEmailBackend(
                        host=config('EMAIL_HOST'),
                        port=config('EMAIL_PORT'),
                        username=config('EMAIL_HOST_USER'),
                        password=config('EMAIL_HOST_PASSWORD'),
                        use_tls=True
                    )

                    email.connection = connection
                    email.send(fail_silently=False)

                    logger.info(f"Email with attachment successfully sent to {recipient_email} for action: {action_type}")
                else:
                    logger.warning("Unknown action type provided for email.")
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
                    subject = f"Procedure Corrections Updated: {procedure.title}"

                    from django.template.loader import render_to_string
                    from django.utils.html import strip_tags

                    context = {
                        'recipient_name': recipient.first_name,
                        'title': procedure.title,
                        'document_number': procedure.no or 'N/A',
                        'review_frequency_year': procedure.review_frequency_year or 0,
                        'review_frequency_month': procedure.review_frequency_month or 0,
                        'document_type': procedure.document_type,
                        'section_number': procedure.no,
                        'rivision': procedure.rivision,
                        "written_by": procedure.written_by,
                        "checked_by": procedure.checked_by,
                        "approved_by": procedure.approved_by,
                        'date': procedure.date,
                    }

                    html_message = render_to_string('qms/procedure/procedure_update_to_checked_by.html', context)
                    plain_message = strip_tags(html_message)

                    email = EmailMultiAlternatives(
                        subject=subject,
                        body=plain_message,
                        from_email=config("DEFAULT_FROM_EMAIL"),
                        to=[recipient_email]
                    )
                    email.attach_alternative(html_message, "text/html")

                    # Attach the uploaded procedure file if it exists
                    if procedure.upload_attachment:
                        try:
                            file_name = procedure.upload_attachment.name.rsplit('/', 1)[-1]
                            file_content = procedure.upload_attachment.read()
                            email.attach(file_name, file_content)
                            logger.info(f"Attached procedure file {file_name} to email")
                        except Exception as attachment_error:
                            logger.error(f"Error attaching file: {str(attachment_error)}")

                    # Use custom backend if required
                    connection = CertifiEmailBackend(
                        host=config('EMAIL_HOST'),
                        port=config('EMAIL_PORT'),
                        username=config('EMAIL_HOST_USER'),
                        password=config('EMAIL_HOST_PASSWORD'),
                        use_tls=True
                    )
                    email.connection = connection
                    email.send(fail_silently=False)

                    logger.info(f"Email with attachment successfully sent to {recipient_email} for action: {action_type}")
                else:
                    logger.warning("Unknown action type provided for email.")
            except Exception as e:
                logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        else:
            logger.warning("Recipient email is None. Skipping email send.")

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

            if from_user == procedure.checked_by and to_user == procedure.written_by:
                template_name = 'qms/procedure/procedure_correction_to_writer.html'
                subject = f"Correction Requested on '{procedure.title}'"
                should_send = True
            elif from_user == procedure.approved_by and to_user == procedure.checked_by:
                template_name = 'qms/procedure/procedure_correction_to_checker.html'
                subject = f"Correction Requested on '{procedure.title}'"
                should_send = procedure.send_email_to_checked_by
            else:
                return

            if not recipient_email or not should_send:
                return

            context = {
                'recipient_name': to_user.first_name,
                'title': procedure.title,
                'document_number': procedure.no or 'N/A',
                'review_frequency_year': procedure.review_frequency_year or 0,
                'review_frequency_month': procedure.review_frequency_month or 0,
                'document_type': procedure.document_type,
                'section_number': procedure.no,
                'rivision': procedure.rivision,
                'written_by': procedure.written_by,
                'checked_by': procedure.checked_by,
                'approved_by': procedure.approved_by,
                'date': procedure.date,
            }

            html_message = render_to_string(template_name, context)
            plain_message = strip_tags(html_message)

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=config("DEFAULT_FROM_EMAIL"),
                to=[recipient_email]
            )
            email.attach_alternative(html_message, "text/html")

            # Attach the file if present
            if procedure.upload_attachment:
                try:
                    file_name = procedure.upload_attachment.name.rsplit('/', 1)[-1]
                    file_content = procedure.upload_attachment.read()
                    email.attach(file_name, file_content)
                    print(f"Attached file {file_name} to correction email.")
                except Exception as attachment_error:
                    print(f"Failed to attach file: {str(attachment_error)}")

            # Optional custom backend (if you're using it)
            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )
            email.connection = connection

            email.send(fail_silently=False)
            print(f"Correction email successfully sent to {recipient_email}")

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
                if current_user == procedure.written_by and not procedure.written_at:
                    procedure.written_at = now()
                    procedure.save()

                current_status = procedure.status

                # Case 1: Checked_by reviews
                if current_status == 'Pending for Review/Checking' and current_user == procedure.checked_by:
                    procedure.status = 'Reviewed,Pending for Approval'
                    procedure.checked_at = now()
                    procedure.save()

                    if procedure.send_notification_to_approved_by:
                        NotificatioProcedure.objects.create(
                            user=procedure.approved_by,
                            procedure=procedure,
                            message=f"Procedure '{procedure.title}' is ready for approval."
                        )

                    if procedure.send_email_to_approved_by:
                        self.send_email_notification(
                            procedure=procedure,
                            recipients=[procedure.approved_by],
                            action_type="review"
                        )

                # Case 2: Approved_by approves
                elif current_status == 'Reviewed,Pending for Approval' and current_user == procedure.approved_by:
                    procedure.status = 'Pending for Publish'
                    procedure.approved_at = now()
                    procedure.save()

                    for user in [procedure.written_by, procedure.checked_by, procedure.approved_by]:
                        if user:
                            NotificatioProcedure.objects.create(
                                user=user,
                                procedure=procedure,
                                message=f"Procedure '{procedure.title}' has been approved and is pending for publish."
                            )

                    self.send_email_notification(
                        procedure=procedure,
                        recipients=[u for u in [procedure.written_by, procedure.checked_by, procedure.approved_by] if u],
                        action_type="approved"
                    )

                # Case 3: Correction Requested
                elif current_status == 'Correction Requested' and current_user == procedure.written_by:
                    procedure.status = 'Pending for Review/Checking'
                    procedure.save()

                else:
                    return Response({
                        'message': 'No action taken. User not authorized for this Procedure.'
                    }, status=status.HTTP_200_OK)

            return Response({
                'status': 'success',
                'message': 'Procedure processed successfully',
                'procedure_status': procedure.status
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in procedure review process: {str(e)}")
            return Response({
                'error': 'An unexpected error occurred',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def send_email_notification(self, procedure, recipients, action_type):
        from decouple import config
        from django.core.mail import EmailMultiAlternatives

        for recipient in recipients:
            recipient_email = recipient.email if recipient else None

            if recipient_email:
                try:
                    if action_type == "review":
                        subject = f"Procedure Submitted for Approval: {procedure.title}"
                        context = {
                            'recipient_name': recipient.first_name,
                            'title': procedure.title,
                            'document_number': procedure.no or 'N/A',
                            'review_frequency_year': procedure.review_frequency_year or 0,
                            'review_frequency_month': procedure.review_frequency_month or 0,
                            'document_type': procedure.document_type,
                            'section_number': procedure.no,
                            'rivision': procedure.rivision,
                            "written_by": procedure.written_by,
                            "checked_by": procedure.checked_by,
                            "approved_by": procedure.approved_by,
                            'date': procedure.date,
                            'document_url': procedure.upload_attachment.url if procedure.upload_attachment else None,
                            'document_name': procedure.upload_attachment.name.rsplit('/', 1)[-1] if procedure.upload_attachment else None,
                        }
                        html_message = render_to_string('qms/procedure/procedure_to_approved_by.html', context)
                        plain_message = strip_tags(html_message)

                    elif action_type == "approved":
                        subject = f"Procedure Approved: {procedure.title}"
                        context = {
                            'recipient_name': recipient.first_name,
                            'title': procedure.title,
                            'document_number': procedure.no or 'N/A',
                            'review_frequency_year': procedure.review_frequency_year or 0,
                            'review_frequency_month': procedure.review_frequency_month or 0,
                            'document_type': procedure.document_type,
                            'section_number': procedure.no,
                            'rivision': procedure.rivision,
                            "written_by": procedure.written_by,
                            "checked_by": procedure.checked_by,
                            "approved_by": procedure.approved_by,
                            'date': procedure.date,
                            'document_url': procedure.upload_attachment.url if procedure.upload_attachment else None,
                            'document_name': procedure.upload_attachment.name.rsplit('/', 1)[-1] if procedure.upload_attachment else None,
                        }
                        html_message = render_to_string('qms/procedure/procedure_publish.html', context)
                        plain_message = strip_tags(html_message)

                    else:
                        logger.warning(f"Unknown action type '{action_type}' for email notification.")
                        continue

                    # Create email
                    email = EmailMultiAlternatives(
                        subject=subject,
                        body=plain_message,
                        from_email=config('DEFAULT_FROM_EMAIL'),
                        to=[recipient_email]
                    )
                    email.attach_alternative(html_message, "text/html")

                    # Attach the procedure document if it exists
                    if procedure.upload_attachment:
                        try:
                            file_name = procedure.upload_attachment.name.rsplit('/', 1)[-1]
                            file_content = procedure.upload_attachment.read()
                            email.attach(file_name, file_content)
                            logger.info(f"Attached procedure file {file_name} to email")
                        except Exception as attachment_error:
                            logger.error(f"Error attaching file: {str(attachment_error)}")

                    # Use custom backend (optional)
                    connection = CertifiEmailBackend(
                        host=config('EMAIL_HOST'),
                        port=config('EMAIL_PORT'),
                        username=config('EMAIL_HOST_USER'),
                        password=config('EMAIL_HOST_PASSWORD'),
                        use_tls=True
                    )
                    email.connection = connection
                    email.send(fail_silently=False)

                    logger.info(f"Email successfully sent to {recipient_email} for action: {action_type}")

                except Exception as e:
                    logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
            else:
                logger.warning("Recipient email is None. Skipping email send.")





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

        if not recipient_email:
            logger.warning("Recipient email is None. Skipping email send.")
            return

        try:
            if action_type == "review":
                subject = f"Record Ready for Review: {record.title}"

                context = {
                    'recipient_name': recipient.first_name,
                    'title': record.title,
                    'document_number': record.no or 'N/A',
                    'review_frequency_year': record.review_frequency_year or 0,
                    'review_frequency_month': record.review_frequency_month or 0,
                    'document_type': record.document_type,
                    'section_number': record.no,
                    'rivision': getattr(record, 'rivision', ''),  # fixed typo if any
                    'written_by': record.written_by,
                    'checked_by': record.checked_by,
                    'approved_by': record.approved_by,
                    'date': record.date,
                }

                html_message = render_to_string('qms/record/record_to_checked_by.html', context)
                plain_message = strip_tags(html_message)

                email = EmailMultiAlternatives(
                    subject=subject,
                    body=plain_message,
                    from_email=config("DEFAULT_FROM_EMAIL"),
                    to=[recipient_email]
                )
                email.attach_alternative(html_message, "text/html")

                # Attach document if available
                if record.upload_attachment:
                    try:
                        file_name = record.upload_attachment.name.rsplit('/', 1)[-1]
                        file_content = record.upload_attachment.read()
                        email.attach(file_name, file_content)
                        logger.info(f"Attached document {file_name} to email")
                    except Exception as attachment_error:
                        logger.error(f"Error attaching file: {str(attachment_error)}")

                # Send using custom backend
                connection = CertifiEmailBackend(
                    host=config('EMAIL_HOST'),
                    port=config('EMAIL_PORT'),
                    username=config('EMAIL_HOST_USER'),
                    password=config('EMAIL_HOST_PASSWORD'),
                    use_tls=True
                )
                email.connection = connection
                email.send(fail_silently=False)

                logger.info(f"Email with attachment successfully sent to {recipient_email} for action: {action_type}")
            else:
                logger.warning(f"Unknown action type '{action_type}' provided for email.")
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}: {str(e)}")


            
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

        if not recipient_email:
            logger.warning("Recipient email is None. Skipping email send.")
            return

        try:
            if action_type == "review":
                subject = f"Record Corrections Updated: {record.title}"

                context = {
                    'recipient_name': recipient.first_name,
                    'title': record.title,
                    'document_number': record.no or 'N/A',
                    'review_frequency_year': record.review_frequency_year or 0,
                    'review_frequency_month': record.review_frequency_month or 0,
                    'document_type': record.document_type,
                    'section_number': record.no,
                    'rivision': getattr(record, 'rivision', ''),  # fixed typo 'rivision'
                    "written_by": record.written_by,
                    "checked_by": record.checked_by,
                    "approved_by": record.approved_by,
                    'date': record.date,
                    'document_url': record.upload_attachment.url if record.upload_attachment else None,
                    'document_name': record.upload_attachment.name.rsplit('/', 1)[-1] if record.upload_attachment else None,
                }

                html_message = render_to_string('qms/record/record_update_to_checked_by.html', context)
                plain_message = strip_tags(html_message)

                email = EmailMultiAlternatives(
                    subject=subject,
                    body=plain_message,
                    from_email=config("DEFAULT_FROM_EMAIL"),
                    to=[recipient_email]
                )
                email.attach_alternative(html_message, "text/html")

                # Attach the document if available
                if record.upload_attachment:
                    try:
                        file_name = record.upload_attachment.name.rsplit('/', 1)[-1]
                        file_content = record.upload_attachment.read()
                        email.attach(file_name, file_content)
                        logger.info(f"Attached document {file_name} to email")
                    except Exception as attachment_error:
                        logger.error(f"Error attaching file: {str(attachment_error)}")

                # Send using custom backend
                connection = CertifiEmailBackend(
                    host=config('EMAIL_HOST'),
                    port=config('EMAIL_PORT'),
                    username=config('EMAIL_HOST_USER'),
                    password=config('EMAIL_HOST_PASSWORD'),
                    use_tls=True
                )
                email.connection = connection
                email.send(fail_silently=False)

                logger.info(f"HTML email with attachment successfully sent to {recipient_email} for action: {action_type}")
            else:
                logger.warning(f"Unknown action type '{action_type}' provided for email.")
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}: {str(e)}")


            

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

            # Determine template and subject based on roles
            if from_user == record.approved_by and to_user == record.checked_by:
                template_name = 'qms/record/record_correction_to_checker.html'
                subject = f"Correction Requested on '{record.title}'"
                should_send = record.send_email_to_checked_by
            elif from_user == record.checked_by and to_user == record.written_by:
                template_name = 'qms/record/record_correction_to_writer.html'
                subject = f"Correction Requested on '{record.title}'"
                should_send = True
            else:
                logger.warning("Invalid role relationship. Email not sent.")
                return

            if not recipient_email or not should_send:
                logger.info("Email sending skipped due to missing recipient or disabled flag.")
                return

            # Prepare email context
            context = {
                'recipient_name': to_user.first_name,
                'title': record.title,
                'document_number': record.no or 'N/A',
                'review_frequency_year': record.review_frequency_year or 0,
                'review_frequency_month': record.review_frequency_month or 0,
                'document_type': record.document_type,
                'section_number': record.no,
                'rivision': getattr(record, 'rivision', ''),  # safe access
                "written_by": record.written_by,
                "checked_by": record.checked_by,
                "approved_by": record.approved_by,
                'date': record.date,
                'document_url': record.upload_attachment.url if record.upload_attachment else None,
                'document_name': record.upload_attachment.name.rsplit('/', 1)[-1] if record.upload_attachment else None,
            }

            html_message = render_to_string(template_name, context)
            plain_message = strip_tags(html_message)

            # Construct email
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=config("DEFAULT_FROM_EMAIL"),
                to=[recipient_email]
            )
            email.attach_alternative(html_message, "text/html")

            # Attach file if available
            if record.upload_attachment:
                try:
                    file_name = record.upload_attachment.name.rsplit('/', 1)[-1]
                    file_content = record.upload_attachment.read()
                    email.attach(file_name, file_content)
                    logger.info(f"Attached document {file_name} to email")
                except Exception as attachment_error:
                    logger.error(f"Error attaching file: {str(attachment_error)}")

            # Use custom backend
            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )
            email.connection = connection
            email.send(fail_silently=False)

            logger.info(f"Correction email successfully sent to {recipient_email}")

        except Exception as e:
            logger.error(f"Failed to send correction email: {str(e)}")



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
                # Mark as written
                if current_user == record.written_by and not record.written_at:
                    record.written_at = now()
                    record.save()

                current_status = record.status

                # Case 1: Checked_by reviews
                if current_status == 'Pending for Review/Checking' and current_user == record.checked_by:
                    record.status = 'Reviewed,Pending for Approval'
                    record.checked_at = now()
                    record.save()

                    if record.send_notification_to_approved_by:
                        NotificationRecord.objects.create(
                            user=record.approved_by,
                            record=record,
                            message=f"Record '{record.title}' is ready for approval."
                        )

                    if record.send_email_to_approved_by:
                        self.send_email_notification(
                            record=record,
                            recipients=[record.approved_by],
                            action_type="review"
                        )

                # Case 2: Approved_by approves
                elif current_status == 'Reviewed,Pending for Approval' and current_user == record.approved_by:
                    record.status = 'Pending for Publish'
                    record.approved_at = now()
                    record.save()

                    for user in [record.written_by, record.checked_by, record.approved_by]:
                        if user:
                            NotificationRecord.objects.create(
                                user=user,
                                record=record,
                                message=f"Record '{record.title}' has been approved and is pending for publish."
                            )

                    self.send_email_notification(
                        record=record,
                        recipients=[u for u in [record.written_by, record.checked_by, record.approved_by] if u],
                        action_type="approved"
                    )

                # Correction requested, reverting status
                elif current_status == 'Correction Requested' and current_user == record.written_by:
                    record.status = 'Pending for Review/Checking'
                    record.save()

                else:
                    return Response({
                        'message': 'No action taken. User not authorized for current record status.'
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

    def send_email_notification(self, record, recipients, action_type):
        

        for recipient in recipients:
            recipient_email = recipient.email if recipient else None

            if recipient_email:
                try:
                    if action_type == "review":
                        subject = f"Record Submitted for Approval: {record.title}"
                        context = {
                            'recipient_name': recipient.first_name,
                            'title': record.title,
                            'document_number': record.no or 'N/A',
                            'review_frequency_year': record.review_frequency_year or 0,
                            'review_frequency_month': record.review_frequency_month or 0,
                            'document_type': record.document_type,
                            'section_number': record.no,
                            'rivision': record.rivision,
                            'written_by': record.written_by,
                            'checked_by': record.checked_by,
                            'approved_by': record.approved_by,
                            'date': record.date,
                            'document_url': record.upload_attachment.url if record.upload_attachment else None,
                            'document_name': record.upload_attachment.name.rsplit('/', 1)[-1] if record.upload_attachment else None,
                        }
                        html_message = render_to_string('qms/record/record_to_approved_by.html', context)
                        plain_message = strip_tags(html_message)

                    elif action_type == "approved":
                        subject = f"Record Approved: {record.title}"
                        context = {
                            'recipient_name': recipient.first_name,
                            'title': record.title,
                            'document_number': record.no or 'N/A',
                            'review_frequency_year': record.review_frequency_year or 0,
                            'review_frequency_month': record.review_frequency_month or 0,
                            'document_type': record.document_type,
                            'section_number': record.no,
                            'rivision': record.rivision,
                            'written_by': record.written_by,
                            'checked_by': record.checked_by,
                            'approved_by': record.approved_by,
                            'date': record.date,
                            'document_url': record.upload_attachment.url if record.upload_attachment else None,
                            'document_name': record.upload_attachment.name.rsplit('/', 1)[-1] if record.upload_attachment else None,
                        }
                        html_message = render_to_string('qms/record/record_publish.html', context)
                        plain_message = strip_tags(html_message)

                    else:
                        logger.warning(f"Unknown action type '{action_type}' for email notification.")
                        continue

                    # Create email
                    email = EmailMultiAlternatives(
                        subject=subject,
                        body=plain_message,
                        from_email=config('DEFAULT_FROM_EMAIL'),
                        to=[recipient_email]
                    )
                    email.attach_alternative(html_message, "text/html")

                    # Attach the record document if it exists
                    if record.upload_attachment:
                        try:
                            file_name = record.upload_attachment.name.rsplit('/', 1)[-1]
                            file_content = record.upload_attachment.read()
                            email.attach(file_name, file_content)
                            logger.info(f"Attached record file {file_name} to email")
                        except Exception as attachment_error:
                            logger.error(f"Error attaching file: {str(attachment_error)}")

                    # Use custom backend
                    connection = CertifiEmailBackend(
                        host=config('EMAIL_HOST'),
                        port=config('EMAIL_PORT'),
                        username=config('EMAIL_HOST_USER'),
                        password=config('EMAIL_HOST_PASSWORD'),
                        use_tls=True
                    )
                    email.connection = connection
                    email.send(fail_silently=False)

                    logger.info(f"Email successfully sent to {recipient_email} for action: {action_type}")

                except Exception as e:
                    logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
            else:
                logger.warning("Recipient email is None. Skipping email send.")


                
                
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
        """Helper method to send email notifications with template and attach record document"""
        from decouple import config
        from django.core.mail import EmailMultiAlternatives
        from django.utils.html import strip_tags
        from django.template.loader import render_to_string
        

        publisher_name = "N/A"
        if record.published_user:
            publisher_name = f"{record.published_user.first_name} {record.published_user.last_name}"
        elif record.approved_by:
            publisher_name = f"{record.approved_by.first_name} {record.approved_by.last_name}"

        subject = f"New Record Published: {record.title}"

        context = {
            'recipient_name': recipient.first_name,
            'title': record.title,
            'document_number': record.no or 'N/A',
            'review_frequency_year': record.review_frequency_year or 0,
            'review_frequency_month': record.review_frequency_month or 0,
            'document_type': record.document_type,
            'section_number': record.no,
            'rivision': record.rivision,
            "written_by": record.written_by,
            "checked_by": record.checked_by,
            "approved_by": record.approved_by,
            'date': record.date,
            'publisher_name': publisher_name,
            'document_url': record.upload_attachment.url if record.upload_attachment else None,
            'document_name': record.upload_attachment.name.rsplit('/', 1)[-1] if record.upload_attachment else None,
        }

        html_message = render_to_string('qms/record/record_published_notification.html', context)
        plain_message = strip_tags(html_message)

        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=config("DEFAULT_FROM_EMAIL"),
            to=[recipient.email]
        )
        email.attach_alternative(html_message, "text/html")

        # Attach file if present
        if record.upload_attachment:
            try:
                file_name = record.upload_attachment.name.rsplit('/', 1)[-1]
                file_content = record.upload_attachment.read()
                email.attach(file_name, file_content)
                logger.info(f"Attached record file {file_name} to email")
            except Exception as attachment_error:
                logger.error(f"Error attaching file: {str(attachment_error)}")

        # Use custom backend
        try:
            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )
            email.connection = connection
            email.send(fail_silently=False)
            logger.info(f"HTML Email sent to {recipient.email}")
        except Exception as e:
            logger.error(f"Failed to send email to {recipient.email}: {str(e)}")

 
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
        """Helper method to send email notifications with template and attach procedure document"""
        from decouple import config
        from django.core.mail import EmailMultiAlternatives
        from django.utils.html import strip_tags
        from django.template.loader import render_to_string

        publisher_name = "N/A"
        if procedure.published_user:
            publisher_name = f"{procedure.published_user.first_name} {procedure.published_user.last_name}"
        elif procedure.approved_by:
            publisher_name = f"{procedure.approved_by.first_name} {procedure.approved_by.last_name}"

        subject = f"New Procedure Published: {procedure.title}"

        # Context for the email template
        context = {
            'recipient_name': recipient.first_name,
            'title': procedure.title,
            'document_number': procedure.no or 'N/A',
            'review_frequency_year': procedure.review_frequency_year or 0,
            'review_frequency_month': procedure.review_frequency_month or 0,
            'document_type': procedure.document_type,
            'section_number': procedure.no,
            'rivision': procedure.rivision,
            "written_by": procedure.written_by,
            "checked_by": procedure.checked_by,
            "approved_by": procedure.approved_by,
            'date': procedure.date,
            'document_url': procedure.upload_attachment.url if procedure.upload_attachment else None,
            'document_name': procedure.upload_attachment.name.rsplit('/', 1)[-1] if procedure.upload_attachment else None,
        }

        html_message = render_to_string('qms/procedure/procedure_published_notification.html', context)
        plain_message = strip_tags(html_message)

        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=config("DEFAULT_FROM_EMAIL"),
            to=[recipient.email]
        )
        email.attach_alternative(html_message, "text/html")

        # Attach the procedure document if it exists
        if procedure.upload_attachment:
            try:
                file_name = procedure.upload_attachment.name.rsplit('/', 1)[-1]
                file_content = procedure.upload_attachment.read()
                email.attach(file_name, file_content)
                logger.info(f"Attached procedure file {file_name} to email")
            except Exception as attachment_error:
                logger.error(f"Error attaching file: {str(attachment_error)}")

        # Use custom backend if needed
        try:
            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )
            email.connection = connection
            email.send(fail_silently=False)
            logger.info(f"HTML Email sent to {recipient.email}")
        except Exception as e:
            logger.error(f"Failed to send email to {recipient.email}: {str(e)}")

        
        


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
    Endpoint to handle creation of Interested Party, Needs with both needs and expectations fields,
    and optionally send notifications.
    """
    def post(self, request):
        print("Received Data:", request.data)   
        try:
            # Extract data from the request
            company_id = request.data.get('company')
            send_notification = request.data.get('send_notification', False)   
            needs_data = request.data.get('needs', [])   

            # Debugging print statements
            print(f"Company ID: {company_id}")
            print(f"Send Notification: {send_notification}")
            print(f"Needs Data: {needs_data}")

            # Check if company_id is provided
            if not company_id:
                return Response(
                    {"error": "Company ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Ensure we can get the company record
            try:
                company = Company.objects.get(id=company_id)
                print(f"Found company: {company.name if hasattr(company, 'name') else company.id}")
            except Company.DoesNotExist:
                print(f"Company with ID {company_id} not found!")
                return Response(
                    {"error": "Company not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = InterestedPartySerializer(data=request.data)

            # Validate the serializer and proceed if valid
            if serializer.is_valid():
                with transaction.atomic():
                    interested_party = serializer.save()
                    logger.info(f"Interested Party created: {interested_party.name}")

                    # Log the interested party data
                    print(f"Interested Party Created: {interested_party.name}")
                    print(f"Interested Party ID: {interested_party.id}")
                    print(f"Interested Party Send Notification: {interested_party.send_notification}")

                    # Create needs with both needs and expectations if provided
                    if needs_data:
                        needs_instances = []
                        for need_item in needs_data:
                            needs_instances.append(
                                Needs(
                                    interested_party=interested_party,
                                    needs=need_item.get('needs', ''),
                                    expectation=need_item.get('expectation', '')
                                )
                            )
                        
                        Needs.objects.bulk_create(needs_instances)
                        logger.info(f"Created {len(needs_instances)} Needs for Interested Party {interested_party.id}")
                        print(f"Created {len(needs_instances)} Needs records for IP {interested_party.id}")
                        
                        # Debug: Print created needs details
                        for i, need in enumerate(needs_instances):
                            print(f"Need {i+1}: needs='{need.needs}', expectation='{need.expectation}'")

                    # Save the send_notification flag - make sure we handle string values too
                    print(f"Setting Send Notification Flag to: {send_notification}")
                    if isinstance(send_notification, str):
                        interested_party.send_notification = send_notification.lower() == 'true'
                    else:
                        interested_party.send_notification = bool(send_notification)
                    interested_party.save()
                    print(f"Updated send_notification to: {interested_party.send_notification}")

                    # If send_notification is True, send notifications and emails
                    if interested_party.send_notification:
                        print(f"Preparing to send notifications for company ID: {company.id}")
                        
                        # Get all users for the company - add debugging
                        company_users = Users.objects.filter(company=company)
                        user_count = company_users.count()
                        print(f"Found {user_count} users for company {company.id}")
                        
                        # Debug: List users found
                        for i, user in enumerate(company_users):
                            print(f"User {i+1}: ID={user.id}, Email={user.email}, Name={user.first_name} {user.last_name if hasattr(user, 'last_name') else ''}")
                        
                        if user_count == 0:
                            print("WARNING: No users found for this company! Cannot send notifications.")
                            
                        notifications = [
                            NotificationInterest(
                                interest=interested_party,
                                title=f"New Interested Party: {interested_party.name}",
                                message=f"A new interested party '{interested_party.name}' has been added."
                            )
                            for user in company_users
                        ]

                        if notifications:
                            # Check the NotificationInterest model fields
                            print(f"Creating {len(notifications)} notifications")
                            try:
                                NotificationInterest.objects.bulk_create(notifications)
                                logger.info(f"Created {len(notifications)} notifications for Interested Party {interested_party.id}")
                                print(f"Successfully created {len(notifications)} notifications")
                            except Exception as e:
                                print(f"ERROR creating notifications: {str(e)}")
                                logger.error(f"Failed to create notifications: {str(e)}")
                        else:
                            print("No notifications to create - no users in company.")

                        # Send email notifications to users
                        print("Preparing to send email notifications")
                        for i, user in enumerate(company_users):
                            if user.email:
                                print(f"Sending email to user {i+1}: {user.email}")
                                try:
                                    self._send_notification_email(interested_party, user)
                                    print(f"Email sent successfully to {user.email}")
                                except Exception as e:
                                    error_msg = f"Failed to send email to {user.email}: {str(e)}"
                                    logger.error(error_msg)
                                    print(error_msg)
                            else:
                                print(f"User {i+1} has no email address, skipping")
                    else:
                        print("Notification flag is set to False. Skipping notifications and emails.")

                return Response(
                    {
                        "message": "Interested Party created successfully",
                        "notification_sent": interested_party.send_notification,
                        "id": interested_party.id
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                # Log serializer errors for debugging
                logger.warning(f"Validation error: {serializer.errors}")
                print(f"Validation error: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            print(f"Error occurred: {str(e)}")
            import traceback
            print(traceback.format_exc())  # Print full stack trace
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _send_notification_email(self, interested_party, recipient, manual=None):
        """
        Sends an HTML email with optional attachments (Interested Party + Manual) using a secure backend.
        """
        recipient_email = recipient.email
        if not recipient_email:
            logger.warning("Recipient email is missing.")
            print("Recipient email is missing.")
            return

        try:
            logger.info(f"Preparing to send email to {recipient_email}")
            print(f"Preparing email for {recipient_email}")
            subject = f"New Interested Party Created: {interested_party.name}"
 
            # Get all needs objects for this interested party
            all_needs = interested_party.needs.all()
            needs_count = all_needs.count()
            print(f"Found {needs_count} needs records for this interested party")
            
            # Debug: Print what we found
            needs_list = []
            expectations_list = []
            for i, need in enumerate(all_needs):
                print(f"Need {i+1}: needs='{need.needs}', expectation='{need.expectation}'")
                if need.needs:
                    needs_list.append(need.needs)
                if need.expectation:
                    expectations_list.append(need.expectation)
            
            context = {
                'recipient_name': recipient.first_name if hasattr(recipient, 'first_name') else 'User',
                'name': interested_party.name,
                'category': interested_party.category,
                'needs': needs_list,
                'expectations': expectations_list,
                'special_requirements': interested_party.special_requirements,
                'legal_requirements': interested_party.legal_requirements,
                'custom_legal_requirements': interested_party.custom_legal_requirements,
                'user_first_name': interested_party.user.first_name if interested_party.user else '',
                'user_last_name': interested_party.user.last_name if interested_party.user else '',
            }

            print(f"Email context prepared: {context}")
            
            try:
                html_message = render_to_string('qms/interested_party/intereste_party_add.html', context)
                print("HTML email template rendered successfully")
                plain_message = strip_tags(html_message)
            except Exception as e:
                print(f"ERROR rendering email template: {str(e)}")
                logger.error(f"Template rendering error: {str(e)}")
                raise

            try:
                # Try to get email configuration values for debugging
                email_host = config("EMAIL_HOST", default="Not configured")
                email_port = config("EMAIL_PORT", default="Not configured")
                email_user = config("EMAIL_HOST_USER", default="Not configured")
                email_from = config("DEFAULT_FROM_EMAIL", default="Not configured")
                
                print(f"Email configuration - HOST: {email_host}, PORT: {email_port}, USER: {email_user}, FROM: {email_from}")
                
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=plain_message,
                    from_email=email_from,
                    to=[recipient_email]
                )
                email.attach_alternative(html_message, "text/html")
                print("Email object created")
            except Exception as e:
                print(f"ERROR creating email object: {str(e)}")
                logger.error(f"Email creation error: {str(e)}")
                raise
 
            if interested_party.file:
                try:
                    file_name = interested_party.file.name.split('/')[-1]
                    file_content = interested_party.file.read()
                    email.attach(file_name, file_content)
                    logger.info(f"Attached Interested Party document: {file_name}")
                    print(f"Attached file: {file_name}")
                except Exception as e:
                    logger.error(f"Error attaching Interested Party document: {str(e)}")
                    print(f"Error attaching Interested Party document: {str(e)}")
            
            try:
                connection = CertifiEmailBackend(
                    host=config('EMAIL_HOST'),
                    port=config('EMAIL_PORT'),
                    username=config('EMAIL_HOST_USER'),
                    password=config('EMAIL_HOST_PASSWORD'),
                    use_tls=True
                )
                print("Email connection established")
                
                email.connection = connection
                print("Sending email now...")
                email.send(fail_silently=False)
                print("Email sent successfully!")

                logger.info(f"Notification email sent to {recipient_email}")
            except Exception as e:
                print(f"ERROR sending email: {str(e)}")
                logger.error(f"Email sending error: {str(e)}")
                raise

        except Exception as e:
            logger.error(f"Failed to send notification email to {recipient_email}: {str(e)}")
            print(f"Failed to send notification email to {recipient_email}: {str(e)}")
            import traceback
            print(traceback.format_exc())  # Print full stack trace




    
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
            from_email=config("DEFAULT_FROM_EMAIL"),
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



import json

class InterestDraftAPIView(APIView):
    def post(self, request, *args, **kwargs):
        print("Request Data:", request.data)

        # Parse the 'data' JSON string if present
        raw_data = request.data.get('data')
        try:
            parsed_data = json.loads(raw_data[0] if isinstance(raw_data, list) else raw_data)
        except (json.JSONDecodeError, TypeError) as e:
            print("JSON decode error:", e)
            return Response({"message": "Invalid data format."}, status=status.HTTP_400_BAD_REQUEST)

        parsed_data['is_draft'] = True

        # Check if file is uploaded
        file_obj = request.FILES.get('file')

        # Serialize InterestedParty data
        serializer = InterestedPartySerializer(data=parsed_data)
        if serializer.is_valid():
            interest = serializer.save()

            # Attach file if present
            if file_obj:
                interest.file = file_obj
                interest.save()

            # Now get needs from parsed data
            needs_data = parsed_data.get('needs', [])
            print("Needs Data:", needs_data)

            if isinstance(needs_data, list):
                for item in needs_data:
                    if not item.get('needs') or not item.get('expectation'):
                        print("Skipping incomplete needs data:", item)
                        continue
                    try:
                        Needs.objects.create(
                            interested_party=interest,
                            needs=item.get('needs'),
                            expectation=item.get('expectation')
                        )
                    except Exception as e:
                        print(f"Error creating Needs: {e}")
                        return Response({"message": f"Error creating Needs: {e}"}, status=status.HTTP_400_BAD_REQUEST)

                print("Needs successfully saved.")
            else:
                print("Invalid needs_data format. Expected a list.")

            return Response({"message": "Interest saved as draft", "data": serializer.data},
                            status=status.HTTP_201_CREATED)
        else:
            print("Serializer Errors:", serializer.errors)
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

        # ✅ FIX: Properly parse boolean input from string or actual boolean
        raw_send_notification = request.data.get('send_notification', False)
        send_notification = str(raw_send_notification).lower() == 'true'

        logger.info(f"Request Data: {request.data}")
        logger.info(f"Raw send_notification value: {raw_send_notification}")
        logger.info(f"Evaluated send_notification: {send_notification}")

        needs_data = request.data.pop('needs', [])

        logger.info(f"Needs Data: {needs_data}")

        serializer = InterestedPartySerializer(interested_party, data=request.data, partial=True)

        if serializer.is_valid():
            instance = serializer.save(is_draft=False)

            # Update Needs with both needs and expectations fields
            if needs_data:
                logger.info(f"Updating Needs...")
                instance.needs.all().delete()
                needs_instances = []
                for need_item in needs_data:
                    needs_instances.append(
                        Needs(
                            interested_party=instance,
                            needs=need_item.get('needs', ''),
                            expectation=need_item.get('expectation', '')
                        )
                    )
                
                Needs.objects.bulk_create(needs_instances)
                logger.info("Needs updated")

            # Notifications & Emails
            if send_notification:
                company_users = Users.objects.filter(company=instance.company)
                
                notifications = [
                    NotificationInterest(
                        interest=instance,
                        title=f"Updated Interested Party: {instance.name}",
                        message=f"The interested party '{instance.name}' has been updated."
                    ) for user in company_users
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

            logger.info(f"Interested Party '{instance.name}' updated successfully")
            return Response(InterestedPartyGetSerializer(instance).data, status=status.HTTP_200_OK)

        logger.error(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _send_notification_email(self, interested_party, recipient):
        recipient_email = recipient.email
        if not recipient_email:
            logger.warning("Recipient email is missing.")
            return

        try:
            subject = f"Interested Party Updated: {interested_party.name}"

            # Get all needs objects for this interested party
            all_needs = interested_party.needs.all()

            context = {
                'recipient_name': recipient.first_name,
                'name': interested_party.name,
                'category': interested_party.category,
                'needs': [need.needs for need in all_needs if need.needs],
                'expectations': [need.expectation for need in all_needs if need.expectation],
                'special_requirements': interested_party.special_requirements,
                'legal_requirements': interested_party.legal_requirements,
                'custom_legal_requirements': interested_party.custom_legal_requirements,
                'user_first_name': interested_party.user.first_name if interested_party.user else '',
                'user_last_name': interested_party.user.last_name if interested_party.user else '',
            }

            html_message = render_to_string('qms/interested_party/intereste_party_edit.html', context)
            plain_message = strip_tags(html_message)

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=config("DEFAULT_FROM_EMAIL"),
                to=[recipient_email]
            )
            email.attach_alternative(html_message, "text/html")

            # Attach file if exists
            if interested_party.file:
                try:
                    file_name = interested_party.file.name.split('/')[-1]
                    file_content = interested_party.file.read()
                    email.attach(file_name, file_content)
                    logger.info(f"Attached Interested Party document: {file_name}")
                except Exception as e:
                    logger.error(f"Error attaching Interested Party document: {str(e)}")

            # Custom email backend (if you're using one)
            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )
            email.connection = connection
            email.send(fail_silently=False)
            logger.info(f"Notification email sent to {recipient_email}")

        except Exception as e:
            logger.error(f"Failed to send notification email to {recipient_email}: {str(e)}")



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
            from_email=config("DEFAULT_FROM_EMAIL"),
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
        print("Received Data:", request.data)  # Print all the received data
        try:
            company_id = request.data.get('company')
            
            # More flexible handling of send_notification flag
            send_notification_value = request.data.get('send_notification', 'false')
            send_notification = send_notification_value == 'true' or send_notification_value is True or send_notification_value == '1'
            print(f"Send notification value: {send_notification_value}, Interpreted as: {send_notification}")

            if not company_id:
                return Response(
                    {"error": "Company ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            company = Company.objects.get(id=company_id)
            print("Company retrieved:", company)

            # Extract legal_requirements IDs from request data
            legal_requirements_ids = []
            for key in request.data.keys():
                if key.startswith('legal_requirements[') and key.endswith(']'):
                    legal_requirements_ids.append(request.data.get(key))
            print("Legal Requirements IDs:", legal_requirements_ids)

            # Create a mutable copy of the data
            data = request.data.copy()

            # Remove the legal_requirements entries from the data before validation
            for key in list(data.keys()):
                if key.startswith('legal_requirements[') and key.endswith(']'):
                    data.pop(key)

            # Print the cleaned data that will be validated
            print("Data after cleaning legal_requirements:", data)

            serializer = ProcessSerializer(data=data)

            if serializer.is_valid():
                with transaction.atomic():
                    process = serializer.save()
                    logger.info(f"Process created: {process.name}")
                    print(f"Process created: {process.name} - ID: {process.id}")

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
                                print(f"Failed to add procedure {procedure_id}: {str(e)}")

                    process.save()

                    # Always send notifications to all users in the company
                    company_users = Users.objects.filter(company=company)
                    users_count = company_users.count()
                    print(f"Users to notify: {users_count}")
                    
                    if not company_users.exists():
                        print("No users found for this company - no notifications will be sent")
                    
                    email_success_count = 0
                    email_failure_count = 0
                    
                    notifications = []
                    for user in company_users:
                        # Create notification object
                        notifications.append(
                            NotificationProcess(
                                processes=process,
                                title=f"New process Party: {process.name}",
                                message=f"A new process party '{process.name}' has been added."
                            )
                        )
                        
                        # Try to send email to all users
                        if user.email:
                            try:
                                email_sent = self._send_notification_email(process, user)
                                if email_sent:
                                    email_success_count += 1
                                else:
                                    email_failure_count += 1
                            except Exception as e:
                                email_failure_count += 1
                                logger.error(f"Failed to send email to {user.email}: {str(e)}")
                                print(f"Failed to send email to {user.email}: {str(e)}")
                        else:
                            print(f"User ID {user.id} has no email address - skipping email")
                    
                    # Bulk create notifications
                    if notifications:
                        NotificationProcess.objects.bulk_create(notifications)
                        logger.info(f"Created {len(notifications)} notifications for process party {process.id}")
                        print(f"Created {len(notifications)} notifications for process party {process.id}")
                    
                    print(f"Email sending summary: {email_success_count} succeeded, {email_failure_count} failed")

                return Response(
                    {
                        "message": "Process Party created successfully",
                        "notification_sent": True,
                        "email_stats": {
                            "success": email_success_count,
                            "failure": email_failure_count
                        }
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                logger.warning(f"Validation error: {serializer.errors}")
                print(f"Validation error: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Company.DoesNotExist:
            print("Company not found.")
            return Response(
                {"error": "Company not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error creating process Party: {str(e)}")
            print(f"Error creating process Party: {str(e)}")
            return Response(
                {"error": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _send_notification_email(self, process, recipient):
        """
        Sends an HTML email with optional attachment using custom backend.
        """
        # Debug email configuration
        print("Email configuration:")
        print(f"Host: {config('EMAIL_HOST')}")
        print(f"Port: {config('EMAIL_PORT')}")
        print(f"User: {config('EMAIL_HOST_USER')}")
        print(f"Password set: {'Yes' if config('EMAIL_HOST_PASSWORD') else 'No'}")
        
        recipient_email = recipient.email
        if not recipient_email:
            print("Recipient email is missing.")
            logger.warning("Recipient email is missing.")
            return False

        try:
            print(f"Preparing to send process email to {recipient_email}")
            logger.info(f"Preparing to send process email to {recipient_email}")

            subject = f"New Process Created: {process.name}"

            context = {
                'recipient_name': recipient.first_name,
                'name': process.name,
                'number': process.no,
                'category': process.type,
                'legal_requirements': [req.title for req in process.legal_requirements.all()],
                'custom_legal_requirements': process.custom_legal_requirements,
                'user_first_name': process.user.first_name if process.user else '',
                'user_last_name': process.user.last_name if process.user else '',
            }

            html_message = render_to_string('qms/process/process_add.html', context)
            plain_message = strip_tags(html_message)

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=config("DEFAULT_FROM_EMAIL"),
                to=[recipient_email]
            )
            email.attach_alternative(html_message, "text/html")

            if process.file:
                try:
                    file_name = process.file.name.split('/')[-1]
                    file_content = process.file.read()
                    email.attach(file_name, file_content)
                    print(f"Attached process document: {file_name}")
                    logger.info(f"Attached process document: {file_name}")
                except Exception as e:
                    print(f"Error attaching process document: {str(e)}")
                    logger.error(f"Error attaching process document: {str(e)}")

            # Use custom backend
            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )
            email.connection = connection

            # Sending the email with specific error handling
            try:
                print("Sending the email...")
                email.send(fail_silently=False)
                
                print(f"Notification email sent to {recipient_email}")
                logger.info(f"Notification email sent to {recipient_email}")
                return True  # Indicate success
            except smtplib.SMTPException as smtp_e:
                # Handle specific SMTP errors
                print(f"SMTP Error sending to {recipient_email}: {str(smtp_e)}")
                logger.error(f"SMTP Error sending to {recipient_email}: {str(smtp_e)}")
                return False
            except Exception as e:
                print(f"Failed to send email to {recipient_email}: {str(e)}")
                logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
                return False

        except Exception as e:
            print(f"Failed to send email to {recipient_email}: {str(e)}")
            logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
            return False


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
    """
    Endpoint to handle updating of process and optionally send notifications.
    """
    def put(self, request, pk):
        try:
            process = get_object_or_404(Processes, pk=pk)
            
            print("Request data:", request.data)
            
            # For DRF's request.data, we need to handle lists differently
            # If legal_requirements is a list in the request, it will already be a list
            # If it's a single value, we need to put it in a list
            legal_requirements = request.data.get('legal_requirements', [])
            if legal_requirements and not isinstance(legal_requirements, list):
                legal_requirements = [legal_requirements]
                
            print("Legal requirements data:", legal_requirements)
            print("Custom legal requirements:", request.data.get('custom_legal_requirements', ''))
            
            # More flexible handling of send_notification flag
            send_notification_value = request.data.get('send_notification', 'false')
            if isinstance(send_notification_value, bool):
                send_notification = send_notification_value
            else:
                send_notification = str(send_notification_value).lower() == 'true' or send_notification_value == '1'
            print(f"Send notification value: {send_notification_value}, Interpreted as: {send_notification}")
            
            data = request.data.copy()
            
            has_custom_text = 'custom_legal_requirements' in request.data and request.data.get('custom_legal_requirements', '').strip()
            
            serializer = ProcessManySerializer(process, data=data, partial=True)
            if serializer.is_valid():
                with transaction.atomic():
                    instance = serializer.save(is_draft=False)
                    logger.info(f"Process updated: {instance.name}")
                    print(f"Process updated: {instance.name} - ID: {instance.id}")
                    
                    # Update and save send_notification flag
                    instance.send_notification = send_notification
                    
                    # Handle legal requirements
                    if has_custom_text:
                        instance.legal_requirements.clear()
                        print("N/A selected - cleared all legal requirements")
                    else:
                        # Convert to integers, handling strings and non-digit values
                        req_ids = []
                        for req_id in legal_requirements:
                            try:
                                if req_id and str(req_id).isdigit():
                                    req_ids.append(int(req_id))
                            except (ValueError, TypeError):
                                print(f"Skipping invalid legal requirement ID: {req_id}")
                                
                        instance.legal_requirements.set(req_ids)
                        print(f"Set legal requirements to: {req_ids}")
                    
                    instance.save()
                    
                    # Send notifications if enabled
                    email_success_count = 0
                    email_failure_count = 0
                    
                    if send_notification:
                        # Get company and users
                        company = instance.company
                        company_users = Users.objects.filter(company=company)
                        users_count = company_users.count()
                        print(f"Users to notify: {users_count}")
                        
                        if not company_users.exists():
                            print("No users found for this company - no notifications will be sent")
                        
                        notifications = []
                        for user in company_users:
                            # Create notification object
                            notifications.append(
                                NotificationProcess(
                                    processes=instance,
                                    title=f"Process Updated: {instance.name}",
                                    message=f"The process '{instance.name}' has been updated."
                                )
                            )
                            
                            # Try to send email to all users
                            if user.email:
                                try:
                                    email_sent = self._send_notification_email(instance, user)
                                    if email_sent:
                                        email_success_count += 1
                                    else:
                                        email_failure_count += 1
                                except Exception as e:
                                    email_failure_count += 1
                                    logger.error(f"Failed to send email to {user.email}: {str(e)}")
                                    print(f"Failed to send email to {user.email}: {str(e)}")
                            else:
                                print(f"User ID {user.id} has no email address - skipping email")
                        
                        # Bulk create notifications
                        if notifications:
                            NotificationProcess.objects.bulk_create(notifications)
                            logger.info(f"Created {len(notifications)} notifications for process update {instance.id}")
                            print(f"Created {len(notifications)} notifications for process update {instance.id}")
                        
                        print(f"Email sending summary: {email_success_count} succeeded, {email_failure_count} failed")
                
                return Response(
                    {
                        "message": "Process updated successfully",
                        "notification_sent": send_notification,
                        "email_stats": {
                            "success": email_success_count if send_notification else 0,
                            "failure": email_failure_count if send_notification else 0
                        },
                        "data": ProcessManySerializer(instance).data
                    },
                    status=status.HTTP_200_OK
                )
                
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error updating process: {str(e)}")
            print(f"Error updating process: {str(e)}")
            return Response(
                {"error": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _send_notification_email(self, process, recipient):
        """
        Sends an HTML email with optional attachment using custom backend.
        """
        # Debug email configuration
        print("Email configuration:")
        print(f"Host: {config('EMAIL_HOST')}")
        print(f"Port: {config('EMAIL_PORT')}")
        print(f"User: {config('EMAIL_HOST_USER')}")
        print(f"Password set: {'Yes' if config('EMAIL_HOST_PASSWORD') else 'No'}")
        
        recipient_email = recipient.email
        if not recipient_email:
            print("Recipient email is missing.")
            logger.warning("Recipient email is missing.")
            return False

        try:
            print(f"Preparing to send process update email to {recipient_email}")
            logger.info(f"Preparing to send process update email to {recipient_email}")

            subject = f"Process Updated: {process.name}"

            context = {
                'recipient_name': recipient.first_name,
                'name': process.name,
                'number': process.no,
                'category': process.type,
                'legal_requirements': [req.title for req in process.legal_requirements.all()],
                'custom_legal_requirements': process.custom_legal_requirements,
                'user_first_name': process.user.first_name if process.user else '',
                'user_last_name': process.user.last_name if process.user else '',
                'is_update': True, 
            }

            html_message = render_to_string('qms/process/process_edit.html', context)
            plain_message = strip_tags(html_message)

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=config("DEFAULT_FROM_EMAIL"),
                to=[recipient_email]
            )
            email.attach_alternative(html_message, "text/html")

            if process.file:
                try:
                    file_name = process.file.name.split('/')[-1]
                    file_content = process.file.read()
                    email.attach(file_name, file_content)
                    print(f"Attached process document: {file_name}")
                    logger.info(f"Attached process document: {file_name}")
                except Exception as e:
                    print(f"Error attaching process document: {str(e)}")
                    logger.error(f"Error attaching process document: {str(e)}")

            # Use custom backend
            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )
            email.connection = connection

            # Sending the email with specific error handling
            try:
                print("Sending the email...")
                email.send(fail_silently=False)
                
                print(f"Update notification email sent to {recipient_email}")
                logger.info(f"Update notification email sent to {recipient_email}")
                return True  # Indicate success
            except smtplib.SMTPException as smtp_e:
                # Handle specific SMTP errors
                print(f"SMTP Error sending to {recipient_email}: {str(smtp_e)}")
                logger.error(f"SMTP Error sending to {recipient_email}: {str(smtp_e)}")
                return False
            except Exception as e:
                print(f"Failed to send email to {recipient_email}: {str(e)}")
                logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
                return False

        except Exception as e:
            print(f"Failed to send email to {recipient_email}: {str(e)}")
            logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
            return False
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
        subject = f"New Compliance Created: {compliance.compliance_name}"
        recipient_email = recipient.email

        print(f"Preparing to send email to: {recipient_email}")

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

        try:
            html_message = render_to_string('qms/compliance/compliance_add_template.html', context)
            plain_message = strip_tags(html_message)

            # Create email
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=config("DEFAULT_FROM_EMAIL"),
                to=[recipient_email]
            )
            email.attach_alternative(html_message, "text/html")

            # Attach compliance document if available
            if compliance.attach_document:
                try:
                    file_name = compliance.attach_document.name.rsplit('/', 1)[-1]
                    file_content = compliance.attach_document.read()
                    email.attach(file_name, file_content)
                    print(f"Attached compliance document: {file_name}")
                except Exception as attachment_error:
                    print(f"Error attaching compliance file: {str(attachment_error)}")

            # Use custom secure backend
            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )

            email.connection = connection
            email.send(fail_silently=False)

            print(f"Email successfully sent to {recipient_email}")

        except Exception as e:
            print(f"Error sending email to {recipient_email}: {e}")





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
    
 

import mimetypes
import traceback
class EditsCompliance(APIView):
    def put(self, request, pk):
        print("Received data:", request.data)
        compliance = get_object_or_404(Compliances, pk=pk)
        mutable_data = request.data.copy()

        # Handle document attachment
        if 'attach_document' in mutable_data and not request.FILES.get('attach_document'):
            print("Removing attach_document from request because it's not a file")
            mutable_data.pop('attach_document')
        
        serializer = ComplianceSerializer(compliance, data=mutable_data, partial=True)

        if serializer.is_valid():
            instance = serializer.save(is_draft=False)

            if instance.send_notification:
                company = instance.company
                company_users = Users.objects.filter(company=company)

                # Create notifications
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

                # Send email notifications
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
        recipient_email = recipient.email

        print(f"Preparing to send email to: {recipient_email}")

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

        try:
            html_message = render_to_string('qms/compliance/compliance_edit_template.html', context)
            plain_message = strip_tags(html_message)

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=config("DEFAULT_FROM_EMAIL"),
                to=[recipient_email]
            )
            email.attach_alternative(html_message, "text/html")

         
            if compliance.attach_document:
                try:
           
                    compliance.attach_document.seek(0)
                    
           
                    file_name = compliance.attach_document.name.rsplit('/', 1)[-1]
                    
                 
                    file_content = compliance.attach_document.read()
                    
                
                    content_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
                    
        
                    email.attach(file_name, file_content, content_type)
                    
                    print(f"Attached compliance document: {file_name} with content type {content_type}")
                except Exception as attachment_error:
                    print(f"Error attaching compliance file: {str(attachment_error)}")
                    traceback.print_exc()   

            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )

            email.connection = connection
            email.send(fail_silently=False)

            print(f"Email successfully sent to {recipient_email}")

        except Exception as e:
            print(f"Error sending email to {recipient_email}: {e}")
            traceback.print_exc() 


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
                return Response({"error": "Company ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            company = Company.objects.get(id=company_id)
            serializer = LegalSerializer(data=request.data)

            if serializer.is_valid():
                with transaction.atomic():
                    legal = serializer.save()
                    logger.info(f"Legal created: {legal.legal_name}")

                    legal.send_notification = send_notification
                    legal.save()

                    if send_notification:
                        company_users = Users.objects.filter(company=company)

                        notifications = [
                            NotificationLegal(
                                legal=legal,
                                title=f"New Legal: {legal.legal_name}",
                                message=f"A new legal requirement '{legal.legal_name}' has been added."
                            )
                            for user in company_users
                        ]

                        if notifications:
                            NotificationLegal.objects.bulk_create(notifications)
                            logger.info(f"Created {len(notifications)} notifications for legal {legal.id}")

                        for user in company_users:
                            if user.email:
                                self._send_email_async(legal, user)

                return Response({
                    "message": "Legal requirement created successfully",
                    "notification_sent": send_notification
                }, status=status.HTTP_201_CREATED)

            else:
                logger.warning(f"Validation error: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Error creating legal requirement: {str(e)}")
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _send_email_async(self, legal, recipient):
        threading.Thread(target=self._send_notification_email, args=(legal, recipient)).start()

    def _send_notification_email(self, legal, recipient):
        subject = f"New Legal Requirement: {legal.legal_name}"
        recipient_email = recipient.email

        context = {
            'legal_name': legal.legal_name,
            'legal_no': legal.legal_no,
            'document_type': legal.document_type,
            'rivision': legal.rivision,
            'date': legal.date,
            'related_record_format': legal.related_record_format,
            'created_by': legal.user,
        }

        try:
            html_message = render_to_string('qms/legal/legal_add_template.html', context)
            plain_message = strip_tags(html_message)

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=config("DEFAULT_FROM_EMAIL"),
                to=[recipient_email]
            )
            email.attach_alternative(html_message, "text/html")

            if legal.attach_document:
                try:
                    file_name = legal.attach_document.name.rsplit('/', 1)[-1]
                    file_content = legal.attach_document.read()
                    email.attach(file_name, file_content)
                    print(f"Attached legal document: {file_name}")
                except Exception as e:
                    print(f"Error attaching document: {e}")

            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )

            email.connection = connection
            email.send(fail_silently=False)
            print(f"Email sent to {recipient_email}")

        except Exception as e:
            print(f"Error sending email to {recipient_email}: {e}")



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
        subject = f"Legal Updated: {legal.legal_name}"
        recipient_email = recipient.email

        context = {
            'legal_name': legal.legal_name,
            'document_type': legal.document_type,
            'legal_no': legal.legal_no,
            'rivision': legal.rivision,
            'date': legal.date,
            'related_record_format': legal.related_record_format,
            'created_by': legal.user,
        }

        try:
            html_message = render_to_string('qms/legal/legal_edit_template.html', context)
            plain_message = strip_tags(html_message)

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=config("DEFAULT_FROM_EMAIL"),
                to=[recipient_email]
            )
            email.attach_alternative(html_message, "text/html")

            if legal.attach_document:
                try:
                    legal.attach_document.seek(0)
                    file_name = legal.attach_document.name.rsplit('/', 1)[-1]
                    file_content = legal.attach_document.read()
                    content_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
                    email.attach(file_name, file_content, content_type)
                    print(f"Attached legal document: {file_name}")
                except Exception as attachment_error:
                    print(f"Error attaching legal file: {str(attachment_error)}")
                    traceback.print_exc()

            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )

            email.connection = connection
            email.send(fail_silently=False)
            print(f"Email successfully sent to {recipient_email}")

        except Exception as e:
            print(f"Error sending email to {recipient_email}: {e}")
            traceback.print_exc()

        
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
                    logger.info(f"Evaluation created successfully with ID: {evaluation.id}")

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
                        {"message": "Evaluation created successfully", "id": evaluation.id},
                        status=status.HTTP_201_CREATED
                    )

            except Exception as e:
                logger.error(f"Error during evaluation creation: {str(e)}")
                return Response(
                    {"error": "An unexpected error occurred."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        logger.error(f"Evaluation creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_email_notification(self, evaluation, recipient, action_type):
        recipient_email = recipient.email if recipient else None

        if recipient_email:
            try:
                if action_type == "review":
                    subject = f"Evaluation Ready for Review: {evaluation.title}"

                    context = {
                        'recipient_name': recipient.first_name,
                        'title': evaluation.title,
                        'document_number': evaluation.no or 'N/A',
                        'review_frequency_year': evaluation.review_frequency_year or 0,
                        'review_frequency_month': evaluation.review_frequency_month or 0,
                        'document_type': evaluation.document_type,
                        'section_number': evaluation.no,
                        'rivision': getattr(evaluation, 'rivision', ''),
                        'written_by': evaluation.written_by,
                        'checked_by': evaluation.checked_by,
                        'approved_by': evaluation.approved_by,
                        'date': evaluation.date,
                    }

                    html_message = render_to_string('qms/evaluation/evaluation_to_checked_by.html', context)
                    plain_message = strip_tags(html_message)

                    # Create email message
                    email = EmailMultiAlternatives(
                        subject=subject,
                        body=plain_message,
                        from_email=config("DEFAULT_FROM_EMAIL"),
                        to=[recipient_email]
                    )
                    email.attach_alternative(html_message, "text/html")

                    # Attach document if available
                    if evaluation.upload_attachment:
                        try:
                            file_name = evaluation.upload_attachment.name.rsplit('/', 1)[-1]
                            file_content = evaluation.upload_attachment.read()
                            email.attach(file_name, file_content)
                            logger.info(f"Attached evaluation document {file_name} to email")
                        except Exception as attachment_error:
                            logger.error(f"Error attaching evaluation file: {str(attachment_error)}")

                    # Optional: Use custom backend
                    connection = CertifiEmailBackend(
                        host=config('EMAIL_HOST'),
                        port=config('EMAIL_PORT'),
                        username=config('EMAIL_HOST_USER'),
                        password=config('EMAIL_HOST_PASSWORD'),
                        use_tls=True
                    )

                    email.connection = connection
                    email.send(fail_silently=False)

                    logger.info(f"Email with attachment successfully sent to {recipient_email} for action: {action_type}")
                else:
                    logger.warning("Unknown action type provided for email.")
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
        print("Request data:", request.data)
        try:
            with transaction.atomic():
                evaluation = Evaluation.objects.get(pk=pk)

                serializer = EvaluationUpdateSerializer(evaluation, data=request.data, partial=True)

                if serializer.is_valid():
                    updated_evaluation = serializer.save()

                    updated_evaluation.written_at = now()
                    updated_evaluation.is_draft = False
                    updated_evaluation.status = 'Pending for Review/Checking'

                    updated_evaluation.send_notification_to_checked_by = parse_bool(request.data.get('send_system_checked'))
                    updated_evaluation.send_email_to_checked_by = parse_bool(request.data.get('send_email_checked'))

                    updated_evaluation.save()

                    # Handle notification/email to checked_by
                    if updated_evaluation.checked_by:
                        if updated_evaluation.send_notification_to_checked_by:
                            try:
                                NotificationEvaluations.objects.create(
                                    user=updated_evaluation.checked_by,
                                    evaluation=updated_evaluation,
                                    title="Evaluation Updated - Review Required",
                                    message=f"Evaluation '{updated_evaluation.title}' has been updated and requires your review."
                                )
                            except Exception as e:
                                logger.error(f"Notification error for checked_by: {str(e)}")

                        if updated_evaluation.send_email_to_checked_by and updated_evaluation.checked_by.email:
                            self.send_email_notification(updated_evaluation, updated_evaluation.checked_by, "review")

                    return Response({"message": "Evaluation updated successfully"}, status=status.HTTP_200_OK)

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Evaluation.DoesNotExist:
            return Response({"error": "Evaluation not found"}, status=status.HTTP_404_NOT_FOUND)

    def send_email_notification(self, evaluation, recipient, action_type):
        recipient_email = recipient.email if recipient else None

        if recipient_email:
            try:
                if action_type == "review":
                    subject = f"Evaluation Ready for Review: {evaluation.title}"

                    # Prepare email content using a custom HTML template
                    context = {
                        'recipient_name': recipient.first_name,
                        'title': evaluation.title,
                        'document_number': evaluation.no or 'N/A',
                        'review_frequency_year': evaluation.review_frequency_year or 0,
                        'review_frequency_month': evaluation.review_frequency_month or 0,
                        'document_type': evaluation.document_type,
                        'section_number': evaluation.no,
                        'rivision': getattr(evaluation, 'rivision', ''),
                        'written_by': evaluation.written_by,
                        'checked_by': evaluation.checked_by,
                        'approved_by': evaluation.approved_by,
                        'date': evaluation.date,
                    }

                    html_message = render_to_string('evaluation/evaluation_update_to_checked_by.html', context)
                    plain_message = strip_tags(html_message)

                    email = EmailMultiAlternatives(
                        subject=subject,
                        body=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[recipient_email]
                    )
                    email.attach_alternative(html_message, "text/html")

                    # Attach the evaluation file if available
                    if evaluation.upload_attachment:
                        try:
                            file_name = evaluation.upload_attachment.name.rsplit('/', 1)[-1]
                            file_content = evaluation.upload_attachment.read()
                            email.attach(file_name, file_content)
                            logger.info(f"Attached evaluation file {file_name} to email")
                        except Exception as attachment_error:
                            logger.error(f"Error attaching file: {str(attachment_error)}")

                    # Use the CertifiEmailBackend for sending email
                    connection = CertifiEmailBackend(
                        host=config('EMAIL_HOST'),
                        port=config('EMAIL_PORT'),
                        username=config('EMAIL_HOST_USER'),
                        password=config('EMAIL_HOST_PASSWORD'),
                        use_tls=True
                    )

                    email.connection = connection
                    email.send(fail_silently=False)

                    logger.info(f"Email with attachment successfully sent to {recipient_email} for action: {action_type}")
                else:
                    logger.warning("Unknown action type provided for email.")
            except Exception as e:
                logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        else:
            logger.warning("Recipient email is None. Skipping email send.")



class SubmitEvaluationCorrectionView(APIView):
    def post(self, request):
        try:
            evaluation_id = request.data.get('evaluation_id')
            correction_text = request.data.get('correction')
            from_user_id = request.data.get('from_user')

            if not all([evaluation_id, correction_text, from_user_id]):
                return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                evaluation = Evaluation.objects.get(id=evaluation_id)
                print(f"Evaluation found: {evaluation.title}")
            except Evaluation.DoesNotExist:
                print(f"Evaluation with ID {evaluation_id} not found.")
                return Response({'error': 'Evaluation not found'}, status=status.HTTP_404_NOT_FOUND)

            try:
                from_user = Users.objects.get(id=from_user_id)
                print(f"User found: {from_user.first_name}")
            except Users.DoesNotExist:
                print(f"User with ID {from_user_id} not found.")
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Determine the recipient based on user role
            if from_user == evaluation.checked_by:
                to_user = evaluation.written_by
            elif from_user == evaluation.approved_by:
                to_user = evaluation.checked_by
            else:
                return Response({'error': 'Invalid user role for correction'}, status=status.HTTP_400_BAD_REQUEST)

            # Creating correction record
            correction = CorrectionEvaluation.objects.create(
                evaluation=evaluation,
                to_user=to_user,
                from_user=from_user,
                correction=correction_text
            )
            print(f"Correction created successfully for {correction.id}.")

            # Update evaluation status
            evaluation.status = 'Correction Requested'
            evaluation.save()
            print(f"Evaluation status updated to 'Correction Requested'.")

            # Create and send notification and email
            self.create_correction_notification(correction)
            self.send_correction_email_notification(correction)

            serializer = CorrectionEvaluationSerializer(correction)
            return Response(
                {'message': 'Correction submitted successfully', 'correction': serializer.data},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            print(f"Unexpected error occurred: {str(e)}")
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
                    f"to {to_user.first_name} for Evaluation: {evaluation.title}"
                )
                notification = NotificationEvaluations.objects.create(
                    user=to_user,
                    evaluation=evaluation,
                    message=message
                )
                print(f"Notification created successfully: {notification.id}")
            else:
                print("Notification not sent due to permission flags or invalid role flow.")
        except Exception as e:
            print(f"Failed to create correction notification: {str(e)}")

    def send_correction_email_notification(self, correction):
        try:
            evaluation = correction.evaluation
            from_user = correction.from_user
            to_user = correction.to_user
            recipient_email = to_user.email if to_user else None

            if from_user == evaluation.checked_by and to_user == evaluation.written_by:
                template_name = 'qms/evaluation/evaluation_correction_to_writer.html'
                subject = f"Correction Requested on '{evaluation.title}'"
                should_send = True
            elif from_user == evaluation.approved_by and to_user == evaluation.checked_by:
                template_name = 'qms/evaluation/evaluation_correction_to_checker.html'
                subject = f"Correction Requested on '{evaluation.title}'"
                should_send = evaluation.send_email_to_checked_by
            else:
                return  # Not a valid correction flow

            if not recipient_email or not should_send:
                return

            context = {
                'recipient_name': to_user.first_name,
                'title': evaluation.title,
                'document_number': evaluation.no or 'N/A',
                'review_frequency_year': evaluation.review_frequency_year or 0,
                'review_frequency_month': evaluation.review_frequency_month or 0,
                'document_type': evaluation.document_type,
                'section_number': evaluation.no,
                'rivision': getattr(evaluation, 'rivision', ''),
                'written_by': evaluation.written_by,
                'checked_by': evaluation.checked_by,
                'approved_by': evaluation.approved_by,
                'date': evaluation.date,
            }

            html_message = render_to_string(template_name, context)
            plain_message = strip_tags(html_message)

            from django.core.mail import EmailMultiAlternatives

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=config("DEFAULT_FROM_EMAIL"),
                to=[recipient_email]
            )
            email.attach_alternative(html_message, "text/html")

            if evaluation.upload_attachment:
                try:
                    file_name = evaluation.upload_attachment.name.rsplit('/', 1)[-1]
                    file_content = evaluation.upload_attachment.read()
                    email.attach(file_name, file_content)
                    print(f"Attached evaluation file {file_name} to correction email.")
                except Exception as attachment_error:
                    print(f"Error attaching file: {str(attachment_error)}")

            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )
            email.connection = connection
            email.send(fail_silently=False)

            print(f"Correction email sent to {recipient_email}.")

        except Exception as e:
            print(f"Error sending correction email: {str(e)}")




            
class CorrectionEvaluationList(generics.ListAPIView):
    serializer_class = CorrectionEvaluationSerializer

    def get_queryset(self):
        evaluation_id = self.kwargs.get("evaluation_id")
        return CorrectionEvaluation.objects.filter(evaluation_id=evaluation_id)
    
    
class EvaluationReviewView(APIView):
    def post(self, request):
        logger.info("Received request for evaluation review process.")

        try:
            evaluation_id = request.data.get('evaluation_id')
            current_user_id = request.data.get('current_user_id')

            if not all([evaluation_id, current_user_id]):
                return Response({'error': 'Missing required parameters'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                evaluation = Evaluation.objects.get(id=evaluation_id)
                current_user = Users.objects.get(id=current_user_id)
            except (Evaluation.DoesNotExist, Users.DoesNotExist):
                return Response({'error': 'Invalid evaluation or user'}, status=status.HTTP_404_NOT_FOUND)

            with transaction.atomic():
                if current_user == evaluation.written_by and not evaluation.written_at:
                    evaluation.written_at = now()
                    evaluation.save()

                current_status = evaluation.status

                # Case 1: Checked_by reviews
                if current_status == 'Pending for Review/Checking' and current_user == evaluation.checked_by:
                    evaluation.status = 'Reviewed,Pending for Approval'
                    evaluation.checked_at = now()
                    evaluation.save()

                    if evaluation.send_notification_to_approved_by:
                        NotificationEvaluations.objects.create(
                            user=evaluation.approved_by,
                            evaluation=evaluation,
                            message=f"Evaluation '{evaluation.title}' is ready for approval."
                        )

                    if evaluation.send_email_to_approved_by:
                        self.send_email_notification(
                            evaluation=evaluation,
                            recipients=[evaluation.approved_by],
                            action_type="review"
                        )

                # Case 2: Approved_by approves
                elif current_status == 'Reviewed,Pending for Approval' and current_user == evaluation.approved_by:
                    evaluation.status = 'Pending for Publish'
                    evaluation.approved_at = now()
                    evaluation.save()

                    for user in [evaluation.written_by, evaluation.checked_by, evaluation.approved_by]:
                        if user:
                            NotificationEvaluations.objects.create(
                                user=user,
                                evaluation=evaluation,
                                message=f"Evaluation '{evaluation.title}' has been approved and is pending for publish."
                            )

                    self.send_email_notification(
                        evaluation=evaluation,
                        recipients=[u for u in [evaluation.written_by, evaluation.checked_by, evaluation.approved_by] if u],
                        action_type="approved"
                    )

                # Case 3: Correction requested
                elif current_status == 'Correction Requested' and current_user == evaluation.written_by:
                    evaluation.status = 'Pending for Review/Checking'
                    evaluation.save()

                else:
                    return Response({
                        'message': 'No action taken. User not authorized for current evaluation status.'
                    }, status=status.HTTP_200_OK)

            return Response({
                'status': 'success',
                'message': 'Evaluation processed successfully',
                'evaluation_status': evaluation.status
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in evaluation review process: {str(e)}")
            return Response({
                'error': 'An unexpected error occurred',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def send_email_notification(self, evaluation, recipients, action_type):
        from decouple import config
        from django.core.mail import EmailMultiAlternatives

        for recipient in recipients:
            recipient_email = recipient.email if recipient else None

            if recipient_email:
                try:
                    if action_type == "review":
                        subject = f"Evaluation Submitted for Approval: {evaluation.title}"
                        context = {
                            'recipient_name': recipient.first_name,
                            'title': evaluation.title,
                            'document_number': evaluation.no or 'N/A',
                            'review_frequency_year': evaluation.review_frequency_year or 0,
                            'review_frequency_month': evaluation.review_frequency_month or 0,
                            'document_type': evaluation.document_type,
                            'section_number': evaluation.no,
                            'rivision': evaluation.rivision,
                            'written_by': evaluation.written_by,
                            'checked_by': evaluation.checked_by,
                            'approved_by': evaluation.approved_by,
                            'date': evaluation.date,
                            'document_url': evaluation.upload_attachment.url if evaluation.upload_attachment else None,
                            'document_name': evaluation.upload_attachment.name.rsplit('/', 1)[-1] if evaluation.upload_attachment else None,
                        }
                        html_message = render_to_string('evaluation/evaluation_to_approved_by.html', context)
                        plain_message = strip_tags(html_message)

                    elif action_type == "approved":
                        subject = f"Evaluation Approved: {evaluation.title}"
                        context = {
                            'recipient_name': recipient.first_name,
                            'title': evaluation.title,
                            'document_number': evaluation.no or 'N/A',
                            'review_frequency_year': evaluation.review_frequency_year or 0,
                            'review_frequency_month': evaluation.review_frequency_month or 0,
                            'document_type': evaluation.document_type,
                            'section_number': evaluation.no,
                            'rivision': evaluation.rivision,
                            'written_by': evaluation.written_by,
                            'checked_by': evaluation.checked_by,
                            'approved_by': evaluation.approved_by,
                            'date': evaluation.date,
                            'document_url': evaluation.upload_attachment.url if evaluation.upload_attachment else None,
                            'document_name': evaluation.upload_attachment.name.rsplit('/', 1)[-1] if evaluation.upload_attachment else None,
                        }
                        html_message = render_to_string('evaluation/evaluation_publish.html', context)
                        plain_message = strip_tags(html_message)

                    else:
                        logger.warning(f"Unknown action type '{action_type}' for email notification.")
                        continue

                    email = EmailMultiAlternatives(
                        subject=subject,
                        body=plain_message,
                        from_email=config('DEFAULT_FROM_EMAIL'),
                        to=[recipient_email]
                    )
                    email.attach_alternative(html_message, "text/html")

                    connection = CertifiEmailBackend(
                        host=config('EMAIL_HOST'),
                        port=config('EMAIL_PORT'),
                        username=config('EMAIL_HOST_USER'),
                        password=config('EMAIL_HOST_PASSWORD'),
                        use_tls=True
                    )
                    email.connection = connection
                    email.send(fail_silently=False)

                    logger.info(f"Email successfully sent to {recipient_email} for action: {action_type}")

                except Exception as e:
                    logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
            else:
                logger.warning("Recipient email is None. Skipping email send.")




class EvaluationPublishNotificationView(APIView):
    """
    Endpoint to handle publishing an evaluation and sending notifications to company users.
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
                            title=f"Evaluation Published: {evaluation.title}",
                            message=f"A new evaluation '{evaluation.title}' has been published."
                        )
                        for user in company_users
                    ]

                    if notifications:
                        NotificationEvaluations.objects.bulk_create(notifications)
                        logger.info(f"Created {len(notifications)} notifications for evaluation {evaluation_id}")

                    for user in company_users:
                        if user.email:
                            try:
                                self._send_publish_email(evaluation, user)
                            except Exception as e:
                                logger.error(f"Failed to send email to {user.email}: {str(e)}")

            return Response(
                {
                    "message": "Evaluation published successfully",
                    "notification_sent": send_notification,
                    "publisher_set": published_by is not None
                },
                status=status.HTTP_200_OK
            )

        except Evaluation.DoesNotExist:
            return Response({"error": "Evaluation not found"}, status=status.HTTP_404_NOT_FOUND)
        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in publish notification: {str(e)}")
            return Response({"error": f"Failed to publish evaluation: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _send_publish_email(self, evaluation, recipient):
     
        publisher_name = "N/A"
        if evaluation.published_user:
            publisher_name = f"{evaluation.published_user.first_name} {evaluation.published_user.last_name}"
        elif evaluation.approved_by:
            publisher_name = f"{evaluation.approved_by.first_name} {evaluation.approved_by.last_name}"

        subject = f"New Evaluation Published: {evaluation.title}"

        context = {
                            'recipient_name': recipient.first_name,
                            'title': evaluation.title,
                            'document_number': evaluation.no or 'N/A',
                            'review_frequency_year': evaluation.review_frequency_year or 0,
                            'review_frequency_month': evaluation.review_frequency_month or 0,
                            'document_type': evaluation.document_type,
                            'section_number': evaluation.no,
                            'rivision': evaluation.rivision,
                            'written_by': evaluation.written_by,
                            'checked_by': evaluation.checked_by,
                            'approved_by': evaluation.approved_by,
                            'date': evaluation.date,
                            'document_url': evaluation.upload_attachment.url if evaluation.upload_attachment else None,
                            'document_name': evaluation.upload_attachment.name.rsplit('/', 1)[-1] if evaluation.upload_attachment else None,
                        }

        html_message = render_to_string('evaluations/evaluation_published_notification.html', context)
        plain_message = strip_tags(html_message)

        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=config("DEFAULT_FROM_EMAIL"),
            to=[recipient.email]
        )
        email.attach_alternative(html_message, "text/html")

        if evaluation.upload_attachment:
            try:
                file_name = evaluation.upload_attachment.name.rsplit('/', 1)[-1]
                file_content = evaluation.upload_attachment.read()
                email.attach(file_name, file_content)
                logger.info(f"Attached evaluation file {file_name} to email")
            except Exception as attachment_error:
                logger.error(f"Error attaching file: {str(attachment_error)}")

        try:
            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )
            email.connection = connection
            email.send(fail_silently=False)
            logger.info(f"HTML Email sent to {recipient.email}")
        except Exception as e:
            logger.error(f"Failed to send email to {recipient.email}: {str(e)}")

        

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
    
    
import threading
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from decouple import config
import logging

from .models import ManagementChanges, NotificationChanges, Company, Users

logger = logging.getLogger(__name__)

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
                            for user in company_users
                        ]

                        if notifications:
                            NotificationChanges.objects.bulk_create(notifications)
                            logger.info(f"Created {len(notifications)} notifications for change ID {changes.id}")

                        # Send email asynchronously to each user
                        for user in company_users:
                            if user.email:
                                self._send_email_async(changes, user)

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
    
    def _send_email_async(self, changes, recipient):
        """
        Sends email in a separate thread to avoid blocking the response.
        """
        threading.Thread(target=self._send_notification_email, args=(changes, recipient)).start()

    def _send_notification_email(self, changes, recipient):
        """
        Helper method to send email notifications about a new Management Change using HTML template.
        """
        subject = f"New Management Change: {changes.moc_title}"
        recipient_email = recipient.email

        print(f"Preparing to send email to: {recipient_email}")

        context = {
            'recipient_name': recipient.first_name,
            'moc_title': changes.moc_title,
            'moc_type': changes.moc_type,
            'moc_no': changes.moc_no,
            'rivision': changes.rivision,
            'date': changes.date,
            'related_record_format': changes.related_record_format,
            'resources_required': changes.resources_required,
            'impact_on_process': changes.impact_on_process,
            'purpose_of_chnage': changes.purpose_of_chnage,
            'potential_cosequences': changes.potential_cosequences,
            'moc_remarks': changes.moc_remarks,
            'created_by': changes.user,
        }
      

        try:
            html_message = render_to_string('qms/changes/changes_add_template.html', context)
            plain_message = strip_tags(html_message)

            # Create email
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=config("DEFAULT_FROM_EMAIL"),
                to=[recipient_email]
            )
            email.attach_alternative(html_message, "text/html")

            # Attach document if available
            if hasattr(changes, 'attach_document') and changes.attach_document:
                try:
                    file_name = changes.attach_document.name.rsplit('/', 1)[-1]
                    file_content = changes.attach_document.read()
                    email.attach(file_name, file_content)
                    print(f"Attached changes document: {file_name}")
                except Exception as attachment_error:
                    print(f"Error attaching changes file: {str(attachment_error)}")

            # Use custom secure backend
            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )

            email.connection = connection
            email.send(fail_silently=False)

            print(f"Email successfully sent to {recipient_email}")
            logger.info(f"Email sent to {recipient_email}")

        except Exception as e:
            print(f"Error sending email to {recipient_email}: {e}")
            logger.error(f"Failed to send email to {recipient_email}: {str(e)}")


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
    
    
import mimetypes
import traceback
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from decouple import config

class EditsChanges(APIView):
    def put(self, request, pk):
        print("Received data:", request.data)

        change_instance = get_object_or_404(ManagementChanges, pk=pk)
        mutable_data = request.data.copy()

        if 'attach_document' in mutable_data and not request.FILES.get('attach_document'):
            print("Removing attach_document from request because it's not a file")
            mutable_data.pop('attach_document')

        serializer = ChangesSerializer(change_instance, data=mutable_data, partial=True)

        if serializer.is_valid():
            instance = serializer.save(is_draft=False)

            file_obj = request.FILES.get('attach_document')
            if file_obj:
                instance.attach_document = file_obj
                instance.save()

            if instance.send_notification and instance.company:
                company_users = Users.objects.filter(company=instance.company)

                notifications = [
                    NotificationChanges(
                        changes=instance,
                        title=f"Updated MOC: {instance.moc_title}",
                        message=f"The MOC '{instance.moc_title}' has been updated."
                    ) for user in company_users
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
                            traceback.print_exc()

            return Response(ChangesSerializer(instance).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _send_notification_email(self, changes, recipient):
        subject = f"MOC Updated: {changes.moc_title}"
        context = {
            'moc_title': changes.moc_title,
            'moc_type': changes.moc_type,
            'moc_no': changes.moc_no,
            'rivision': changes.rivision,
            'date': changes.date,
            'related_record_format': changes.related_record_format,
            'resources_required': changes.resources_required,
            'impact_on_process': changes.impact_on_process,
            'purpose_of_chnage': changes.purpose_of_chnage,
            'potential_cosequences': changes.potential_cosequences,
            'moc_remarks': changes.moc_remarks,
            'created_by': changes.user,
            'recipient': recipient,
        }

        try:
            html_message = render_to_string('qms/changes/changes_edit_template.html', context)
            plain_message = strip_tags(html_message)

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=config("DEFAULT_FROM_EMAIL"),
                to=[recipient.email]
            )
            email.attach_alternative(html_message, "text/html")

            # Attach file if available
            if changes.attach_document:
                try:
                    changes.attach_document.seek(0)
                    file_name = changes.attach_document.name.rsplit('/', 1)[-1]
                    file_content = changes.attach_document.read()
                    content_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
                    email.attach(file_name, file_content, content_type)
                    print(f"Attached MOC document: {file_name} with content type {content_type}")
                except Exception as e:
                    print(f"Error attaching MOC file: {str(e)}")
                    traceback.print_exc()

            # Send using custom backend
            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )
            email.connection = connection
            email.send(fail_silently=False)
            print(f"Email successfully sent to {recipient.email}")

        except Exception as e:
            print(f"Error sending email to {recipient.email}: {e}")
            traceback.print_exc()




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

    def send_email_notification(self, sustainability, recipient, action_type):
        recipient_email = recipient.email if recipient else None

        if recipient_email:
            try:
                if action_type == "review":
                    subject = f"Sustainability Document Ready for Review: {sustainability.title}"

                    context = {
                        'recipient_name': recipient.first_name,
                        'title': sustainability.title,
                        'document_number': sustainability.no or 'N/A',
                        'review_frequency_year': sustainability.review_frequency_year or 0,
                        'review_frequency_month': sustainability.review_frequency_month or 0,
                        'document_type': sustainability.document_type,
                        'section_number': sustainability.no,
                        'rivision': sustainability.rivision,
                        'written_by': sustainability.written_by,
                        'checked_by': sustainability.checked_by,
                        'approved_by': sustainability.approved_by,
                        'date': sustainability.date,
                    }

                    html_message = render_to_string('qms/sustainability/sustainability_to_checked_by.html', context)
                    plain_message = strip_tags(html_message)

                    # Compose email
                    email = EmailMultiAlternatives(
                        subject=subject,
                        body=plain_message,
                        from_email=config("DEFAULT_FROM_EMAIL"),
                        to=[recipient_email]
                    )
                    email.attach_alternative(html_message, "text/html")

                 
                    if sustainability.upload_attachment:
                        try:
                            file_name = sustainability.upload_attachment.name.rsplit('/', 1)[-1]
                            file_content = sustainability.upload_attachment.read()
                            email.attach(file_name, file_content)
                            logger.info(f"Attached sustainability document {file_name} to email")
                        except Exception as attachment_error:
                            logger.error(f"Error attaching sustainability file: {str(attachment_error)}")

                    # Use custom email backend
                    connection = CertifiEmailBackend(
                        host=config('EMAIL_HOST'),
                        port=config('EMAIL_PORT'),
                        username=config('EMAIL_HOST_USER'),
                        password=config('EMAIL_HOST_PASSWORD'),
                        use_tls=True
                    )

                    email.connection = connection
                    email.send(fail_silently=False)

                    logger.info(f"Email with attachment successfully sent to {recipient_email} for action: {action_type}")
                else:
                    logger.warning("Unknown action type provided for email.")
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
        print("=== STARTING SUSTAINABILITY UPDATE ===")
        print("Request data:", request.data)
        try:
            with transaction.atomic():
                sustainability = Sustainabilities.objects.get(pk=pk)
                serializer = SustainabilityUpdateSerializer(sustainability, data=request.data, partial=True)

                if serializer.is_valid():
                    updated_sustainability = serializer.save()
                    
                    # Set standard fields (identical to Manual)
                    updated_sustainability.written_at = now()
                    updated_sustainability.is_draft = False
                    updated_sustainability.status = 'Pending for Review/Checking'

                    # EXACT SAME LOGIC AS MANUAL VIEW
                    updated_sustainability.send_notification_to_checked_by = parse_bool(
                        request.data.get('send_notification_to_checked_by', False)
                    )
                    updated_sustainability.send_email_to_checked_by = parse_bool(
                        request.data.get('send_email_to_checked_by', False)
                    )
                    
                    updated_sustainability.save()

                    # IDENTICAL NOTIFICATION/EMAIL HANDLING AS MANUAL
                    if updated_sustainability.checked_by:
                        if updated_sustainability.send_notification_to_checked_by:
                            try:
                                NotificationSustainability.objects.create(
                                    user=updated_sustainability.checked_by,
                                    sustainability=updated_sustainability,
                                    title="Sustainability Updated - Review Required",
                                    message=f"Sustainability '{updated_sustainability.title}' requires review"
                                )
                                print("Created notification for checked_by")
                            except Exception as e:
                                logger.error(f"Notification error: {str(e)}")

                        if updated_sustainability.send_email_to_checked_by:
                            self.send_email_notification(
                                updated_sustainability, 
                                updated_sustainability.checked_by, 
                                "review"
                            )
                            print("Sent email to checked_by")

                    return Response({"message": "Updated successfully"}, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Sustainabilities.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in update: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def send_email_notification(self, sustainability, recipient, action_type):
        """IDENTICAL TO MANUAL VIEW'S EMAIL FUNCTION"""
        recipient_email = recipient.email if recipient else None
        
        if not recipient_email:
            print("No recipient email available")
            return

        try:
            subject = f"Sustainability Update: {sustainability.title}"
            context = {
                        'recipient_name': recipient.first_name,
                        'title': sustainability.title,
                        'document_number': sustainability.no or 'N/A',
                        'review_frequency_year': sustainability.review_frequency_year or 0,
                        'review_frequency_month': sustainability.review_frequency_month or 0,
                        'document_type': sustainability.document_type,
                        'section_number': sustainability.no,
                        'rivision': getattr(sustainability, 'rivision', ''),
                        'written_by': sustainability.written_by,
                        'checked_by': sustainability.checked_by,
                        'approved_by': sustainability.approved_by,
                        'date': sustainability.date,
                    }

            html_message = render_to_string(
                'sustainability/sustainability_update_to_checked_by.html',   
                context
            )
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=strip_tags(html_message),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email]
            )
            email.attach_alternative(html_message, "text/html")
            
            # Attach file if exists (same as Manual)
            if sustainability.upload_attachment:
                try:
                    email.attach(
                        sustainability.upload_attachment.name.split('/')[-1],
                        sustainability.upload_attachment.read()
                    )
                except Exception as e:
                    logger.error(f"Attachment error: {str(e)}")

            email.send(fail_silently=False)
            print(f"Email sent to {recipient_email}")

        except Exception as e:
            logger.error(f"Email failed: {str(e)}")
            print(f"!!! EMAIL ERROR: {str(e)}")




class SubmitCorrectionSustainabilityView(APIView):
    def post(self, request):
        try:
            # Extract data from request
            sustainability_id = request.data.get('sustainability_id')
            correction_text = request.data.get('correction')
            from_user_id = request.data.get('from_user')

            # Check if all required fields are provided
            if not all([sustainability_id, correction_text, from_user_id]):
                return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

            # Get sustainability object
            try:
                sustainability = Sustainabilities.objects.get(id=sustainability_id)
            except Sustainabilities.DoesNotExist:
                return Response({'error': 'Sustainability document not found'}, status=status.HTTP_404_NOT_FOUND)

            # Get user object
            try:
                from_user = Users.objects.get(id=from_user_id)
            except Users.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Validate user role and determine the recipient of the correction
            if from_user == sustainability.checked_by:
                to_user = sustainability.written_by
            elif from_user == sustainability.approved_by:
                to_user = sustainability.checked_by
            else:
                return Response({'error': 'Invalid user role for correction'}, status=status.HTTP_400_BAD_REQUEST)

            # Delete any existing corrections from this user for the same document
            CorrectionSustainability.objects.filter(
                sustainability=sustainability,
                from_user=from_user
            ).delete()

            # Create correction
            correction = CorrectionSustainability.objects.create(
                sustainability=sustainability,
                to_user=to_user,
                from_user=from_user,
                correction=correction_text
            )

            # Update sustainability status
            sustainability.status = 'Correction Requested'
            sustainability.save()

            # Create notification and send email
            self.create_correction_notification(correction)
            self.send_correction_email_notification(correction)

            # Serialize and return response
            serializer = CorrectionSustainabilitySerializer(correction)
            return Response(
                {'message': 'Correction submitted successfully', 'correction': serializer.data},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            print(f"Error occurred in submit correction: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create_correction_notification(self, correction):
        try:
            sustainability = correction.sustainability
            to_user = correction.to_user
            from_user = correction.from_user

            # Determine if notification should be sent based on user roles
            if from_user == sustainability.approved_by and to_user == sustainability.checked_by:
                should_send = sustainability.send_notification_to_checked_by
            elif from_user == sustainability.checked_by and to_user == sustainability.written_by:
                should_send = True
            else:
                should_send = False

            if should_send:
                message = (
                    f"Correction Request from {from_user.first_name} "
                    f"to {to_user.first_name} for Sustainability: {sustainability.title}"
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
            from_user = correction.from_user
            to_user = correction.to_user
            recipient_email = to_user.email if to_user else None

            # Define template and subject based on user roles
            if from_user == sustainability.checked_by and to_user == sustainability.written_by:
                template_name = 'sustainability/sustainability_correction_to_writer.html'
                subject = f"Correction Requested on '{sustainability.title}'"
                should_send = True
            elif from_user == sustainability.approved_by and to_user == sustainability.checked_by:
                template_name = 'sustainability/sustainability_correction_to_checker.html'
                subject = f"Correction Requested on '{sustainability.title}'"
                should_send = sustainability.send_email_to_checked_by
            else:
                return  # Not a valid correction flow

            # Check if email sending is enabled and recipient is valid
            if not recipient_email or not should_send:
                return

            # Prepare email context
            context = {
                'recipient_name': to_user.first_name,
                'title': sustainability.title,
                'document_number': sustainability.no or 'N/A',
                'review_frequency_year': sustainability.review_frequency_year or 0,
                'review_frequency_month': sustainability.review_frequency_month or 0,
                'document_type': sustainability.document_type,
                'section_number': sustainability.no,
                'rivision': getattr(sustainability, 'rivision', ''),
                'written_by': sustainability.written_by,
                'checked_by': sustainability.checked_by,
                'approved_by': sustainability.approved_by,
                'date': sustainability.date,
                'correction_text': correction.correction,
                'from_user_name': from_user.first_name
            }

            # Render email message
            html_message = render_to_string(template_name, context)
            plain_message = strip_tags(html_message)

            # Send email
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=config("DEFAULT_FROM_EMAIL"),
                to=[recipient_email]
            )
            email.attach_alternative(html_message, "text/html")

            # Attach sustainability file if exists
            if sustainability.upload_attachment:
                try:
                    file_name = sustainability.upload_attachment.name.rsplit('/', 1)[-1]
                    file_content = sustainability.upload_attachment.read()
                    email.attach(file_name, file_content)
                    print(f"Attached file {file_name} to correction email.")
                except Exception as attachment_error:
                    print(f"Failed to attach file: {str(attachment_error)}")

            # Use custom email backend
            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )
            email.connection = connection
            email.send(fail_silently=False)

            print(f"Correction email successfully sent to {recipient_email}")

        except Exception as e:
            print(f"Error sending correction email: {str(e)}")


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
                    sustainability.save()

                current_status = sustainability.status

                # Case 1: Checked_by reviews
                if current_status == 'Pending for Review/Checking' and current_user == sustainability.checked_by:
                    sustainability.status = 'Reviewed,Pending for Approval'
                    sustainability.checked_at = now()
                    sustainability.save()

                    if sustainability.send_notification_to_approved_by:
                        NotificationSustainability.objects.create(
                            user=sustainability.approved_by,
                            sustainability=sustainability,
                            message=f"Sustainability document '{sustainability.title}' is ready for approval."
                        )

                    if sustainability.send_email_to_approved_by:
                        self.send_email_notification(
                            sustainability=sustainability,
                            recipients=[sustainability.approved_by],
                            action_type="review"
                        )

                # Case 2: Approved_by approves
                elif current_status == 'Reviewed,Pending for Approval' and current_user == sustainability.approved_by:
                    sustainability.status = 'Pending for Publish'
                    sustainability.approved_at = now()
                    sustainability.save()

                    # Send notifications to all parties (like manual version)
                    for user in [sustainability.written_by, sustainability.checked_by, sustainability.approved_by]:
                        if user:
                            NotificationSustainability.objects.create(
                                user=user,
                                sustainability=sustainability,
                                message=f"Sustainability document '{sustainability.title}' has been approved and is pending for publish."
                            )

                    # Send emails to all parties (like manual version)
                    self.send_email_notification(
                        sustainability=sustainability,
                        recipients=[u for u in [sustainability.written_by, sustainability.checked_by, sustainability.approved_by] if u],
                        action_type="approved"
                    )

                # Correction Requested Case
                elif current_status == 'Correction Requested' and current_user == sustainability.written_by:
                    sustainability.status = 'Pending for Review/Checking'
                    sustainability.save()

                else:
                    return Response({
                        'message': 'No action taken. User not authorized for current sustainability status.'
                    }, status=status.HTTP_200_OK)

            return Response({
                'status': 'success',
                'message': 'Sustainability document processed successfully',
                'sustainability_status': sustainability.status
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in sustainability review process: {str(e)}")
            return Response({
                'error': 'An unexpected error occurred',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def send_email_notification(self, sustainability, recipients, action_type):
        for recipient in recipients:
            recipient_email = recipient.email if recipient else None

            if recipient_email:
                try:
                    if action_type == "review":
                        subject = f"Sustainability Submitted for Approval: {sustainability.title}"
                        context = {
                            'recipient_name': recipient.first_name,
                            'title': sustainability.title,
                            'document_number': sustainability.no or 'N/A',
                            'review_frequency_year': sustainability.review_frequency_year or 0,
                            'review_frequency_month': sustainability.review_frequency_month or 0,
                            'document_type': sustainability.document_type,
                            'section_number': sustainability.no,
                            'rivision': getattr(sustainability, 'rivision', ''),
                            'written_by': sustainability.written_by,
                            'checked_by': sustainability.checked_by,
                            'approved_by': sustainability.approved_by,
                            'date': sustainability.date,
                            'document_url': sustainability.upload_attachment.url if sustainability.upload_attachment else None,
                            'document_name': sustainability.upload_attachment.name.rsplit('/', 1)[-1] if sustainability.upload_attachment else None,
                        }
                        html_message = render_to_string('sustainability/sustainability_to_approved_by.html', context)
                        plain_message = strip_tags(html_message)

                    elif action_type == "approved":
                        subject = f"Sustainability Approved: {sustainability.title}"
                        context = {
                            'recipient_name': recipient.first_name,
                            'title': sustainability.title,
                            'document_number': sustainability.no or 'N/A',
                            'review_frequency_year': sustainability.review_frequency_year or 0,
                            'review_frequency_month': sustainability.review_frequency_month or 0,
                            'document_type': sustainability.document_type,
                            'section_number': sustainability.no,
                            'rivision': getattr(sustainability, 'rivision', ''),
                            'written_by': sustainability.written_by,
                            'checked_by': sustainability.checked_by,
                            'approved_by': sustainability.approved_by,
                            'date': sustainability.date,
                            'document_url': sustainability.upload_attachment.url if sustainability.upload_attachment else None,
                            'document_name': sustainability.upload_attachment.name.rsplit('/', 1)[-1] if sustainability.upload_attachment else None,
                        }
                        html_message = render_to_string('sustainability/sustainability_publish.html', context)
                        plain_message = strip_tags(html_message)

                    else:
                        logger.warning(f"Unknown action type '{action_type}' for email notification.")
                        continue

                    # Create email
                    email = EmailMultiAlternatives(
                        subject=subject,
                        body=plain_message,
                        from_email=config('DEFAULT_FROM_EMAIL'),
                        to=[recipient_email]
                    )
                    email.attach_alternative(html_message, "text/html")

                    # Attach the sustainability document if it exists
                    if sustainability.upload_attachment:
                        try:
                            file_name = sustainability.upload_attachment.name.rsplit('/', 1)[-1]
                            file_content = sustainability.upload_attachment.read()
                            email.attach(file_name, file_content)
                            logger.info(f"Attached sustainability file {file_name} to email")
                        except Exception as attachment_error:
                            logger.error(f"Error attaching file: {str(attachment_error)}")

                    # Use custom backend (optional)
                    connection = CertifiEmailBackend(
                        host=config('EMAIL_HOST'),
                        port=config('EMAIL_PORT'),
                        username=config('EMAIL_HOST_USER'),
                        password=config('EMAIL_HOST_PASSWORD'),
                        use_tls=True
                    )
                    email.connection = connection
                    email.send(fail_silently=False)

                    logger.info(f"Email successfully sent to {recipient_email} for action: {action_type}")

                except Exception as e:
                    logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
            else:
                logger.warning("Recipient email is None. Skipping email send.")



 

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
                # Update sustainability status and published information
                sustainability.status = 'Published'
                sustainability.published_at = now()
                
                # Set the published_user if the ID was provided
                if published_by:
                    try:
                        publishing_user = Users.objects.get(id=published_by)
                        sustainability.published_user = publishing_user
                    except Users.DoesNotExist:
                        logger.warning(f"Publisher user ID {published_by} not found")
                
                # Only send notifications if requested
                sustainability.send_notification = send_notification
                sustainability.save()

                # Only proceed with notifications if send_notification is True
                if send_notification:
                    # Get all users in the company
                    company_users = Users.objects.filter(company=company)

                    # Create notifications for each user
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

                    # Send emails
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
        """Helper method to send email notifications with template and attach document"""
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags

        publisher_name = "N/A"
        if sustainability.published_user:
            publisher_name = f"{sustainability.published_user.first_name} {sustainability.published_user.last_name}"
        elif sustainability.approved_by:
            publisher_name = f"{sustainability.approved_by.first_name} {sustainability.approved_by.last_name}"

        subject = f"New Sustainability Document Published: {sustainability.title}"

        context = {
            'recipient_name': recipient.first_name,
            'title': sustainability.title,
            'document_number': sustainability.no or 'N/A',
            'review_frequency_year': sustainability.review_frequency_year or 0,
            'review_frequency_month': sustainability.review_frequency_month or 0,
            'document_type': sustainability.document_type,
            'section_number': sustainability.no,
            'rivision': getattr(sustainability, 'rivision', ''),
            "written_by": sustainability.written_by,
            "checked_by": sustainability.checked_by,
            "approved_by": sustainability.approved_by,
            'date': sustainability.date,
            'document_url': sustainability.upload_attachment.url if sustainability.upload_attachment else None,
            'document_name': sustainability.upload_attachment.name.rsplit('/', 1)[-1] if sustainability.upload_attachment else None,
        }

        html_message = render_to_string('sustainability/sustainability_published_notification.html', context)
        plain_message = strip_tags(html_message)

        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=config("DEFAULT_FROM_EMAIL"),
            to=[recipient.email]
        )
        email.attach_alternative(html_message, "text/html")

        if sustainability.upload_attachment:
            try:
                file_name = sustainability.upload_attachment.name.rsplit('/', 1)[-1]
                file_content = sustainability.upload_attachment.read()
                email.attach(file_name, file_content)
                logger.info(f"Attached sustainability file {file_name} to email")
            except Exception as attachment_error:
                logger.error(f"Error attaching file: {str(attachment_error)}")

        # Use custom backend if needed
        try:
            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )
            email.connection = connection
            email.send(fail_silently=False)
            logger.info(f"HTML Email sent to {recipient.email}")
        except Exception as e:
            logger.error(f"Failed to send email to {recipient.email}: {str(e)}")


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

                    # Send notifications if required
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

                        # Send emails asynchronously
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
        Send HTML-formatted email notification about the new training, 
        with optional document attachment.
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
             'created_by': training.user
        }

        html_message = render_to_string('qms/training/training_add.html', context)
        plain_message = strip_tags(html_message)

        # Prepare email with attachment if document exists
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=config("DEFAULT_FROM_EMAIL"),
            to=[recipient_email]
        )
        email.attach_alternative(html_message, "text/html")

        # Attach training document if available
        if training.attachment:
            try:
                file_name = training.attachment.name.rsplit('/', 1)[-1]
                file_content = training.attachment.read()
                email.attach(file_name, file_content)
                print(f"Attached training document: {file_name}")
            except Exception as attachment_error:
                print(f"Error attaching training file: {str(attachment_error)}")

        # Use custom email backend
        connection = CertifiEmailBackend(
            host=config('EMAIL_HOST'),
            port=config('EMAIL_PORT'),
            username=config('EMAIL_HOST_USER'),
            password=config('EMAIL_HOST_PASSWORD'),
            use_tls=True
        )
        email.connection = connection
        email.send(fail_silently=False)

        print(f"Email successfully sent to {recipient_email}")



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
        try:
            training = get_object_or_404(Training, pk=pk)
            send_notification = request.data.get('send_notification', 'false') == 'true'

            serializer = TrainingSerializer(training, data=request.data, partial=True)
            if serializer.is_valid():
                with transaction.atomic():
                    training = serializer.save()

                    logger.info(f"Training updated: {training.training_title}")

                    if send_notification:
                        attendees = training.training_attendees.all()
                        users_to_notify = [training.evaluation_by, training.requested_by] + list(attendees)

                        # Create notifications
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
                                try:
                                    self._send_email_async(training, user)
                                except Exception as e:
                                    logger.error(f"Failed to send email to {user.email}: {e}")

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
             'created_by': training.user
        }

        try:
            html_message = render_to_string('qms/training/training_update.html', context)
            plain_message = strip_tags(html_message)

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=config("DEFAULT_FROM_EMAIL"),
                to=[recipient_email]
            )
            email.attach_alternative(html_message, "text/html")

            # Attach file if exists
            if training.attachment:
                try:
                    training.attachment.seek(0)
                    file_name = training.attachment.name.rsplit('/', 1)[-1]
                    file_content = training.attachment.read()
                    content_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
                    email.attach(file_name, file_content, content_type)
                    logger.info(f"Attached training document: {file_name}")
                except Exception as attachment_error:
                    logger.error(f"Error attaching file: {attachment_error}")
                    traceback.print_exc()

            # Custom Email Backend
            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )

            email.connection = connection
            email.send(fail_silently=False)
            logger.info(f"Email successfully sent to {recipient_email}")

        except Exception as e:
            logger.error(f"Error sending training email to {recipient_email}: {e}")
            traceback.print_exc()


 

class TrainingCompleteAndNotifyView(APIView):
    def post(self, request, training_id):
        try:
            training = Training.objects.get(id=training_id)
            company = training.company

            if not company:
                return Response(
                    {"error": "Associated company not found for this training."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not training.send_notification:
                training.send_notification = True
                training.save(update_fields=['send_notification'])

            with transaction.atomic():
                training.status = 'Completed'
                training.save(update_fields=['status'])

                logger.info(f"Training '{training.training_title}' marked as Completed")

                if training.send_notification:
                    company_users = Users.objects.filter(company=company)

                    # Create notifications
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

                    # Send emails asynchronously
                    for user in company_users:
                        if user and user.email:
                            self._send_email_async(training, user)

            return Response(
                {"message": "Training marked as completed successfully."},
                status=status.HTTP_200_OK
            )

        except Training.DoesNotExist:
            return Response({"error": "Training not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Error in TrainingCompleteAndNotifyView: {str(e)}")
            return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _send_email_async(self, training, recipient):
        threading.Thread(target=self._send_email, args=(training, recipient)).start()

    def _send_email(self, training, recipient):
        subject = f"Training Completed: {training.training_title}"
        recipient_email = recipient.email

        context = {
            'training_title': training.training_title,
            'expected_results': training.expected_results,
            'actual_results': training.actual_results,
            'type_of_training': training.type_of_training,
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
             'created_by': training.user
        }

        try:
            html_message = render_to_string('qms/training/training_completed.html', context)
        except Exception as e:
            logger.warning(f"Template rendering failed: {str(e)}")
            html_message = f"<p>Training {training.training_title} completed.</p>"

        plain_message = strip_tags(html_message)

        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=config("DEFAULT_FROM_EMAIL"),
            to=[recipient_email]
        )
        email.attach_alternative(html_message, "text/html")

        if training.attachment:
            try:
                file_name = training.attachment.name.rsplit('/', 1)[-1]
                file_content = training.attachment.read()
                email.attach(file_name, file_content)
                logger.info(f"Attached document: {file_name}")
            except Exception as e:
                logger.error(f"Attachment error: {str(e)}")

        connection = CertifiEmailBackend(
            host=config('EMAIL_HOST'),
            port=config('EMAIL_PORT'),
            username=config('EMAIL_HOST_USER'),
            password=config('EMAIL_HOST_PASSWORD'),
            use_tls=True
        )
        email.connection = connection
        email.send(fail_silently=False)
        logger.info(f"Email sent to {recipient_email}")



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
                return Response({"error": "Company not found."}, status=status.HTTP_404_NOT_FOUND)

            try:
                performance = EmployeePerformance.objects.get(id=evaluation_id, company=company)
            except EmployeePerformance.DoesNotExist:
                return Response({"error": "Evaluation not found or does not belong to this company."}, status=status.HTTP_404_NOT_FOUND)

            users = Users.objects.filter(company=company, is_trash=False)

            response_data = []
            for user in users:
                user_questions = PerformanceQuestions.objects.filter(performance=performance, user=user)
                questions_data = [
                    {
                        "question_text": q.question_text,
                        "answer": q.answer
                    } for q in user_questions
                ]

                response_data.append({
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "status": user.status,
                    "questions": questions_data
                })

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": "Unexpected error occurred.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            
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

        except SurveyQuestions.DoesNotExist:
            return Response({"error": "Question not found."}, status=status.HTTP_404_NOT_FOUND)


# class UserSurveysAnswersView(APIView):
#     def get(self, request, company_id, survey_id):
#         try:
  
#             try:
#                 company = Company.objects.get(id=company_id)
#             except Company.DoesNotExist:
#                 return Response(
#                     {"error": "Company not found."},
#                     status=status.HTTP_404_NOT_FOUND
#                 )
          
#             try:
#                 survey = EmployeeSurvey.objects.get(id=survey_id, company=company)
#             except EmployeeSurvey.DoesNotExist:
#                 return Response(
#                     {"error": "Survey not found or does not belong to the specified company."},
#                     status=status.HTTP_404_NOT_FOUND
#                 )
           
#             company_users = Users.objects.filter(company=company, is_trash=False)
           
#             submitted_user_ids = SurveyQuestions.objects.filter(
#                 survey=survey,
#                 user__isnull=False
#             ).values_list('user_id', flat=True).distinct()
            
#             not_submitted_users = company_users.exclude(id__in=submitted_user_ids)
      
#             user_data = [
#                 {
#                     "id": user.id,
#                     "first_name": user.first_name,
#                     "last_name": user.last_name,
#                     "email": user.email,
#                     "status": user.status
#                 }
#                 for user in not_submitted_users
#             ]

#             return Response(user_data, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response(
#                 {"error": "An unexpected error occurred.", "details": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

class UserSurveysAnswersView(APIView):
    def get(self, request, company_id, survey_id):
        try:
            try:
                company = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                return Response({"error": "Company not found."}, status=status.HTTP_404_NOT_FOUND)

            try:
                 survey = EmployeeSurvey.objects.get(id=survey_id, company=company)
            except EmployeeSurvey.DoesNotExist:
                return Response({"error": "Evaluation not found or does not belong to this company."}, status=status.HTTP_404_NOT_FOUND)

            users = Users.objects.filter(company=company, is_trash=False)

            response_data = []
            for user in users:
                user_questions = SurveyQuestions.objects.filter(survey=survey, user=user)
                questions_data = [
                    {
                        "question_text": q.question_text,
                        "answer": q.answer
                    } for q in user_questions
                ]

                response_data.append({
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "status": user.status,
                    "questions": questions_data
                })

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": "Unexpected error occurred.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

           
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
        print("Received Data:", request.data)
        try:
            company_id = request.data.get('company')
            send_notification = request.data.get('send_notification', False)

            if isinstance(send_notification, str):
                send_notification = send_notification.lower() == 'true'
            print(" Send Notification Flag:", send_notification)

            if not company_id:
                return Response(
                    {"error": "Company ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            company = Company.objects.get(id=company_id)
            serializer = MeetingSerializer(data=request.data)

            if serializer.is_valid():
                with transaction.atomic():
                    meeting = serializer.save()
                    print(f" Meeting created: {meeting.title}")
                    meeting.send_notification = send_notification
                    meeting.save()

                    attendees_ids = request.data.get('attendees', [])
                    for attendee_id in attendees_ids:
                        try:
                            attendee = Users.objects.get(id=attendee_id)
                            meeting.attendees.add(attendee)
                        except Users.DoesNotExist:
                            pass

                    agenda_ids = request.data.get('agenda', [])
                    for agenda_id in agenda_ids:
                        try:
                            agenda = Agenda.objects.get(id=agenda_id)
                            meeting.agenda.add(agenda)
                        except Agenda.DoesNotExist:
                            pass

                    if send_notification:
                        notifications = []
                        for attendee in meeting.attendees.all():
                            notifications.append(MeetingNotification(
                                user=attendee,
                                meeting=meeting,
                                title=f"Meeting Invitation: {meeting.title}",
                                message=f"You have been invited to a meeting on {meeting.date} at {meeting.start_time}."
                            ))

                        if notifications:
                            MeetingNotification.objects.bulk_create(notifications)
                            print(f" Created {len(notifications)} notifications for meeting {meeting.id}")

                        for attendee in meeting.attendees.all():
                            if attendee.email:
                                self._send_email_async(meeting, attendee)

                return Response({
                    "message": "Meeting created successfully",
                    "notification_sent": send_notification
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f" Error creating meeting: {str(e)}")
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _send_email_async(self, meeting, recipient):
        threading.Thread(target=self._send_notification_email, args=(meeting, recipient)).start()

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
            'created_by': meeting.user
        }

        html_message = render_to_string('qms/meeting/meeting_add.html', context)
        plain_message = strip_tags(html_message)

        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=config("DEFAULT_FROM_EMAIL"),
            to=[recipient_email]
        )
        email.attach_alternative(html_message, "text/html")

        # Attach meeting file if exists
        if meeting.file:
            try:
                file_name = meeting.file.name.rsplit('/', 1)[-1]
                file_content = meeting.file.read()
                email.attach(file_name, file_content)
                print(f"📎 Attached meeting file: {file_name}")
            except Exception as attachment_error:
                print(f"Error attaching meeting file: {str(attachment_error)}")

        # Custom email backend
        connection = CertifiEmailBackend(
            host=config('EMAIL_HOST'),
            port=config('EMAIL_PORT'),
            username=config('EMAIL_HOST_USER'),
            password=config('EMAIL_HOST_PASSWORD'),
            use_tls=True
        )
        email.connection = connection
        email.send(fail_silently=False)

        print(f"📧 Email successfully sent to {recipient_email}")



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

                        # Create notifications
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
                                try:
                                    self._send_email_async(meeting, user)
                                except Exception as e:
                                    logger.error(f"Failed to send email to {user.email}: {e}")

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
            'created_by':meeting.user
        }

        try:
            html_message = render_to_string('qms/meeting/meeting_update.html', context)
            plain_message = strip_tags(html_message)

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=config("DEFAULT_FROM_EMAIL"),
                to=[recipient_email]
            )
            email.attach_alternative(html_message, "text/html")

            # Attach file if exists
            if meeting.file:
                try:
                    meeting.file.seek(0)
                    file_name = meeting.file.name.rsplit('/', 1)[-1]
                    file_content = meeting.file.read()
                    content_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
                    email.attach(file_name, file_content, content_type)
                    logger.info(f"Attached meeting document: {file_name}")
                except Exception as attachment_error:
                    logger.error(f"Error attaching file: {attachment_error}")
                    traceback.print_exc()

            # Custom Email Backend
            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )

            email.connection = connection
            email.send(fail_silently=False)
            logger.info(f"Email successfully sent to {recipient_email}")

        except Exception as e:
            logger.error(f"Error sending meeting email to {recipient_email}: {e}")
            traceback.print_exc()


        
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

                
                    if send_notification and executor_id:
                        try:
                            executor = Users.objects.get(id=executor_id)
                            
                        
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
            'created_by':car_number.user
        }

        try:
            html_message = render_to_string('qms/car/car_add_template.html', context)
            plain_message = strip_tags(html_message)

         
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=config("DEFAULT_FROM_EMAIL"),
                to=[recipient_email]
            )
            email.attach_alternative(html_message, "text/html")

      
            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )
            email.connection = connection
            email.send(fail_silently=False)

            logger.info(f"Email successfully sent to {recipient_email}")

        except Exception as e:
            logger.error(f"Error sending CAR email to {recipient_email}: {e}")



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
        serializer = CarNumberGetSerializer(car_number)
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
 
        data = {}
        
     
        for key in request.data:
            if key != 'upload_attachment':
                data[key] = request.data[key]
   
        data['is_draft'] = True
        
      
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
        serializer = CarNumberGetSerializer(agendas, many=True)
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
        internal_problem = self.get_object(pk)  
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
        print("requsetd",request.data)
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
        serializer = SupplierProblemGetSerializer(supplier_problem)
        return Response(serializer.data, status=status.HTTP_200_OK)

 
    def put(self, request, pk):
        supplier_problem = self.get_object(pk)
        if supplier_problem is None:
            return Response({"error": "SupplierProblem not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = SupplierProblemSerializer(supplier_problem, data=request.data)
        if serializer.is_valid():
            serializer.save(is_draft=False)
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
     
        agendas = SupplierProblem.objects.filter(company_id=company_id,is_draft=False)
        serializer = SupplierProblemGetSerializer(agendas, many=True)
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
        recipient_email = recipient.email if recipient else None

        if recipient_email:
            try:
                if action_type == "review":
                    subject = f"Manual Ready for Review: {manual.title}"
               

                    context = {
                        'recipient_name': recipient.first_name,
                        'title': manual.title,
                        'document_number': manual.no or 'N/A',
                        'review_frequency_year': manual.review_frequency_year or 0,
                        'review_frequency_month': manual.review_frequency_month or 0,
                        'document_type': manual.document_type,
                        'section_number': manual.no,
                        'rivision': manual.rivision,
                        "written_by": manual.written_by,
                        "checked_by": manual.checked_by,
                        "approved_by": manual.approved_by,
                        'date': manual.date,
                        'document_url': manual.upload_attachment.url if manual.upload_attachment else None,
                        'document_name': manual.upload_attachment.name.rsplit('/', 1)[-1] if manual.upload_attachment else None,
                    }

                    html_message = render_to_string('qms/manual/manual_to_checked_by.html', context)
                    plain_message = strip_tags(html_message)

                    email = EmailMultiAlternatives(
                        subject=subject,
                        body=plain_message,
                        from_email=config("DEFAULT_FROM_EMAIL"),
                        to=[recipient_email]
                    )
                    email.attach_alternative(html_message, "text/html")

                    # Attach document if available
                    if manual.upload_attachment:
                        try:
                            file_name = manual.upload_attachment.name.rsplit('/', 1)[-1]
                            file_content = manual.upload_attachment.read()
                            email.attach(file_name, file_content)
                            logger.info(f"Attached manual document {file_name} to email")
                        except Exception as attachment_error:
                            logger.error(f"Error attaching manual file: {str(attachment_error)}")

                     
                   
                    connection = CertifiEmailBackend(
                        host=config('EMAIL_HOST'),
                        port=config('EMAIL_PORT'),
                        username=config('EMAIL_HOST_USER'),
                        password=config('EMAIL_HOST_PASSWORD'),
                        use_tls=True
                    )

                    email.connection = connection
                    email.send(fail_silently=False)

                    logger.info(f"Email with attachment successfully sent to {recipient_email} for action: {action_type}")
                else:
                    logger.warning("Unknown action type provided for email.")
                    return
            except Exception as e:
                logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        else:
            logger.warning("Recipient email is None. Skipping email send.")


class SuppEvaluationCreateView(APIView):
    def post(self, request):
        serializer = SupplierEvaluationSerializer(data=request.data)
        if serializer.is_valid():
       
            serializer.save()   
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class SupplierEvalAllList(APIView):
    def get(self, request, company_id):
        try:
        
            if not Company.objects.filter(id=company_id).exists():
                return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

           
            company_policies = SupplierEvaluation.objects.filter(company_id=company_id ,is_draft=False)

           
            serializer = SupplierEvaluationSerializer(company_policies, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class  SuppEvalUpdateView(APIView):
    def put(self, request, pk):
        try:
            documentation = SupplierEvaluation.objects.get(pk=pk)
        except SupplierEvaluationSerializer.DoesNotExist:
            return Response({"error": "Supplier Evaluation not found"}, status=status.HTTP_404_NOT_FOUND) 
        data = request.data.copy()      
        data['is_draft'] = False
        serializer = SupplierEvaluationSerializer(documentation, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            documentation = SupplierEvaluation.objects.get(pk=pk)
        except SupplierEvaluation.DoesNotExist:
            return Response({"error": "Supplier Evaluation not found"}, status=status.HTTP_404_NOT_FOUND)
        
        documentation.delete()   
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
    
class SuppEvalDetailView(APIView):
    def get(self, request, id):
        policy = get_object_or_404(SupplierEvaluation, id=id)
        serializer = SupplierEvaluationSerializer(policy)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SuppEvalDraftAPIView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data.copy()  
        data['is_draft'] = True  

        serializer =SupplierEvaluationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Supplie Evaluation  saved as draft", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class SuppEvlDraftAllList(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        record = SupplierEvaluation.objects.filter(user=user, is_draft=True)
        serializer =SupplierEvaluationSerializer(record, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class SuppEvlView(APIView):
 
    def get(self, request, user_id):
   
        draft_records = SupplierEvaluation.objects.filter(is_draft=True, user_id=user_id)
        
        serializer = SupplierEvaluationSerializer(draft_records, many=True)
        
        return Response({
            "count": draft_records.count(),
            "draft_records": serializer.data
        }, status=status.HTTP_200_OK)


class SupEvalQuestionQuestionAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SupEvalQuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SupEvalQuestionQuestionsByEvaluationAPIView(APIView):
    def get(self, request, supp_evaluation_id, *args, **kwargs):
        questions = SupplierEvaluationQuestions.objects.filter(supp_evaluation_id=supp_evaluation_id)
        serializer = SupEvalQuestionSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)   
    

class DeleteSuppQuestionAPIView(APIView):
    def delete(self, request, question_id, *args, **kwargs):
        try:
            question = SupplierEvaluationQuestions.objects.get(id=question_id)
            question.delete()
            return Response({"message": "Question deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except SupplierEvaluationQuestions.DoesNotExist:
            return Response({"error": "Question not found."}, status=status.HTTP_404_NOT_FOUND)
        
        
class SupplierSuppEvlAnswersView(APIView):
    def get(self, request, company_id, supp_evaluation_id):
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({"error": "Company not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            supp_evaluation = SupplierEvaluation.objects.get(id=supp_evaluation_id, company=company)
        except SupplierEvaluation.DoesNotExist:
            return Response({"error": "Supplier evaluation not found or does not belong to the specified company."},
                            status=status.HTTP_404_NOT_FOUND)

        # Get all suppliers for the company
        company_suppliers = Supplier.objects.filter(company=company)

        # Get supplier IDs that have submitted answers
        submitted_supplier_ids = SupplierEvaluationQuestions.objects.filter(
            supp_evaluation=supp_evaluation,
            Supplier__isnull=False
        ).values_list('Supplier_id', flat=True).distinct()

        # Get suppliers who have NOT submitted
        not_submitted_suppliers = company_suppliers.exclude(id__in=submitted_supplier_ids)

        supplier_data = [
            {
                "id": supplier.id,
                "company_name": supplier.company_name,
                "email": supplier.email,
                "address": supplier.address,
                "state": supplier.state,
                "country": supplier.country,
                "city": supplier.city,
                "postal_code": supplier.postal_code,
                "phone": supplier.phone,
                "alternate_phone": supplier.alternate_phone,
                "fax": supplier.fax,
                "contact_person": supplier.contact_person,
                "qualified_to_supply": supplier.qualified_to_supply,
                "notes": supplier.notes,
                "active": supplier.active,
                "status": supplier.status,
                "approved_by": supplier.approved_by.first_name if supplier.approved_by else None,
                "selection_criteria": supplier.selection_criteria,
                "approved_date": supplier.approved_date,
                "is_draft": supplier.is_draft
            }
            for supplier in not_submitted_suppliers
        ]

        return Response(supplier_data, status=status.HTTP_200_OK)


class AddSSuppAnswerToQuestionAPIView(APIView):
    def patch(self, request, question_id, *args, **kwargs):
        try:
            question = SupplierEvaluationQuestions.objects.get(id=question_id)
        except SupplierEvaluationQuestions.DoesNotExist:
            return Response({"error": "Question not found."}, status=status.HTTP_404_NOT_FOUND)

        answer = request.data.get('answer')
        supplier_id = request.data.get('supplier_id')

        if not answer:
            return Response({"error": "Answer is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not supplier_id:
            return Response({"error": "Supplier ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            supplier = Supplier.objects.get(id=supplier_id)
        except Supplier.DoesNotExist:
            return Response({"error": "Supplier not found."}, status=status.HTTP_404_NOT_FOUND)

        question.answer = answer
        question.Supplier = supplier  
        question.save()

        return Response({"message": "Answer and supplier updated successfully."}, status=status.HTTP_200_OK)
        

class CustomerAPIView(APIView):
   
    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CustomerView(APIView):
    def get(self, request, company_id):
        agendas = Customer.objects.filter(company_id=company_id,is_draft=False)
        serializer = CustomerSerializer(agendas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomerDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return None

 
    def get(self, request, pk):
        supplier = self.get_object(pk)
        if not supplier:
            return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CustomerSerializer(supplier)
        return Response(serializer.data, status=status.HTTP_200_OK)

   
    def put(self, request, pk):
        customer = self.get_object(pk)
        if not customer:
            return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CustomerSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save(is_draft=False)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request, pk):
        supplier = self.get_object(pk)
        if not supplier:
            return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)
        supplier.delete()
        return Response({"message": "Customer deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    

class CustomerDraftAPIView(APIView):
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
        
        serializer = CustomerSerializer(data=data)
        if serializer.is_valid():
            manual = serializer.save()
            
            # Assign file if provided
            if file_obj:
                manual.upload_attachment = file_obj
                manual.save()
                
            return Response({"message": "Customer saved as draft", "data": serializer.data}, 
                           status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CustomerDraftAllList(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        record = Customer.objects.filter(user=user, is_draft=True)
        serializer =CustomerSerializer(record, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryListCreateView(APIView):
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CompanycategoryView(APIView):
    def get(self, request, company_id):
        agendas = Category.objects.filter(company_id=company_id)
        serializer = CategorySerializer(agendas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

 
   
class CategoryDetailView(APIView):
    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None


    def delete(self, request, pk):
        agenda = self.get_object(pk)
        if not agenda:
            return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
        agenda.delete()
        return Response({"message": "Agenda Category successfully."}, status=status.HTTP_204_NO_CONTENT)
    
class ComplaintsCreateView(generics.CreateAPIView):
    queryset = Complaints.objects.all()
    serializer_class = ComplaintsSerializer

    
class ComplaintsView(APIView):
    def get(self, request, company_id):
        agendas = Complaints.objects.filter(company_id=company_id,is_draft=False)
        serializer = ComplaintGetSerializer(agendas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class ComplaintsDetailView(APIView):
   
    def get_object(self, pk):
        try:
            return Complaints.objects.get(pk=pk)
        except Complaints.DoesNotExist:
            return None

    def get(self, request, pk):
        internal_problem = self.get_object(pk)  # Renamed from car_number to internal_problem for clarity
        if not internal_problem:
            return Response({"error": "Complaint not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ComplaintGetSerializer(internal_problem)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        internal_problem = self.get_object(pk)
        if not internal_problem:
            return Response({"error": "Complaint not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ComplaintsSerializer(internal_problem, data=request.data, partial=True)   
        if serializer.is_valid():
            complaint = serializer.save(is_draft=False)
            
           
            if 'category' in request.data:
                complaint.category.set(request.data['category'])   
            
            return Response(ComplaintsSerializer(complaint).data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    def delete(self, request, pk):
        car_number = self.get_object(pk)
        if not car_number:
            return Response({"error": "Complaint not found."}, status=status.HTTP_404_NOT_FOUND)
        car_number.delete()
        return Response({"message": "Complaint deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class ComplaintsDraftAPIView(APIView):
    def post(self, request, *args, **kwargs):
      
        data = {}
        
        # Copy over simple data fields 
        for key in request.data:
            if key != 'upload_attachment':
                data[key] = request.data[key]
        
        # Set is_draft flag
        data['is_draft'] = True
        
        # Handle file separately
        file_obj = request.FILES.get('upload_attachment')
        
        serializer = ComplaintsSerializer(data=data)
        if serializer.is_valid():
            manual = serializer.save()
            
            # Assign file if provided
            if file_obj:
                manual.upload_attachment = file_obj
                manual.save()
                
            return Response({"message": "Complaints saved as draft", "data": serializer.data}, 
                           status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ComplaintDraftAllList(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        record = Complaints.objects.filter(user=user, is_draft=True)
        serializer =ComplaintGetSerializer(record, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    

class CustomerSurveyCreateView(APIView):
    def post(self, request):
        serializer = CustomerSatisfactionSerializer(data=request.data)
        if serializer.is_valid():
       
            serializer.save()   
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CustomerSurveyEvalAllList(APIView):
    def get(self, request, company_id):
        try:
        
            if not Company.objects.filter(id=company_id).exists():
                return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

           
            company_policies = CustomerSatisfaction.objects.filter(company_id=company_id ,is_draft=False)

           
            serializer = CustomerSatisfactionSerializer(company_policies, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class  CustomerSurveyUpdateView(APIView):
    def put(self, request, pk):
        try:
            documentation = CustomerSatisfaction.objects.get(pk=pk)
        except CustomerSatisfactionSerializer.DoesNotExist:
            return Response({"error": "Customer Satisfaction Evaluation not found"}, status=status.HTTP_404_NOT_FOUND) 
        data = request.data.copy()      
        data['is_draft'] = False
        serializer = CustomerSatisfactionSerializer(documentation, data=data)
        if serializer.is_valid():
            
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            documentation = CustomerSatisfaction.objects.get(pk=pk)
        except CustomerSatisfaction.DoesNotExist:
            return Response({"error": "Customer Satisfaction Evaluation not found"}, status=status.HTTP_404_NOT_FOUND)
        
        documentation.delete()   
        return Response(status=status.HTTP_204_NO_CONTENT)

class CustomerSurveyDetailView(APIView):
    def get(self, request, id):
        policy = get_object_or_404(CustomerSatisfaction, id=id)
        serializer = CustomerSatisfactionSerializer(policy)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CustomerSurveyDraftAPIView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data.copy()  
        data['is_draft'] = True  

        serializer =CustomerSatisfactionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Customer Satisfaction  saved as draft", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerSurveyDraftAllList(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        record = CustomerSatisfaction.objects.filter(user=user, is_draft=True)
        serializer =CustomerSatisfactionSerializer(record, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CustomerSurveyView(APIView):
 
    def get(self, request, user_id):
   
        draft_records = CustomerSatisfaction.objects.filter(is_draft=True, user_id=user_id)
        
        serializer = CustomerSatisfactionSerializer(draft_records, many=True)
        
        return Response({
            "count": draft_records.count(),
            "draft_records": serializer.data
        }, status=status.HTTP_200_OK)

class CustomerSurveyQuestionQuestionAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CustomerQuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CustomerSurveyByEvaluationAPIView(APIView):
    def get(self, request, customer_id, *args, **kwargs):
        questions = CustomerQuestions.objects.filter(customer_id=customer_id)
        serializer = CustomerQuestionSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)   
    

class DeleteCustomerSurveyQuestionAPIView(APIView):
    def delete(self, request, question_id, *args, **kwargs):
        try:
            question = CustomerQuestionSerializer.objects.get(id=question_id)
            question.delete()
            return Response({"message": "Question deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except CustomerQuestions.DoesNotExist:
            return Response({"error": "Question not found."}, status=status.HTTP_404_NOT_FOUND)

class AddSCustomerSurveyAnswerToQuestionAPIView(APIView):
    def patch(self, request, question_id, *args, **kwargs):
        try:
            question = CustomerQuestions.objects.get(id=question_id)
        except CustomerQuestions.DoesNotExist:
            return Response({"error": "Question not found."}, status=status.HTTP_404_NOT_FOUND)

        answer = request.data.get('answer')
        customer_id = request.data.get('customer_id')

        if not answer:
            return Response({"error": "Answer is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not customer_id:
            return Response({"error": "Customer ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)

        question.answer = answer
        question.customer_qsn = customer  # Use correct field
        question.save()

        return Response({"message": "Answer and customer updated successfully."}, status=status.HTTP_200_OK)




class CustomerCustomerSurveyAnswersView(APIView):
    def get(self, request, company_id, customer_id):
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({"error": "Company not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            survey = CustomerSatisfaction.objects.get(id=customer_id, company=company)
        except CustomerSatisfaction.DoesNotExist:
            return Response({"error": "Customer satisfaction not found or does not belong to the specified company."},
                            status=status.HTTP_404_NOT_FOUND)

        company_customers = Customer.objects.filter(company=company)

        # Get customer_qsn IDs that have submitted answers for the given survey
        submitted_customer_ids = CustomerQuestions.objects.filter(
            customer=survey,
            customer_qsn__isnull=False
        ).values_list('customer_qsn_id', flat=True).distinct()

        not_submitted_customers = company_customers.exclude(id__in=submitted_customer_ids)

        customer_data = [
            {
                "id": customer.id,
                "name": customer.name,
                "address": customer.address,
                "city": customer.city,
                "state": customer.state,
                "zipcode": customer.zipcode,
                "country": customer.country,
                "email": customer.email,
                "contact_person": customer.contact_person,
                "phone": customer.phone,
                "alternate_phone": customer.alternate_phone,
                "fax": customer.fax,
                "notes": customer.notes,
                "is_draft": customer.is_draft
            }
            for customer in not_submitted_customers
        ]

        return Response(customer_data, status=status.HTTP_200_OK)

            
            
class SupplierproblemDraftAPIView(APIView):
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
        
        serializer = SupplierProblemSerializer(data=data)
        if serializer.is_valid():
            manual = serializer.save()
            
            # Assign file if provided
            if file_obj:
                manual.upload_attachment = file_obj
                manual.save()
                
            return Response({"message": "CarNumber saved as draft", "data": serializer.data}, 
                           status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SupplierproblemDraftAllList(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        record = SupplierProblem.objects.filter(user=user, is_draft=True)
        serializer =SupplierProblemGetSerializer(record, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class ProcedureDraftEditView(APIView):
    def put(self, request, id):
        logger.info("Received manual edit request.")

        try:
            # Try to get the manual by ID
            manual = Procedure.objects.get(id=id)
            
            # Create a serializer instance for updating the manual
            serializer = ProcedureSerializer(manual, data=request.data, partial=True)
            
            if serializer.is_valid():
                try:
                    with transaction.atomic():
                        # Save the changes to the manual
                        manual = serializer.save()

                        # Set `is_draft` to False when the manual is edited
                        manual.is_draft = False  # This is crucial for your requirement

                        # Apply the changes to the manual
                        manual.save()

                        logger.info(f"Procedure updated successfully with ID: {manual.id}")

                        # Send notifications and emails like in manual creation
                        if manual.checked_by:
                            if manual.send_notification_to_checked_by:
                                self._send_notifications(manual)

                            if manual.send_email_to_checked_by and manual.checked_by.email:
                                self.send_email_notification(manual, manual.checked_by, "review")

                        return Response(
                            {"message": "Procedure updated successfully", "id": manual.id},
                            status=status.HTTP_200_OK
                        )

                except Exception as e:
                    logger.error(f"Error during Procedure update: {str(e)}")
                    return Response(
                        {"error": "An unexpected error occurred."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Procedure.DoesNotExist:
            return Response({"error": "Procedure not found."}, status=status.HTTP_404_NOT_FOUND)

    def _send_notifications(self, manual):
     
        if manual.checked_by:
            try:
                NotificatioProcedure.objects.create(
                    user=manual.checked_by,
                    procedure=manual,
                    title="Notification for Checking/Review",
                    message="A Procedure has been created/updated for your review."
                )
                logger.info(f"Notification created for checked_by user {manual.checked_by.id}")
            except Exception as e:
                logger.error(f"Error creating notification for checked_by: {str(e)}")

    def send_email_notification(self, procedure, recipient, action_type):
        recipient_email = recipient.email if recipient else None

        if recipient_email:
            try:
                if action_type == "review":
                    subject = f"Procedure Ready for Review: {procedure.title}"
                   

                    context = {
                        'recipient_name': recipient.first_name,
                        'title': procedure.title,
                        'document_number': procedure.no or 'N/A',
                        'review_frequency_year': procedure.review_frequency_year or 0,
                        'review_frequency_month': procedure.review_frequency_month or 0,
                        'document_type': procedure.document_type,
                        'section_number': procedure.no,
                        'rivision': procedure.rivision,
                        "written_by": procedure.written_by,
                        "checked_by": procedure.checked_by,
                        "approved_by": procedure.approved_by,
                        'date': procedure.date,
                        'document_url': procedure.upload_attachment.url if procedure.upload_attachment else None,
                        'document_name': procedure.upload_attachment.name.rsplit('/', 1)[-1] if procedure.upload_attachment else None,
                    }

                    html_message = render_to_string('qms/Procedure/Procedure_to_checked_by.html', context)
                    plain_message = strip_tags(html_message)

                
                    email = EmailMultiAlternatives(
                        subject=subject,
                        body=plain_message,
                        from_email=config("DEFAULT_FROM_EMAIL"),
                        to=[recipient_email]
                    )
                    email.attach_alternative(html_message, "text/html")

                    # Attach document if available
                    if procedure.upload_attachment:
                        try:
                            file_name = procedure.upload_attachment.name.rsplit('/', 1)[-1]
                            file_content = procedure.upload_attachment.read()
                            email.attach(file_name, file_content)
                            logger.info(f"Attached procedure document {file_name} to email")
                        except Exception as attachment_error:
                            logger.error(f"Error attaching procedure file: {str(attachment_error)}")

  
                    connection = CertifiEmailBackend(
                        host=config('EMAIL_HOST'),
                        port=config('EMAIL_PORT'),
                        username=config('EMAIL_HOST_USER'),
                        password=config('EMAIL_HOST_PASSWORD'),
                        use_tls=True
                    )

                    email.connection = connection
                    email.send(fail_silently=False)

                    logger.info(f"Email with attachment successfully sent to {recipient_email} for action: {action_type}")
                else:
                    logger.warning("Unknown action type provided for email.")
                    return
            except Exception as e:
                logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        else:
            logger.warning("Recipient email is None. Skipping email send.")
            
            
class EvaluationDraftEditView(APIView):
    def put(self, request, id):
        logger.info("Received manual edit request.")

        try:
            # Try to get the manual by ID
            manual = Evaluation.objects.get(id=id)
            
            # Create a serializer instance for updating the manual
            serializer = EvaluationSerializer(manual, data=request.data, partial=True)
            
            if serializer.is_valid():
                try:
                    with transaction.atomic():
                        # Save the changes to the manual
                        manual = serializer.save()

                        # Set `is_draft` to False when the manual is edited
                        manual.is_draft = False  # This is crucial for your requirement

                        # Apply the changes to the manual
                        manual.save()

                        logger.info(f"Evaluation updated successfully with ID: {manual.id}")

                        # Send notifications and emails like in manual creation
                        if manual.checked_by:
                            if manual.send_notification_to_checked_by:
                                self._send_notifications(manual)

                            if manual.send_email_to_checked_by and manual.checked_by.email:
                                self.send_email_notification(manual, manual.checked_by, "review")

                        return Response(
                            {"message": "Evaluation updated successfully", "id": manual.id},
                            status=status.HTTP_200_OK
                        )

                except Exception as e:
                    logger.error(f"Error during Evaluation update: {str(e)}")
                    return Response(
                        {"error": "An unexpected error occurred."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Evaluation.DoesNotExist:
            return Response({"error": "Evaluation not found."}, status=status.HTTP_404_NOT_FOUND)

    def _send_notifications(self, manual):
        # Your notification sending logic (same as in the creation view)
        if manual.checked_by:
            try:
                # Using the correct model name 'NotificationEvaluations' (plural)
                NotificationEvaluations.objects.create(
                    user=manual.checked_by,
                    evaluation=manual,
                    title="Notification for Checking/Review",
                    message="A Evaluation has been created for your review."
                )
                logger.info(f"Notification created for checked_by user {manual.checked_by.id}")
            except Exception as e:
                logger.error(f"Error creating notification for checked_by: {str(e)}")

    def send_email_notification(self, procedure, recipient, action_type):
        recipient_email = recipient.email if recipient else None
        
        if recipient_email:
            try:
                if action_type == "review":
                    subject = f"Procedure Ready for Review: {procedure.title}"
                    context = {
                        'recipient_name': recipient.first_name,
                        'title': procedure.title,
                        'document_number': procedure.no or 'N/A',
                        'review_frequency_year': procedure.review_frequency_year or 0,
                        'review_frequency_month': procedure.review_frequency_month or 0,
                        'document_type': procedure.document_type,
                        'section_number': procedure.no,
                        'rivision': procedure.rivision,
                        "written_by": procedure.written_by,
                        "checked_by": procedure.checked_by,
                        "approved_by": procedure.approved_by,
                        'date': procedure.date,
                        'document_url': procedure.upload_attachment.url if procedure.upload_attachment else None,
                        'document_name': procedure.upload_attachment.name.rsplit('/', 1)[-1] if procedure.upload_attachment else None,
                    }

                    html_message = render_to_string('qms/evaluation/evaluation_to_checked_by.html', context)
                    plain_message = strip_tags(html_message)

                    
                    email = EmailMultiAlternatives(
                        subject=subject,
                        body=plain_message,
                        from_email=config("DEFAULT_FROM_EMAIL"),
                        to=[recipient_email]
                    )
                    email.attach_alternative(html_message, "text/html")

              
                    if procedure.upload_attachment:
                        try:
                            file_name = procedure.upload_attachment.name.rsplit('/', 1)[-1]
                            file_content = procedure.upload_attachment.read()
                            email.attach(file_name, file_content)
                            logger.info(f"Attached evaluation document {file_name} to email")
                        except Exception as attachment_error:
                            logger.error(f"Error attaching evaluation file: {str(attachment_error)}")

                    # Use the custom email backend
                    connection = CertifiEmailBackend(
                        host=config('EMAIL_HOST'),
                        port=config('EMAIL_PORT'),
                        username=config('EMAIL_HOST_USER'),
                        password=config('EMAIL_HOST_PASSWORD'),
                        use_tls=True
                    )

                    email.connection = connection
                    email.send(fail_silently=False)

                    logger.info(f"Email with attachment successfully sent to {recipient_email} for action: {action_type}")
                else:
                    logger.warning("Unknown action type provided for email.")
                    return
            except Exception as e:
                logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        else:
            logger.warning("Recipient email is None. Skipping email send.")
            
            

class RecordraftEditView(APIView):
    def put(self, request, id):
        logger.info("Received manual edit request.")

        try:
            # Try to get the manual by ID
            manual = RecordFormat.objects.get(id=id)
            
            # Create a serializer instance for updating the manual
            serializer = RecordFormatSerializer(manual, data=request.data, partial=True)
            
            if serializer.is_valid():
                try:
                    with transaction.atomic():
                        # Save the changes to the manual
                        manual = serializer.save()

                        # Set `is_draft` to False when the manual is edited
                        manual.is_draft = False  # This is crucial for your requirement

                        # Apply the changes to the manual
                        manual.save()

                        logger.info(f"Evaluation updated successfully with ID: {manual.id}")

                        # Send notifications and emails like in manual creation
                        if manual.checked_by:
                            if manual.send_notification_to_checked_by:
                                self._send_notifications(manual)

                            if manual.send_email_to_checked_by and manual.checked_by.email:
                                self.send_email_notification(manual, manual.checked_by, "review")

                        return Response(
                            {"message": "RecordFormat updated successfully", "id": manual.id},
                            status=status.HTTP_200_OK
                        )

                except Exception as e:
                    logger.error(f"Error during RecordFormat update: {str(e)}")
                    return Response(
                        {"error": "An unexpected error occurred."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except RecordFormat.DoesNotExist:
            return Response({"error": "RecordFormat not found."}, status=status.HTTP_404_NOT_FOUND)

    def _send_notifications(self, manual):
        # Your notification sending logic (same as in the creation view)
        if manual.checked_by:
            try:
                NotificationRecord.objects.create(
                    user=manual.checked_by,
                    record=manual,
                    title="Notification for Checking/Review",
                    message="A RecordFormat has been created for your review."
                )
                logger.info(f"Notification created for checked_by user {manual.checked_by.id}")
            except Exception as e:
                logger.error(f"Error creating notification for checked_by: {str(e)}")

    def send_email_notification(self, record, recipient, action_type):
        recipient_email = recipient.email if recipient else None

        if recipient_email:
            try:
                if action_type == "review":
                    subject = f"Record Format Ready for Review: {record.title}"
          
                    context = {
                        'recipient_name': recipient.first_name,
                        'title': record.title,
                        'document_number': record.no or 'N/A',
                        'review_frequency_year': record.review_frequency_year or 0,
                        'review_frequency_month': record.review_frequency_month or 0,
                        'document_type': record.document_type,
                        'section_number': record.no,
                        'rivision': record.rivision,
                        "written_by": record.written_by,
                        "checked_by": record.checked_by,
                        "approved_by": record.approved_by,
                        'date': record.date,
                        'document_url': record.upload_attachment.url if record.upload_attachment else None,
                        'document_name': record.upload_attachment.name.rsplit('/', 1)[-1] if record.upload_attachment else None,
                    }

                    html_message = render_to_string('qms/record/record_to_checked_by.html', context)
                    plain_message = strip_tags(html_message)
 
                    email = EmailMultiAlternatives(
                        subject=subject,
                        body=plain_message,
                        from_email=config("DEFAULT_FROM_EMAIL"),
                        to=[recipient_email]
                    )
                    email.attach_alternative(html_message, "text/html")

                    # Attach document if available
                    if record.upload_attachment:
                        try:
                            file_name = record.upload_attachment.name.rsplit('/', 1)[-1]
                            file_content = record.upload_attachment.read()
                            email.attach(file_name, file_content)
                            logger.info(f"Attached record document {file_name} to email")
                        except Exception as attachment_error:
                            logger.error(f"Error attaching record file: {str(attachment_error)}")

     
                    connection = CertifiEmailBackend(
                        host=config('EMAIL_HOST'),
                        port=config('EMAIL_PORT'),
                        username=config('EMAIL_HOST_USER'),
                        password=config('EMAIL_HOST_PASSWORD'),
                        use_tls=True
                    )

                    email.connection = connection
                    email.send(fail_silently=False)

                    logger.info(f"Email with attachment successfully sent to {recipient_email} for action: {action_type}")
                else:
                    logger.warning("Unknown action type provided for email.")
                    return
            except Exception as e:
                logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        else:
            logger.warning("Recipient email is None. Skipping email send.")
            
            
class ProcessDraftEditView(APIView):
    """
    Endpoint to handle updating of a draft process to a final process with optional notifications.
    """
    def put(self, request, pk):
        try:
            process = get_object_or_404(Processes, pk=pk, is_draft=True)
            print("Editing draft process:", process.name)
            print("Received Data:", request.data)  # Print all the received data
            
            # More flexible handling of send_notification flag
            send_notification_value = request.data.get('send_notification', 'false')
            if isinstance(send_notification_value, bool):
                send_notification = send_notification_value
            else:
                send_notification = str(send_notification_value).lower() == 'true' or send_notification_value == '1'
            print(f"Send notification value: {send_notification_value}, Interpreted as: {send_notification}")
            
            # Extract legal_requirements IDs from request data
            legal_requirements = request.data.get('legal_requirements', [])
            if legal_requirements and not isinstance(legal_requirements, list):
                legal_requirements = [legal_requirements]
            print("Legal Requirements IDs:", legal_requirements)
            
            # Check for custom legal requirements
            has_custom_text = 'custom_legal_requirements' in request.data and request.data.get('custom_legal_requirements', '').strip()
            
            # Create a mutable copy of the data
            data = request.data.copy()
            
            # Ensure is_draft is set to False when finalizing
            data['is_draft'] = False
            
            # Handle file upload if present
            file_obj = request.FILES.get('file') or request.FILES.get('upload_attachment')
            
            serializer = ProcessManySerializer(process, data=data, partial=True)
            
            if serializer.is_valid():
                with transaction.atomic():
                    instance = serializer.save(is_draft=False)
                    logger.info(f"Draft process finalized: {instance.name}")
                    print(f"Draft process finalized: {instance.name} - ID: {instance.id}")
                    
                    # Update and save send_notification flag
                    instance.send_notification = send_notification
                    
                    # Handle file if present
                    if file_obj:
                        instance.file = file_obj
                    
                    # Handle legal requirements
                    if has_custom_text:
                        instance.legal_requirements.clear()
                        print("Custom text provided - cleared all legal requirements")
                    else:
                        # Convert to integers, handling strings and non-digit values
                        req_ids = []
                        for req_id in legal_requirements:
                            try:
                                if req_id and str(req_id).isdigit():
                                    req_ids.append(int(req_id))
                            except (ValueError, TypeError):
                                print(f"Skipping invalid legal requirement ID: {req_id}")
                                
                        instance.legal_requirements.set(req_ids)
                        print(f"Set legal requirements to: {req_ids}")
                    
                    instance.save()
                    
                    # Send notifications if enabled
                    email_success_count = 0
                    email_failure_count = 0
                    
                    if send_notification:
                        # Get company and users
                        company = instance.company
                        company_users = Users.objects.filter(company=company)
                        users_count = company_users.count()
                        print(f"Users to notify: {users_count}")
                        
                        if not company_users.exists():
                            print("No users found for this company - no notifications will be sent")
                        
                        notifications = []
                        for user in company_users:
                            # Create notification object
                            notifications.append(
                                NotificationProcess(
                                    processes=instance,
                                    title=f"New Process Published: {instance.name}",
                                    message=f"The draft process '{instance.name}' has been finalized and published."
                                )
                            )
                            
                            # Try to send email to all users
                            if user.email:
                                try:
                                    email_sent = self._send_notification_email(instance, user)
                                    if email_sent:
                                        email_success_count += 1
                                    else:
                                        email_failure_count += 1
                                except Exception as e:
                                    email_failure_count += 1
                                    logger.error(f"Failed to send email to {user.email}: {str(e)}")
                                    print(f"Failed to send email to {user.email}: {str(e)}")
                            else:
                                print(f"User ID {user.id} has no email address - skipping email")
                        
                        # Bulk create notifications
                        if notifications:
                            NotificationProcess.objects.bulk_create(notifications)
                            logger.info(f"Created {len(notifications)} notifications for process publication {instance.id}")
                            print(f"Created {len(notifications)} notifications for process publication {instance.id}")
                        
                        print(f"Email sending summary: {email_success_count} succeeded, {email_failure_count} failed")
                
                return Response(
                    {
                        "message": "Draft process published successfully",
                        "notification_sent": send_notification,
                        "email_stats": {
                            "success": email_success_count if send_notification else 0,
                            "failure": email_failure_count if send_notification else 0
                        },
                        "data": ProcessManySerializer(instance).data
                    },
                    status=status.HTTP_200_OK
                )
                
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error publishing draft process: {str(e)}")
            print(f"Error publishing draft process: {str(e)}")
            return Response(
                {"error": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _send_notification_email(self, process, recipient):
        """
        Sends an HTML email with optional attachment using custom backend.
        """
        # Debug email configuration
        print("Email configuration:")
        print(f"Host: {config('EMAIL_HOST')}")
        print(f"Port: {config('EMAIL_PORT')}")
        print(f"User: {config('EMAIL_HOST_USER')}")
        print(f"Password set: {'Yes' if config('EMAIL_HOST_PASSWORD') else 'No'}")
        
        recipient_email = recipient.email
        if not recipient_email:
            print("Recipient email is missing.")
            logger.warning("Recipient email is missing.")
            return False

        try:
            print(f"Preparing to send process publication email to {recipient_email}")
            logger.info(f"Preparing to send process publication email to {recipient_email}")

            subject = f"New Process Published: {process.name}"

            context = {
                'recipient_name': recipient.first_name,
                'name': process.name,
                'number': process.no,
                'category': process.type,
                'legal_requirements': [req.title for req in process.legal_requirements.all()],
                'custom_legal_requirements': process.custom_legal_requirements,
                'user_first_name': process.user.first_name if process.user else '',
                'user_last_name': process.user.last_name if process.user else '',
                'is_draft_published': True,  # Flag to indicate this is a draft being published
            }

            # Use the same template as process_update.html
            html_message = render_to_string('qms/process/process_add.html', context)
            plain_message = strip_tags(html_message)

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=config("DEFAULT_FROM_EMAIL"),
                to=[recipient_email]
            )
            email.attach_alternative(html_message, "text/html")

            if process.file:
                try:
                    file_name = process.file.name.split('/')[-1]
                    file_content = process.file.read()
                    email.attach(file_name, file_content)
                    print(f"Attached process document: {file_name}")
                    logger.info(f"Attached process document: {file_name}")
                except Exception as e:
                    print(f"Error attaching process document: {str(e)}")
                    logger.error(f"Error attaching process document: {str(e)}")

            # Use custom backend
            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )
            email.connection = connection

            # Sending the email with specific error handling
            try:
                print("Sending the email...")
                email.send(fail_silently=False)
                
                print(f"Publication notification email sent to {recipient_email}")
                logger.info(f"Publication notification email sent to {recipient_email}")
                return True  # Indicate success
            except smtplib.SMTPException as smtp_e:
                # Handle specific SMTP errors
                print(f"SMTP Error sending to {recipient_email}: {str(smtp_e)}")
                logger.error(f"SMTP Error sending to {recipient_email}: {str(smtp_e)}")
                return False
            except Exception as e:
                print(f"Failed to send email to {recipient_email}: {str(e)}")
                logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
                return False

        except Exception as e:
            print(f"Failed to send email to {recipient_email}: {str(e)}")
            logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
            return False
        
        
class InterestedPartyEditDraftView(APIView):
    """
    Endpoint to handle editing of Draft Interested Party, making it final, and optionally sending notifications.
    """
    def put(self, request, draft_id):
        print("Received Data for Draft Edit:", request.data)  # Print all incoming data for debugging
        try:
            # Find the draft interested party
            try:
                interested_party = InterestedParty.objects.get(id=draft_id, is_draft=True)
            except InterestedParty.DoesNotExist:
                return Response(
                    {"error": "Draft not found or already published"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Handle the case where request.data is a list instead of a dictionary
            request_data = request.data
            if isinstance(request_data, list) and len(request_data) > 0:
                request_data = request_data[0]
                print("Converted list data to dictionary:", request_data)
            
            # Extract data from the request
            company_id = request_data.get('company')
            send_notification = request_data.get('send_notification', False)  # Default to False if not provided
            needs_data = request_data.get('needs', [])

            # Debugging print statements
            print(f"Company ID: {company_id}")
            print(f"Send Notification: {send_notification}")
            print(f"Needs Data: {needs_data}")

            # Check if company_id is provided
            if not company_id:
                return Response(
                    {"error": "Company ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            company = Company.objects.get(id=company_id)
            serializer = InterestedPartySerializer(interested_party, data=request_data, partial=True)

            # Validate the serializer and proceed if valid
            if serializer.is_valid():
                with transaction.atomic():
                    # Set is_draft to False to publish it
                    serializer.validated_data['is_draft'] = False
                    interested_party = serializer.save()
                    logger.info(f"Interested Party published from draft: {interested_party.name}")

                    # Log the interested party data
                    print(f"Interested Party Published: {interested_party.name}")
                    print(f"Interested Party ID: {interested_party.id}")
                    print(f"Interested Party Send Notification: {interested_party.send_notification}")
                    
                    # Handle file upload if provided
                    file_obj = request.FILES.get('upload_attachment') if hasattr(request, 'FILES') else None
                    if file_obj:
                        interested_party.file = file_obj
                        interested_party.save()
                        logger.info(f"Uploaded attachment for Interested Party {interested_party.id}")

                    # Update needs with both needs and expectations fields
                    if needs_data is not None:
                        # Delete existing needs
                        Needs.objects.filter(interested_party=interested_party).delete()
                        
                        # Create new needs with both needs and expectations fields
                        needs_instances = []
                        for need_item in needs_data:
                            needs_instances.append(
                                Needs(
                                    interested_party=interested_party,
                                    needs=need_item.get('needs', ''),
                                    expectation=need_item.get('expectation', '')
                                )
                            )
                        
                        Needs.objects.bulk_create(needs_instances)
                        logger.info(f"Updated {len(needs_instances)} Needs for Interested Party {interested_party.id}")

                    # Save the send_notification flag
                    print(f"Setting Send Notification Flag to: {send_notification}")
                    interested_party.send_notification = send_notification
                    interested_party.save()

                    # If send_notification is True, send notifications and emails
                    if send_notification:
                        company_users = Users.objects.filter(company=company)
                        notifications = [
                            NotificationInterest(
                                interest=interested_party,
                                title=f"Interested Party Published: {interested_party.name}",
                                message=f"An interested party '{interested_party.name}' has been published from draft."
                            )
                            for user in company_users
                        ]

                        if notifications:
                            NotificationInterest.objects.bulk_create(notifications)
                            logger.info(f"Created {len(notifications)} notifications for Interested Party {interested_party.id}")
                        else:
                            print("No notifications to send.")

                        # Send email notifications to users
                        for user in company_users:
                            if user.email:
                                try:
                                    self._send_notification_email(interested_party, user)
                                except Exception as e:
                                    logger.error(f"Failed to send email to {user.email}: {str(e)}")
                                    print(f"Failed to send email to {user.email}: {str(e)}")
                    else:
                        print("Notification flag is set to False. Skipping notifications and emails.")

                return Response(
                    {
                        "message": "Interested Party published successfully from draft",
                        "notification_sent": send_notification
                    },
                    status=status.HTTP_200_OK
                )
            else:
                # Log serializer errors for debugging
                logger.warning(f"Validation error: {serializer.errors}")
                print(f"Validation error: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Company.DoesNotExist:
            return Response(
                {"error": "Company not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            print(f"Error occurred: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _send_notification_email(self, interested_party, recipient, manual=None):
        """
        Sends an HTML email with optional attachments (Interested Party + Manual) using a secure backend.
        """
        recipient_email = recipient.email
        if not recipient_email:
            logger.warning("Recipient email is missing.")
            print("Recipient email is missing.")
            return

        try:
            logger.info(f"Preparing to send email to {recipient_email}")
            subject = f"Interested Party Published: {interested_party.name}"

            # Get all needs objects for this interested party 
            all_needs = interested_party.needs.all()
 
            context = {
                'recipient_name': recipient.first_name,
                'name': interested_party.name,
                'category': interested_party.category,
                'needs': [need.needs for need in all_needs if need.needs],
                'expectations': [need.expectation for need in all_needs if need.expectation],
                'special_requirements': interested_party.special_requirements,
                'legal_requirements': interested_party.legal_requirements,
                'custom_legal_requirements': interested_party.custom_legal_requirements,
                'user_first_name': interested_party.user.first_name if interested_party.user else '',
                'user_last_name': interested_party.user.last_name if interested_party.user else '',
            }

            html_message = render_to_string('qms/interested_party/intereste_party_add.html', context)
            plain_message = strip_tags(html_message)

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=config("DEFAULT_FROM_EMAIL"),
                to=[recipient_email]
            )
            email.attach_alternative(html_message, "text/html")
 
            if interested_party.file:
                try:
                    file_name = interested_party.file.name.split('/')[-1]
                    file_content = interested_party.file.read()
                    email.attach(file_name, file_content)
                    logger.info(f"Attached Interested Party document: {file_name}")
                except Exception as e:
                    logger.error(f"Error attaching Interested Party document: {str(e)}")
                    print(f"Error attaching Interested Party document: {str(e)}")
                    
            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )

            email.connection = connection
            email.send(fail_silently=False)

            logger.info(f"Notification email sent to {recipient_email}")
            print(f"Notification email sent to {recipient_email}")

        except Exception as e:
            logger.error(f"Failed to send notification email to {recipient_email}: {str(e)}")
            print(f"Failed to send notification email to {recipient_email}: {str(e)}")
            
            
# Add these imports at the top of your file if not already there
import mimetypes
import traceback

class EditsDraftCompliance(APIView):
    def put(self, request, pk):
        print("Received data:", request.data)
        
        # Get the existing compliance record
        compliance = get_object_or_404(Compliances, pk=pk)
        
        mutable_data = request.data.copy()
        
        if 'attach_document' in mutable_data and not request.FILES.get('attach_document'):
            print("Removing attach_document from request because it's not a file")
            mutable_data.pop('attach_document')
      
        # Set is_draft to False
        mutable_data['is_draft'] = False
        
        # Update the existing instance instead of creating a new one
        serializer = ComplianceSerializer(compliance, data=mutable_data, partial=True)

        if serializer.is_valid():
            compliance_instance = serializer.save()

       
            file_obj = request.FILES.get('attach_document')
            if file_obj:
                compliance_instance.attach_document = file_obj
                compliance_instance.save()

            if compliance_instance.send_notification:
                company = compliance_instance.company
                company_users = Users.objects.filter(company=company)

                notifications = [
                    ComplianceNotification(
                        compliance=compliance_instance,
                        title=f"Add Compliance: {compliance_instance.compliance_name}",
                        message=f"The compliance '{compliance_instance.compliance_name}' has been created."
                    )
                    for user in company_users
                ]
                
                if notifications:
                    ComplianceNotification.objects.bulk_create(notifications)
                    logger.info(f"Created {len(notifications)} notifications for compliance {compliance_instance.id}")

                for user in company_users:
                    if user.email:
                        try:
                            self._send_notification_email(compliance_instance, user)
                        except Exception as e:
                            logger.error(f"Failed to send email to {user.email}: {str(e)}")

            return Response(ComplianceSerializer(compliance_instance).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _send_notification_email(self, compliance, recipient):
        subject = f"Compliance Updated: {compliance.compliance_name}"
        recipient_email = recipient.email

        print(f"Preparing to send email to: {recipient_email}")

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

        try:
            # Prepare HTML message
            html_message = render_to_string('qms/compliance/compliance_add_template.html', context)
            plain_message = strip_tags(html_message)

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=config("DEFAULT_FROM_EMAIL"),
                to=[recipient_email]
            )
            email.attach_alternative(html_message, "text/html")

            # Attach compliance document if available
            if compliance.attach_document:
                try:
                    # Reset file pointer to the beginning
                    compliance.attach_document.seek(0)
                    
                    # Get file name
                    file_name = compliance.attach_document.name.rsplit('/', 1)[-1]
                    
                    # Read content
                    file_content = compliance.attach_document.read()
                    
                    # Determine MIME type
                    content_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
                    
                    # Attach with proper content type
                    email.attach(file_name, file_content, content_type)
                    
                    print(f"Attached compliance document: {file_name} with content type {content_type}")
                except Exception as attachment_error:
                    print(f"Error attaching compliance file: {str(attachment_error)}")
                    traceback.print_exc()  # Print full traceback for debugging

            # Send email via custom email backend
            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )

            email.connection = connection
            email.send(fail_silently=False)

            print(f"Email successfully sent to {recipient_email}")

        except Exception as e:
            print(f"Error sending email to {recipient_email}: {e}")
            traceback.print_exc()   
            
            
 

class EditsDraftManagementChanges(APIView):
    def put(self, request, pk):
        print("Received data:", request.data)

        # Get the existing ManagementChanges record
        change = get_object_or_404(ManagementChanges, pk=pk)

        mutable_data = request.data.copy()

        # Remove non-file 'attach_document' if it's not being re-uploaded
        if 'attach_document' in mutable_data and not request.FILES.get('attach_document'):
            print("Removing attach_document from request because it's not a file")
            mutable_data.pop('attach_document')

        # Set is_draft to False
        mutable_data['is_draft'] = False

        # Update the instance
        serializer = ChangesSerializer(change, data=mutable_data, partial=True)

        if serializer.is_valid():
            with transaction.atomic():
                change_instance = serializer.save()

                # Save file if re-uploaded
                file_obj = request.FILES.get('attach_document')
                if file_obj:
                    change_instance.attach_document = file_obj
                    change_instance.save()

                if change_instance.send_notification:
                    company = change_instance.company
                    company_users = Users.objects.filter(company=company)

                    notifications = [
                        NotificationChanges(
                            changes=change_instance,
                            title=f"Updated Change: {change_instance.moc_title}",
                            message=f"The management change '{change_instance.moc_title}' has been updated."
                        )
                        for user in company_users
                    ]

                    if notifications:
                        NotificationChanges.objects.bulk_create(notifications)
                        logger.info(f"Created {len(notifications)} notifications for change ID {change_instance.id}")

                    for user in company_users:
                        if user.email:
                            try:
                                self._send_notification_email(change_instance, user)
                            except Exception as e:
                                logger.error(f"Failed to send email to {user.email}: {str(e)}")

            return Response(ChangesSerializer(change_instance).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _send_notification_email(self, change, recipient):
        subject = f"Updated Management Change: {change.moc_title}"
        recipient_email = recipient.email

        print(f"Preparing to send email to: {recipient_email}")

        context = {
            'recipient_name': recipient.first_name,
            'moc_title': change.moc_title,
            'moc_type': change.moc_type,
            'moc_no': change.moc_no,
            'rivision': change.rivision,
            'date': change.date,
            'related_record_format': change.related_record_format,
            'resources_required': change.resources_required,
            'impact_on_process': change.impact_on_process,
            'purpose_of_chnage': change.purpose_of_chnage,
            'potential_cosequences': change.potential_cosequences,
            'moc_remarks': change.moc_remarks,
            'created_by': change.user,
        }

        try:
            html_message = render_to_string('qms/changes/changes_add_template.html', context)
            plain_message = strip_tags(html_message)

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=config("DEFAULT_FROM_EMAIL"),
                to=[recipient_email]
            )
            email.attach_alternative(html_message, "text/html")

            # Attach document if exists
            if change.attach_document:
                try:
                    change.attach_document.seek(0)
                    file_name = change.attach_document.name.rsplit('/', 1)[-1]
                    file_content = change.attach_document.read()
                    content_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
                    email.attach(file_name, file_content, content_type)
                    print(f"Attached document: {file_name} with type {content_type}")
                except Exception as attachment_error:
                    print(f"Attachment error: {attachment_error}")
                    traceback.print_exc()

            # Send using secure backend
            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )

            email.connection = connection
            email.send(fail_silently=False)
            print(f"Email sent to {recipient_email}")

        except Exception as e:
            print(f"Error sending email: {e}")
            traceback.print_exc()


class EditDraftTrainingAPIView(APIView):
    """
    Edit an existing draft training. On save, is_draft becomes False and 
    it behaves like training creation (including notifications and emails).
    """
    def put(self, request, pk):
        print("Received Data:", request.data)

        training = get_object_or_404(Training, pk=pk)

        mutable_data = request.data.copy()

        # Automatically mark as not draft
        mutable_data['is_draft'] = False

        send_notification = mutable_data.get('send_notification', 'false') == 'true'

        # Remove attachment if not actually uploaded
        if 'attachment' in mutable_data and not request.FILES.get('attachment'):
            print("Removing 'attachment' field because no file was uploaded.")
            mutable_data.pop('attachment')

        serializer = TrainingSerializer(training, data=mutable_data, partial=True)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    training_instance = serializer.save()

                    # Handle file attachment if present
                    file_obj = request.FILES.get('attachment')
                    if file_obj:
                        training_instance.attachment = file_obj
                        training_instance.save()

                    logger.info(f"Draft Training Added: {training_instance.training_title}")

                    # Notifications
                    if send_notification:
                        attendees = training_instance.training_attendees.all()
                        users_to_notify = [
                            training_instance.evaluation_by,
                            training_instance.requested_by,
                            *attendees
                        ]

                        notifications = [
                            TrainingNotification(
                                training=training_instance,
                                title=f"Training Finalized: {training_instance.training_title}",
                                message=f"The training '{training_instance.training_title}' has been finalized."
                            )
                            for user in users_to_notify if user
                        ]

                        if notifications:
                            TrainingNotification.objects.bulk_create(notifications)
                            logger.info(f"Created {len(notifications)} notifications for training {training_instance.id}")

                        # Email users asynchronously
                        for user in users_to_notify:
                            if user and user.email:
                                self._send_email_async(training_instance, user)

                return Response(
                    {
                        "message": "Draft training Added successfully and finalized.",
                        "notification_sent": send_notification
                    },
                    status=status.HTTP_200_OK
                )

            except Exception as e:
                logger.error(f"Error finalizing draft training: {str(e)}")
                return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.warning(f"Validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _send_email_async(self, training, recipient):
        threading.Thread(target=self._send_notification_email, args=(training, recipient)).start()

    def _send_notification_email(self, training, recipient):
        subject = f"Finalized Training: {training.training_title}"
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
            'created_by': training.user
        }

        html_message = render_to_string('qms/training/training_add.html', context)
        plain_message = strip_tags(html_message)

        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=config("DEFAULT_FROM_EMAIL"),
            to=[recipient_email]
        )
        email.attach_alternative(html_message, "text/html")

        if training.attachment:
            try:
                file_name = training.attachment.name.rsplit('/', 1)[-1]
                training.attachment.seek(0)
                file_content = training.attachment.read()
                email.attach(file_name, file_content)
            except Exception as e:
                print(f"Attachment error: {e}")

        connection = CertifiEmailBackend(
            host=config('EMAIL_HOST'),
            port=config('EMAIL_PORT'),
            username=config('EMAIL_HOST_USER'),
            password=config('EMAIL_HOST_PASSWORD'),
            use_tls=True
        )
        email.connection = connection
        email.send(fail_silently=False)
        print(f"Email sent to {recipient_email}")



class MeetingUpdateDraftView(APIView):
    def put(self, request, pk):
        print("Received data:", request.data)

        # Get the existing meeting record
        meeting = get_object_or_404(Meeting, pk=pk)

        # Copy the request data to make modifications (e.g., removing the file if not provided)
        mutable_data = request.data.copy()

        # If the meeting is currently in draft, set is_draft to False to make it a finalized meeting
        mutable_data['is_draft'] = False

        # Check if the meeting is being updated with a document
        if 'file' in mutable_data and not request.FILES.get('file'):
            print("Removing file from request because it's not a file")
            mutable_data.pop('file')

        # Use the serializer to validate and update the meeting
        serializer = MeetingSerializer(meeting, data=mutable_data, partial=True)

        if serializer.is_valid():
            # Save the updated meeting data
            meeting_instance = serializer.save()

            # Handle file attachment if provided
            file_obj = request.FILES.get('file')
            if file_obj:
                meeting_instance.file = file_obj
                meeting_instance.save()

            # If notifications are enabled, send notifications and emails to attendees
            if meeting_instance.send_notification:
                attendees = meeting_instance.attendees.all()
                notifications = [
                    MeetingNotification(
                        user=attendee,
                        meeting=meeting_instance,
                        title=f"Meeting Updated: {meeting_instance.title}",
                        message=f"The meeting '{meeting_instance.title}' has been updated."
                    )
                    for attendee in attendees
                ]

                if notifications:
                    MeetingNotification.objects.bulk_create(notifications)
                    print(f"Created {len(notifications)} notifications for meeting {meeting_instance.id}")

                for attendee in attendees:
                    if attendee.email:
                        try:
                            self._send_notification_email(meeting_instance, attendee)
                        except Exception as e:
                            print(f"Failed to send email to {attendee.email}: {str(e)}")

            return Response(MeetingSerializer(meeting_instance).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _send_notification_email(self, meeting, recipient):
        subject = f"Meeting Updated: {meeting.title}"
        recipient_email = recipient.email

        print(f"Preparing to send email to: {recipient_email}")

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
            'created_by':meeting.user
        }

        try:
            # Prepare HTML message
            html_message = render_to_string('qms/meeting/meeting_add.html', context)
            plain_message = strip_tags(html_message)

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=config("DEFAULT_FROM_EMAIL"),
                to=[recipient_email]
            )
            email.attach_alternative(html_message, "text/html")

            # Attach meeting document if available
            if meeting.file:
                try:
                    # Reset file pointer to the beginning
                    meeting.file.seek(0)
                    
                    # Get file name
                    file_name = meeting.file.name.rsplit('/', 1)[-1]
                    
                    # Read content
                    file_content = meeting.file.read()
                    
                    # Determine MIME type
                    content_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
                    
                    # Attach with proper content type
                    email.attach(file_name, file_content, content_type)
                    
                    print(f"Attached meeting document: {file_name} with content type {content_type}")
                except Exception as attachment_error:
                    print(f"Error attaching meeting file: {str(attachment_error)}")

            # Send email via custom email backend
            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )

            email.connection = connection
            email.send(fail_silently=False)

            print(f"Email successfully sent to {recipient_email}")

        except Exception as e:
            print(f"Error sending email to {recipient_email}: {e}")




class SustainabilityDraftEditView(APIView):
    def put(self, request, id):
        logger.info("Received sustainability edit request.")

        try:
            # Try to get the sustainability document by ID
            sustainability = Sustainabilities.objects.get(id=id)
            
            # Create a serializer instance for updating the document
            serializer = SustainabilitySerializer(sustainability, data=request.data, partial=True)
            
            if serializer.is_valid():
                try:
                    with transaction.atomic():
                        # Save the changes to the sustainability document
                        sustainability = serializer.save()

                        # Set `is_draft` to False when edited
                        sustainability.is_draft = False

                        # Apply the changes
                        sustainability.save()

                        logger.info(f"Sustainability document updated successfully with ID: {sustainability.id}")

                        # Send notifications and emails like in creation
                        if sustainability.checked_by:
                            if sustainability.send_notification_to_checked_by:
                                self._send_notifications(sustainability)

                            if sustainability.send_email_to_checked_by and sustainability.checked_by.email:
                                self.send_email_notification(sustainability, sustainability.checked_by, "review")

                        return Response(
                            {"message": "Sustainability document updated successfully", "id": sustainability.id},
                            status=status.HTTP_200_OK
                        )

                except Exception as e:
                    logger.error(f"Error during sustainability update: {str(e)}")
                    return Response(
                        {"error": "An unexpected error occurred."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Sustainabilities.DoesNotExist:
            return Response({"error": "Sustainability document not found."}, status=status.HTTP_404_NOT_FOUND)

    def _send_notifications(self, sustainability):
       
        if sustainability.checked_by:
            try:
                NotificationSustainability.objects.create(
                    user=sustainability.checked_by,
                    sustainability=sustainability,
                    title="Notification for Checking/Review",
                    message="A sustainability document has been created/updated for your review."
                )
                logger.info(f"Notification created for checked_by user {sustainability.checked_by.id}")
            except Exception as e:
                logger.error(f"Error creating notification for checked_by: {str(e)}")

    def send_email_notification(self, sustainability, recipient, action_type):
        recipient_email = recipient.email if recipient else None

        if recipient_email:
            try:
                if action_type == "review":
                    subject = f"Sustainability Document Ready for Review: {sustainability.title}"

                    context = {
                        'recipient_name': recipient.first_name,
                        'title': sustainability.title,
                        'document_number': sustainability.no or 'N/A',
                        'review_frequency_year': sustainability.review_frequency_year or 0,
                        'review_frequency_month': sustainability.review_frequency_month or 0,
                        'document_type': sustainability.document_type,
                        'section_number': sustainability.no,
                        'rivision': getattr(sustainability, 'rivision', ''),
                        "written_by": sustainability.written_by,
                        "checked_by": sustainability.checked_by,
                        "approved_by": sustainability.approved_by,
                        'date': sustainability.date,
                        'document_url': sustainability.upload_attachment.url if sustainability.upload_attachment else None,
                        'document_name': sustainability.upload_attachment.name.rsplit('/', 1)[-1] if sustainability.upload_attachment else None,
                    }

                    html_message = render_to_string('sustainability/sustainability_to_checked_by.html', context)
                    plain_message = strip_tags(html_message)

                    email = EmailMultiAlternatives(
                        subject=subject,
                        body=plain_message,
                        from_email=config("DEFAULT_FROM_EMAIL"),
                        to=[recipient_email]
                    )
                    email.attach_alternative(html_message, "text/html")

                    # Attach document if available
                    if sustainability.upload_attachment:
                        try:
                            file_name = sustainability.upload_attachment.name.rsplit('/', 1)[-1]
                            file_content = sustainability.upload_attachment.read()
                            email.attach(file_name, file_content)
                            logger.info(f"Attached sustainability document {file_name} to email")
                        except Exception as attachment_error:
                            logger.error(f"Error attaching sustainability file: {str(attachment_error)}")

                    connection = CertifiEmailBackend(
                        host=config('EMAIL_HOST'),
                        port=config('EMAIL_PORT'),
                        username=config('EMAIL_HOST_USER'),
                        password=config('EMAIL_HOST_PASSWORD'),
                        use_tls=True
                    )

                    email.connection = connection
                    email.send(fail_silently=False)

                    logger.info(f"Email with attachment successfully sent to {recipient_email} for action: {action_type}")
                else:
                    logger.warning("Unknown action type provided for email.")
                    return
            except Exception as e:
                logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        else:
            logger.warning("Recipient email is None. Skipping email send.")
            
            
            
class EditDraftLegalAPIView(APIView):
    def put(self, request, pk):
        print("Received Data for Edit Draft Legal:", request.data)

        legal = get_object_or_404(Legal, pk=pk)

        mutable_data = request.data.copy()
        file_obj = request.FILES.get('attach_document')

        if 'attach_document' in mutable_data and not file_obj:
            print("Removing attach_document from request as it is not a valid file.")
            mutable_data.pop('attach_document')

        mutable_data['is_draft'] = False  # Automatically set is_draft to False

        serializer = LegalSerializer(legal, data=mutable_data, partial=True)
        if serializer.is_valid():
            legal_instance = serializer.save()

            if file_obj:
                legal_instance.attach_document = file_obj
                legal_instance.save()

            send_notification = mutable_data.get('send_notification', 'false') == 'true'
            legal_instance.send_notification = send_notification
            legal_instance.save()

            if send_notification:
                company_users = Users.objects.filter(company=legal_instance.company)

                notifications = [
                    NotificationLegal(
                        legal=legal_instance,
                        title=f"Updated Legal: {legal_instance.legal_name}",
                        message=f"The legal requirement '{legal_instance.legal_name}' has been updated."
                    )
                    for user in company_users
                ]
                NotificationLegal.objects.bulk_create(notifications)

                for user in company_users:
                    if user.email:
                        threading.Thread(target=self._send_notification_email, args=(legal_instance, user)).start()

            return Response(LegalSerializer(legal_instance).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _send_notification_email(self, legal, recipient):
        subject = f"Legal Requirement Updated: {legal.legal_name}"
        recipient_email = recipient.email

        context = {
            'legal_name': legal.legal_name,
            'legal_no': legal.legal_no,
            'document_type': legal.document_type,
            'rivision': legal.rivision,
            'date': legal.date,
            'related_record_format': legal.related_record_format,
            'created_by': legal.user,
        }

        try:
            html_message = render_to_string('qms/legal/legal_add_template.html', context)
            plain_message = strip_tags(html_message)

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=config("DEFAULT_FROM_EMAIL"),
                to=[recipient_email]
            )
            email.attach_alternative(html_message, "text/html")

            if legal.attach_document:
                try:
                    legal.attach_document.seek(0)
                    file_name = legal.attach_document.name.rsplit('/', 1)[-1]
                    file_content = legal.attach_document.read()
                    content_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
                    email.attach(file_name, file_content, content_type)
                except Exception as attachment_error:
                    print(f"Error attaching document: {attachment_error}")
                    traceback.print_exc()

            connection = CertifiEmailBackend(
                host=config('EMAIL_HOST'),
                port=config('EMAIL_PORT'),
                username=config('EMAIL_HOST_USER'),
                password=config('EMAIL_HOST_PASSWORD'),
                use_tls=True
            )
            email.connection = connection
            email.send(fail_silently=False)

            print(f"Email sent to {recipient_email}")

        except Exception as e:
            print(f"Error sending email to {recipient_email}: {e}")
            traceback.print_exc()
            
            
class TrainingEvaluationCreateView(APIView):
    def post(self, request):
        serializer = TrainingEvaluationSerializer(data=request.data)
        if serializer.is_valid():
       
            serializer.save()   
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TrainingEvaluationAllList(APIView):
    def get(self, request, company_id):
        try:
        
            if not Company.objects.filter(id=company_id).exists():
                return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

           
            company_policies = EmployeeTrainingEvaluation.objects.filter(company_id=company_id ,is_draft=False)

           
            serializer = TrainingEvaluationSerializer(company_policies, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class  TrainingEvaluationUpdateView(APIView):
    def put(self, request, pk):
        try:
            documentation = EmployeeTrainingEvaluation.objects.get(pk=pk)
        except TrainingEvaluationSerializer.DoesNotExist:
            return Response({"error": "Employee Training Evaluation not found"}, status=status.HTTP_404_NOT_FOUND) 
        data = request.data.copy()      
        data['is_draft'] = False
        serializer = TrainingEvaluationSerializer(documentation, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            documentation = EmployeeTrainingEvaluation.objects.get(pk=pk)
        except EmployeeTrainingEvaluation.DoesNotExist:
            return Response({"error": "Employee Training Evaluation not found"}, status=status.HTTP_404_NOT_FOUND)
        
        documentation.delete()   
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class TrainingEvaluationDetailView(APIView):
    def get(self, request, id):
        policy = get_object_or_404(EmployeeTrainingEvaluation, id=id)
        serializer = TrainingEvaluationSerializer(policy)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class TrainingEvaluationDraftAPIView(APIView):
    def post(self, request, *args, **kwargs):
        
        data = {}

        
        for key in request.data:
            if key != 'upload_attachment':
                data[key] = request.data[key]
        
        
        data['is_draft'] = True
        
       
        file_obj = request.FILES.get('upload_attachment')

        
        serializer = TrainingEvaluationSerializer(data=data)
        if serializer.is_valid():
            evaluation = serializer.save()
            
            
            if file_obj:
                evaluation.upload_attachment = file_obj
                evaluation.save()

            return Response({
                "message": "Employee Evaluation saved as draft",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TrainingEvaluationDraftAllList(APIView):
    def get(self, request, user_id):
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        record = EmployeeTrainingEvaluation.objects.filter(user=user, is_draft=True)
        serializer =TrainingEvaluationSerializer(record, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TrainingEvaluationView(APIView):
 
    def get(self, request, user_id):
   
        draft_records = EmployeeTrainingEvaluation.objects.filter(is_draft=True, user_id=user_id)
        
        serializer = TrainingEvaluationSerializer(draft_records, many=True)
        
        return Response({
            "count": draft_records.count(),
            "draft_records": serializer.data
        }, status=status.HTTP_200_OK)


class AddTrainingEvaluationQuestionAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = TrainingEvaluationQuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TrainingEvaluationQuestionsByEvaluationAPIView(APIView):
    def get(self, request, emp_training_eval_id, *args, **kwargs):
        questions = EmployeeTrainingEvaluationQuestions.objects.filter(emp_training_eval_id=emp_training_eval_id)
        serializer = TrainingEvaluationQuestionSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)   

class DeleteTrainingEvaluationQuestionAPIView(APIView):
    def delete(self, request, question_id, *args, **kwargs):
        try:
            question = EmployeeTrainingEvaluationQuestions.objects.get(id=question_id)
            question.delete()
            return Response({"message": "Question deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except EmployeeTrainingEvaluationQuestions.DoesNotExist:
            return Response({"error": "Question not found."}, status=status.HTTP_404_NOT_FOUND)
        
        
class TrainingAddAnswerToQuestionAPIView(APIView):
    def patch(self, request, question_id, *args, **kwargs):
        try:
            question = EmployeeTrainingEvaluationQuestions.objects.get(id=question_id)
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

        except EmployeeTrainingEvaluationQuestions.DoesNotExist:
            return Response({"error": "Question not found."}, status=status.HTTP_404_NOT_FOUND)
        
# class TrainingUsersNotSubmittedAnswersView(APIView):
#     def get(self, request, company_id, evaluation_id):
#         try:
  
#             try:
#                 company = Company.objects.get(id=company_id)
#             except Company.DoesNotExist:
#                 return Response(
#                     {"error": "Company not found."},
#                     status=status.HTTP_404_NOT_FOUND
#                 )
          
#             try:
#                 emp_training_eval = EmployeeTrainingEvaluation.objects.get(id=evaluation_id, company=company)
#             except EmployeeTrainingEvaluation.DoesNotExist:
#                 return Response(
#                     {"error": "Evaluation not found or does not belong to the specified company."},
#                     status=status.HTTP_404_NOT_FOUND
#                 )
           
#             company_users = Users.objects.filter(company=company, is_trash=False)
           
#             submitted_user_ids = EmployeeTrainingEvaluationQuestions.objects.filter(
#                 emp_training_eval=emp_training_eval,
#                 user__isnull=False
#             ).values_list('user_id', flat=True).distinct()
            
#             not_submitted_users = company_users.exclude(id__in=submitted_user_ids)
      
#             user_data = [
#                 {
#                     "id": user.id,
#                     "first_name": user.first_name,
#                     "last_name": user.last_name,
#                     "email": user.email,
#                     "status": user.status
#                 }
#                 for user in not_submitted_users
#             ]

#             return Response(user_data, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response(
#                 {"error": "An unexpected error occurred.", "details": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )


class TrainingUsersNotSubmittedAnswersView(APIView):
    def get(self, request, company_id, evaluation_id):
        try:
            try:
                company = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                return Response({"error": "Company not found."}, status=status.HTTP_404_NOT_FOUND)

            try:
                emp_training_eval = EmployeeTrainingEvaluation.objects.get(id=evaluation_id, company=company)
            except EmployeeTrainingEvaluation.DoesNotExist:
                return Response({"error": "Evaluation not found or does not belong to this company."}, status=status.HTTP_404_NOT_FOUND)

            users = Users.objects.filter(company=company, is_trash=False)

            response_data = []
            for user in users:
                user_questions = EmployeeTrainingEvaluationQuestions.objects.filter( emp_training_eval=emp_training_eval, user=user)
                questions_data = [
                    {
                        "question_text": q.question_text,
                        "answer": q.answer
                    } for q in user_questions
                ]

                response_data.append({
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "status": user.status,
                    "questions": questions_data
                })

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": "Unexpected error occurred.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            
class UserInboxMessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
  

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            raise NotFound("User not found.")

        return Message.objects.filter(to_user=user).order_by('-created_at')
    
    
class MessageDetailView(generics.RetrieveAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
 
    lookup_field = 'id'

    def get_object(self):
        try:
            return Message.objects.get(id=self.kwargs['id'])
        except Message.DoesNotExist:
            raise NotFound("Message not found.")