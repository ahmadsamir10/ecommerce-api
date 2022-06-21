from rest_framework import serializers
from users.models import User, UserAddress, Wishlist
from core.models import ProductRate




class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'username', 'email', 'mobile', 'password']
        extra_kwargs = {'password':{'write_only':True}, 'mobile':{'write_only':True}, 'full_name':{'write_only':True},}
        
    def create(self, validated_data):
        return self.Meta.model.objects.create_user(**validated_data)
    
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(max_length=128, required=True)


class AccountDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'username', 'mobile', 'email']
        
        
class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        exclude = ['user']
    
    def create(self, validated_data):
        user =  self.context['request'].user
        address = user.address.create(**validated_data)
        
        return address
        

class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        exclude = ['user']
        
        
    def create(self, validated_data):
        user =  self.context['request'].user
        wishlist = user.wishlist.create(**validated_data)
        
        return wishlist
    

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRate
        exclude = ['rater']
        
    def create(self, validated_data):
        user = self.context['request'].user
        review = user.rate.create(**validated_data)
        return review
    

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'username', 'email', 'mobile', 'is_staff']
        extra_kwargs = {'is_staff':{'read_only':True}}