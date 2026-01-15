from django.urls import path
from .views import CompanyDetailItemAPIView, LoginAPIView, RefreshTokenAPIView, UserRegAPIView, VerifyEmailCodeAPIView

urlpatterns = [
    
    path('reg-user/', UserRegAPIView.as_view(), name='user-reg-api'),
    path('verify-email/', VerifyEmailCodeAPIView.as_view(), name='verify-email-api'),
    path('login/',LoginAPIView.as_view(),name='login'),
    path("refresh-token/", RefreshTokenAPIView.as_view(),name="refresh-token"),
    path("company-detail-item/",CompanyDetailItemAPIView.as_view(),name="company-detail"),
]