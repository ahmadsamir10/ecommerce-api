from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from core.models import Brand, Category, Country, DiscountOffer, Product, Slider, SubCategory
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
        queryset = Category.objects.all()
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
    queryset = Product.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filter_fields = ['category', 'subcategory']
    ordering_fields = ['created_at', 'num_of_sales', 'rate']
    ordering = ('-id',)


class RetrieveProductView(RetrieveAPIView):
    lookup_field = 'pk'
    serializer_class = ProductSerializer
    queryset = Product.objects.all()


class ListCountryView(ListAPIView):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()


class ListCityByCountryView(RetrieveAPIView):
    serializer_class = CountryCitySerializer
    queryset = Country.objects.all()
    
    
class HomeView(APIView):
    def get(self, request):
        
        sliders = Slider.objects.all()
        sliders_serializer = SliderSerilaizer(instance=sliders, many=True)
        
        products = Product.objects.all().order_by('-num_of_sales')[:8]
        products_serializer = ProductSerializer(instance=products, many=True)
        
        categories = Category.objects.all()
        categories_serializer = CategorySerializer(instance=categories, many=True)
        
        new_products = Product.objects.all().order_by('-created_at')[:8]
        new_products_serializer = ProductSerializer(instance=new_products, many=True)
        
        women_products = Product.objects.filter(category=3).order_by('?')[:8]
        women_products_serializer = ProductSerializer(instance=women_products, many=True)
        
        data = {
            'galleries': sliders_serializer.data,
            'best_selling': products_serializer.data,
            'categories' : categories_serializer.data,
            'new_arrivals': new_products_serializer.data,
            'woman_category': women_products_serializer.data,
        }
        return Response(data)
     

class ListBrandsView(ListAPIView):
    serializer_class = BrandSerializer
    queryset = Brand.objects.all()
  

class ProductSerachView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['english_name', 'arabic_name', 'english_description', 'arabic_description', 'category__category_arabic_name', 'category__category_english_name']
    
    
class ProductFilterView(ListAPIView):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    filter_class = ProductFilter
    
class ListOffersView(ListAPIView):
    serializer_class = OfferSerializer
    queryset = DiscountOffer.objects.filter(active=True)
    