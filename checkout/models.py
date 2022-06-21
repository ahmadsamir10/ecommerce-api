from django.db import models
from datetime import datetime
from .utils import payment_methods_choices, order_status_choices



class OrderProduct(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='orderproduct')
    ordered = models.BooleanField(default=False)
    canceled = models.BooleanField(default=False)
    product = models.ForeignKey('core.Product', on_delete=models.CASCADE)
    color = models.ForeignKey('core.Color', on_delete=models.CASCADE)
    size = models.ForeignKey('core.Size', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    
    def __str__(self):
        return f'{self.quantity}x({self.product.english_name})  for  {self.user}'

    def total_product_price(self, coupon_discount=None):
        try:
            if self.product.discount.still_active():
                discount_value = self.product.discount.discount_value/100
                total = self.product.price * self.quantity
                total_product_price = total - (total*discount_value)
                if coupon_discount:
                    total_discount_value = discount_value+coupon_discount
                    total = self.product.price * self.quantity
                    total_product_price = total - (total*total_discount_value)
            elif coupon_discount:
                total = self.product.price * self.quantity
                total_product_price = total - (total*coupon_discount)
            else: 
                total_product_price = self.product.price * self.quantity
            return total_product_price
        
        except:
            if coupon_discount:
                total = self.product.price * self.quantity
                total_product_price = total - (total*coupon_discount)
            else:
                total_product_price = self.product.price * self.quantity
            return total_product_price

    def save(self, *args, **kwargs):
        
        super(OrderProduct, self).save(*args, **kwargs)
        if self.ordered and self.canceled:
            self.size.quantity += self.quantity
            self.size.save()


class Order(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='order')
    products = models.ManyToManyField(OrderProduct, blank=True, related_name='products')
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(null=True)
    billing_address = models.ForeignKey('users.UserAddress', on_delete=models.SET_NULL, blank=True, null=True)
    payment_info = models.CharField(max_length=16, choices=payment_methods_choices, default='cash')
    coupon_code = models.ForeignKey('core.DiscountCoupon',on_delete=models.SET_NULL, blank=True, null=True)
    total = models.FloatField(default=0)
    shipping_cost = models.FloatField(default=0)
    ordered = models.BooleanField(default=False)
    canceled = models.BooleanField(default=False)
    status = models.CharField(max_length=16, choices=order_status_choices, null=True, blank=True)
    
    def __str__(self):
        if self.ordered == True:
            return 'Completed Order for '  + self.user.username 
        return 'in Progress Order for '  + self.user.username
    
    
    def save(self, *args, **kwargs):
        # add date and time if the order is completed
        if self.ordered == True:
            self.ordered_date = datetime.now()
            for orderproduct in self.products.all():
                orderproduct.ordered = True
                orderproduct.save()
                if orderproduct.quantity <= orderproduct.size.quantity:
                    orderproduct.size.quantity -= orderproduct.quantity
                    orderproduct.size.save()
                    orderproduct.product.num_of_sales += orderproduct.quantity
                    orderproduct.product.save()
                else:    
                    orderproduct.quantity = orderproduct.size.quantity
                    orderproduct.save()
                    orderproduct.product.num_of_sales += orderproduct.quantity
                    orderproduct.product.save()

                    
        super(Order, self).save(*args, **kwargs)
       



