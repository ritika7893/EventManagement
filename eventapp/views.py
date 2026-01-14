from .models import  AllLog, EmailVerification, UserReg
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from .serializers import  UserRegSerializer
# Create your views here.
class UserRegAPIView(APIView):
   
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