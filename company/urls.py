
from django.urls import path
from  .views import *

urlpatterns = [
    
    path('company/login/', CompanyLoginView.as_view(), name='company-login'),
    path('users/create/', UserCreate.as_view(), name='user-create'), 
    path('users/<int:company_id>/', UserList.as_view(), name='user-list'),  
    path('users-active/<int:company_id>/', ActriveUserList.as_view(), name='user-list'), 
   
    path('user/<int:pk>/', UserDetailView.as_view(), name='user-detail'),   
    path('users/update/<int:pk>/', UserUpdateView.as_view(), name='user-update'),   
    path('users/delete/<int:pk>/', UserDelete.as_view(), name='user-delete'),
    path('validate-email/', ValidateEmailView.as_view(), name='validate_email_userid'),
    path('validate-email-edit/', ValidateEmailEditView.as_view(), name='validate_email_userid'),
    path('validate-username/', ValidatuseridView.as_view(), name='validate_email_userid'),
    path('validate-username-edit/', ValidateUsernameEditView.as_view(), name='validate_email_userid'),
    path('user/<int:id>/change-status/', ChangeUserStatusView.as_view(), name='change-company-status'),
    path('permissions/<int:user_id>/', UserPermissionsAPIView.as_view(), name='company-detail'), 
    path('user/change-password/<int:user_id>/', ChangeUserPasswordView.as_view(), name='change-password'),
 
 
 
    
    path('business-risks/', BusinessRiskView.as_view(), name='business-risk-list-create'), 
    path('business-risks/<int:pk>/', BusinessRiskDetailView.as_view(), name='business-risk-detail-update-delete'), 


    


    
    path('corrcetion-cause/', CorrectionCauseView.as_view(), name='baseline-list-create'),
    path('corrcetion-cause/<int:pk>/', CorrectionCauseDetailView.as_view(), name='baseline-detail'),
    
    path('corrective-actions/', CorrectiveActionListView.as_view(), name='corrective-action-list'),
    path('corrective-actions/<int:pk>/', CorrectiveActionDetailView.as_view(), name='corrective-action-detail'),
    


    
 
    
 
 
   
    
 
    path('user/change-password/<int:id>/', UserChangePasswordView.as_view(), name='change-password'),
    path('edit-logo/<int:user_id>/', EditUserLogoAPIView.as_view(), name='edit-company-logo'), 
    # path('user/<int:user_id>/', UserDetailAPIView.as_view(), name='user-detail'),
    

]


