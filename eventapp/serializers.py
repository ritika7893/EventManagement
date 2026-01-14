from rest_framework import serializers
from .models import  AllLog, EmailVerification, UserReg   
from django.contrib.auth.hashers import make_password
from .utils import generate_verification_code, send_email_verification_code
class UserRegSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReg
        fields = "__all__"
        read_only_fields = ["user_id", "created_at", "updated_at"]
       

    def create(self, validated_data):
    # Remove phone for AllLog
        phone = validated_data.pop("phone")
        
        # Set role
        role = "user"

        # Remove password and hash it
        raw_password = validated_data.pop("password")
        hashed_password = make_password(raw_password)

        # Create UserReg
        user = UserReg.objects.create(
            **validated_data,
            password=hashed_password
        )

        # Create AllLog entry
        AllLog.objects.create(
            unique_id=user.user_id,
            email=user.email,
            phone=phone,
            password=hashed_password,
            role=role
        )

        # Create verification code
        code = generate_verification_code()
        EmailVerification.objects.create(user=user, verification_code=code)

        # Send email via utility
        send_email_verification_code(user, code)

        return user

