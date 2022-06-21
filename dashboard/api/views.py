from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group
from django_filters.rest_framework import DjangoFilterBackend
from checkout.models import Order
from users.api.permissions import IsStaffOrNotAllowed
from users.models import User
from core.models import (
                            Brand,
                            City,
                            Country,
                            DiscountOffer,
                            Partner,
                            Product,
                            Category,
                            Slider,
                            Advertisement,
                            DiscountCoupon,
                            SubCategory
                        )
from .serializers import (                            
                            CitySerializer,
                            CountrySerializer,
                            ProductSerializer,
                            CategorySerializer,
                            SliderSerilaizer,
                            AdvertisementSerilaizer,
                            DiscountCouponSerilaizer,
                            SubCategorySerializer,
                            BrandSerializer,
                            DiscountOfferSerializer,
                            PartnerSerializer,
                            GroupSerializer,
                            StaffSerializer,
                            UserSerializer,
                            OrderSerializer
                            
                        )



# crud view for groups 
class GroupView(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsStaffOrNotAllowed, DjangoModelPermissions]
    
    
# crud view for Staff and staff groups 
class StaffView(ModelViewSet):
    queryset = User.objects.filter(is_staff=True)
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated, IsStaffOrNotAllowed, DjangoModelPermissions]
    

# crud view for users
class UsersView(ModelViewSet):
    queryset = User.objects.filter(is_staff=False)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsStaffOrNotAllowed, DjangoModelPermissions]


class MainView(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrNotAllowed]
    
    def get(self, request):
        data = {
            'sliders' : Slider.objects.all().count(),
            'categories' : Category.objects.all().count(),
            'brands' : Brand.objects.all().count(),
            'users' : User.objects.filter(is_staff=False, is_superuser=False).count(),
            'active_users' : User.objects.filter(is_staff=False, is_superuser=False, is_active=True).count(),
            'inactive_users' : User.objects.filter(is_staff=False, is_superuser=False, is_active=False).count(),
            'products' : Product.objects.all().count(),
            'orders': Order.objects.all().count(),
            'pending_orders': Order.objects.filter(ordered=True, canceled=False).count(),
            'accepted_orders': Order.objects.filter(ordered=True, canceled=False, status='accepted').count(),
            'canceled_orders': Order.objects.filter(ordered=True, canceled=True).count(),
            'rejected_orders': Order.objects.filter(ordered=True, canceled=False, status='rejected').count(),
            'inway_orders': Order.objects.filter(ordered=True, canceled=False, status='inway').count(),
            'delivered_orders': Order.objects.filter(ordered=True, canceled=False, status='delivered').count(),
            'staff_members': User.objects.filter(is_staff=True).count(),
            'countries' : Country.objects.all().count(),
            'cities' : City.objects.all().count(),
        }
        return Response(data, status=status.HTTP_200_OK)
    
# crud view for sliders
class SliderView(ModelViewSet):
    queryset = Slider.objects.all()
    serializer_class = SliderSerilaizer
    permission_classes = [IsAuthenticated, IsStaffOrNotAllowed, DjangoModelPermissions]
    
# crud view for ads
class AdvertisementView(ModelViewSet):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerilaizer
    permission_classes = [IsAuthenticated, IsStaffOrNotAllowed, DjangoModelPermissions]
    
# crud view for discount coupon
class DiscountCouponView(ModelViewSet):
    queryset = DiscountCoupon.objects.all()
    serializer_class = DiscountCouponSerilaizer
    permission_classes = [IsAuthenticated, IsStaffOrNotAllowed, DjangoModelPermissions]

class CategoryView(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsStaffOrNotAllowed, DjangoModelPermissions]

class SubCategoryView(ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [IsAuthenticated, IsStaffOrNotAllowed, DjangoModelPermissions]
    
class BrandView(ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated, IsStaffOrNotAllowed, DjangoModelPermissions]
       
class DiscountOfferView(ModelViewSet):
    queryset = DiscountOffer.objects.all()
    serializer_class = DiscountOfferSerializer
    permission_classes = [IsAuthenticated, IsStaffOrNotAllowed, DjangoModelPermissions]
       
# crud view for products 
class ProductView(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsStaffOrNotAllowed, DjangoModelPermissions]

class PartnerView(ModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    permission_classes = [IsAuthenticated, IsStaffOrNotAllowed, DjangoModelPermissions]

class CountryView(ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAuthenticated, IsStaffOrNotAllowed, DjangoModelPermissions]

class CityView(ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticated, IsStaffOrNotAllowed, DjangoModelPermissions]


class OrderView(ModelViewSet):
    queryset = Order.objects.filter(ordered=True)
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsStaffOrNotAllowed, DjangoModelPermissions]
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('ordered', 'canceled', 'status') 


## admin login

class AdminLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if user.is_staff == True:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key
            })
            
        else:
            return Response({'response':'Regular users not allowed'}, status=status.HTTP_400_BAD_REQUEST)
