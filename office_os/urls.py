from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from core.views import (
    root_view,
    health_view,
    TemplateDownloadView,
    ImportModuleView,
    CandidateListCreateView,
    OnboardingCreateView,
    AttendanceListCreateView,
)

urlpatterns = [
    path('', root_view, name='root'),
    path('health', health_view, name='health'),
    path('api/', include('accounts.urls')),
    path('api/', include('hr.urls')),
    path('api/', include('workflows.urls')),
    path('api/', include('finance.urls')),
    path('api/', include('companies.urls')),
    path('api/templates/<str:module>', TemplateDownloadView.as_view(), name='templates'),
    path('api/import/<str:module>', ImportModuleView.as_view(), name='import'),
    path('api/hrms/candidates', CandidateListCreateView.as_view(), name='hrms-candidates'),
    path('api/hrms/onboarding', OnboardingCreateView.as_view(), name='hrms-onboarding'),
    path('api/hrms/attendance', AttendanceListCreateView.as_view(), name='hrms-attendance'),
    path('api/schema', SpectacularAPIView.as_view(), name='schema'),
    path('docs', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
