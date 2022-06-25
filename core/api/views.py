from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.db.models import Prefetch
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from core.models import Brand, Category, Country, DiscountOffer, Product, Slider, SubCategory, Color
from dashboard.api.serializers import BrandSerializer, SliderSerilaizer, SubCategorySerializer
from core.custom_filters import ProductFilter
from .serializers import (
                            CategorySerializer,
                            OfferSerializer,
                            ProductSerializer,
                            CountrySerializer,
                            CountryCitySerializer
                        )


class ListRetrieveCategoryView(ViewSet):
    def list(self, request):
        queryset = Category.objects.prefetch_related('subcategory').all()
        serializer = CategorySerializer(instance=queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        queryset = Category.objects.all()
        category = get_object_or_404(queryset, pk=pk)
        serializer = CategorySerializer(instance=category)
        return Response(serializer.data)


class RetrieveSubCategoryView(RetrieveAPIView):
    lookup_field = 'pk'
    serializer_class = SubCategorySerializer
    queryset = SubCategory.objects.all()


class ListSubcategoryByCategoryView(RetrieveAPIView):
    lookup_field = 'pk'
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    

class ListProductsView(ListAPIView):
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filter_fields = ['category', 'subcategory']
    ordering_fields = ['created_at', 'num_of_sales', 'rate']
    ordering = ('-id',)
    
    def get_queryset(self):
        colors = Color.objects.prefetch_related('sizes', 'images')
        qs = Product.objects.select_related('discount').all()
        qs = qs.prefetch_related(Prefetch('colors', queryset=colors), 'reviews')
        return qs


class RetrieveProductView(RetrieveAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    lookup_url_kwarg = 'pk'
    
    def get_object(self):
        pk = self.kwargs['pk']
        instance = Product.objects.select_related('discount').get(pk=pk)
        return instance


class ListCountryView(ListAPIView):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()


class ListCityByCountryView(RetrieveAPIView):
    serializer_class = CountryCitySerializer
    queryset = Country.objects.prefetch_related('cities').all()
    
    
class HomeView(APIView):
    
    def cached_or_query(self, key, qs):
        cached = cache.get(key)
        if cached != None:
            value = cached
        else:
            value = qs
            cache.set(key, value, timeout=None)
        return value
    
    def get(self, request):
        
        colors = Color.objects.prefetch_related('sizes', 'images')
        _products = Product.objects.select_related('discount').prefetch_related(Prefetch('colors', queryset=colors), 'reviews')
        
        ##
        sliders = self.cached_or_query('sliders_qs', Slider.objects.all())
        sliders_serializer = SliderSerilaizer(instance=sliders, many=True)
    
        best_selling_products = _products.order_by('-num_of_sales')[:8]
        best_selling_products_serializer = ProductSerializer(instance=best_selling_products, many=True)
        
        categories = self.cached_or_query('categories_qs', Category.objects.prefetch_related('subcategory').all())
        categories_serializer = CategorySerializer(instance=categories, many=True)
        
        new_products = self.cached_or_query('new_products_qs', _products.order_by('-created_at')[:8])
        new_products_serializer = ProductSerializer(instance=new_products, many=True)
        
        women_products = _products.filter(category__category_english_name='women\s').order_by('?')[:8]
        women_products_serializer = ProductSerializer(instance=women_products, many=True)
        
        data = {
            'galleries': sliders_serializer.data,
            'best_selling': best_selling_products_serializer.data,
            'categories' : categories_serializer.data,
            'new_arrivals': new_products_serializer.data,
            'woman_category': women_products_serializer.data,
        }
        return Response(data)
     

class ListBrandsView(ListAPIView):
    serializer_class = BrandSerializer
    queryset = Brand.objects.all()
  

class ProductSerachView(ListAPIView):
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['english_name', 'arabic_name', 'english_description', 'arabic_description', 'category__category_arabic_name', 'category__category_english_name']
    
    def get_queryset(self):
        colors = Color.objects.prefetch_related('sizes', 'images')
        qs = Product.objects.select_related('discount').all()
        qs = qs.prefetch_related(Prefetch('colors', queryset=colors), 'reviews')
        return qs

    
    
class ProductFilterView(ListAPIView):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    filter_class = ProductFilter
    
class ListOffersView(ListAPIView):
    serializer_class = OfferSerializer
    queryset = DiscountOffer.objects.filter(active=True)
    