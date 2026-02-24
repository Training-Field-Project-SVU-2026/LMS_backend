from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.text import slugify
import uuid

# =================== User Manager ===================
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# =================== User ===================
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('student', 'Student'),
        ('instructor', 'Instructor'),
    )

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    image = models.ImageField(upload_to='photo/', null=True, blank=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True,null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  

    objects = UserManager()  

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{slugify(self.first_name)}-{str(uuid.uuid4())[:8]}"
        super().save(*args, **kwargs)
    def __str__(self):
        return self.email

# =================== Student ===================
class Student(models.Model):
    user = models.OneToOneField(User, related_name="student_profile", on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Student"

# =================== Instructor ===================
class Instructor(models.Model):
    user = models.OneToOneField(User, related_name="instructor_profile", on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    description = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - Instructor"