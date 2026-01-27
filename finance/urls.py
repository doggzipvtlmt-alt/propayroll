from django.urls import path

from finance import views

urlpatterns = [
    path('finance/revenue', views.RevenueView.as_view(), name='finance-revenue'),
    path('finance/expenses', views.ExpenseView.as_view(), name='finance-expenses'),
    path('finance/payroll', views.PayrollView.as_view(), name='finance-payroll'),
    path('finance/budgets', views.BudgetView.as_view(), name='finance-budgets'),
    path('finance/reports', views.ReportExportView.as_view(), name='finance-reports'),
]
