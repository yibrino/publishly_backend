from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, user_email, user_password=None, **extra_fields):
        if not user_email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(user_email)
        user = self.model(user_email=email, **extra_fields)
        user.set_password(user_password)  # Hash the password using Django's default mechanism
        user.save(using=self._db)
        return user

    def create_superuser(self, user_email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(user_email, password, **extra_fields)




class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    user_username = models.CharField(max_length=255)
    user_email = models.EmailField(max_length=255, unique=True, default='default@example.com')
    user_firstname = models.CharField(max_length=255)
    user_lastname = models.CharField(max_length=255)



    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    # Custom related_name to avoid clashes with Django's default User model
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',  # Avoid clash by providing a unique related_name
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',  # Avoid clash by providing a unique related_name
        blank=True
    )

    USERNAME_FIELD = 'user_email'
    REQUIRED_FIELDS = ['user_username']

    def __str__(self):
        return self.user_email
    
    
class Profile(models.Model):
    # One-to-One relationship with the customized User model
    profile_id = models.AutoField(primary_key=True,null=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
 

    user_bio = models.TextField(blank=True, null=True)
    user_website = models.URLField(blank=True, null=True)
    user_profile_picture = models.URLField(blank=True, null=True, default='https://via.placeholder.com/150')
    # Followers: users who follow this user

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.user_username}"
  
    

class Follower(models.Model):
    follower_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')  # The user being followed
    follower_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')  # The user who is following
    followed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.follower.username} follows {self.profile.user.username}"
    
