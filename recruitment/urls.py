from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='recruitment-home'),
    path('intake', views.intake, name='recruitment-intake'),
    path('pipeline', views.pipeline, name='recruitment-pipeline'),
    path('candidate/<int:candidate_id>/status', views.update_status, name='recruitment-update-status'),
    path('candidate/<int:candidate_id>/reminder', views.send_reminder, name='recruitment-send-reminder'),
    path('login/<str:role>', views.pin_login, name='recruitment-pin'),
    path('interviewer/today', views.interviewer_today, name='recruitment-interviewer-today'),
    path('interviewer/<int:candidate_id>/action', views.interviewer_action, name='recruitment-interviewer-action'),
    path('hr/panel', views.hr_panel, name='recruitment-hr-panel'),
    path('hr/<int:candidate_id>/document', views.hr_update_document, name='recruitment-hr-document'),
    path('hr/<int:candidate_id>/finalize', views.hr_finalize, name='recruitment-hr-finalize'),
    path('admin/dashboard', views.admin_dashboard, name='recruitment-admin-dashboard'),
]
