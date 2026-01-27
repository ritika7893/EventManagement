
from eventapp.permissions import IsAdminRole
from .models import ConcertEventServiceItem, ContactUs, CorporateEventServiceItem, EntertainmentEventServiceItem, Event, AboutUsItem, AllLog, CardComponentItem, CarsouselItem1, CompanyDetailsItem, DiscoverYourTalentItem, EmailVerification, EventParticipant, GalleryItem, PageItem, PrivatePartiesEventServiceItem, SeminarEventServiceItem, TopNav1, UserReg
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from .serializers import  AboutUsItemSerializer, CardComponentItemSerializer, CarsouselItem1Serializer,  CompanyDetailItemSerializer, ConcertEventServiceItemSerializer, ContactUsSerializer, CorporateEventServiceItemSerializer, DiscoverYourTalentItemSerializer, EntertainmentEventsServiceItemSerializer,  EventParticipantSerializer, EventSerializer, GalleryItemSerializer,  PageItemSerializer, PageNavbarSerializer, PrivatePartiesEventServiceItemSerializer, ResendEmailOTPSerializer, ResetPasswordEmailOTPSerializer, ResetPasswordSerializer, SeminarEventServiceItemSerializer, TopNav1Serializer, UserRegSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import make_password,check_password
# Create your views here.
class UserRegAPIView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [AllowAny()]
    def get(self, request):
        user_id = request.query_params.get("user_id")

        if user_id:
            try:
                user = UserReg.objects.get(user_id=user_id)
                serializer = UserRegSerializer(user)
                return Response({"success": True, "data": serializer.data})
            except UserReg.DoesNotExist:
                return Response(
                    {"success": False, "message": "User not found"},
                    status=404
                )

        users = UserReg.objects.all().order_by("-created_at")
        serializer = UserRegSerializer(users, many=True)
        return Response({"success": True, "data": serializer.data})

  
    def post(self, request):
        serializer = UserRegSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        if hasattr(user, "_resent"):
            return Response({
                "success": False,
                "message": "Email not verified. Verification code resent."
            }, status=status.HTTP_200_OK)

        return Response({
            "success": True,
            "message": "Registration successful. Verification email sent.",
            "user_id": user.user_id
        }, status=status.HTTP_201_CREATED)

    def put(self, request):
        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"success": False, "message": "user_id is required"},
                status=400
            )

        try:
            user = UserReg.objects.get(user_id=user_id)
        except UserReg.DoesNotExist:
            return Response(
                {"success": False, "message": "User not found"},
                status=404
            )

        serializer = UserRegSerializer(
            user, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "User updated successfully"}
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )
    
class VerifyEmailCodeAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")

        if not email or not code:
            return Response(
                {"success": False, "message": "Email and code are required"},
                status=400
            )

        try:
            verification = EmailVerification.objects.filter(
                user__email=email,
                verification_code=code,
                is_verified=False
            ).latest("created_at")
        except EmailVerification.DoesNotExist:
            return Response(
                {"success": False, "message": "Invalid verification code"},
                status=400
            )

        verification.is_verified = True
        verification.verified_at = now()
        verification.save()

        # Mark AllLog verified
        AllLog.objects.filter(email=email).update(is_verified=True)

        return Response(
            {"success": True, "message": "Email Code verified successfully"}
        )
class LoginAPIView(APIView):
    def post(self, request):
        email_or_phone = request.data.get("email_or_phone")
        password = request.data.get("password")

        if not email_or_phone or not password:
            return Response(
                {"error": "Email/Phone and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get user
            if "@" in email_or_phone:
                user = AllLog.objects.get(email=email_or_phone)
            else:
                user = AllLog.objects.get(phone=email_or_phone)

            if not user.is_active or not user.is_verified:
                return Response(
                    {"error": "Account is disabled"},
                    status=status.HTTP_403_FORBIDDEN
                )
          

            if not check_password(password, user.password):
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            
            refresh = RefreshToken.for_user(user)
            refresh["unique_id"] = user.unique_id
            refresh["role"] = user.role

            return Response(
                {
                    "message": "Login successful",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "unique_id": user.unique_id,
                    "role": user.role,
                },
                status=status.HTTP_200_OK
            )

        except AllLog.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
class RefreshTokenAPIView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            refresh = RefreshToken(refresh_token)
            access = refresh.access_token

            return Response(
                {
                    "access": str(access)
                },
                status=status.HTTP_200_OK
            )

        except TokenError:
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )
class DiscoverYourTalentItemAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    
    def get_permissions(self):
        return [AllowAny()] if self.request.method == "GET" else [IsAdminRole()]

    def get(self, request):
        item_id = request.query_params.get("id")

        if item_id:
            try:
                item = DiscoverYourTalentItem.objects.get(id=item_id)
                serializer = DiscoverYourTalentItemSerializer(item)
                return Response({"success": True, "data": serializer.data})
            except DiscoverYourTalentItem.DoesNotExist:
                return Response(
                    {"success": False, "message": "Item not found"},
                    status=404
                )

        items = DiscoverYourTalentItem.objects.all().order_by("-id")
        serializer = DiscoverYourTalentItemSerializer(items, many=True)
        return Response({"success": True, "data": serializer.data})

    # 🔹 POST (create)
    def post(self, request):
        serializer = DiscoverYourTalentItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Item created successfully"},
                status=201
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )

   
    def put(self, request):
        item_id = request.data.get("id")
        if not item_id:
            return Response(
                {"success": False, "message": "Item ID is required"},
                status=400
            )

        try:
            item = DiscoverYourTalentItem.objects.get(id=item_id)
        except DiscoverYourTalentItem.DoesNotExist:
            return Response(
                {"success": False, "message": "Item not found"},
                status=404
            )

        serializer = DiscoverYourTalentItemSerializer(
            item, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Item updated successfully"}
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )

   
    def delete(self, request):
        item_id = request.data.get("id")
        if not item_id:
            return Response(
                {"success": False, "message": "Item ID is required"},
                status=400
            )

        try:
            DiscoverYourTalentItem.objects.get(id=item_id).delete()
            return Response(
                {"success": True, "message": "Item deleted successfully"}
            )
        except DiscoverYourTalentItem.DoesNotExist:
            return Response(
                {"success": False, "message": "Item not found"},
                status=404
            )
class CompanyDetailItemAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        return [AllowAny()] if self.request.method == "GET" else [IsAdminRole()]

    def get(self, request):
        item_id = request.query_params.get("id")

        if item_id:
            try:
                item = CompanyDetailsItem.objects.get(id=item_id)
                return Response({"success": True, "data": CompanyDetailItemSerializer(item).data})
            except CompanyDetailsItem.DoesNotExist:
                return Response({"success": False, "message": "Company not found"}, status=404)

        items = CompanyDetailsItem.objects.all().order_by("-id")
        return Response({"success": True, "data": CompanyDetailItemSerializer(items, many=True).data})

    def post(self, request):
        serializer = CompanyDetailItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Company created successfully"}, status=201)
        return Response({"success": False, "errors": serializer.errors}, status=400)

    def put(self, request):
        item_id = request.data.get("id")
        if not item_id:
            return Response({"success": False, "message": "Item ID is required"}, status=400)

        try:
            item = CompanyDetailsItem.objects.get(id=item_id)
        except CompanyDetailsItem.DoesNotExist:
            return Response({"success": False, "message": "Company not found"}, status=404)

        serializer = CompanyDetailItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Company updated successfully"})
        return Response({"success": False, "errors": serializer.errors}, status=400)

    def delete(self, request):
        item_id = request.data.get("id")
        if not item_id:
            return Response({"success": False, "message": "Item ID is required"}, status=400)

        try:
            CompanyDetailsItem.objects.get(id=item_id).delete()
            return Response({"success": True, "message": "Company deleted successfully"})
        except CompanyDetailsItem.DoesNotExist:
            return Response({"success": False, "message": "Company not found"}, status=404)
        
class EventAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        return [AllowAny()] if self.request.method == "GET" else [IsAdminRole()]

    def get(self, request):
        event_id = request.query_params.get("event_id")

        if event_id:
            event = Event.objects.filter(event_id=event_id).first()
            if not event:
                return Response({"success": False, "message": "Event not found"}, status=404)

            return Response({"success": True, "data": EventSerializer(event).data})

        events = Event.objects.all().order_by("-created_at")
        return Response({"success": True, "data": EventSerializer(events, many=True).data})

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Event created successfully"}, status=201)

        return Response({"success": False, "errors": serializer.errors}, status=400)

    def put(self, request):
        event_id = request.data.get("event_id")
        if not event_id:
            return Response({"success": False, "message": "event_id is required"}, status=400)

        event = Event.objects.filter(event_id=event_id).first()
        if not event:
            return Response({"success": False, "message": "Event not found"}, status=404)

        serializer = EventSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Event updated successfully"})

        return Response({"success": False, "errors": serializer.errors}, status=400)

    def delete(self, request):
        event_id = request.data.get("event_id")
        if not event_id:
            return Response({"success": False, "message": "event_id is required"}, status=400)

        deleted, _ = Event.objects.filter(event_id=event_id).delete()
        if not deleted:
            return Response({"success": False, "message": "Event not found"}, status=404)

        return Response({"success": True, "message": "Event deleted successfully"})
class PageAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        return [AllowAny()] if self.request.method == "GET" else [IsAdminRole()]

    def get(self, request):
        page_id = request.query_params.get("id")

        if page_id:
            page = PageItem.objects.filter(id=page_id).first()
            if not page:
                return Response(
                    {"success": False, "message": "Page not found"},
                    status=404
                )

            return Response(
                {"success": True, "data": PageItemSerializer(page).data}
            )

        pages = PageItem.objects.all().order_by("-created_at")
        return Response(
            {"success": True, "data": PageItemSerializer(pages, many=True).data}
        )


    def post(self, request):
        serializer = PageItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Page created successfully"},
                status=201
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )


    def put(self, request):
        page_id = request.data.get("id")
        if not page_id:
            return Response(
                {"success": False, "message": "id is required"},
                status=400
            )

        page = PageItem.objects.filter(id=page_id).first()
        if not page:
            return Response(
                {"success": False, "message": "Page not found"},
                status=404
            )

        serializer = PageItemSerializer(page, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Page updated successfully"}
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )


    def delete(self, request):
        page_id = request.data.get("id")
        if not page_id:
            return Response(
                {"success": False, "message": "id is required"},
                status=400
            )

        deleted, _ = PageItem.objects.filter(id=page_id).delete()
        if not deleted:
            return Response(
                {"success": False, "message": "Page not found"},
                status=404
            )

        return Response(
            {"success": True, "message": "Page deleted successfully"}
        )
class CardComponentAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        return [AllowAny()] if self.request.method == "GET" else [IsAdminRole()]
    def get(self, request):
        page_id = request.query_params.get("page_id")
        card_id = request.query_params.get("id")

        if card_id:
            card = CardComponentItem.objects.filter(id=card_id).first()
            if not card:
                return Response(
                    {"success": False, "message": "Card not found"},
                    status=404
                )

            return Response(
                {"success": True, "data": CardComponentItemSerializer(card).data}
            )

        if page_id:
            cards = CardComponentItem.objects.filter(
                page_id=page_id
            ).order_by("-created_at")

            return Response(
                {"success": True, "data": CardComponentItemSerializer(cards, many=True).data}
            )

        cards = CardComponentItem.objects.all().order_by("-created_at")
        return Response(
            {"success": True, "data": CardComponentItemSerializer(cards, many=True).data}
        )
    def post(self, request):
        serializer = CardComponentItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Card created successfully"},
                status=201
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )
    def put(self, request):
        card_id = request.data.get("id")
        if not card_id:
            return Response(
                {"success": False, "message": "id is required"},
                status=400
            )

        card = CardComponentItem.objects.filter(id=card_id).first()
        if not card:
            return Response(
                {"success": False, "message": "Card not found"},
                status=404
            )

        serializer = CardComponentItemSerializer(
            card, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Card updated successfully"}
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )
    def delete(self, request):
        card_id = request.data.get("id")
        if not card_id:
            return Response(
                {"success": False, "message": "id is required"},
                status=400
            )

        deleted, _ = CardComponentItem.objects.filter(id=card_id).delete()
        if not deleted:
            return Response(
                {"success": False, "message": "Card not found"},
                status=404
            )

        return Response(
            {"success": True, "message": "Card deleted successfully"}
        )
class CarsouselItem1APIView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        return [AllowAny()] if self.request.method == "GET" else [IsAdminRole()]

   
    def get(self, request):
        page_id = request.query_params.get("page_id")
        carousel_id = request.query_params.get("id")

        if carousel_id:
            carousel = CarsouselItem1.objects.filter(id=carousel_id).first()
            if not carousel:
                return Response({"success": False, "message": "Not found"}, status=404)

            return Response({"success": True, "data": CarsouselItem1Serializer(carousel).data})

        if page_id:
            return Response({
                "success": True,
                "data": CarsouselItem1Serializer(
                    CarsouselItem1.objects.filter(page_id=page_id),
                    many=True
                ).data
            })

        return Response({
            "success": True,
            "data": CarsouselItem1Serializer(
                CarsouselItem1.objects.all(),
                many=True
            ).data
        })

   
    def post(self, request):
        serializer = CarsouselItem1Serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True,"message": "Carousel item created successfully"}, status=201)

        return Response({"success": False, "message": "Invalid data"}, status=400)

  
    def put(self, request):
        carousel_id = request.data.get("id")
        carousel = CarsouselItem1.objects.filter(id=carousel_id).first()

        if not carousel:
            return Response({"success": False, "message": "Carousel item not found"}, status=404)

        serializer = CarsouselItem1Serializer(carousel, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True,"message": "Carousel item updated successfully"})

        return Response({"success": False}, status=400)


    def delete(self, request):
        carousel_id = request.data.get("id")
        deleted, _ = CarsouselItem1.objects.filter(id=carousel_id).delete()

        if not deleted:
            return Response({"success": False, "message": "Carousel item not found"}, status=404)

        return Response({"success": True, "message": "Carousel item deleted successfully"})

class AboutUsItemAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    def get_permissions(self):
        return [AllowAny()] if self.request.method == "GET" else [IsAdminRole()]


    def get(self, request):
        page_id = request.query_params.get("page_id")
        about_id = request.query_params.get("id")

        if about_id:
            about = AboutUsItem.objects.filter(id=about_id).first()
            if not about:
                return Response(
                    {"success": False, "message": "AboutUs not found"},
                    status=404
                )

            return Response(
                {"success": True, "data": AboutUsItemSerializer(about).data}
            )

        if page_id:
            about_list = AboutUsItem.objects.filter(
                page_id=page_id
            ).order_by("-created_at")

            return Response(
                {"success": True, "data": AboutUsItemSerializer(about_list, many=True).data}
            )

        about_list = AboutUsItem.objects.all().order_by("-created_at")
        return Response(
            {"success": True, "data": AboutUsItemSerializer(about_list, many=True).data}
        )

    def post(self, request):
        serializer = AboutUsItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "AboutUs created successfully"},
                status=201
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )

    def put(self, request):
        about_id = request.data.get("id")
        if not about_id:
            return Response(
                {"success": False, "message": "id is required"},
                status=400
            )

        about = AboutUsItem.objects.filter(id=about_id).first()
        if not about:
            return Response(
                {"success": False, "message": "AboutUs not found"},
                status=404
            )

        serializer = AboutUsItemSerializer(
            about, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "AboutUs updated successfully"}
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )

    def delete(self, request):
        about_id = request.data.get("id")
        if not about_id:
            return Response(
                {"success": False, "message": "id is required"},
                status=400
            )

        deleted, _ = AboutUsItem.objects.filter(id=about_id).delete()
        if not deleted:
            return Response(
                {"success": False, "message": "AboutUs not found"},
                status=404
            )

        return Response(
            {"success": True, "message": "AboutUs deleted successfully"}
        )


class TopNav1APIView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        return [AllowAny()] if self.request.method == "GET" else [IsAdminRole()]

    def get(self, request):
        item_id = request.query_params.get("id")

        if item_id:
            try:
                item = TopNav1.objects.get(id=item_id)
                return Response(
                    {"success": True, "data": TopNav1Serializer(item).data}
                )
            except TopNav1.DoesNotExist:
                return Response(
                    {"success": False, "message": "TopNav item not found"},
                    status=404
                )

       
        queryset = TopNav1.objects.all()
        serializer = TopNav1Serializer(queryset, many=True)

        response = {
            "success": True,
            "left": [],
            "right": []
        }

        for item in serializer.data:
            pos = item.get("position")
            if pos in response:
                response[pos].append(item)

        return Response(response)

    def post(self, request):
        serializer = TopNav1Serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "TopNav item created successfully"},
                status=201
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )

    def put(self, request):
        item_id = request.data.get("id")
        if not item_id:
            return Response(
                {"success": False, "message": "Item ID is required"},
                status=400
            )

        try:
            item = TopNav1.objects.get(id=item_id)
        except TopNav1.DoesNotExist:
            return Response(
                {"success": False, "message": "TopNav item not found"},
                status=404
            )

        serializer = TopNav1Serializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "TopNav item updated successfully"}
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )

    def delete(self, request):
        item_id = request.data.get("id")
        if not item_id:
            return Response(
                {"success": False, "message": "Item ID is required"},
                status=400
            )

        try:
            TopNav1.objects.get(id=item_id).delete()
            return Response(
                {"success": True, "message": "TopNav item deleted successfully"}
            )
        except TopNav1.DoesNotExist:
            return Response(
                {"success": False, "message": "TopNav item not found"},
                status=404
            )
class NavbarAPIView(APIView):
    def get(self, request):
        root_pages = PageItem.objects.filter(
            parent__isnull=True,
            show_in_nav=True
        ).order_by("nav_order")

        serializer = PageNavbarSerializer(root_pages, many=True)
        return Response(serializer.data)
class EventParticipantAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]  # only logged-in users
        return [AllowAny()] 
    def post(self, request):
        serializer = EventParticipantSerializer(data=request.data)
        if serializer.is_valid():
            participant = serializer.save()
            return Response(
                {"success": True, "message": "Participant registered successfully",},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request):
            user_id = request.query_params.get("user_id")
            event_id = request.query_params.get("event_id")

            queryset = EventParticipant.objects.all()

            if user_id:
                queryset = queryset.filter(user_id__user_id=user_id)

            if event_id:
                queryset = queryset.filter(event_id__event_id=event_id)

            serializer = EventParticipantSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
from rest_framework.decorators import api_view
@api_view(['GET'])
def get_user_id_by_email(request):
    email = request.query_params.get("email")

    if not email:
        return Response(
            {"message": "email is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = UserReg.objects.get(email=email)
        return Response(
            {
                "user_id": user.user_id,
                "message": "User found"
            },
            status=status.HTTP_200_OK
        )
    except UserReg.DoesNotExist:
        return Response(
            {"message": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )
class ContactUsAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        return [IsAdminRole()]
    
    def post(self, request):
        serializer = ContactUsSerializer(data=request.data)
        if serializer.is_valid():
            contact = serializer.save()
            return Response(
                {"message": "Contact message submitted successfully!"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request):
        contacts = ContactUs.objects.all().order_by('-id')
        serializer = ContactUsSerializer(contacts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
class ResendEmailOTPView(APIView):
    def post(self, request):
        serializer = ResendEmailOTPSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.save()
            return Response(data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ResetPasswordEmailOTPAPIView(APIView):
    def post(self,request):
        serializer=ResetPasswordEmailOTPSerializer(data=request.data)
        if serializer.is_valid():
            data=serializer.save()
            return Response(data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
class ResetPasswordAPIView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.save())
        return Response(serializer.errors, status=400)
class CorporateEventServiceItemAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        return [AllowAny()] if self.request.method == "GET" else [IsAdminRole()]

    def get(self, request):
        item_id = request.query_params.get("id")

        if item_id:
            try:
                item = CorporateEventServiceItem.objects.get(id=item_id)
                serializer = CorporateEventServiceItemSerializer(item)
                return Response({"success": True, "data": serializer.data})
            except CorporateEventServiceItem.DoesNotExist:
                return Response(
                    {"success": False, "message": "Item not found"},
                    status=404
                )

        items = CorporateEventServiceItem.objects.all().order_by("-id")
        serializer = CorporateEventServiceItemSerializer(items, many=True)
        return Response({"success": True, "data": serializer.data})


    def post(self, request):
        serializer = CorporateEventServiceItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Corporate event service item created successfully"
                },
                status=201
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )

  
    def put(self, request):
        item_id = request.data.get("id")
        if not item_id:
            return Response(
                {"success": False, "message": "Item ID is required"},
                status=400
            )

        try:
            item = CorporateEventServiceItem.objects.get(id=item_id)
        except CorporateEventServiceItem.DoesNotExist:
            return Response(
                {"success": False, "message": "Item not found"},
                status=404
            )

        serializer = CorporateEventServiceItemSerializer(
            item, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Corporate event service item updated successfully"
                }
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )

    def delete(self, request):
        item_id = request.data.get("id")
        if not item_id:
            return Response(
                {"success": False, "message": "Item ID is required"},
                status=400
            )

        try:
            CorporateEventServiceItem.objects.get(id=item_id).delete()
            return Response(
                {
                    "success": True,
                    "message": "Corporate event service item deleted successfully"
                }
            )
        except CorporateEventServiceItem.DoesNotExist:
            return Response(
                {"success": False, "message": "Item not found"},
                status=404
            )
        

class EntertainmentEventServiceItemAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        return [AllowAny()] if self.request.method == "GET" else [IsAdminRole()]

    def get(self, request):
        item_id = request.query_params.get("id")

        if item_id:
            try:
                item = EntertainmentEventServiceItem.objects.get(id=item_id)
                serializer = EntertainmentEventsServiceItemSerializer(item)
                return Response({"success": True, "data": serializer.data})
            except EntertainmentEventServiceItem.DoesNotExist:
                return Response(
                    {"success": False, "message": "Item not found"},
                    status=404
                )

        items = EntertainmentEventServiceItem.objects.all().order_by("-id")
        serializer = EntertainmentEventsServiceItemSerializer(items, many=True)
        return Response({"success": True, "data": serializer.data})

    def post(self, request):
        serializer = EntertainmentEventsServiceItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Entertainment event service item created successfully"
                },
                status=201
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )

    def put(self, request):
        item_id = request.data.get("id")
        if not item_id:
            return Response(
                {"success": False, "message": "Item ID is required"},
                status=400
            )

        try:
            item = EntertainmentEventServiceItem.objects.get(id=item_id)
        except EntertainmentEventServiceItem.DoesNotExist:
            return Response(
                {"success": False, "message": "Item not found"},
                status=404
            )

        serializer = EntertainmentEventsServiceItemSerializer(
            item, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Entertainment event service item updated successfully"
                }
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )

    def delete(self, request):
        item_id = request.data.get("id")
        if not item_id:
            return Response(
                {"success": False, "message": "Item ID is required"},
                status=400
            )

        try:
            EntertainmentEventServiceItem.objects.get(id=item_id).delete()
            return Response(
                {
                    "success": True,
                    "message": "Entertainment event service item deleted successfully"
                }
            )
        except EntertainmentEventServiceItem.DoesNotExist:
            return Response(
                {"success": False, "message": "Item not found"},
                status=404
            )
        


class ConcertEventServiceItemAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        return [AllowAny()] if self.request.method == "GET" else [IsAdminRole()]

    def get(self, request):
        item_id = request.query_params.get("id")

        if item_id:
            try:
                item = ConcertEventServiceItem.objects.get(id=item_id)
                serializer = ConcertEventServiceItemSerializer(item)
                return Response({"success": True, "data": serializer.data})
            except ConcertEventServiceItem.DoesNotExist:
                return Response(
                    {"success": False, "message": "Item not found"},
                    status=404
                )

        items = ConcertEventServiceItem.objects.all().order_by("-id")
        serializer = ConcertEventServiceItemSerializer(items, many=True)
        return Response({"success": True, "data": serializer.data})

    def post(self, request):
        serializer = ConcertEventServiceItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Concert event service item created successfully"
                },
                status=201
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )

    def put(self, request):
        item_id = request.data.get("id")
        if not item_id:
            return Response(
                {"success": False, "message": "Item ID is required"},
                status=400
            )

        try:
            item = ConcertEventServiceItem.objects.get(id=item_id)
        except ConcertEventServiceItem.DoesNotExist:
            return Response(
                {"success": False, "message": "Item not found"},
                status=404
            )

        serializer = ConcertEventServiceItemSerializer(
            item, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Concert event service item updated successfully"
                }
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )

    def delete(self, request):
        item_id = request.data.get("id")
        if not item_id:
            return Response(
                {"success": False, "message": "Item ID is required"},
                status=400
            )

        try:
            ConcertEventServiceItem.objects.get(id=item_id).delete()
            return Response(
                {
                    "success": True,
                    "message": "Concert event service item deleted successfully"
                }
            )
        except ConcertEventServiceItem.DoesNotExist:
            return Response(
                {"success": False, "message": "Item not found"},
                status=404
            )
        
class PrivatePartiesEventServiceItemAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        return [AllowAny()] if self.request.method == "GET" else [IsAdminRole()]

    def get(self, request):
        item_id = request.query_params.get("id")

        if item_id:
            try:
                item = PrivatePartiesEventServiceItem.objects.get(id=item_id)
                serializer = PrivatePartiesEventServiceItemSerializer(item)
                return Response({"success": True, "data": serializer.data})
            except PrivatePartiesEventServiceItem.DoesNotExist:
                return Response(
                    {"success": False, "message": "Item not found"},
                    status=404
                )

        items = PrivatePartiesEventServiceItem.objects.all().order_by("-id")
        serializer = PrivatePartiesEventServiceItemSerializer(items, many=True)
        return Response({"success": True, "data": serializer.data})

    def post(self, request):
        serializer = PrivatePartiesEventServiceItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Private parties event service item created successfully"
                },
                status=201
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )

    def put(self, request):
        item_id = request.data.get("id")
        if not item_id:
            return Response(
                {"success": False, "message": "Item ID is required"},
                status=400
            )

        try:
            item = PrivatePartiesEventServiceItem.objects.get(id=item_id)
        except PrivatePartiesEventServiceItem.DoesNotExist:
            return Response(
                {"success": False, "message": "Item not found"},
                status=404
            )

        serializer = PrivatePartiesEventServiceItemSerializer(
            item, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Private parties event service item updated successfully"
                }
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )

    def delete(self, request):
        item_id = request.data.get("id")
        if not item_id:
            return Response(
                {"success": False, "message": "Item ID is required"},
                status=400
            )

        try:
            PrivatePartiesEventServiceItem.objects.get(id=item_id).delete()
            return Response(
                {
                    "success": True,
                    "message": "Private parties event service item deleted successfully"
                }
            )
        except PrivatePartiesEventServiceItem.DoesNotExist:
            return Response(
                {"success": False, "message": "Item not found"},
                status=404
            )
        


class SeminarEventServiceItemAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        return [AllowAny()] if self.request.method == "GET" else [IsAdminRole()]

    def get(self, request):
        item_id = request.query_params.get("id")

        if item_id:
            try:
                item = SeminarEventServiceItem.objects.get(id=item_id)
                serializer = SeminarEventServiceItemSerializer(item)
                return Response({"success": True, "data": serializer.data})
            except SeminarEventServiceItem.DoesNotExist:
                return Response(
                    {"success": False, "message": "Item not found"},
                    status=404
                )

        items = SeminarEventServiceItem.objects.all().order_by("-id")
        serializer = SeminarEventServiceItemSerializer(items, many=True)
        return Response({"success": True, "data": serializer.data})

    def post(self, request):
        serializer = SeminarEventServiceItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Seminar event service item created successfully"
                },
                status=201
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )

    def put(self, request):
        item_id = request.data.get("id")
        if not item_id:
            return Response(
                {"success": False, "message": "Item ID is required"},
                status=400
            )

        try:
            item = SeminarEventServiceItem.objects.get(id=item_id)
        except SeminarEventServiceItem.DoesNotExist:
            return Response(
                {"success": False, "message": "Item not found"},
                status=404
            )

        serializer = SeminarEventServiceItemSerializer(
            item, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Seminar event service item updated successfully"
                }
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )

    def delete(self, request):
        item_id = request.data.get("id")
        if not item_id:
            return Response(
                {"success": False, "message": "Item ID is required"},
                status=400
            )

        try:
            SeminarEventServiceItem.objects.get(id=item_id).delete()
            return Response(
                {
                    "success": True,
                    "message": "Seminar event service item deleted successfully"
                }
            )
        except SeminarEventServiceItem.DoesNotExist:
            return Response(
                {"success": False, "message": "Item not found"},
                status=404
            )
        
        
class GalleryItemAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        return [AllowAny()] if self.request.method == "GET" else [IsAdminRole()]

    def get(self, request):
        item_id = request.query_params.get("id")

        if item_id:
            try:
                item = GalleryItem.objects.get(id=item_id)
                serializer = GalleryItemSerializer(item)
                return Response({"success": True, "data": serializer.data})
            except GalleryItem.DoesNotExist:
                return Response(
                    {"success": False, "message": "Item not found"},
                    status=404
                )

        items = GalleryItem.objects.all().order_by("-id")
        serializer = GalleryItemSerializer(items, many=True)
        return Response({"success": True, "data": serializer.data})

    def post(self, request):
        serializer = GalleryItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Gallery item created successfully"
                },
                status=201
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )

    def put(self, request):
        item_id = request.data.get("id")
        if not item_id:
            return Response(
                {"success": False, "message": "Item ID is required"},
                status=400
            )

        try:
            item = GalleryItem.objects.get(id=item_id)
        except GalleryItem.DoesNotExist:
            return Response(
                {"success": False, "message": "Item not found"},
                status=404
            )

        serializer = GalleryItemSerializer(
            item, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Gallery item updated successfully"
                }
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )

    def delete(self, request):
        item_id = request.data.get("id")
        if not item_id:
            return Response(
                {"success": False, "message": "Item ID is required"},
                status=400
            )

        try:
            GalleryItem.objects.get(id=item_id).delete()
            return Response(
                {
                    "success": True,
                    "message": "Gallery item deleted successfully"
                }
            )
        except GalleryItem.DoesNotExist:
            return Response(
                {"success": False, "message": "Item not found"},
                status=404
            )