from django.urls import path
from .views import CardComponentAPIView, CarsouselItem1APIView, CompanyDetailItemAPIView, EventAPIView, LoginAPIView, PageAPIView, RefreshTokenAPIView, UserRegAPIView, VerifyEmailCodeAPIView

urlpatterns = [
    
    path('reg-user/', UserRegAPIView.as_view(), name='user-reg-api'),
    path('verify-email/', VerifyEmailCodeAPIView.as_view(), name='verify-email-api'),
    path('login/',LoginAPIView.as_view(),name='login'),
    path("refresh-token/", RefreshTokenAPIView.as_view(),name="refresh-token"),
    path("company-detail-item/",CompanyDetailItemAPIView.as_view(),name="company-detail"),
    path("event-item/",EventAPIView.as_view(),name="event-item"),
    path("pages-item/", PageAPIView.as_view(), name="pages"),
    path("cards-item/", CardComponentAPIView.as_view(), name="cards"),
    path("carousel1-item/", CarsouselItem1APIView.as_view(), name="carousel-api"),
]