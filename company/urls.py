
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
 

 
    path('process_activity/', ProcessActivityListCreate.as_view(), name='process_activity-list-create'),
    path('process_activity/<int:pk>/', ProcessActivityDetail.as_view(), name='process_activity-detail'),
    path('environmental-aspects/', EnvironmentalAspectView.as_view(), name='environmental-aspect-list-create'),   
    path('environmental-aspects/<int:pk>/', EnvironmentalAspectDetailView.as_view(), name='environmental-aspect-detail-update-delete'), 
    path('environmental-impacts/', EnvironmentalImpactView.as_view(), name='environmental-impact-list-create'), 
    path('environmental-impacts/<int:pk>/', EnvironmentalImpactDetailView.as_view(), name='environmental-impact-detail-update-delete'),
 
    path('environmental-incidents/', EnvironmentalIncidentsView.as_view(), name='incident-list-create'),   
    path('environmental-incidents/<int:pk>/', EnvironmentalIncidentDetailView.as_view(), name='incident-detail-update-delete'),
    path('environmental-waste/', EnvironmentalWasteView.as_view(), name='waste-list-create'),   
    path('environmental-waste/<int:pk>/', EnvironmentalWasteDetailView.as_view(), name='waste-detail-update-delete'),  
    path('process_health/', ProcessHealthListCreate.as_view(), name='process_activity-list-create'),
    path('process_health/<int:pk>/', ProcessHealthDetail.as_view(), name='process_activity-detail'),
    path('health-safety/', HealthSafetyView.as_view(), name='hazard-list-create'),  
    path('health-safety/<int:pk>/', HealthSafetyDetailView.as_view(), name='hazard-detail-update-delete'),
    path('risk-assessment/', RiskAssessmentView.as_view(), name='assessment-list-create'), 
    path('risk-assessment/<int:pk>/', RiskAssessmentDetailView.as_view(), name='assessment-detail-update-delete'),
    path('health-root-causes/', HealthRootCauseView.as_view(), name='root-cause-list-create'),   
    path('health-root-causes/<int:pk>/', HealthRootCauseDetailView.as_view(), name='root-cause-detail-update-delete'),
    path('health-incidents/', HealthIncidentsView.as_view(), name='health-incidents-list-create'),   
    path('health-incidents/<int:pk>/', HealthIncidentsDetailView.as_view(), name='health-incidents-detail-update-delete'), 
    path('business-risks/', BusinessRiskView.as_view(), name='business-risk-list-create'), 
    path('business-risks/<int:pk>/', BusinessRiskDetailView.as_view(), name='business-risk-detail-update-delete'), 
    path('review-type/', ReviewTypeView.as_view(), name='root-cause-list-create'),   
    path('review-type/<int:pk>/', ReviewTypeDetailView.as_view(), name='root-cause-detail-update-delete'),
    path('energy-reviews/', EnergyReviewView.as_view(), name='energy-review-list-create'),  
    path('energy-reviews/<int:pk>/', EnergyReviewDetailView.as_view(), name='energy-review-detail'), 
    path('review-baseline/', BaselineReviewView.as_view(), name='root-cause-list-create'),   
    path('review-baseline/<int:pk>/', BaselineReviewDetailView.as_view(), name='root-cause-detail-update-delete'),
    path('baselines/', BaselineView.as_view(), name='baseline-list-create'),
    path('baselines/<int:pk>/', BaselineDetailView.as_view(), name='baseline-detail'),
    path('energy-source/', EnergySourceView.as_view(), name='root-cause-list-create'),   
    path('energy-source/<int:pk>/', EnergySourceDetailView.as_view(), name='root-cause-detail-update-delete'),
    path('significant_energy/', SignificantEnergyListView.as_view(), name='significant_energy_list'),  
    path('significant_energy/<int:pk>/', SignificantEnergyDetailView.as_view(), name='significant_energy_detail'),
    
    path('energy-improvements/', EnergyImprovementsListCreateAPIView.as_view(), name='energy-improvements-list-create'),
    path('energy-improvements/<int:pk>/', EnergyImprovementsDetailAPIView.as_view(), name='energy-improvements-detail'),
    
    path('energy-action/', EnergyActionView.as_view(), name='baseline-list-create'),
    path('energy-action/<int:pk>/', EnergyActionDetailView.as_view(), name='baseline-detail'),
    
    path('corrcetion-cause/', CorrectionCauseView.as_view(), name='baseline-list-create'),
    path('corrcetion-cause/<int:pk>/', CorrectionCauseDetailView.as_view(), name='baseline-detail'),
    
    path('corrective-actions/', CorrectiveActionListView.as_view(), name='corrective-action-list'),
    path('corrective-actions/<int:pk>/', CorrectiveActionDetailView.as_view(), name='corrective-action-detail'),
    
    path('preventive-actions/', PreventiveActionListCreateView.as_view(), name='preventive-action-list-create'),
    path('preventive-actions/<int:pk>/', PreventiveActionDetailView.as_view(), name='preventive-action-detail'),
    
    path('objectives/', ObjectivesListCreateView.as_view(), name='objectives-list-create'),
    path('objectives/<int:pk>/', ObjectivesDetailView.as_view(), name='objectives-detail'),
    
    path('targets/', TargetsPView.as_view(), name='targets-list'), 
    path('targets/<int:pk>/', TargetsPDetailView.as_view(), name='targets-detail'), 
    
    path('conformity-causes/', ConformityCauseView.as_view(), name='conformity-cause-list'),  
    path('conformity-causes/<int:pk>/', ConformityCauseDetailView.as_view(), name='conformity-cause-detail'), 
    path('conformities/', ConformityView.as_view(), name='conformity-list'),   
    path('conformities/<int:pk>/', ConformityDetailView.as_view(), name='conformity-detail'), 
    
 
   
    
 
    path('user/change-password/<int:id>/', UserChangePasswordView.as_view(), name='change-password'),
    path('edit-logo/<int:user_id>/', EditUserLogoAPIView.as_view(), name='edit-company-logo'), 
    # path('user/<int:user_id>/', UserDetailAPIView.as_view(), name='user-detail'),
    

]


