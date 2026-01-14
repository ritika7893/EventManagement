from django.urls import path
from .views import UserRegAPIView, VerifyEmailCodeAPIView

urlpatterns = [
    
    path('reg-user/', UserRegAPIView.as_view(), name='user-reg-api'),
    path('verify-email/', VerifyEmailCodeAPIView.as_view(), name='verify-email-api'),
]