from xml.etree.ElementInclude import include
from django.urls import path, include
from rest_framework import routers
from .views import (    
                        CreateProductReview,
                        ListCreateUserWishlist,
                        RegisterView,
                        UserLoginView,
                        ChangePasswordView,
                        AccountDetailsView,
                        LogoutView,
                        UserAddressView,
                        ActivateAccountView,
                        MyProfileView
                    )

app_name = 'users'

router = routers.SimpleRouter()
router.register(r'my-addresses', UserAddressView, 'my-addresses')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', UserLoginView.as_view(), name='login'),
    path('auth/logout', LogoutView.as_view(), name='logout'),
    path('change-password', ChangePasswordView.as_view(), name='change-password'),
    path('reset-password/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('account-details', AccountDetailsView.as_view(), name='account-details'),
    path('my-wishlist', ListCreateUserWishlist.as_view(), name='my-wishlist' ),
    path('product-review/', CreateProductReview.as_view(), name='product-review'),
    path('my-profile', MyProfileView.as_view() , name='my-profile')
]


urlpatterns += router.urls