from django.contrib import admin
from .models import Order, OrderProduct
# Register your models here.


models = [Order, OrderProduct]

admin.site.register(models)