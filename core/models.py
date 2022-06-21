import secrets
from datetime import datetime
from django.db import models 
from django.core import validators
from django.dispatch import receiver
from django.db.models.signals import post_save
from .utils import stars_choices



class Category(models.Model):
    category_image = models.ImageField(upload_to ='category_images/', null=True, blank=True)
    category_background_image = models.ImageField(upload_to ='category_background_images/', null=True, blank=True)
    category_arabic_name = models.CharField(max_length=128)
    category_english_name = models.CharField(max_length=128)
    
    def __str__(self):
        return self.category_english_name
 
    
class SubCategory(models.Model):
    subcategory_arabic_name = models.CharField(max_length=128)
    subcategory_english_name = models.CharField(max_length=128)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategory')
    image = models.ImageField(upload_to='subcategory_images/', null=True, blank=True)
    creation_date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.subcategory_english_name} -> {self.category} '


class Brand(models.Model):
    brand_arabic_name = models.CharField(max_length=128)
    brand_english_name = models.CharField(max_length=128)
    creation_date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.brand_english_name
    

class Product(models.Model):
    english_name = models.CharField(max_length=256)
    arabic_name = models.CharField(max_length=256)
    price = models.FloatField()
    english_description = models.TextField()
    arabic_description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='product')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, related_name='product')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, related_name='product')
    image = models.ImageField(null=True, blank=True, upload_to='products_images/')
    is_available = models.BooleanField(default=True)
    popularity = models.BooleanField(default=False)
    num_of_sales = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    rate = models.IntegerField(default=0)
    
    def __str__(self):
        return self.english_name
    
    def save(self, *args, **kwargs):
        if self.num_of_sales >= 5 :
            self.popularity = True
        
        # check availability of all sizes related to product
        available_or_not = []
        for color in self.colors.all():
            for size in color.sizes.all():
                if size.quantity == 0:
                    available_or_not.append(False)
                else:
                    available_or_not.append(True)
        if any(available_or_not):
            self.is_available = True
        else:
            self.is_available = False
            
        super(Product, self).save(*args, **kwargs)


class ProductRate(models.Model):
    rater = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='rate')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rate = models.IntegerField(choices=stars_choices)
    comment = models.CharField(max_length=512)

@receiver(post_save, sender=ProductRate)
def average_product_rate(sender, instance=None, created=None, **kwargs):
    if created:
        product = instance.product
        all_product = ProductRate.objects.filter(product=product)
        rate_list = [p.rate for p in all_product]      
        product.rate = sum(rate_list)/len(rate_list)
        product.save()
        
    

class Color(models.Model):
    color_code = models.CharField(max_length=20)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='colors', null=True)
    def __str__(self):
        return f'color -> {self.color_code} for product -> {self.product}'   
    
        
class Image(models.Model):
    image = models.ImageField(null=True, upload_to='products_images/')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='images', null=True)
    
    def __str__(self):
        return f'image for -> {self.color}' 
    
    

class Size(models.Model):
    size = models.CharField(max_length=128)
    quantity = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=False)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='sizes', null=True)
    
    def __str__(self):
        return f'size {self.size} for -> {self.color}' 
    
    def save(self, *args, **kwargs):
        if self.quantity == 0:
            self.available = False
        else:
            self.available = True
        
        super(Size, self).save(*args, **kwargs)
        self.color.product.save()
    
    
    
class Slider(models.Model):
    image= models.ImageField(upload_to='slider/')
    english_title = models.CharField(max_length=256)
    arabic_title = models.CharField(max_length=256)
    
    def __str__(self):
        return f'slider object -> {self.english_title}'
    

BANNER_CHOICES = (
    ('large_banner', 'Large Banner'),
    ('mid_banner','Mid Banner')
)



class Advertisement(models.Model):
    image= models.ImageField(upload_to='advertisement/')
    english_title = models.CharField(max_length=256)
    arabic_title = models.CharField(max_length=256)
    english_description = models.TextField()
    arabic_description = models.TextField()
    ad_url = models.CharField(max_length=256)
    banner_size = models.CharField(max_length=20, choices=BANNER_CHOICES)
    
    def __str__(self):
        return 'new ads -> {self.english_title}'
    
    
class DiscountOffer(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='discount')
    discount_value = models.IntegerField(validators=[validators.MinValueValidator(0, 'Discount Value Can\'t be lower than 0%'),validators.MaxValueValidator(100, 'Discount Value Can\'t be greater than 100%')])
    disount_value_exp_date = models.DateField()
    active = models.BooleanField(default=True)
    
    def still_active(self):
        exp_date = self.disount_value_exp_date.strftime("%m/%d/%Y")
        now = datetime.now()
        today = now.strftime("%m/%d/%Y")
        if exp_date <= today:
            self.active = False
            self.save()
            return False
        else:
            return True
        
    def __str__(self):
        return f'disount for product -> {self.product.english_name}'
    

class DiscountCoupon(models.Model):
    max_orders = models.IntegerField()
    discount_value = models.IntegerField(validators=[validators.MinValueValidator(0, 'Discount Value Can\'t be lower than 0%'),validators.MaxValueValidator(100, 'Discount Value Can\'t be greater than 100%')])
    coupon_exp_date = models.DateField()
    code = models.CharField(max_length=30, null=True, blank=True)
    active = models.BooleanField(default=True)
    
    
    def __str__(self):
        return self.code
    
    def save(self, *args, **kwargs):
        
        if self.max_orders <= 0:
            self.active = False
        else:
            self.active = True
            
        if not self.code:
             self.code = secrets.token_urlsafe(16)
        super(DiscountCoupon, self).save(*args, **kwargs)
    
    def still_active(self):
        exp_date = self.coupon_exp_date.strftime("%m/%d/%Y")
        now = datetime.now()
        today = now.strftime("%m/%d/%Y")
        if exp_date <= today or self.max_orders==0:
            self.active = False
            self.save()
            return False
        else:
            return True 
        
    

class Partner(models.Model):
    image = models.ImageField(upload_to='partners/')
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

class Country(models.Model):
    arabic_name = models.CharField(max_length=128)
    english_name = models.CharField(max_length=128)
    
    def __str__(self):
        return self.english_name
    
    
class City(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='cities')
    arabic_name = models.CharField(max_length=128)
    english_name = models.CharField(max_length=128)
    shipping_cost = models.FloatField()
    
    def __str__(self):
        return self.english_name
    


