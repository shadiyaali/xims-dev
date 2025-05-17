from django.contrib import admin
from .models import *
 


admin.site.register(PolicyDocumentation)
admin.site.register(Manual)
admin.site.register(Procedure)
admin.site.register(RecordFormat)
admin.site.register(NotificationQMS)
admin.site.register(CorrectionQMS)
admin.site.register(NotificatioProcedure)
admin.site.register(CorrectionProcedure)
admin.site.register(NotificationRecord)
admin.site.register(CorrectionRecord)
admin.site.register(Compliances)
admin.site.register(InterestedParty)
admin.site.register(Needs)
 
admin.site.register(NotificationInterest)
admin.site.register(Processes)
admin.site.register(NotificationProcess)
admin.site.register(ComplianceNotification)
admin.site.register(LegalRequirement)
admin.site.register(NotificationLegal)
admin.site.register(Evaluation)
admin.site.register(CorrectionEvaluation)
admin.site.register(NotificationEvaluations)
admin.site.register(ManagementChanges)
admin.site.register(NotificationChanges)
admin.site.register(Sustainabilities)
admin.site.register(CorrectionSustainability)
admin.site.register(NotificationSustainability)
admin.site.register(AwarenessTraining)
admin.site.register(Training)
admin.site.register(TrainingNotification)
admin.site.register(EmployeePerformance)
admin.site.register(PerformanceQuestions)
admin.site.register(EmployeeSurvey)
admin.site.register(SurveyQuestions)
admin.site.register(Scope)
admin.site.register(Agenda)
admin.site.register(Meeting)
admin.site.register(MeetingNotification)

admin.site.register(Audit)
admin.site.register(Inspection)
admin.site.register(Cause)

admin.site.register(RootCause)
admin.site.register(CarNumber)
admin.site.register(CarNotification)

admin.site.register(InternalProblem)
admin.site.register(Supplier)
admin.site.register(SupplierProblem)
admin.site.register(SupplierEvaluation)
admin.site.register(SupplierEvaluationQuestions)
admin.site.register(Complaints)
admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(CustomerQuestions)
admin.site.register(CustomerSatisfaction)

admin.site.register(EmployeeTrainingEvaluation)
admin.site.register(EmployeeTrainingEvaluationQuestions)

admin.site.register(Message)
 

admin.site.register(PreventiveAction)
admin.site.register(PreventiveActionNotification)

admin.site.register(Objectives)
admin.site.register(Targets)
admin.site.register(Programs)

admin.site.register(ConformityCause)
admin.site.register(ConformityReport)
admin.site.register(ConformityNotification)

admin.site.register(ReviewType)
admin.site.register(EnergyReview)

admin.site.register(BaselineReview)
admin.site.register(Baseline)
admin.site.register(Enpis)

admin.site.register(EnergyImprovement)

admin.site.register(EnergyAction)
admin.site.register(ProgramAction)


admin.site.register(EnergySource)
admin.site.register(SignificantEnergy)

 
admin.site.register(ProcessActivity)
admin.site.register(EnvironmentalAspect)
admin.site.register(NotificationAspect)
admin.site.register(CorrectionAspect)

admin.site.register(EnvironmentalImpact)
admin.site.register(NotificationImpact)
admin.site.register(CorrectionImpact)

admin.site.register(EnvironmentalIncidents)
admin.site.register(IncidentRoot)


admin.site.register(EnvironmentalWaste)

admin.site.register(ProcessHealth)
admin.site.register(HealthSafety)
admin.site.register(NotificationHealth)
admin.site.register(CorrectionHealth)


admin.site.register(RiskAssessment)
admin.site.register(NotificationAssessments)
admin.site.register(CorrectionAssessments)


admin.site.register(HealthRootCause)
admin.site.register(HealthIncidents)