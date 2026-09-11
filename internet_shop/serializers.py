from rest_framework import serializers

from internet_shop.models import Product
from internet_shop.models import Category
from internet_shop.models import Customer
from internet_shop.models import Order
from internet_shop.models import OrderDetail

from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

# №2
class CategorySerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        if 'request' in self.context:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'user']
        read_only_fields = ['user']

# №1
class ProductSerializer(serializers.ModelSerializer):
    #category = CategorySerializer(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    
    """def create(self, validated_data):
        if 'request' in self.context:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)"""
        
    def create(self, validated_data):
        print(f"Request in context: {'request' in self.context}")
        if 'request' in self.context:
            print(f"User: {self.context['request'].user}")
            validated_data['user'] = self.context['request'].user
        else:
            print("No request in context!")
        return super().create(validated_data)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description', 'quantity', 'category', 'picture', 'user']
        read_only_fields = ['user']
        
# №3    
class CustomerSerializer(serializers.ModelSerializer):
    def create(self, validated_data): 
        if 'request' in self.context:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    class Meta:
        model = Customer
        fields = ['id', 'name', 'address', 'phone_number', 'email', 'picture', 'user']
        read_only_fields = ['user'] 
        
# №4
class OrderSerializer(serializers.ModelSerializer):
    #customer = CustomerSerializer(read_only=True)
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    
    def create(self, validated_data):
        if 'request' in self.context:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'date', 'status', 'customer', 'user']
        read_only_fields = ['user']

# №5     
class OrderDetailSerializer(serializers.ModelSerializer):
    #order = OrderSerializer(read_only=True)
    #product = ProductSerializer(read_only=True)
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    
    def create(self, validated_data):
        if 'request' in self.context:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    class Meta:
        model = OrderDetail
        fields = ['id', 'order', 'product', 'quantity', 'user']
        read_only_fields = ['user']