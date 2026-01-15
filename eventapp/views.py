from eventapp.permissions import IsAdminRole
from .models import  AllLog, CompanyDetailsItem, DiscoverYourTalentItem, EmailVerification, UserReg
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from .serializers import  CompanyDetailItemSerializer, DiscoverYourTalentItemSerializer, UserRegSerializer
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
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "User registered successfully"},
                status=201
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )

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
            {"success": True, "message": "Email verified successfully"}
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

    # 🔹 DELETE
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
