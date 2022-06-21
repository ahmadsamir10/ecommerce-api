from rest_framework import serializers
from checkout.models import Order, OrderProduct
from core.models import DiscountCoupon




class OrderProductSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(required=True, min_value=1)
    class Meta:
        model = OrderProduct
        fields = ['id', 'product', 'color', 'size', 'quantity']

    # VALIDATE DATA BEFORE PERFORM ACTIONS 
    def validate(self, data):
        product = data.get('product') 
        if product.is_available == True:
            color = data.get('color')
            if color.product == product:  
                size = data.get('size')
                if size.color.product == product and size.available:
                    if size.quantity >= data.get('quantity'):
                        pass
                    else:
                        raise serializers.ValidationError({"size": f"The available quantity of the selected size is {size.quantity}"})
                else:
                    size = data.get('size')
                    raise serializers.ValidationError({"size": f"Invalid pk \"{size.id}\" - object does not exist."})
            else:
                color = data.get('color')
                raise serializers.ValidationError({"color": f"Invalid pk \"{color.id}\" - object does not exist."})
            return data
        else: 
            raise serializers.ValidationError({"product": f"Invalid pk \"{product.id}\" - object does not exist."})
    # CREATE ORDERPRODUCT FOR THE REQUESTED USER
    def create(self, validated_data):
        user = self.context['request'].user
        instance = self.Meta.model.objects.create(user=user, **validated_data)
        return instance
    
    
class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True, read_only=True)
    coupon_code = serializers.CharField(max_length=64, required=False)
    class Meta:
        model = Order
        fields = ['id', 'billing_address', 'payment_info', 'coupon_code', 'total', 'shipping_cost', 'ordered_date', 'ordered', 'canceled', 'products']
        extra_kwargs = {
            'billing_address': {'required': True, 'allow_null':True},
            'total':{'read_only':True},
            'shipping_cost':{'read_only':True},
            'ordered_date':{'read_only':True},
            }
    
    # VALIDATE DATA BEFORE PERFORM ACTIONS
    def validate(self, data):
        if data.get('billing_address') != None:
            user = self.context['request'].user
            address_id = data.get('billing_address').id
            user_addresses = user.address.filter(id=address_id).exists()
            if not user_addresses:
                raise serializers.ValidationError({"billing_address": f"Invalid pk \"{address_id}\" - object does not exist."})
        return data
    # CREATE ORDER FOR THE REQUESTED USER IF THE CART IS NOT EMPTY .. ELSE RAISE VALIDATION ERROR
    def create(self, validated_data):
        user = self.context['request'].user
        # make sure that there is items in the cart 
        if OrderProduct.objects.filter(user=user, ordered=False).exists():
            all_user_products = user.orderproduct.all()
            # if there is coupon code (Discount Coupon) added to the order
            if validated_data.get('coupon_code'):
                coupon_serial = validated_data.pop('coupon_code')
                # check if the given code is related to actual DiscountCoupon Object
                if DiscountCoupon.objects.filter(code=coupon_serial).exists():
                    coupon_code = DiscountCoupon.objects.get(code=coupon_serial)
                    # check if the coupon code is still active (not expired by date or deactivated by staff)
                    if coupon_code.still_active():
                        # if coupon is active .. create order 
                        order = Order.objects.create(user=user, coupon_code=coupon_code, **validated_data)
                    else:
                        # if coupon is not active .. create order without it
                        order = Order.objects.create(user=user, **validated_data)
                else:
                    # if coupon is not exists .. create order without it
                    order = Order.objects.create(user=user, **validated_data)
            else:
                # if there is no coupon code given by the user .. create order without it
                order = Order.objects.create(user=user, **validated_data)
            
            #loop over all user's items and add it to the order object (created below)
            for product in all_user_products:
                order.products.add(product)
            
            #check for coupon code 
            if order.coupon_code:
                # sum total cart price 
                total_price = 0
                for orderproduct in order.products.all():
                    coupon = order.coupon_code
                    coupon_discount = coupon.discount_value/100
                    total_price += orderproduct.total_product_price(coupon_discount=coupon_discount)
                # remove 1 from coupon max orders
                order.coupon_code.max_orders -= 1
                order.coupon_code.save()
                # add total order price after discount coupon and product discount offer 
                order.total = total_price
                order.save()
                
            else:
                # sum total cart price 
                total_price = 0
                for orderproduct in order.products.all():
                    total_price += orderproduct.total_product_price()
                order.total = total_price
                order.save()
            
            #add shipping cost based on user's address
            order.shipping_cost = order.billing_address.city.shipping_cost 
            order.save() 
            return order
        # if the cart is empty .. raise validation error
        else:
            raise serializers.ValidationError({"products": ["there is no Products in your cart"]})
    # OVERRIDING UPDATE METHOD TO CHECKOUT OR CANCEL ORDERS   
    def update(self, instance, validated_data):
        if instance.ordered == True:
            if instance.canceled == False:
                if validated_data.get('canceled') == True:
                    instance.canceled == True
                    for orderproduct in instance.products.all():
                        orderproduct.canceled = True
                        orderproduct.save()
                elif validated_data.get('canceled') == None:
                    pass
                else:
                    raise serializers.ValidationError({"canceled": "Already not canceled."})
            else:
                if validated_data.get('canceled') != None:
                    if validated_data.get('canceled') == True:
                        raise serializers.ValidationError({"canceled": "Already canceled."})
                    raise serializers.ValidationError({"canceled": "Already canceled and you can't undo this proccess."})
                        
            if validated_data.get('ordered') != None:
                if validated_data.get('ordered') == True:
                    raise serializers.ValidationError({"ordered": "Already ordered."})
                else:
                    raise serializers.ValidationError({"ordered": "Already Ordered, you can now cancel it."})
                
        elif validated_data.get('canceled') == False:
            raise serializers.ValidationError({"canceled": "Already not canceled."})
        
        elif validated_data.get('canceled') == True:
            raise serializers.ValidationError({"canceled": "Can't cancel not ordered order."})
        else:
            if validated_data.get('ordered') == False:
                raise serializers.ValidationError({"ordered": "Already not ordered."})
             
        return super().update(instance, validated_data)