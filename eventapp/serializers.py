
from datetime import timezone
from django.forms import ValidationError
from rest_framework import serializers
from .models import  AboutUsItem, ConcertEventServiceItem, ContactUs, CorporateEventServiceItem, EntertainmentEventServiceItem, Event,AllLog,  CardComponentItem, CarsouselItem1,EventParticipant, CompanyDetailsItem, DiscoverYourTalentItem, EmailVerification, GalleryItem, PageItem, PrivatePartiesEventServiceItem, SeminarEventServiceItem,  TopNav1, UserReg   
from django.contrib.auth.hashers import make_password
from .utils import generate_verification_code, send_email_verification_code, send_password_reset_otp, send_resend_email_otp
from django.utils import timezone
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
    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        if password:
            hashed_password = make_password(password)
            instance.password = hashed_password

            AllLog.objects.filter(
                unique_id=instance.user_id
            ).update(password=hashed_password)

     
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class DiscoverYourTalentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscoverYourTalentItem
        fields = "__all__"
class CompanyDetailItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyDetailsItem
        fields = "__all__"

class EventSerializer(serializers.ModelSerializer):
    is_past = serializers.SerializerMethodField()
    is_present = serializers.SerializerMethodField()
    is_upcoming = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = [
            "event_id", "created_at", "updated_at",
            "is_past", "is_present", "is_upcoming"
        ]
    def validate(self, attrs):
        user = attrs.get("user_id")
        event = attrs.get("event_id")

        if EventParticipant.objects.filter(
            user_id=user,
            event_id=event
        ).exists():
            raise serializers.ValidationError(
                "You have already participated in this event."
            )

        return attrs

    def get_is_past(self, obj):
        if not obj.event_date_time:
            return False
        return obj.event_date_time.date() < timezone.now().date()

    def get_is_present(self, obj):
        if not obj.event_date_time:
            return False
        return obj.event_date_time.date() == timezone.now().date()

    def get_is_upcoming(self, obj):
        if not obj.event_date_time:
            return False
        return obj.event_date_time.date() > timezone.now().date()

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

class PageNavbarSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = PageItem
        fields = ["id", "page_title", "children"]

    def get_children(self, obj):
        children_qs = obj.children.filter(show_in_nav=True).order_by("nav_order")
        return PageNavbarSerializer(children_qs, many=True).data
    
class AboutUsItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUsItem
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
class PageItemSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = PageItem
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class TopNav1Serializer(serializers.ModelSerializer):
    class Meta:
        model = TopNav1
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

class EventParticipantSerializer(serializers.ModelSerializer):

    user_id = serializers.CharField(write_only=True)
    event_id = serializers.CharField(write_only=True)


    user_detail = serializers.SerializerMethodField(read_only=True)
    event_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EventParticipant
        fields = [
            "id",
            "user_id",
            "event_id",
            "user_detail",
            "event_detail",
            "created_at"
        ]

    def create(self, validated_data):
        user_id = validated_data.pop("user_id")
        event_id = validated_data.pop("event_id")

        try:
            user = UserReg.objects.get(user_id=user_id)
        except UserReg.DoesNotExist:
            raise serializers.ValidationError({"user_id": "Invalid user_id"})

        try:
            event = Event.objects.get(event_id=event_id)
        except Event.DoesNotExist:
            raise serializers.ValidationError({"event_id": "Invalid event_id"})

        # prevent duplicate entry
        participant, created = EventParticipant.objects.get_or_create(
            user_id=user,
            event_id=event
        )

        if not created:
            raise serializers.ValidationError("User already joined this event")

        return participant

    def get_user_detail(self, obj):
        return {
            "user_id": obj.user_id.user_id,
            "full_name": obj.user_id.full_name,
            "email": obj.user_id.email,
            "phone": obj.user_id.phone,
            "user_type": obj.user_id.user_type,
        }

    def get_event_detail(self, obj):
        return {
            "event_id": obj.event_id.event_id,
            "event_name": obj.event_id.event_name,
            "event_type": obj.event_id.event_type,
            "event_date_time": obj.event_id.event_date_time,
            "venue": obj.event_id.venue,
        }

class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = "__all__"
class ResendEmailOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get("email")

        try:
            user = UserReg.objects.get(email=email)
        except UserReg.DoesNotExist:
            raise serializers.ValidationError({
                "email": "User with this email does not exist."
            })

        verification = EmailVerification.objects.filter(user=user).first()

        if not verification:
            raise serializers.ValidationError(
                "No email verification request found."
            )

        if verification.is_verified:
            raise serializers.ValidationError(
                "Email is already verified."
            )

        attrs["user"] = user
        attrs["verification"] = verification
        return attrs

    def save(self):
        user = self.validated_data["user"]
        verification = self.validated_data["verification"]

        code = generate_verification_code()

        verification.verification_code = code
        verification.is_verified = False
        verification.created_at = timezone.now()
        verification.verified_at = None
        verification.save(update_fields=[
            "verification_code",
            "is_verified",
            "created_at",
            "verified_at"
        ])


        send_resend_email_otp(user, code)

        return {
            "message": "Verification code resent successfully."
        }
class ResetPasswordEmailOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs["email"]

        try:
            user = UserReg.objects.get(email=email)
        except UserReg.DoesNotExist:
            raise serializers.ValidationError(
                "No user found with this email."
            )

        attrs["user"] = user
        return attrs

    def save(self):
        user = self.validated_data["user"]
        code = generate_verification_code()

        EmailVerification.objects.update_or_create(
            user=user,
            defaults={
                "verification_code": code,
                "is_verified": False,
                "verified_at": None
            }
        )

        send_password_reset_otp(user, code)

        return {
            "message": "Password reset OTP sent successfully."
        }
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(min_length=8)
    

    def validate(self, attrs):
        try:
            user = UserReg.objects.get(email=attrs["email"])
        except UserReg.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        verification = EmailVerification.objects.filter(
            user=user,
            is_verified=True
        ).first()

        if not verification:
            raise serializers.ValidationError(
                "OTP verification required before resetting password."
            )

        attrs["user"] = user
        attrs["verification"] = verification
        return attrs

    def save(self):
        user = self.validated_data["user"]
        verification = self.validated_data["verification"]

        hashed_password = make_password(
            self.validated_data["new_password"]
        )

        user.password = hashed_password
        user.save(update_fields=["password"])

        AllLog.objects.filter(
            unique_id=user.user_id
        ).update(password=hashed_password)

        verification.delete()

        return {"message": "Password reset successfully."}
    
class CorporateEventServiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorporateEventServiceItem
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
    

class EntertainmentEventsServiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=EntertainmentEventServiceItem
        fields="__all__"
        read_only_fields=["id","created_at","updated_at"]

class ConcertEventServiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=ConcertEventServiceItem
        fields="__all__"
        read_only_fields=["id","created_at","updated_at"]
        

class PrivatePartiesEventServiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=PrivatePartiesEventServiceItem
        fields="__all__"
        read_only_fields=["id","created_at","updated_at"]

class SeminarEventServiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=SeminarEventServiceItem
        fields="__all__"
        read_only_fields=["id","created_at","updated_at"]

class GalleryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=GalleryItem
        fields="__all__"
        read_only_fields=["id","created_at","updated_at"]