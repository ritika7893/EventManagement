from datetime import datetime
from django.utils import timezone
import random
from django.db import models


# Create your models here.
def generate_id(prefix):
    current_year = datetime.now().year
    random_number = random.randint(100000, 999999)
    return f"{prefix}/{current_year}/{random_number}"

class AllLog(models.Model):
    id = models.AutoField(primary_key=True)
    unique_id = models.CharField(unique=True, max_length=50, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=255,default='')
    role = models.CharField(max_length=50)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    def __str__(self):
        return f"{self.email} ({self.role})"
    
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False
    
class UserReg(models.Model):
    USER_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('team', 'Team'),
    ]
    user_id = models.CharField(max_length=20,unique=True,editable=False)
    user_type=models.CharField( max_length=100,choices=USER_TYPE_CHOICES,default='individual')
    team_name=models.CharField(max_length=100,blank=True, null=True)
    full_name = models.CharField(max_length=100,null=True, blank=True)
    gender= models.CharField(max_length=100,null=True, blank=True)
    email = models.EmailField(unique=True,null=True, blank=True)
    phone= models.CharField(max_length=15, unique=True,null=True, blank=True)
    password = models.CharField(max_length=255,null=True, blank=True)
    talent_scope = models.JSONField(default=list, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    social_media_link = models.JSONField(default=list, null=True, blank=True)
    additional_link = models.JSONField(default=list, null=True, blank=True)
    portfolio_file=models.FileField(upload_to="",blank=True,null=True)
    national_level_certificate = models.FileField(upload_to="portfolio_file/",blank=True,null=True)
    internation_level_certificate_award=models.FileField(upload_to="international_level_certificate_award/",blank=True,null=True)
    state_level_certificate=models.FileField(upload_to="state_level_certificate/",blank=True,null=True)
    district_level_certificate=models.FileField(upload_to="district_level_certificate/",blank=True,null=True)
    college_level_certificate=models.FileField(upload_to="college_level_certificate/",blank=True,null=True)
    other_certificate=models.FileField(upload_to="other_certificate/",blank=True,null=True)
    address = models.TextField(blank=True, null=True)
   
    country = models.CharField(max_length=100,blank=True, null=True)
    state = models.CharField(max_length=100,blank=True, null=True)
    city = models.CharField(max_length=100,blank=True, null=True)
    introduction = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = generate_id("USR")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user_id})"
class EmailVerification(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey("UserReg",on_delete=models.CASCADE,related_name="email_verifications")
    verification_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - Verified: {self.is_verified}"

class DiscoverYourTalentItem(models.Model):
    page_title = models.CharField(max_length=255,blank=True, null=True)
    title = models.CharField(max_length=255,blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="discovertalent_images/", blank=True, null=True)
    module = models.JSONField(default=list, blank=True)  # JSON field with default empty list
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class CompanyDetailsItem(models.Model):
    company_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    logo = models.ImageField(upload_to="company_logos/", blank=True, null=True)
    profile_link=models.JSONField(default=list, blank=True)  # JSON field with default empty list
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name
class Event(models.Model):
    event_id=models.CharField(max_length=20,unique=True,editable=False)
    event_name = models.CharField(max_length=255,blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    event_date_time=models.DateTimeField (blank=True, null=True)
    event_type=models.CharField(max_length=100,blank=True, null=True)
    image = models.ImageField(upload_to="event_images/", blank=True, null=True) 
    venue = models.CharField(max_length=255,blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        if not self.event_id:
            self.event_id = generate_id("EVT")
        super().save(*args, **kwargs)
    def __str__(self):
        return self.event_name
    
class PageItem(models.Model):
    page_title = models.CharField(max_length=200)
    parent = models.ForeignKey("self",on_delete=models.CASCADE, related_name="children",null=True, blank=True)
    show_in_nav = models.BooleanField(default=True)
    nav_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nav_order"]

    def __str__(self):
        return self.page_title
class CardComponentItem(models.Model):
    page = models.ForeignKey(PageItem,on_delete=models.CASCADE,related_name="cards")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="cardcomponent/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title

class CarsouselItem1(models.Model):
  
    title=models.CharField(max_length=200)
    sub_title=models.CharField(max_length=200,blank=True,null=True)
    description=models.TextField(blank=True,null=True)
    image=models.ImageField(upload_to="carousel_images/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AboutUsItem(models.Model):
    page=models.ForeignKey(PageItem,on_delete=models.CASCADE,related_name="aboutus")
    title=models.CharField(max_length=200)
    description=models.TextField(blank=True,null=True)  
    image=models.ImageField(upload_to="aboutus_images/")
    module=models.JSONField(default=list, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TopNav1(models.Model):
    POSITION_CHOICES = (
        ("left", "Left"),
        ("right", "Right"),
    )
    position = models.CharField(max_length=10, choices=POSITION_CHOICES,default="left")
    text=models.TextField(blank=True,null=True)
    icon=models.ImageField(upload_to="company_email_phone/", blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.text
    
class EventParticipant(models.Model):
    user_id = models.ForeignKey(UserReg, on_delete=models.CASCADE, related_name="event_participations",to_field='user_id')
    event_id= models.ForeignKey(Event, on_delete=models.CASCADE, related_name="participants",to_field='event_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_id', 'event_id')

    def __str__(self):
        return f"{self.user.user_id} → {self.event.event_name}"
class ContactUs(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    mobile_number = models.CharField(max_length=15,blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.full_name} - {self.subject}"


class CorporateEventServiceItem(models.Model):
    title=models.CharField(max_length=200,blank=True, null=True)
    description=models.TextField(blank=True, null=True)
    module=models.JSONField(default=list, blank=True, null=True)
    image=models.ImageField(upload_to="corporate_service_images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class EntertainmentEventServiceItem(models.Model):
    title=models.CharField(max_length=200,blank=True, null=True)
    description=models.TextField(blank=True, null=True)
    module=models.JSONField(default=list, blank=True, null=True)
    image=models.ImageField(upload_to="entertainment_service_images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ConcertEventServiceItem(models.Model):
    title=models.CharField(max_length=200,blank=True, null=True)
    description=models.TextField(blank=True, null=True)
    module=models.JSONField(default=list, blank=True, null=True)
    image=models.ImageField(upload_to="concert_service_images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title


class PrivatePartiesEventServiceItem(models.Model):
    title=models.CharField(max_length=200,blank=True, null=True)
    description=models.TextField(blank=True, null=True)
    module=models.JSONField(default=list, blank=True, null=True)
    image=models.ImageField(upload_to="private_parties_service_images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title
    
class SeminarEventServiceItem(models.Model):
    title=models.CharField(max_length=200,blank=True, null=True)
    description=models.TextField(blank=True, null=True)
    module=models.JSONField(default=list, blank=True, null=True)
    image=models.ImageField(upload_to="seminar_service_images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title
    
class GalleryItem(models.Model):
    title=models.CharField(max_length=200,blank=True, null=True)
    description=models.TextField(blank=True, null=True)
    image=models.ImageField(upload_to="gallery_images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
