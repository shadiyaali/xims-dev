
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
    
   
    # interested party type 
    path('cause-party/create/', CausePartyCreateView.as_view(), name='agenda-list-create'), 
    path('cause-party/company/<int:company_id>/', CompanyCausePartyView.as_view(), name='company-agendas'),  
    path('agcause-partyenda/<int:pk>/', CausePartyDetailView.as_view(), name='agenda-detail'),
    
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
    path('car-number/update/<int:pk>/', CarNumberEditAPIView.as_view(), name='car-draft-update'),
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
    path('messages/trash/<int:user_id>/', UserTrashMessageListView.as_view(), name='user-inbox'), 
    path('messages/replay-trash/<int:user_id>/', UserTrashReplyMessageListView.as_view(), name='user-inbox'), 
    path('messages/forward-trash/<int:user_id>/', UserTrashForwardMessageListView.as_view(), name='user-inbox'), 

    
    
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
    path('targets/create/', TargetCreateView.as_view(), name='target-create'),
    path('targets/<int:company_id>/', TargetsList.as_view(), name='manual-list'),
    path('targets-get/<int:pk>/', TargetView.as_view(), name='target-detail'),
    path('targets/draft-create/', TargetsDraftAPIView.as_view(), name='manual-create'),  
    path('targets-draft/<int:user_id>/', TargetsDraftAllList.as_view(), name='manual-list'),
    path('targets/drafts-count/<int:user_id>/',  TargetsView.as_view(), name='draft-manuals'),
    
 
    # ConformityCause
    path('conf-cause/create/', ConfirmitycauseCreateView.as_view(), name='agenda-list-create'), 
    path('conf-cause/company/<int:company_id>/', ConformityCauseCompanyView.as_view(), name='company-agendas'),  
    path('conf-cause/<int:pk>/', ConformityCauseDetailView.as_view(), name='agenda-detail'),
    
    # Conformity Report
    path('conformity/create/', ConformityCreateAPIView.as_view(), name='car-number-list-create'),
    path('conformity/<int:pk>/', ConformityDetailView.as_view(), name='car-number-detail'),
    path('conformity/draft-create/', ConformityDraftAPIView.as_view(), name='manual-create'),
    path('conformity/company/<int:company_id>/', ConformityCompanyCauseView.as_view(), name='company-agendas'),
    path('conformity/draft/<user_id>/', ConformityDraftCompanyView.as_view(), name='company-agendas'),   
    path('conformity/next-action/<int:company_id>/', GetNextNCRConformity.as_view(), name='get-next-action-number'),
    path('conformity/update/<int:pk>/', ConformityEditAPIView.as_view(), name='car-draft-update'),
    path('conformity-draft/update/<int:pk>/', ConformityDraftUpdateAPIView.as_view(), name='car-draft-update'),
    path('conformity/drafts-count/<int:user_id>/', conformityView.as_view(), name='draft-manuals'),
    
    # Review Type
    path('review-type/create/', ReviewTypeCreateView.as_view(), name='agenda-list-create'), 
    path('review-type/company/<int:company_id>/', ReviewTypeCompanyView.as_view(), name='company-agendas'),  
    path('review-type/<int:pk>/', ReviewTypeDetailView.as_view(), name='agenda-detail'),
    
    # Energy Review
    path('energy-review/create/', EnergyReviewCreateAPIView.as_view(), name='car-number-list-create'),
    path('energy-review/<int:pk>/', EnergyReviewDetailView.as_view(), name='car-number-detail'),
    path('energy-review/draft-create/', EnergyReviewDraftAPIView.as_view(), name='manual-create'),
    path('energy-review/company/<int:company_id>/', EnergyReviewCompanyCauseView.as_view(), name='company-agendas'),
    path('energy-review/draft/<user_id>/', EnergyReviewDraftCompanyView.as_view(), name='company-agendas'),   
    path('energy-review/next-action/<int:company_id>/', GetNextNCRReviewEnergy.as_view(), name='get-next-action-number'),
    path('energy-review/update/<int:pk>/', EnergyReviewEditAPIView.as_view(), name='car-draft-update'),
    path('energy-review-draft/update/<int:pk>/', EnergyReviewDraftUpdateAPIView.as_view(), name='car-draft-update'),
    path('energy-review/drafts-count/<int:user_id>/', EnergyReviewCountView.as_view(), name='draft-manuals'),
    
    
    # Energy Baseline Review Type
    path('baseline-reviewtype/create/', BaselineReviewTypeView.as_view(), name='root-cause-list-create'),   
    path('baseline-reviewtype/company/<int:company_id>/', BaselineReviewTypeCompanyView.as_view(), name='company-agendas'), 
    path('baseline-reviewtype/<int:pk>/', BaselineReviewDetailView.as_view(), name='root-cause-detail-update-delete'),
    
    # Energy Baseline
    path('baselines/create/', BaselineView.as_view(), name='baseline-list-create'),
    path('baselines/company/<int:company_id>/', BaselineCompanyView.as_view(), name='company-agendas'), 
    path('baselines/<int:pk>/', BaselineDetailView.as_view(), name='baseline-detail'),
    path('baselines/draft-create/', BaselineDraftAPIView.as_view(), name='manual-create'),  
    path('baselines-draft/<int:user_id>/', BaselineDraftAllList.as_view(), name='manual-list'),
    path('baselines/drafts-count/<int:user_id>/',  BaselineDraftView.as_view(), name='draft-manuals'),
    
    # Energy Improvement Performance
    path('energy-improvements/create/', EnergyImprovementsListCreateAPIView.as_view(), name='energy-improvements-list-create'),
    path('energy-improvements/company/<int:company_id>/', EnergyImprovementsCompanyView.as_view(), name='company-agendas'), 
    path('energy-improvements/<int:pk>/', EnergyImprovementsDetailAPIView.as_view(), name='energy-improvements-detail'),
    path('energy-improvements/draft-create/', EnergyImprovementsDraftAPIView.as_view(), name='manual-create'),  
    path('energy-improvements-draft/<int:user_id>/', EnergyImprovementsDraftAllList.as_view(), name='manual-list'),
    path('energy-improvements/drafts-count/<int:user_id>/',  EnergyImprovementsView.as_view(), name='draft-manuals'),
    path('energy-improvements/next-action/<int:company_id>/', GetNextEnergyImprovementEIO.as_view(), name='get-next-action-number'),
    
    # Energy Action
    path('energy-action/create/', EnergyActionView.as_view(), name='baseline-list-create'),
    path('energy-action/company/<int:company_id>/', EnergyActionCompanyView.as_view(), name='company-agendas'), 
    path('energy-action/<int:pk>/', EnergyActionDetailView.as_view(), name='baseline-detail'), 
    path('energy-action/draft-create/', EnergyActionDraftAPIView.as_view(), name='manual-create'),  
    path('energy-action-draft/<int:user_id>/', EnergyActionDraftAllList.as_view(), name='manual-list'),
    path('energy-action/drafts-count/<int:user_id>/',  EnergyActionView.as_view(), name='draft-manuals'),
    path('energy-action/next-action/<int:company_id>/', GetNextEnergyActionPlan.as_view(), name='get-next-action-number'),    
    # Source type
    path('source-type/create/', EnergySourceView.as_view(), name='root-cause-list-create'),   
    path('source-type/company/<int:company_id>/', EnergySourceReviewTypeCompanyView.as_view(), name='company-agendas'), 
    path('source-type/<int:pk>/', EnergySourceReviewDetailView.as_view(), name='root-cause-detail-update-delete'),
    
    # Significant Energy Use
    path('significant/create/', SignificantEnergyCreateAPIView.as_view(), name='car-number-list-create'),
    path('significant/<int:pk>/', SignificantEnergyDetailView.as_view(), name='car-number-detail'),
    path('significant/draft-create/', SignificantDraftAPIView.as_view(), name='manual-create'),
    path('significant/company/<int:company_id>/', SignificantCompanyCauseView.as_view(), name='company-agendas'),
    path('significant/draft/<user_id>/', SignificantDraftCompanyView.as_view(), name='company-agendas'),   
    path('significant/next-action/<int:company_id>/', GetNextsignificantReviewEnergy.as_view(), name='get-next-action-number'),
    path('significant/update/<int:pk>/', SignificantEnergyEditAPIView.as_view(), name='car-draft-update'),
    path('significant-draft/update/<int:pk>/', SignificantEnergyDraftUpdateAPIView.as_view(), name='car-draft-update'),
    path('significant/drafts-count/<int:user_id>/', SignificantCountView.as_view(), name='draft-manuals'),
    
   #  Process Activity  in Environmental Aspect
    path('process-activity/create/', ProcessActivityView.as_view(), name='root-cause-list-create'),   
    path('process-activity/company/<int:company_id>/', ProcessActivityReviewTypeCompanyView.as_view(), name='company-agendas'), 
    path('process-activity/<int:pk>/', ProcessActivityReviewDetailView.as_view(), name='root-cause-detail-update-delete'),
    
    # Risk Environmental Aspect
    path('aspect-create/', EnvironmentalAspectCreateView.as_view(), name='manual-list-create'),
    path('aspect/<int:company_id>/', AspectAllList.as_view(), name='manual-list'),
    path('aspect-detail/<int:pk>/', AspectDetailView.as_view(), name='manual-detail'),  
    path('aspect/<int:pk>/update/', EnvironmentalAspectUpdateView.as_view(), name='manual-update'),   
    path('aspect/submit-correction/', SubmitAspectCorrectionView.as_view(), name='submit-correction'),
    path('aspect/<int:aspect_correction_id>/corrections/', AspectCorrectionsListView.as_view(), name='manual-corrections-list'),   
    path('aspect-review/', AspectReviewView.as_view(), name='manual-review'),
    path('aspect/<int:aspect_id>/publish-notification/', AspectPublishNotificationView.as_view(), name='publish-notification'),
    path('aspect/draft-create/', AspectDraftAPIView.as_view(), name='manual-create'),
    path('aspect-draft/<int:user_id>/', AspectDraftAllList.as_view(), name='manual-list'),
    path('aspect/drafts-count/<int:user_id>/', AspectanualcountAPIView.as_view(), name='draft-manuals'),    
    path("notifications-aspect/<int:user_id>/", AspectNotificationView.as_view(), name="user-notifications"),  
    path("notifications/aspect<int:user_id>/", NotificationsAspect.as_view(), name="notifications_by_user"),
    path('aspect/count-notifications/<int:user_id>/', AspectUnreadNotificationsAPIView.as_view(), name='unread-notifications'),
    path('notifications-aspect/<int:notification_id>/read/', AspectMarkReadAPIView.as_view(), name='mark-notification-read'),
    path('aspect-draft/create/<int:id>/', AspectDraftEditView.as_view(), name='manual-update'),
    path('aspect/next-action/<int:company_id>/', GetNextAspectNumberView.as_view(), name='get-next-action-number'),
    
    
    # Environmental Impact Assessment
    path('impact-create/', ImpactCreateView.as_view(), name='manual-list-create'),
    path('impact/<int:company_id>/', ImpactAllList.as_view(), name='manual-list'),
    path('impact-detail/<int:pk>/', ImpactDetailView.as_view(), name='manual-detail'), 
    path('impact/<int:pk>/update/', ImpactUpdateView.as_view(), name='manual-update'),   
    path('impact/submit-correction/', SubmitImpactCorrectionView.as_view(), name='submit-correction'),
    path('impact/<int:impact_correction_id>/corrections/', ImpactCorrectionsListView.as_view(), name='manual-corrections-list'),   
    path('impact-review/', ImpactReviewView.as_view(), name='manual-review'),
    path('impact/<int:impact_id>/publish-notification/', ImpactPublishNotificationView.as_view(), name='publish-notification'),
    path('impact/draft-create/', ImpactDraftAPIView.as_view(), name='manual-create'),
    path('impact-draft/<int:user_id>/', ImpactDraftAllList.as_view(), name='manual-list'),
    path('impact/drafts-count/<int:user_id>/', DraftImpactcountAPIView.as_view(), name='draft-manuals'),    
    path("impact-notifications/<int:user_id>/", NotificationImpactView.as_view(), name="user-notifications"),  
    path("notifications/impact/<int:user_id>/", ImpactNotificationsQMS.as_view(), name="notifications_by_user"),
    path('impact/count-notifications/<int:user_id>/', ImpactUnreadNotificationsAPIView.as_view(), name='unread-notifications'),
    path('impact/notifications/<int:notification_id>/read/', ImpactMarkNotificationReadAPIView.as_view(), name='mark-notification-read'),
    path('manual/create/<int:id>/', ManualDraftEditView.as_view(), name='manual-update'),
    
    #  Environment Incident Root Cause
    path('incident-root/create/', IncidentRootActivityView.as_view(), name='root-cause-list-create'),   
    path('incident-root/company/<int:company_id>/', IncidentRootReviewDetailView.as_view(), name='company-agendas'), 
    path('incident-root/<int:pk>/', IncidentRootReviewTypeCompanyView.as_view(), name='root-cause-detail-update-delete'),
    
    # Environmental Incident
    path('incident/create/', IncidentCreateAPIView.as_view(), name='car-number-list-create'),
    path('incident-get/<int:pk>/', EnvironmentalIncidentsDetailView.as_view(), name='car-number-detail'),
    path('incident/draft-create/', IncidentDraftAPIView.as_view(), name='manual-create'),
    path('incident/company/<int:company_id>/', IncidentCompanyCauseView.as_view(), name='company-agendas'),
    path('incident/draft/<user_id>/', IncidentDraftCompanyCauseView.as_view(), name='company-agendas'),   
    path('incident/next-action/<int:company_id>/', GetNextIncidentNumberView.as_view(), name='get-next-action-number'),
    path('incident/update/<int:pk>/', EnvironmentalIncidentEditAPIView.as_view(), name='car-draft-update'),
    path('incident-draft/update/<int:pk>/', EnvironmentalInciDraftUpdateAPIView.as_view(), name='car-draft-update'),
    
    
    # Environmental Waste Management   
    path('waste/<int:company_id>/', WasteAllList.as_view(), name='manual-list'),
    path('waste-detail/<int:pk>/', WasteDetailView.as_view(), name='manual-detail'),
    path('waste-create/', EnvironmentalWasteCreateView.as_view(), name='manual-list-create'),
    path('waste/<int:pk>/update/', WasteUpdateView.as_view(), name='manual-update'),   
    path('waste/submit-correction/', SubmitWasteCorrectionView.as_view(), name='submit-correction'),
    path('waste/<int:waste_correction_id>/corrections/', WasteCorrectionsListView.as_view(), name='manual-corrections-list'),   
    path('waste-review/', WasteReviewView.as_view(), name='manual-review'),
    path('waste/<int:waste_id>/publish-notification/', WastePublishNotificationView.as_view(), name='publish-notification'),
    path('waste/draft-create/', EnvironmentalWasteDraftAPIView.as_view(), name='manual-create'),
    path('waste-draft/<int:user_id>/', WasteDraftAllList.as_view(), name='manual-list'),
    path('waste/drafts-count/<int:user_id>/', DraftWastecountAPIView.as_view(), name='draft-manuals'),    
    path("waste/notifications/<int:user_id>/", WasteNotificationView.as_view(), name="user-notifications"),  
    path("notifications-waste/<int:user_id>/", WasteNotificationsQMS.as_view(), name="notifications_by_user"),
    path('waste/count-notifications/<int:user_id>/', WasteUnreadNotificationsAPIView.as_view(), name='unread-notifications'),
    path('waste/notifications/<int:notification_id>/read/', WasteMarkNotificationAPIView.as_view(), name='mark-notification-read'),
    path('waste/create/<int:id>/', WasteDraftEditView.as_view(), name='manual-update'),
    path('waste/next-action/<int:company_id>/', GetNextWMPNumberView.as_view(), name='get-next-action-number'),
    
    
    # Health and Safety Incident process
    path('health-root/create/', ProcessHealthView.as_view(), name='root-cause-list-create'),   
    path('health-root/company/<int:company_id>/', ProcessHealthCompanyView.as_view(), name='company-agendas'), 
    path('health-root/<int:pk>/', ProcessHealthDetailView.as_view(), name='root-cause-detail-update-delete'),
    
      
    # Health and Safety
    path('health/<int:company_id>/', HealthAllList.as_view(), name='manual-list'),
    path('health-detail/<int:pk>/', HealthDetailView.as_view(), name='manual-detail'),
    path('heath-create/', HealthSafetyCreateView.as_view(), name='manual-list-create'),
    path('health/<int:pk>/update/', HealthUpdateView.as_view(), name='manual-update'),   
    path('health/submit-correction/', SubmitHealthCorrectionView.as_view(), name='submit-correction'),
    path('health/<int:health_correction_id>/corrections/', HealthCorrectionsListView.as_view(), name='manual-corrections-list'),   
    path('health-review/', HealthReviewView.as_view(), name='manual-review'),
    path('health/<int:health_id>/publish-notification/', HealthPublishNotificationView.as_view(), name='publish-notification'),
    path('health/draft-create/', EnvironmentalHealthDraftAPIView.as_view(), name='manual-create'),
    path('health-draft/<int:user_id>/', HealthDraftAllList.as_view(), name='manual-list'),
    path('health/drafts-count/<int:user_id>/', DraftHealthcountAPIView.as_view(), name='draft-manuals'),    
    path("health/notifications/<int:user_id>/", HealthNotificationView.as_view(), name="user-notifications"),  
    path("notifications-health/<int:user_id>/", HealthNotificationsQMS.as_view(), name="notifications_by_user"),
    path('health/count-notifications/<int:user_id>/', HealthUnreadNotificationsAPIView.as_view(), name='unread-notifications'),
    path('health/notifications/<int:notification_id>/read/', HealthMarkNotificationAPIView.as_view(), name='mark-notification-read'),
    path('health/create/<int:id>/', HealthDraftEditView.as_view(), name='manual-update'),
    path('health/next-action/<int:company_id>/', GetNextHazardNumberView.as_view(), name='get-next-action-number'),
    
    
    # Health and Safety Risk Assessments
    path('assessment/<int:company_id>/', AssessmentAllList.as_view(), name='manual-list'),
    path('assessment-detail/<int:pk>/', AssessmentDetailView.as_view(), name='manual-detail'),
    path('assessment-create/', RiskAssessmentCreateView.as_view(), name='manual-list-create'),
    path('assessment/<int:pk>/update/', RiskAssessmentUpdateView.as_view(), name='manual-update'),   
    path('assessment/submit-correction/', RiskAssessmentCorrectionView.as_view(), name='submit-correction'),
    path('assessment/<int:assessment_correction_id>/corrections/', AssessmentCorrectionsListView.as_view(), name='manual-corrections-list'),   
    path('assessment-review/', AssessmentReviewView.as_view(), name='manual-review'),
    path('assessment/<int:assessment_id>/publish-notification/', AssessmentPublishNotificationView.as_view(), name='publish-notification'),
    path('assessment/draft-create/', AssessmentlDraftAPIView.as_view(), name='manual-create'),
    path('assessment-draft/<int:user_id>/', AssessmentDraftAllList.as_view(), name='manual-list'),
    path('assessment/drafts-count/<int:user_id>/', AssessmentcountAPIView.as_view(), name='draft-manuals'),    
    path("assessment/notifications/<int:user_id>/", AssessmentNotificationView.as_view(), name="user-notifications"),  
    path("notifications-assessment/<int:user_id>/", AssessmentNotificationsQMS.as_view(), name="notifications_by_user"),
    path('assessment/count-notifications/<int:user_id>/', AssessmentUnreadNotificationsAPIView.as_view(), name='unread-notifications'),
    path('assessment/notifications/<int:notification_id>/read/', AssessmentMarkNotificationAPIView.as_view(), name='mark-notification-read'),
    path('assessment/create/<int:id>/', AssessmentDraftEditView.as_view(), name='manual-update'),
    
    # HealthRootCause in Health and Safety Incidents
    path('safety-root/create/', SafetyRoothView.as_view(), name='root-cause-list-create'),   
    path('safety-root/company/<int:company_id>/', SafetyRootCompanyView.as_view(), name='company-agendas'), 
    path('safety-root/<int:pk>/', SafetyRootDetailView.as_view(), name='root-cause-detail-update-delete'),
    
    
    path('safety_incidents/', HealthIncidentCreateAPIView.as_view(), name='car-number-list-create'),
    path('safety_incidents/<int:pk>/', HealthIncidentDetailView.as_view(), name='car-number-detail'),
    path('safety_incidents/draft-create/', HealthIncidentDraftAPIView.as_view(), name='manual-create'),
    path('safety_incidents/company/<int:company_id>/', HealthIncidentCompanyView.as_view(), name='company-agendas'),
    path('safety_incidents/draft/<user_id>/', HealthIncidentDrafteView.as_view(), name='company-agendas'),   
    path('safety_incidents/next-action/<int:company_id>/', GetNextIncidentNumberView.as_view(), name='get-next-action-number'),
    path('safety_incidents/update/<int:pk>/', HealthIncidentEditAPIView.as_view(), name='car-draft-update'),
    path('safety_incidents-draft/update/<int:pk>/', HealthIncidentDraftUpdateAPIView.as_view(), name='car-draft-update'),
       
]



