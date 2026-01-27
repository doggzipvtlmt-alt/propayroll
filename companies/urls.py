from django.urls import path

from companies import views

urlpatterns = [
    path('employee/me', views.EmployeeProfileView.as_view(), name='employee-me'),
    path('employee/documents', views.EmployeeDocumentView.as_view(), name='employee-documents'),
    path('employee/leave-requests', views.LeaveRequestView.as_view(), name='employee-leave'),
    path('employee/salary-slips', views.SalarySlipView.as_view(), name='employee-salary'),
    path('employee/grievances', views.GrievanceView.as_view(), name='employee-grievance'),
    path('employee/notices', views.NoticesView.as_view(), name='employee-notices'),
    path('employee/surveys', views.SurveysView.as_view(), name='employee-surveys'),
]
