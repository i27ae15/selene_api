from django.db import models
from django.utils import timezone

from dotenv import load_dotenv

load_dotenv()

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        
        if not email:
            raise ValueError("User must have an email")
        email = self.normalize_email(email)
        user = self.model(
            email=email, 
            username=username,
            **extra_fields)
        user.set_password(password)
        
        user.save(using=self._db)
        return user


    def create_superuser(self, username, email, password=None, **extra_fields):
        user = self.create_user(username, email, password=password, **extra_fields)
        user.is_active = True
        user.is_staff = True
        user.is_admin = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    
    # foreignkeys 
    
    # -----------------------------------------------------------
    # fields 
 
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
        
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_tester = models.BooleanField(default=False)
        
    last_name = models.CharField(max_length=255)
    
    objects = CustomUserManager()
    
    phone = models.CharField(max_length=120, default='')

    registration_date = models.DateTimeField(default=timezone.now)
    
    username = models.CharField(max_length=255, unique=True)
    role = models.IntegerField(default=2)
    
    
    # USER PERMISSIONS 
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "username"]

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


    def get_short_name(self):
        return self.username
    
    
    def has_perm(self, perm, obj=None):
        return True


    def has_module_perms(self, app_label):
        return True


    # def __str__(self):
    #     return f'{self.id} - {self.email} - {self.organization.name}'
