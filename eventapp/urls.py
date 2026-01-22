from django.urls import path
 
from .views import AboutUsItemAPIView, CardComponentAPIView, CarsouselItem1APIView, CompanyDetailItemAPIView, EventAPIView, EventParticipantAPIView, LoginAPIView, NavbarAPIView, PageAPIView, RefreshTokenAPIView, TopNav1APIView, UserRegAPIView, VerifyEmailCodeAPIView, get_user_id_by_email

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
    path("aboutus-item/",AboutUsItemAPIView.as_view(),name="aboutus-api"),
    path("top-nav-1/", TopNav1APIView.as_view(), name="top-nav-api"),
    path("navbar-list/", NavbarAPIView.as_view(), name="navbar-api"),
    path("event-participant/", EventParticipantAPIView.as_view(), name="event-participant-api"),
    path("get-userid/", get_user_id_by_email,name="get-user-id"),
]