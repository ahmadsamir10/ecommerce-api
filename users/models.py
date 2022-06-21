from django.db import models
from django.contrib.auth.models import AbstractBaseUser , PermissionsMixin, BaseUserManager
from core.models import Country, City
from phonenumber_field.modelfields import PhoneNumberField







class CustomAccountManger(BaseUserManager):
    def create_user(self, email, username, full_name, mobile, password, **other_fields):
        
        if not email:
            raise ValueError('You must provide an email address')
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, full_name=full_name, mobile=mobile, **other_fields)
        user.set_password(password)
        user.save()
        return user
    
    
    def create_staff(self, email, username, full_name, mobile, password, is_staff, is_active, **other_fields):
        
        return self.create_user(email=email, username=username, password=password, full_name=full_name, mobile=mobile, is_staff=is_staff, is_active=is_active)
    
    
    def create_superuser(self, email, username, full_name, mobile, password, **other_fields):
        
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        
        if other_fields.get('is_staff') is not True:
            raise ValueError('Superuser must be assigned to is_staff=True')
        if other_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must be assigned to is_superuser=True')
        
        return self.create_user(email, username, full_name, mobile, password, **other_fields)



class User(AbstractBaseUser, PermissionsMixin):
        
    email       = models.EmailField(max_length=128, unique=True)
    username   = models.CharField(max_length=128, unique=True)
    full_name   = models.CharField(max_length=128)
    mobile      = PhoneNumberField()
    image       = models.ImageField(default='profile.png', upload_to='users/')
    created_at  = models.DateTimeField(auto_now_add=True)
    is_staff    = models.BooleanField(default=False)
    is_active   = models.BooleanField(default=False)
    
    objects = CustomAccountManger()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'full_name', 'mobile']
    
    
    def __str__(self):
        return self.username
    

class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='address')
    address = models.CharField(max_length=250)
    street_1 = models.CharField(max_length=250)
    street_2 = models.CharField(max_length=250)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    zip_code = models.CharField(max_length=12)
    
    def __str__(self):
        return 'address for ' + self.user.username
    

class Wishlist(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='wishlist')
    product = models.OneToOneField('core.Product', on_delete=models.CASCADE)


class Activation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=8)