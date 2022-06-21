from django_filters import FilterSet, AllValuesFilter
from django_filters import DateTimeFilter, NumberFilter, BooleanFilter
from .models import Product



class ProductFilter(FilterSet):
     
    min_price = NumberFilter(field_name='price', lookup_expr='gte')
    max_price = NumberFilter(field_name='price', lookup_expr='lte')
    category = AllValuesFilter(field_name='category')
    subcategory = AllValuesFilter(field_name='subcategory')
    brand = AllValuesFilter(field_name='brand')
    popularity = BooleanFilter(field_name='popularity')
    class Meta:
        model = Product
        fields = ['min_price', 'max_price', 'category', 'subcategory', 'brand', 'popularity']
