from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group
from django.db.models import Prefetch
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from checkout.models import Order
from users.api.permissions import IsStaffOrNotAllowed
from users.models import User
from.utils import set_cache_if_exists
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
                            SubCategory,
                            Color
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
    queryset = User.objects.prefetch_related('groups').filter(is_staff=True)
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated, IsStaffOrNotAllowed, DjangoModelPermissions]
    
    def create(self, request, *args, **kwargs):
        created = super().create(request, *args, **kwargs)
        set_cache_if_exists(key='staff_members', add=1)
        return created
    
    def destroy(self, request, *args, **kwargs):
        destroyed = super().destroy(request, *args, **kwargs)
        set_cache_if_exists(key='staff_members', remove=1)
        return destroyed

    
    

# crud view for users
class UsersView(ModelViewSet):
    queryset = User.objects.filter(is_staff=False)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsStaffOrNotAllowed, DjangoModelPermissions]
    



class MainView(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrNotAllowed]
    
    def cached_or_query_counters(self, key, model, filters=None):
            cached = cache.get(key)
            if cached != None:
                count = cached
            else:
                if filters is not None:
                    value = model.objects.filter(**filters).count()
                    cache.set(key, value, timeout=None)
                    count = value
                else:
                    value = model.objects.all().count()
                    cache.set(key, value, timeout=None)
                    count = value
            return count
    
    def get(self, request):
        
        data = {
            'sliders' : self.cached_or_query_counters('sliders', Slider),
            'categories' : self.cached_or_query_counters('categories', Category),
            'brands' : self.cached_or_query_counters('brands', Brand),
            'users' : self.cached_or_query_counters('users', User, filters={'is_staff':False, 'is_superuser':False}),
            'active_users' : self.cached_or_query_counters('active_users', User, filters={'is_staff':False, 'is_superuser':False, 'is_active':True}),
            'inactive_users' : self.cached_or_query_counters('inactive_users', User, filters={'is_staff':False, 'is_superuser':False, 'is_active':False}),
            'products' : self.cached_or_query_counters('products', Product),
            'orders': Order.objects.all().count(),
            'pending_orders': self.cached_or_query_counters('pending_orders', Order, filters={'ordered':True, 'canceled':False}),
            'canceled_orders': self.cached_or_query_counters('canceled_orders', Order, filters={'ordered':True, 'canceled':True}),
            'accepted_orders': self.cached_or_query_counters('accepted_orders', Order, filters={'status':'accepted'}),
            'rejected_orders': self.cached_or_query_counters('rejected_orders', Order, filters={'status':'rejected'}),
            'inway_orders': self.cached_or_query_counters('inway_orders', Order, filters={'status':'inway'}),
            'delivered_orders': self.cached_or_query_counters('delivered_orders', Order, filters={'status':'delivered'}),
            'staff_members': self.cached_or_query_counters('staff_members', User, filters={'is_staff':True}),
            'countries' : self.cached_or_query_counters('countries', Country),
            'cities' : self.cached_or_query_counters('cities', City),
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
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsStaffOrNotAllowed, DjangoModelPermissions]
    
    def get_queryset(self):
        colors = Color.objects.prefetch_related('sizes', 'images')
        qs = Product.objects.select_related('discount').all()
        qs = qs.prefetch_related(Prefetch('colors', queryset=colors), 'reviews')
        return qs

class PartnerView(ModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    permission_classes = [IsAuthenticated, IsStaffOrNotAllowed, DjangoModelPermissions]


class CountryView(ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAuthenticated, IsStaffOrNotAllowed, DjangoModelPermissions]
    
    def create(self, request, *args, **kwargs):
        created = super().create(request, *args, **kwargs)
        set_cache_if_exists(key='countries', add=1)
        return created
        
    
    def destroy(self, request, *args, **kwargs):
        destroyed = super().destroy(request, *args, **kwargs)
        set_cache_if_exists(key='countries', remove=1)
        return destroyed

    


class CityView(ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticated, IsStaffOrNotAllowed, DjangoModelPermissions]
    
    def create(self, request, *args, **kwargs):
        created = super().create(request, *args, **kwargs)
        set_cache_if_exists(key='cities', add=1)
        return created
    
    def destroy(self, request, *args, **kwargs):
        destroyed = super().destroy(request, *args, **kwargs)
        set_cache_if_exists(key='cities', remove=1)
        return destroyed



class OrderView(ModelViewSet):
    
    serializer_class = OrderSerializer
    queryset = Order.objects.prefetch_related('products__color', 'products__product', 'products__size').filter(ordered=True)
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
