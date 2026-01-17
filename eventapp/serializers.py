from sched import Event
from django.forms import ValidationError
from rest_framework import serializers
from .models import  AboutUsItem, AllLog,  CardComponentItem, CarsouselItem1, CompanyDetailsItem, DiscoverYourTalentItem, EmailVerification,PageItem, UserReg   
from django.contrib.auth.hashers import make_password
from .utils import generate_verification_code, send_email_verification_code

class UserRegSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReg
        fields = "__all__"
        extra_kwargs = {
            "email": {"validators": []},
            "phone": {"validators": []},
        }

  

    def create(self, validated_data):
        email = validated_data.get("email")
        phone = validated_data.get("phone")
        raw_password = validated_data.pop("password")

        existing_user = UserReg.objects.filter(email=email).first()


        if existing_user:
            verification = EmailVerification.objects.filter(user=existing_user).first()

     
            if verification and not verification.is_verified:
                code = generate_verification_code()

                EmailVerification.objects.update_or_create(
                    user=existing_user,
                    defaults={"verification_code": code}
                )

                send_email_verification_code(existing_user, code)

                existing_user._resent = True
                return existing_user

            raise serializers.ValidationError({
                "email": "Email already registered and verified."
            })

   
        if phone and UserReg.objects.filter(phone=phone).exists():
            raise serializers.ValidationError({
                "phone": "This phone number is already in use."
            })

        hashed_password = make_password(raw_password)

        user = UserReg.objects.create(
            **validated_data,
            password=hashed_password
        )

       
        AllLog.objects.create(
            unique_id=user.user_id,
            email=user.email,
            phone=user.phone,
            password=hashed_password,
            role="user"
        )

       
        code = generate_verification_code()
        EmailVerification.objects.create(
            user=user,
            verification_code=code
        )

        send_email_verification_code(user, code)

        return user

class DiscoverYourTalentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscoverYourTalentItem
        fields = "__all__"
class CompanyDetailItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyDetailsItem
        fields = "__all__"

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = ["event_id", "created_at", "updated_at"]

class CarsouselItem1Serializer(serializers.ModelSerializer):
    class Meta:
        model = CarsouselItem1
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
class CardComponentItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CardComponentItem
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

class AboutUsItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUsItem
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
class PageItemSerializer(serializers.ModelSerializer):
    cards = CardComponentItemSerializer(many=True, read_only=True)
    carousels1 = CarsouselItem1Serializer(many=True, read_only=True)
    aboutus = AboutUsItemSerializer(many=True, read_only=True)
    class Meta:
        model = PageItem
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

