from django.urls import path

from workflows import views

urlpatterns = [
    path('workflows/appraisals', views.AppraisalListCreateView.as_view(), name='appraisals'),
    path('workflows/appraisals/<str:appraisal_id>/submit', views.AppraisalSubmitView.as_view(), name='appraisal-submit'),
    path('workflows/appraisals/<str:appraisal_id>/approve', views.AppraisalApproveView.as_view(), name='appraisal-approve'),
    path('workflows/promotions', views.PromotionListCreateView.as_view(), name='promotions'),
    path('workflows/promotions/<str:promotion_id>/approve', views.PromotionApproveView.as_view(), name='promotion-approve'),
    path('workflows/promotions/<str:promotion_id>/reject', views.PromotionRejectView.as_view(), name='promotion-reject'),
]
