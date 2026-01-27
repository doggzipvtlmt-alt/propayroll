from django.urls import path

from hr import views

urlpatterns = [
    path('hr/employees', views.EmployeeListCreateView.as_view(), name='employees'),
    path('hr/employees/<str:employee_id>', views.EmployeeDetailView.as_view(), name='employee-detail'),
    path('hr/employees/<str:employee_id>/approve', views.EmployeeApprovalView.as_view(), name='employee-approve'),
    path('hr/employees/<str:employee_id>/reject', views.EmployeeRejectView.as_view(), name='employee-reject'),
    path('hr/salary-limits', views.SalaryLimitView.as_view(), name='salary-limits'),
    path('hr/dashboard', views.HRDashboardView.as_view(), name='hr-dashboard'),
]
