from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import User, UserAddress, Wishlist
# Register your models here.




class UserAdminConfig(UserAdmin):
    model = User
    search_fields = ('email', 'username', 'full_name', 'mobile', 'image',)
    list_filter = ('is_active', 'is_staff', 'is_superuser' )
    ordering =('-created_at', )
    list_display = ('email', 'username', 'full_name', 'mobile', 'image', 'is_active', 'is_staff', )
    fieldsets = (
        (None, {'fields': ('email', 'username', 'full_name', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser')}),
        ('Personal', {'fields': ('mobile', 'image',)}),
    )
    

admin.site.register(User, UserAdminConfig)
admin.site.register(UserAddress)
admin.site.register(Wishlist)