from rest_framework import serializers
from core.models import Category, Country, DiscountOffer, Product, ProductRate, Size, Image, Color, SubCategory
from dashboard.api.serializers import CitySerializer, CountrySerializer



class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'size', 'quantity']
        
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image']

class ColorSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    sizes = SizeSerializer(many=True, read_only=True)
    class Meta:
        model = Color
        fields = ['id', 'color_code', 'images', 'sizes']


class ProductRateSerilaizer(serializers.ModelSerializer):
    class Meta:
        mdoel = ProductRate
        exclude = ['product']


class ProductSerializer(serializers.ModelSerializer):
    colors = ColorSerializer(many=True, read_only=True)
    reviews = ProductRateSerilaizer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = [
            'id',
            'english_name',
            'arabic_name',
            'price',
            'english_description',
            'arabic_description',
            'category',
            'subcategory',
            'brand',
            'image',
            'discount',
            'rate',
            'reviews',
            'is_available',
            'colors',
            ]


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'subcategory_arabic_name', 'subcategory_english_name', 'image']


class CategorySerializer(serializers.ModelSerializer):
    subcategory = SubcategorySerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'category_image', 'category_background_image', 'category_arabic_name', 'category_english_name', 'subcategory']

       
class CategoryProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'category_image', 'category_background_image', 'category_arabic_name', 'category_english_name', 'product']
        

class CountryCitySerializer(serializers.ModelSerializer):
    cities = CitySerializer(many=True, read_only=True)
    class Meta:
        model = Country
        fields = ['id', 'arabic_name', 'english_name', 'cities']
        
class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountOffer
        exclude = ['active', 'disount_value_exp_date']
