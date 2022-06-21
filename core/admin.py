from django.contrib import admin
from .models import *


models_list = [Product, Category, SubCategory, Brand, ProductRate, DiscountCoupon, DiscountOffer, Size, Color, Image]



admin.site.register(models_list)

