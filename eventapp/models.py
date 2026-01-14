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
    user_id = models.CharField(max_length=20,unique=True,editable=False)
    first_name = models.CharField(max_length=100,null=True, blank=True)
    last_name = models.CharField(max_length=100,null=True, blank=True)
    email = models.EmailField(unique=True,null=True, blank=True)
    phone= models.CharField(max_length=15, unique=True,null=True, blank=True)
    password = models.CharField(max_length=255,null=True, blank=True)
    talent_scope = models.JSONField(default=list, null=True, blank=True)
    portfolio_link = models.JSONField(default=list, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
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
