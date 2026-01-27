from django.urls import path

from accounts import views

urlpatterns = [
    path('auth/signup', views.SignupView.as_view(), name='auth-signup'),
    path('auth/login', views.LoginView.as_view(), name='auth-login'),
    path('auth/pending', views.PendingSignupView.as_view(), name='auth-pending'),
    path('auth/approve/<str:request_id>', views.ApproveSignupView.as_view(), name='auth-approve'),
    path('auth/reject/<str:request_id>', views.RejectSignupView.as_view(), name='auth-reject'),
]
