from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserProfileManager(BaseUserManager):
    """Manage User Profile"""
    def create_user(self, email, name, contact=None, last_name=None, password=None, company_name=None, designation=None):
        """create a new user profile"""
        if not email:
            raise ValueError("User must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, last_name=last_name, contact=contact, company_name=company_name, designation=designation)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, name, password):
        """create and save a new superuser with details"""
        user = self.create_user(email, name, password)

        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    """Database model for users in the system"""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=80)
    contact = models.CharField(max_length=12, blank=True, null=True, )
    company_name = models.CharField(max_length=120, null=True)
    last_name = models.CharField(max_length=80, blank=True, null=True, )
    profile_pic = models.ImageField(upload_to='images/profile/', blank=True, null=True)
    designation = models.CharField(max_length=120, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserProfileManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        """Retrieve User Full Name"""
        return "{} {}".format(self.name, self.last_name)

    def __str__(self):
        """Return string representation"""
        return self.email
