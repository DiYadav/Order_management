from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomerManager(BaseUserManager):

    use_in_migrations = True
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email address is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)

class Customer(AbstractUser):
    username=None
    email=models.EmailField(unique=True, max_length=255)
    phone_number=models.CharField(max_length=15, blank=True, null=True)
    
    USERNAME_FIELD="email"
    REQUIRED_FIELDS=[]

    objects = CustomerManager()

    def __str__(self):
        return self.email

