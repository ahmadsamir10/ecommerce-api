from django.urls import path
from rest_framework import routers
from users.api.views import LogoutView
from .views import (
                        CityView,
                        CountryView,
                        OrderView,
                        ProductView,
                        CategoryView,
                        SliderView,
                        AdvertisementView,
                        DiscountCouponView,
                        SubCategoryView,
                        BrandView,
                        DiscountOfferView,
                        PartnerView,
                        MainView,
                        AdminLoginView,
                        GroupView,
                        StaffView,
                        UsersView
                        
                    )


app_name = 'dashboard'


router = routers.SimpleRouter()
router.register(r'sliders', SliderView, 'sliders')
router.register(r'ads', AdvertisementView, 'ads')
router.register(r'discount-coupons', DiscountCouponView, 'discount-coupons')
router.register(r'categories', CategoryView, 'categories')
router.register(r'subcategories', SubCategoryView, 'subcategories')
router.register(r'brands', BrandView, 'brands')
router.register(r'discount-offers', DiscountOfferView, 'discount-offers')
router.register(r'products', ProductView, 'products')
router.register(r'partners', PartnerView, 'partners')
router.register(r'countries', CountryView, 'countries')
router.register(r'cities', CityView, 'cities')
router.register(r'orders', OrderView, 'orders')
router.register(r'groups', GroupView, 'groups')
router.register(r'staff', StaffView, 'staff')
router.register(r'users', UsersView, 'users')


urlpatterns = router.urls


urlpatterns += [
    path('main', MainView.as_view(), name='main'),
    path('login', AdminLoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
]