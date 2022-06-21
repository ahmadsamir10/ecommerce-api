from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.contrib.auth.models import Group
from checkout.models import Order, OrderProduct
from users.models import User
from core.models import (
                            Advertisement,
                            Brand,
                            City,
                            Country,
                            DiscountCoupon,
                            Category,
                            Partner,
                            Product,
                            Color,
                            Image,
                            Size,
                            DiscountOffer,
                            Slider,
                            SubCategory
                        )




class SliderSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = Slider
        fields = '__all__'


class AdvertisementSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = '__all__'


class DiscountCouponSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = DiscountCoupon
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        exclude = ('creation_date', )


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        exclude = ('creation_date',)


class DiscountOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountOffer
        fields = '__all__'

###
class SizeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = Size
        fields = ['id', 'size', 'quantity']
        
class ImageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = Image
        fields = ['id', 'image']

class ColorSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    images = ImageSerializer(many=True)
    sizes = SizeSerializer(many=True)
    class Meta:
        model = Color
        fields = ['id', 'color_code', 'images', 'sizes']

class DiscountOfferProductSerializer(DiscountOfferSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = DiscountOffer
        fields =['id', 'discount_value', 'disount_value_exp_date']

class ProductSerializer(serializers.ModelSerializer):
    colors = ColorSerializer(many=True)
    discount = DiscountOfferProductSerializer(many=False, required=False, allow_null=True)

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
            'colors',
            'discount'
            ]
        ordering = ['-id']


    def create(self, validated_data):
        #pop out first-layer data
        colors_data = validated_data.pop('colors')
        
        
        #create product object
        product = Product.objects.create(**validated_data)
        
        #create DiscountOffer objects based on the data below
        try:
            if validated_data['discount']:
                discount_data = validated_data.pop('discount')
                DiscountOffer.objects.create(**discount_data, product=product)
        except KeyError:
            pass
            
        #loop into color data cause it's in many to one rel with product instance
        for color_data in colors_data:
            images_data = color_data.pop('images')
            sizes_data = color_data.pop('sizes')
            new_color = Color.objects.create(product=product, **color_data)
            # loop into second layer data (size, images) cause it's in many to one rel with color instance
            for image_data in images_data:
                Image.objects.create(color=new_color, **image_data)
            for size_data in sizes_data:
                Size.objects.create(color=new_color, **size_data)

        return product


    def update(self, instance, validated_data):
        
        # main product data updated
        instance.english_name = validated_data.get('english_name', instance.english_name)
        instance.arabic_name = validated_data.get('arabic_name', instance.arabic_name)
        instance.price = validated_data.get('price', instance.price)
        instance.english_description = validated_data.get('english_description', instance.english_description)
        instance.arabic_description = validated_data.get('arabic_description', instance.arabic_description)
        instance.category = validated_data.get('category', instance.category)
        instance.subcategory = validated_data.get('subcategory', instance.subcategory)
        instance.brand = validated_data.get('brand', instance.brand)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        # ids list for overwriting the already existing objects 
        keep_colors = []
        keep_images = []
        keep_sizes = []
        if 'colors' in validated_data.keys():
            #pop out first-layer data
            colors_data = validated_data.pop('colors')
            # (first layer) loop over color instances and update, create, or delete data  
            for color in colors_data:
                if 'images' in color.keys():
                    images_data = color.pop('images')
                else:
                    images_data = False
                    
                if 'sizes' in color.keys():
                    sizes_data = color.pop('sizes')
                else:
                    sizes_data = False
                    
                if "id" in color.keys():
                    if Color.objects.filter(id=color['id']).exists():
                        c = Color.objects.get(id=color['id'])
                        c.color_code = color.get('color_code', c.color_code)
                        c.save()
                        keep_colors.append(c.id)
                        
                        if images_data:
                            # (second layer) loop over image instances and update, create, or delete data
                            for image in images_data:
                                if "id" in image.keys():
                                    if Image.objects.filter(id=image['id']).exists():
                                        i = Image.objects.get(id=image['id'])
                                        i.image = image.get('image', i.image)
                                        i.save()
                                        keep_images.append(i.id)
                                    else:
                                        continue
                                else:
                                    i = Image.objects.create(**image, color=c)
                                    keep_images.append(i.id)
                            
                            for image in c.images.all():
                                if image.id not in keep_images:
                                    image.delete()

                        if sizes_data:
                            # (second layer) loop over size instances and update, create, or delete data
                            for size in sizes_data:
                                if "id" in size.keys():
                                    if Size.objects.filter(id=size['id']).exists():
                                        s = Size.objects.get(id=size['id'])
                                        s.size = size.get('size', s.size)
                                        s.quantity = size.get('quantity', s.quantity)
                                        s.save()
                                        keep_sizes.append(s.id)
                                    else:
                                        continue
                                else:
                                    s = Size.objects.create(**size, color=c)
                                    keep_sizes.append(s.id)
                            
                            for size in c.sizes.all():
                                if size.id not in keep_sizes:
                                    size.delete()
                                
                    else:
                        continue
                else:
                    c = Color.objects.create(**color, product=instance)
                    keep_colors.append(c.id)
                        
            for color in instance.colors.all():
                if color.id not in keep_colors:
                    color.delete()

        return instance
###  



class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = '__all__'
  
        
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'
     
        
class CitySerializer(serializers.ModelSerializer):
    #country = CountrySerializer()
    class Meta:
        model = City
        fields = '__all__'
        

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'
   
     
class StaffGroupsSerializer(GroupSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = Group
        fields = ['id', 'name']
        extra_kwargs = { 'name':{'read_only':True}}




class StaffSerializer(serializers.ModelSerializer):
    groups = StaffGroupsSerializer(many=True)
    
    class Meta:
        model = User
        fields = ['id', 'full_name', 'username', 'email', 'mobile', 'groups', 'password', 'is_staff']
        extra_kwargs = {'is_staff': {'read_only':True}, 'password': {'write_only': True}, 'groups':{'read_only':True}}
        ordering = ['-id']
        
    def create(self, validated_data):
        groups_data = validated_data.pop('groups')
        validated_data['is_staff'] = True
        validated_data['is_active'] = True
        staff_user = self.Meta.model.objects.create_staff(**validated_data)
        for group in groups_data:
            group_id = get_object_or_404(Group, **group)
            staff_user.groups.add(group_id)
        return staff_user
    
    def update(self, instance, validated_data):
        
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.mobile = validated_data.get('mobile', instance.mobile)
        instance.password = validated_data.get('password', instance.password)
        instance.set_password(instance.password)
        instance.save()
        
        # to prevent patch request errors 
        if 'groups' in validated_data.keys():
            groups_data = validated_data.pop('groups')
            
            keep_groups = []
            for group in groups_data:
                if "id" in group.keys():
                    if Group.objects.filter(id=group['id']).exists():
                        g = Group.objects.get(id=group['id'])
                        instance.groups.add(g)
                        keep_groups.append(g.id)
                    else:
                        continue
                else:
                    continue
            
            for group in instance.groups.all():
                if group.id not in keep_groups:
                    instance.groups.remove(group)    
            
        return instance
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'image',  'username', 'full_name', 'mobile', 'email', 'password', 'is_active', 'created_at']
        extra_kwargs = {'is_active': {'read_only':True}, 'username': {'write_only': True}, 'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['is_active'] = True
        return self.Meta.model.objects.create_user(**validated_data)
    
    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.username = validated_data.get('username', instance.username)
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.mobile = validated_data.get('mobile', instance.mobile)
        instance.email = validated_data.get('email', instance.email)
        instance.password = validated_data.get('password', instance.password)
        instance.set_password(instance.password)
        instance.save()
        
        return instance
    

class OrderProductSerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField(read_only=True,slug_field="english_name")
    color = serializers.SlugRelatedField(read_only=True,slug_field="color_code")
    size = serializers.SlugRelatedField(read_only=True,slug_field="size")
    class Meta:
        model = OrderProduct
        fields = ['id', 'product', 'color', 'size', 'quantity']
    
    
class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'billing_address',
            'ordered_date',
            'payment_info',
            'total',
            'shipping_cost',
            'coupon_code',
            'ordered',
            'canceled',
            'status',
            'products'
                  ]
        extra_kwargs = {
            'ordered':{'read_only':True},
            'canceled':{'read_only':True},
            'billing_address':{'read_only':True},
            'payment_info':{'read_only':True},
            'total':{'read_only':True},
            'shipping_cost':{'read_only':True},
            'coupon_code':{'read_only':True},
            'products':{'read_only':True},
            'ordered_date':{'read_only':True},
            }
        
