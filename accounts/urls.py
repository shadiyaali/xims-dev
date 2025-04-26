from django.urls import path
from  .views import *

urlpatterns = [
    path('login/', AdminLoginView.as_view(), name='admin-login'),
    path('create-company/', CreateCompanyView.as_view(), name='create_company'),
    path('companies/', CompanyListView.as_view(), name='company-list'),
    path('companies/update/<int:id>/', CompanyUpdateView.as_view(), name='company-update'),
    path('company/<int:id>/change-status/', ChangeCompanyStatusView.as_view(), name='change-company-status'),
    path('company/<int:id>/delete/', DeleteCompanyView.as_view(), name='delete-company'),
    path('permissions/', PermissionListView.as_view(), name='permission-list'),
    path('companies/<int:id>/', SingleCompanyListView.as_view(), name='company-list'),
    path('companies/count/', CompanyCountView.as_view(), name='company-count'),
    path('users/count/', UserCountView.as_view(), name='company-count'),
    path('subscriptions/', SubscriptionListCreateView.as_view(), name='subscription-list-create'),
    path('subscriptions/<int:pk>/', SubscriptionDetailView.as_view(), name='subscription-detail'),
    path('subscribers/', SubscriberListCreateAPIView.as_view(), name='subscriber-list-create'),
    path('subscribers/<int:pk>/', SubscriberRetrieveUpdateDestroyAPIView.as_view(), name='subscriber-detail'),
    path('subscriber/<int:pk>/change-status/', ChangeSubscriberStatus.as_view(), name='change-company-status'),
    path('subscriptions/status/', SubscriptionStatusAPIView.as_view(), name='subscription_status'),
    path('subscribers/fifteen/', ExpiringfifteenAPIView.as_view(), name='expiring-subscribers'),
    path('subscribers/thirty/', ExpiringthirtyAPIView.as_view(), name='expiring-subscribers'),
    path('subscribers/sixty/', ExpiringsixtyAPIView.as_view(), name='expiring-subscribers'),
    path('subscribers/ninety/', ExpiringninetyAPIView.as_view(), name='expiring-subscribers'),
    path('admin-change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('active-company-count/', ActiveCompanyCountAPIView.as_view(), name='active-company-count'),
    path('validate-email/', ValidateEmailView.as_view(), name='validate_email_userid'),
    path('validate-edit/', ValidateEmailEditView.as_view(), name='validate_email_userid'),
    path('validate-userid/', ValidatuseridView.as_view(), name='validate_email_userid'),
    path('validate-userid-edit/', ValidateUserlEditView.as_view(), name='validate_email_userid'),
    path('admins-detail/', AdminDetailsAPIView.as_view(), name='admin-details'),
    path('companies/change-password/<int:id>/', CompanyChangePasswordView.as_view(), name='change-password'),
    path('admin-company/change-password/<int:id>/', CompanyAdminPasswordView.as_view(), name='change-password'),
    path('permissions/<int:company_id>/', CompanyDetailAPIView.as_view(), name='company-detail'), 
    path('edit-logo/<int:company_id>/', EditCompanyLogoAPIView.as_view(), name='edit-company-logo'), 
    path('change-profile-photo/', ChangeProfilePhotoAPIView.as_view(), name='change-profile-photo'),
]



