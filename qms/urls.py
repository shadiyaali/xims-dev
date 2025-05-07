
from django.urls import path
from  .views import *

urlpatterns = [
    
    # policy
    path('policy/', PolicyDocumentationCreateView.as_view(), name='documentation-list'),  
    path('policy/<int:company_id>/', PolicyAllList.as_view(), name='documentation-list'),
    path('policy/<int:pk>/update/', PolicyDocumentationUpdateView.as_view(), name='documentation-update'),  
    path('policy-get/<int:id>/', PolicyDocumentationDetailView.as_view(), name='policy-detail'),
    path('policy-download/<int:policy_id>/', PolicyFileDownloadView.as_view(), name='policy_download'),
    
    # Manual
    path('manuals/', ManualView.as_view(), name='manual-list-create'),
    path('manuals/<int:company_id>/', ManualAllList.as_view(), name='manual-list'),
    path('manual-detail/<int:pk>/', ManualDetailView.as_view(), name='manual-detail'),
    path('manuals-create/', ManualCreateView.as_view(), name='manual-list-create'),
    path('manuals/<int:pk>/update/', ManualUpdateView.as_view(), name='manual-update'),   
    path('submit-correction/', SubmitCorrectionView.as_view(), name='submit-correction'),
    path('manuals/<int:manual_id>/corrections/', ManualCorrectionsListView.as_view(), name='manual-corrections-list'),   
    path('manual-review/', ManualReviewView.as_view(), name='manual-review'),
    path('manuals/<int:manual_id>/publish-notification/', ManualPublishNotificationView.as_view(), name='publish-notification'),
    path('manuals/draft-create/', ManualDraftAPIView.as_view(), name='manual-create'),
    path('manuals-draft/<int:user_id>/', ManualDraftAllList.as_view(), name='manual-list'),
    path('manuals/drafts-count/<int:user_id>/', DraftManualcountAPIView.as_view(), name='draft-manuals'),    
    path("notifications/<int:user_id>/", NotificationView.as_view(), name="user-notifications"),
    path("notifications/read/", NotificationView.as_view(), name="mark-notifications-read"),
    path("notifications/<int:user_id>/", NotificationsQMS.as_view(), name="notifications_by_user"),
    path('count-notifications/<int:user_id>/', UnreadNotificationsAPIView.as_view(), name='unread-notifications'),
    path('notifications/<int:notification_id>/read/', MarkNotificationReadAPIView.as_view(), name='mark-notification-read'),
    path('manual/create/<int:id>/', ManualDraftEditView.as_view(), name='manual-update'),
    
    # Procedure
    path('procedure-create/', ProcedureCreateView.as_view(), name='manual-list-create'),
    path('procedure/<int:company_id>/', ProcedureAllList.as_view(), name='manual-list'),
    path('procedure-publish/<int:company_id>/', ProcedurePublishedList.as_view(), name='manual-list'),
    path('procedure-detail/<int:pk>/', ProcedureDetailView.as_view(), name='manual-detail'),
    path('procedure/<int:pk>/update/', ProcedureUpdateView.as_view(), name='manual-update'),
    path('procedure/submit-correction/', SubmitCorrectionProcedureView.as_view(), name='submit-correction'),
    path('procedure/<int:procedure_id>/corrections/', CorrectionProcedureList.as_view(), name='manual-corrections-list'),
    path('procedure-review/', ProcedureReviewView.as_view(), name='manual-review'),
    path('procedure/<int:procedure_id>/publish-notification/', ProcedurePublishNotificationView.as_view(), name='publish-notification'),
    path('procedure/draft-create/', ProcedureDraftAPIView.as_view(), name='manual-create'),
    path('procedure-draft/<int:user_id>/', ProcedureDraftAllList.as_view(), name='manual-list'),
    path('procedure/drafts-count/<int:user_id>/', DrafProcedurecountAPIView.as_view(), name='draft-manuals'),
    path("notifications-procedure/<int:user_id>/", NotificationsProcedure.as_view(), name="notifications_by_user"),
    path("procedure-notification/<int:user_id>/", NotificationsLastProcedure.as_view(), name="notifications_by_user"),
    path('procedure/count-notifications/<int:user_id>/', UnreadProcedureNotificationsAPIView.as_view(), name='unread-notifications'),
    path('notifications-procedure/<int:notification_id>/read/', MarkProcedureNotificationReadAPIView.as_view(), name='mark-notification-read'),
    path('procedure/create/<int:id>/', ProcedureDraftEditView.as_view(), name='manual-update'),
    
    # Record Format
    path('record-create/', RecordCreateView.as_view(), name='manual-list-create'),
    path('record/<int:company_id>/', RecordAllList.as_view(), name='manual-list'),
    path('record-detail/<int:pk>/', RecordDetailView.as_view(), name='manual-detail'),
    path('record/<int:pk>/update/', RecordUpdateView.as_view(), name='manual-update'),
    path('record/submit-correction/', SubmitCorrectionRecordView.as_view(), name='submit-correction'),
    path('record/<int:record_id>/corrections/', CorrectionRecordList.as_view(), name='manual-corrections-list'),
    path('record-review/', RecordReviewView.as_view(), name='manual-review'),
    path('record/<int:record_id>/publish-notification/', RecordPublishNotificationView.as_view(), name='publish-notification'),
    path('record/draft-create/', RecordDraftAPIView.as_view(), name='manual-create'),
    path('record-draft/<int:user_id>/', RecordDraftAllList.as_view(), name='manual-list'),
    path('record/drafts-count/<int:user_id>/', DrafRecordcountAPIView.as_view(), name='draft-manuals'),
    path("notifications-record/<int:user_id>/", NotificationsRecord.as_view(), name="notifications_by_user"),
    path("record-notification/<int:user_id>/", NotificationsLastRecord.as_view(), name="notifications_by_user"),
    path('record/count-notifications/<int:user_id>/', UnreadRecordNotificationsAPIView.as_view(), name='unread-notifications'),
    path('notifications-record/<int:notification_id>/read/', MarkRecordNotificationReadAPIView.as_view(), name='mark-notification-read'),
    path('record/create/<int:id>/', RecordraftEditView.as_view(), name='manual-update'),
 
 
    # Compliance
    path('compliance/<int:company_id>/', ComplianecesList.as_view(), name='manual-list'),
    path('compliances-get/<int:pk>/', ComplianceDetailView.as_view(), name='compliance-detail'),   
    path('compliances/create/', ComplianceCreateAPIView.as_view(), name='compliance-detail'), 
    path('compliance/draft-create/', ComplianceDraftAPIView.as_view(), name='manual-create'),  
    path('compliances/<int:pk>/edit/', EditsCompliance.as_view(), name='edit-interested-party'),
    path('compliance-draft/<int:user_id>/', ComplianceDraftAllList.as_view(), name='manual-list'),
    path('compliance/drafts-count/<int:user_id>/',  ComplainceView.as_view(), name='draft-manuals'),
    path('compliances-draft/edit/<int:pk>/', EditsDraftCompliance.as_view(), name='compliance_edit'),
    
   
    # Interested Parties
    path('interested-parties/<int:company_id>/', InterestedPartyList.as_view(), name='manual-list'),
    path('interested-parties-get/<int:pk>/', InterestedPartyDetailView.as_view(), name='interested-party-detail'),
    path('interested-parties/', InterestedPartyCreateView.as_view(), name='interested-party-list-create'),
    path('interst/draft-create/', InterestDraftAPIView.as_view(), name='manual-create'),
    path('interst-draft/<int:user_id>/', InterstDraftAllList.as_view(), name='manual-list'),
    path('interested-parties/<int:pk>/edit/', EditInterestedParty.as_view(), name='edit-interested-party'),
    path('interst/drafts-count/<int:user_id>/', DrafInterstAPIView.as_view(), name='draft-manuals'),
    path('interst/create/<draft_id>/', InterestedPartyEditDraftView.as_view(), name='process-draft-edit'),
   
    # Processes
    path('processes/<int:company_id>/', ProcessList.as_view(), name='manual-list'),
    path('processes-get/<int:pk>/', ProcessDetailView.as_view(), name='interested-party-detail'),
    path('processes/', ProcessCreateAPIView.as_view(), name='interested-party-list-create'),
    path('processes/draft-create/', ProcessDraftAPIView.as_view(), name='manual-create'),
    path('processes/<int:user_id>/', ProcessAllList.as_view(), name='manual-list'),
    path('processes/<int:pk>/edit/', EditProcess.as_view(), name='edit-interested-party'),
    path('process-draft/<int:user_id>/', ProcessesDraftAllList.as_view(), name='manual-list'),
    path('processes/drafts-count/<int:user_id>/', ProcessAPIView.as_view(), name='draft-manuals'),
    path('processes/create/<int:pk>/', ProcessDraftEditView.as_view(), name='process-draft-edit'),
    
    # Legal And other Requirements
    path('legal/<int:company_id>/', LegalList.as_view(), name='manual-list'),
    path('legal-get/<int:pk>/', LegalDetailView.as_view(), name='compliance-detail'),   
    path('legal/create/', LegalCreateAPIView.as_view(), name='compliance-detail'), 
    path('legal/draft-create/', LegalDraftAPIView.as_view(), name='manual-create'),  
    path('legal/<int:pk>/edit/', EditsLegal.as_view(), name='edit-interested-party'),
    path('legal-draft/<int:user_id>/', LegalDraftAllList.as_view(), name='manual-list'),
    path('legal/drafts-count/<int:user_id>/',  LegalView.as_view(), name='draft-manuals'),
    path('legal/create/<int:pk>/', EditDraftLegalAPIView.as_view(), name='process-draft-edit'),
    
     
    
    # Evaluation of compliance
    path('evaluation-create/', EvaluationCreateView.as_view(), name='manual-list-create'),
    path('evaluation/<int:company_id>/', EvaluationAllList.as_view(), name='manual-list'),
    path('evaluation-detail/<int:pk>/', EvaluationDetailView.as_view(), name='manual-detail'),
    path('evaluation/<int:pk>/update/', EvaluationUpdateView.as_view(), name='manual-update'),
    path('evaluation/submit-correction/', SubmitEvaluationCorrectionView.as_view(), name='submit-correction'),
    path('evaluation/<int:evaluation_id>/corrections/', CorrectionEvaluationList.as_view(), name='manual-corrections-list'),
    path('evaluation-review/', EvaluationReviewView.as_view(), name='manual-review'),
    path('evaluation/<int:evaluation_id>/publish-notification/', EvaluationPublishNotificationView.as_view(), name='publish-notification'),
    path('evaluation/draft-create/', PEvaluationDraftAPIView.as_view(), name='manual-create'),
    path('evaluation-draft/<int:user_id>/', EvaluationDraftAllList.as_view(), name='manual-list'),
    path('evaluation/drafts-count/<int:user_id>/', DrafEvaluationcountAPIView.as_view(), name='draft-manuals'),
    path("notifications-evaluation/<int:user_id>/", NotificationEvaluation.as_view(), name="notifications_by_user"),
    path("evaluation-notification/<int:user_id>/", NotificationsLastEvaluation.as_view(), name="notifications_by_user"),
    path('evaluation/count-notifications/<int:user_id>/', UnreadEvaluationNotificationsAPIView.as_view(), name='unread-notifications'),
    path('notifications-evaluation/<int:notification_id>/read/', MarkEvaluationNotificationReadAPIView.as_view(), name='mark-notification-read'),
    path('evaluation/create/<int:id>/',  EvaluationDraftEditView.as_view(), name='manual-update'),
   
    # mamagement of change
    path('changes/<int:company_id>/', ChangesList.as_view(), name='manual-list'),
    path('changes-get/<int:pk>/', ChangesDetailView.as_view(), name='compliance-detail'),   
    path('changes/create/', ChangesCreateAPIView.as_view(), name='compliance-detail'), 
    path('changes/draft-create/', ChangesDraftAPIView.as_view(), name='manual-create'),  
    path('changes/<int:pk>/edit/', EditsChanges.as_view(), name='edit-interested-party'),
    path('changes-draft/<int:user_id>/', ChangesDraftAllList.as_view(), name='manual-list'),
    path('changes/drafts-count/<int:user_id>/',  ChangesView.as_view(), name='draft-manuals'),
    path('changes/create/<int:id>/',  EditsDraftManagementChanges.as_view(), name='manual-update'),
 
    # Sustainability
    path('sustainability-create/', SustainabilityCreateView.as_view(), name='manual-list-create'),
    path('sustainability/<int:company_id>/', SustainabilityAllList.as_view(), name='manual-list'),
    path('sustainability-detail/<int:pk>/', SustainabilityDetailView.as_view(), name='manual-detail'),
    path('sustainability/<int:pk>/update/', SustainabilityUpdateView.as_view(), name='manual-update'),
    path('sustainability/submit-correction/', SubmitCorrectionSustainabilityView.as_view(), name='submit-correction'),
    path('sustainability/<int:sustainability_id>/corrections/', CorrectionSustainabilityList.as_view(), name='manual-corrections-list'),
    path('sustainability-review/', SustainabilityReviewView.as_view(), name='manual-review'),
    path('sustainability/<int:sustainability_id>/publish-notification/', SustainabilityPublishNotificationView.as_view(), name='publish-notification'),
    path('sustainability/draft-create/', SustainabilityDraftAPIView.as_view(), name='manual-create'),
    path('sustainability-draft/<int:user_id>/', SustainabilityDraftAllList.as_view(), name='manual-list'),
    path('sustainability/drafts-count/<int:user_id>/', DraftSustainabilityCountAPIView.as_view(), name='draft-manuals'),
    path("notifications-sustainability/<int:user_id>/", NotificationSustainabilityView.as_view(), name="notifications_by_user"),
    path("sustainability-notification/<int:user_id>/", NotificationsLastSustainability.as_view(), name="notifications_by_user"),
    path('sustainability/count-notifications/<int:user_id>/', UnreadSustainabilityNotificationsAPIView.as_view(), name='unread-notifications'),
    path('notifications-sustainability/<int:notification_id>/read/', MarkSustainabilityNotificationReadAPIView.as_view(), name='mark-notification-read'),
    path('sustainability/create/<int:id>/', SustainabilityDraftEditView.as_view(), name='manual-update'),
    
    # Awareness Training
    path('awareness/create/', AwarenessTrainingCreateView.as_view(), name='documentation-list'),  
    path('awareness/<int:company_id>/', AwarenessAllList.as_view(), name='documentation-list'),
    path('awareness/<int:pk>/update/', AwarenessUpdateView.as_view(), name='documentation-update'),  
    path('awareness-get/<int:id>/', AwarenessDetailView.as_view(), name='policy-detail'),
    path('awareness/draft-create/', AwarenessDraftAPIView.as_view(), name='manual-create'),  
    path('awareness-draft/<int:user_id>/', AwarenessDraftAllList.as_view(), name='manual-list'),
    path('awareness/drafts-count/<int:user_id>/',  AwarenessView.as_view(), name='draft-manuals'),
    
    # Training
    path('training/<int:company_id>/', TrainingList.as_view(), name='manual-list'),
    path('training-get/<int:pk>/', TrainingDetailView.as_view(), name='compliance-detail'),   
    path('training/create/', TrainingCreateAPIView.as_view(), name='compliance-detail'), 
    path('training/draft-create/', TrainingDraftAPIView.as_view(), name='manual-create'),  
    path('training/<int:pk>/edit/', TrainingUpdateAPIView.as_view(), name='edit-interested-party'),
    path('training-draft/<int:user_id>/', TrainingDraftAllList.as_view(), name='manual-list'),
    path('training/drafts-count/<int:user_id>/',  TrainingView.as_view(), name='draft-manuals'),
    path('training/<int:training_id>/complete/', TrainingCompleteAndNotifyView.as_view(), name='training-complete-notify'),
    path('training/by-attendee/<int:user_id>/', TrainingsByAttendeeAPIView.as_view(), name='training-by-attendee'),
    path('training/evaluated-by/<int:user_id>/', TrainingsEvaluatedByUserAPIView.as_view(), name='trainings-evaluated-by-user'),
    path('training/create/<int:pk>/',  EditDraftTrainingAPIView.as_view(), name='manual-update'),
    
    
    # Performance Evaluation
    path('performance/create/', PerformanceCreateView.as_view(), name='documentation-list'),  
    path('performance/<int:company_id>/', PerformanceAllList.as_view(), name='documentation-list'),
    path('performance/<int:pk>/update/', PerformanceUpdateView.as_view(), name='documentation-update'),  
    path('performance-get/<int:id>/', PerformanceDetailView.as_view(), name='policy-detail'),
    path('performance/draft-create/', PerformanceDraftAPIView.as_view(), name='manual-create'),  
    path('performance-draft/<int:user_id>/', PerformanceDraftAllList.as_view(), name='manual-list'),
    path('performance/drafts-count/<int:user_id>/',  PerformanceView.as_view(), name='draft-manuals'),
    path('performance/question-add/', AddPerformanceQuestionAPIView.as_view(), name='add-performance-question'),
    path('performance/<int:performance_id>/questions/', PerformanceQuestionsByEvaluationAPIView.as_view(), name='performance-questions'),
    path('performance/question/<int:question_id>/delete/', DeletePerformanceQuestionAPIView.as_view(), name='delete-performance-question'),
    path('performance/question/answer/<int:question_id>/', AddAnswerToQuestionAPIView.as_view(), name='add-answer-to-question'),
    path('performance/<int:company_id>/evaluation/<int:evaluation_id>/',UsersNotSubmittedAnswersView.as_view(),name='unsubmitted-users'),  
    
    
    
    # Employee Satisfaction Survey    
    path('survey/create/', SurveyCreateView.as_view(), name='documentation-list'),  
    path('survey/<int:company_id>/', SurveyAllList.as_view(), name='documentation-list'),
    path('survey/<int:pk>/update/', SurveyUpdateView.as_view(), name='documentation-update'),  
    path('survey-get/<int:id>/', SurveyDetailView.as_view(), name='policy-detail'),
    path('survey/draft-create/', SurveyDraftAPIView.as_view(), name='manual-create'),  
    path('survey-draft/<int:user_id>/', SurveyDraftAllList.as_view(), name='manual-list'),
    path('survey/drafts-count/<int:user_id>/',  SurveyView.as_view(), name='draft-manuals'),
    path('survey/question-add/', AddSurveyQuestionAPIView.as_view(), name='add-performance-question'),
    path('survey/<int:survey_id>/questions/', SurveyQuestionsByEvaluationAPIView.as_view(), name='performance-questions'),
    path('survey/question/<int:question_id>/delete/', DeleteSurveyQuestionAPIView.as_view(), name='delete-performance-question'),
    path('survey/question/answer/<int:question_id>/', AddSurveyAnswerToQuestionAPIView.as_view(), name='add-answer-to-question'),
    path('survey/<int:company_id>/evaluation/<int:survey_id>/',UserSurveysAnswersView.as_view(),name='unsubmitted-users'),  
     
    # Scope Statements
    path('scope/', ScopeCreateView.as_view(), name='documentation-list'),  
    path('scope/<int:company_id>/', ScopeAllList.as_view(), name='documentation-list'),
    path('scope/<int:pk>/update/', ScopeUpdateView.as_view(), name='documentation-update'),  
    path('scope-get/<int:id>/', ScopeDetailView.as_view(), name='policy-detail'),
    path('scope-download/<int:policy_id>/', ScopeFileDownloadView.as_view(), name='policy_download'),
    
    # Agenda in Add Meeting
    path('agenda/create/', AgendaListCreateView.as_view(), name='agenda-list-create'), 
    path('agenda/company/<int:company_id>/', CompanyAgendaView.as_view(), name='company-agendas'),  
    path('agenda/<int:pk>/', AgendaDetailView.as_view(), name='agenda-detail'),
    
    # Meeting
    path('meeting/create/', MeetingCreateView.as_view(), name='compliance-detail'),
    path('meeting/company/<int:company_id>/', MeetingAllList.as_view(), name='company-agendas'),  
    path('meeting-get/<int:pk>/', MeetingDetailView.as_view(), name='compliance-detail'),   
    path('meeting/<int:pk>/edit/', MeetingUpdateAPIView.as_view(), name='edit-interested-party'),
    path('meeting/draft-create/', MeetingDraftAPIView.as_view(), name='manual-create'), 
    path('meeting-draft/<int:user_id>/', MeetingDraftAllList.as_view(), name='manual-list'),
    path('meeting-draft/edit/<int:pk>/', MeetingUpdateDraftView.as_view(), name='compliance_edit'),
    
    # Audit
    path('audit/create/', AuditCreateAPIView.as_view(), name='audit-list-create'),
    path('audit/company/<int:company_id>/', CompanyAuditView.as_view(), name='company-agendas'),
    path('audits/<int:pk>/', AuditDetailView.as_view(), name='audit-detail'),
    path('audit/draft-create/', AuditDraftAPIView.as_view(), name='manual-create'),
    path('audit-draft/<int:user_id>/', AuditDraftAllList.as_view(), name='manual-list'),
    path('audit-get/<int:pk>/', AuditDetailAPIView.as_view(), name='audit-detail'),
    path('audits/<int:audit_id>/upload-reports/', AuditReportUploadView.as_view(), name='upload-audit-reports'),
    path('audit/<int:audit_id>/report/', GetAuditReportView.as_view(), name='get-audit-report'),
    
    # Inspection
    path('inspection/create/', InspectionCreateAPIView.as_view(), name='audit-list-create'),
    path('inspection/company/<int:company_id>/', CompanyinspectionView.as_view(), name='company-agendas'),
    path('inspection/<int:pk>/', InspectionDetailView.as_view(), name='audit-detail'),
    path('inspection/draft-create/', InspesctionDraftAPIView.as_view(), name='manual-create'),
    path('inspection-draft/<int:user_id>/', InspectionDraftAllList.as_view(), name='manual-list'),
    path('inspection-get/<int:pk>/', InspectionDetailAPIView.as_view(), name='audit-detail'),
    path('inspection/<int:audit_id>/upload-reports/', InspectionReportUploadView.as_view(), name='upload-audit-reports'),
    path('inspection/<int:audit_id>/report/', GetInspectionReportView.as_view(), name='get-audit-report'),
    
    # cause in Internal Problems
    path('cause/create/', CauseListCreateView.as_view(), name='agenda-list-create'), 
    path('cause/company/<int:company_id>/', CompanyCauseView.as_view(), name='company-agendas'),  
    path('cause/<int:pk>/', CauseDetailView.as_view(), name='agenda-detail'),
    
    # root cause in CAR number
    path('root-cause/create/', RootCauseListCreateView.as_view(), name='agenda-list-create'), 
    path('root-cause/company/<int:company_id>/', RootCompanyCauseView.as_view(), name='company-agendas'),  
    path('root-cause/<int:pk>/', RootCauseDetailView.as_view(), name='agenda-detail'),
    
    # CAR number 
    path('car-numbers/', CarNumberCreateAPIView.as_view(), name='car-number-list-create'),
    path('car-numbers/<int:pk>/', CarNumberDetailView.as_view(), name='car-number-detail'),
    path('car/draft-create/', CarDraftAPIView.as_view(), name='manual-create'),
    path('car_no/company/<int:company_id>/', CarNCompanyCauseView.as_view(), name='company-agendas'),
    path('car_no/draft/<user_id>/', CarNDraftCompanyCauseView.as_view(), name='company-agendas'),   
    path('car-number/next-action/<int:company_id>/', GetNextActionNumberView.as_view(), name='get-next-action-number'),
    path('car-draft/update/<int:pk>/', CarDraftUpdateAPIView.as_view(), name='car-draft-update'),
 
    
    
    # Internal Problems 
    path('internal-problems/create/', InternalProblemCreateView.as_view(), name='create-internal-problem'),
    path('internal-problems/company/<int:company_id>/', InternalProblemView.as_view(), name='company-agendas'),
    path('internal-problems/<int:pk>/', InternalDetailView.as_view(), name='car-number-detail'),
    path('internal-problems/draft-create/', InternalDraftAPIView.as_view(), name='manual-create'),
    path('internal-problems-draft/<int:user_id>/', IternalDraftAllList.as_view(), name='manual-list'),
    
    # Supplier 
    path('suppliers/create/', SupplierAPIView.as_view(), name='supplier-list'), 
    path('suppliers/company/<int:company_id>/', SupplierView.as_view(), name='company-agendas'), 
    path('suppliers/<int:pk>/', SupplierDetailAPIView.as_view(), name='supplier-detail'),
    path('suppliers/draft-create/', SupplierDraftAPIView.as_view(), name='manual-create'),
    path('suppliers-draft/<int:user_id>/', SupplierDraftAllList.as_view(), name='manual-list'),
    
    # supplier Problems
    path('supplier-problems/', SupplierProblemAPIView.as_view(), name='supplier-problems'),
    path('supplier-problems/<int:pk>/', SupplierProblemDetailAPIView.as_view(), name='supplier-problem-detail'),
    path('supplier-problems/company/<int:company_id>/',  SupplierProblemView.as_view(), name='company-agendas'),
    path('supplier-problems/draft-create/', SupplierproblemDraftAPIView.as_view(), name='manual-create'),
    path('supplier-problems-draft/<int:user_id>/', SupplierproblemDraftAllList.as_view(), name='manual-list'),
   
 
    
    # supplier evaluation  
    path('supplier/evaluation/create/', SuppEvaluationCreateView.as_view(), name='documentation-list'),  
    path('supplier/evaluation/<int:company_id>/', SupplierEvalAllList.as_view(), name='documentation-list'),
    path('supplier/evaluation/<int:pk>/update/', SuppEvalUpdateView.as_view(), name='documentation-update'),  
    path('supplier/evaluation-get/<int:id>/', SuppEvalDetailView.as_view(), name='policy-detail'),
    path('supplier/evaluation/draft-create/', SuppEvalDraftAPIView.as_view(), name='manual-create'),  
    path('supplier/evaluation-draft/<int:user_id>/', SuppEvlDraftAllList.as_view(), name='manual-list'),
    path('supplier/evaluation/drafts-count/<int:user_id>/',  SuppEvlView.as_view(), name='draft-manuals'),
    path('supplier/evaluation/question-add/', SupEvalQuestionQuestionAPIView.as_view(), name='add-performance-question'),
    path('supplier/evaluation/<int:supp_evaluation_id>/questions/', SupEvalQuestionQuestionsByEvaluationAPIView.as_view(), name='performance-questions'),
    path('supplier/evaluation/question/<int:question_id>/delete/', DeleteSuppQuestionAPIView.as_view(), name='delete-performance-question'),
    path('supplier/evaluation/question/answer/<int:question_id>/', AddSSuppAnswerToQuestionAPIView.as_view(), name='add-answer-to-question'),
    path('supplier/evaluation/<int:company_id>/evaluation/<int:supp_evaluation_id>/',SupplierSuppEvlAnswersView.as_view(),name='unsubmitted-users'),  
    
    
    # customer
    path('customer/create/', CustomerAPIView.as_view(), name='supplier-list'), 
    path('customer/company/<int:company_id>/', CustomerView.as_view(), name='company-agendas'), 
    path('customer/<int:pk>/', CustomerDetailAPIView.as_view(), name='supplier-detail'),
    path('customer/draft-create/', CustomerDraftAPIView.as_view(), name='manual-create'),
    path('customer-draft/<int:user_id>/', CustomerDraftAllList.as_view(), name='manual-list'),
    
    # category in customer
    path('category/create/', CategoryListCreateView.as_view(), name='agenda-list-create'), 
    path('category/company/<int:company_id>/', CompanycategoryView.as_view(), name='company-agendas'),  
    path('category/<int:pk>/', CategoryDetailView.as_view(), name='agenda-detail'),
    
    # Complaints and Feedbacks
    path('complaints/create/', ComplaintsCreateView.as_view(), name='create-internal-problem'),
    path('complaints/company/<int:company_id>/', ComplaintsView.as_view(), name='company-agendas'),
    path('complaints/<int:pk>/', ComplaintsDetailView.as_view(), name='car-number-detail'),
    path('complaints/draft-create/', ComplaintsDraftAPIView.as_view(), name='manual-create'),
    path('complaints-draft/<int:user_id>/', ComplaintDraftAllList.as_view(), name='manual-list'),
    
    
    # Customer satisfaction survey
    path('customer/survey/create/', CustomerSurveyCreateView.as_view(), name='documentation-list'),  
    path('customer/survey/<int:company_id>/', CustomerSurveyEvalAllList.as_view(), name='documentation-list'),
    path('customer/survey/<int:pk>/update/', CustomerSurveyUpdateView.as_view(), name='documentation-update'),  
    path('customer/survey/-get/<int:id>/', CustomerSurveyDetailView.as_view(), name='policy-detail'),
    path('customer/survey/draft-create/', CustomerSurveyDraftAPIView.as_view(), name='manual-create'),  
    path('customer/survey-draft/<int:user_id>/', CustomerSurveyDraftAllList.as_view(), name='manual-list'),
    path('customer/survey/drafts-count/<int:user_id>/',  CustomerSurveyView.as_view(), name='draft-manuals'),
    path('customer/survey/question-add/', CustomerSurveyQuestionQuestionAPIView.as_view(), name='add-performance-question'),
    path('customer/survey/<int:customer_id>/questions/', CustomerSurveyByEvaluationAPIView.as_view(), name='performance-questions'),
    path('customer/survey/question/<int:question_id>/delete/', DeleteCustomerSurveyQuestionAPIView.as_view(), name='delete-performance-question'),
    path('customer/survey/question/answer/<int:question_id>/', AddSCustomerSurveyAnswerToQuestionAPIView.as_view(), name='add-answer-to-question'),
    path('customer/survey/<int:company_id>/evaluation/<int:customer_id>/',CustomerCustomerSurveyAnswersView.as_view(),name='unsubmitted-users'),  
    
    
    # traing evaluation
    path('training-evaluation/create/', TrainingEvaluationCreateView.as_view(), name='documentation-list'),  
    path('training-evaluation/<int:company_id>/', TrainingEvaluationAllList.as_view(), name='documentation-list'),
    path('training-evaluation/<int:pk>/update/', TrainingEvaluationUpdateView.as_view(), name='documentation-update'),  
    path('training-evaluation-get/<int:id>/', TrainingEvaluationDetailView.as_view(), name='policy-detail'),
    path('training-evaluation/draft-create/', TrainingEvaluationDraftAPIView.as_view(), name='manual-create'),  
    path('training-evaluation-draft/<int:user_id>/', TrainingEvaluationDraftAllList.as_view(), name='manual-list'),
    path('training-evaluation/drafts-count/<int:user_id>/',  TrainingEvaluationView.as_view(), name='draft-manuals'),
    path('training-evaluation/question-add/', AddTrainingEvaluationQuestionAPIView.as_view(), name='add-performance-question'),
    path('training-evaluation/<int:emp_training_eval_id>/questions/', TrainingEvaluationQuestionsByEvaluationAPIView.as_view(), name='performance-questions'),
    path('training-evaluation/question/<int:question_id>/delete/', DeleteTrainingEvaluationQuestionAPIView.as_view(), name='delete-performance-question'),
    path('training-evaluation/question/answer/<int:question_id>/', TrainingAddAnswerToQuestionAPIView.as_view(), name='add-answer-to-question'),
    path('training-evaluation/<int:company_id>/evaluation/<int:evaluation_id>/',TrainingUsersNotSubmittedAnswersView.as_view(),name='unsubmitted-users'),
    
        
    # System message
    path('messages/create/', MessageCreateAPIView.as_view(), name='message-create'), 
    path('messages/inbox/<int:user_id>/', UserInboxMessageListView.as_view(), name='user-inbox'), 
    path('messages/<int:id>/', MessageDetailView.as_view(), name='message-detail'),
    path('replay-message/send/', SendReplayMessageView.as_view(), name='send-replay-message'),
    path('forward-message/send/', SendForwardMessageView.as_view(), name='send-replay-message'),
    path('messages/outbox/<int:user_id>/', UserOutboxMessageListView.as_view(), name='user-inbox'), 
    path('messages/<int:id>/trash/', MarkMessageAsTrashView.as_view(), name='mark_message_as_trash'),
    path('messages/<int:id>/restore/', MarkRestoreAsTrashView.as_view(), name='mark_message_as_trash'),
    path('messages-replay/inbox/<int:user_id>/', UserInboxReplayListView.as_view(), name='user-inbox'), 
    path('messages-forward/inbox/<int:user_id>/', UserInboxForwardListView.as_view(), name='user-inbox'), 
    path('messages-replay/<int:id>/trash/', MarkReplayMessageAsTrashView.as_view(), name='mark_message_as_trash'),
    path('messages-replay/<int:id>/restore/', MarkRestoreAsReplayTrashView.as_view(), name='mark_message_as_trash'),
    path('messages-forward/<int:id>/trash/', MarkForwardMessageAsTrashView.as_view(), name='mark_message_as_trash'),
    path('messages-forward/<int:id>/restore/', MarkRestoreAsForwardTrashView.as_view(), name='mark_message_as_trash'),
    path('messages-replay/outbox/<int:user_id>/', UserOutboxReplayMessageListView.as_view(), name='user-inbox'), 
    path('messages-forward/outbox/<int:user_id>/', UserOutboxForwardMessageListView.as_view(), name='user-inbox'), 
    path('messages/<int:id>/delete/', DeleteMessageView.as_view(), name='delete-message'),
    path('replay/<int:id>/delete/', DeleteReplayView.as_view(), name='delete-message'),
    path('forward/<int:id>/delete/', DeleteForwardView.as_view(), name='delete-message'),
    path('message/draft-create/', MessageDraftAPIView.as_view(), name='manual-create'),  
    path('message-draft/edit/<int:id>/', DraftMessageAsTrashView.as_view(), name='compliance_edit'),
    
    
    # Preventive Action
    path('preventive/create/', PreventiveActionCreateAPIView.as_view(), name='message-create'), 
    path('preventive/<int:company_id>/', PreventiveList.as_view(), name='manual-list'),
    path('preventive-get/<int:pk>/', PreventiveDetailView.as_view(), name='compliance-detail'),  
    path('preventive/draft-create/', PreventiveDraftAPIView.as_view(), name='manual-create'),  
    path('preventive-actions/<int:pk>/edit/', PreventiveActionEditAPIView.as_view(), name='preventive-action-edit'),
    path('preventive-draft/<int:user_id>/', PreventiveDraftAllList.as_view(), name='manual-list'),
    path('preventive/drafts-count/<int:user_id>/',  PreventiveView.as_view(), name='draft-manuals'),
    path('preventive-draft/edit/<int:pk>/', PreventiveDraftUpdateAPIView.as_view(), name='compliance_edit'),
     
   
    # Objectives
    path('objectives/create/', ObjectivesListCreateView.as_view(), name='objectives-list-create'),
    path('objectives/<int:company_id>/', ObjectiveList.as_view(), name='manual-list'),
    path('objectives-get/<int:pk>/', ObjectivesDetailView.as_view(), name='objectives-detail'),
    path('objectives/draft-create/', ObjectiveDraftAPIView.as_view(), name='manual-create'),  
    path('objectives-draft/<int:user_id>/', ObjectiveDraftAllList.as_view(), name='manual-list'),
    path('objectives/drafts-count/<int:user_id>/',  ObjectiveView.as_view(), name='draft-manuals'),
    
    # Targets
    path('target/create/', TargetListCreateView.as_view(), name='objectives-list-create'),
    path('objectives/<int:company_id>/', ObjectiveList.as_view(), name='manual-list'),
    path('objectives-get/<int:pk>/', ObjectivesDetailView.as_view(), name='objectives-detail'),
    path('objectives/draft-create/', ObjectiveDraftAPIView.as_view(), name='manual-create'),  
    path('objectives-draft/<int:user_id>/', ObjectiveDraftAllList.as_view(), name='manual-list'),
    path('objectives/drafts-count/<int:user_id>/',  ObjectiveView.as_view(), name='draft-manuals'),
]



