from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import ProductOrderView, OrderView

urlpatterns = []

router = SimpleRouter()
router.register('cart', ProductOrderView, 'cart')
router.register('orders', OrderView, 'orders')

urlpatterns += router.urls
