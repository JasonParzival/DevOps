from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers
from django.db.models import Avg, Count, Max, Min, Sum
from rest_framework.permissions import IsAuthenticated, AllowAny

from internet_shop.models import Product
from internet_shop.serializers import ProductSerializer

from internet_shop.models import Category
from internet_shop.serializers import CategorySerializer

from internet_shop.models import Customer
from internet_shop.serializers import CustomerSerializer

from internet_shop.models import Order
from internet_shop.serializers import OrderSerializer

from internet_shop.models import OrderDetail
from internet_shop.serializers import OrderDetailSerializer

from internet_shop.serializers import UserSerializer
from django.contrib.auth.models import User

class UsersViewset(
    mixins.ListModelMixin,
    GenericViewSet
):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return super().get_queryset()
        return User.objects.none()

class ProductsViewset(
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin, 
    GenericViewSet
):
    permission_classes = [IsAuthenticated]
    
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user_id')
            if user_id:
                qs = qs.filter(user_id=user_id)
            return qs
        
        qs = qs.filter(user=self.request.user) 
        return qs
        
    class ProductStatsSerializer(serializers.Serializer):
        total_count = serializers.IntegerField()
        avg_price = serializers.DecimalField(max_digits=10, decimal_places=2)
        min_price = serializers.DecimalField(max_digits=10, decimal_places=2)
        max_price = serializers.DecimalField(max_digits=10, decimal_places=2)
        total_stock = serializers.IntegerField()
    
    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        if request.user.is_superuser:
            queryset = Product.objects.all()
        else:
            queryset = Product.objects.filter(user=request.user)
        
        stats = queryset.aggregate(
            total_count=Count("id"),
            avg_price=Avg("price"),
            min_price=Min("price"),
            max_price=Max("price"),
            total_stock=Sum("quantity")
        )
        
        serializer = self.ProductStatsSerializer(instance=stats)
        return Response(serializer.data)
    
class CategoriesViewset(
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin, 
    GenericViewSet
):
    permission_classes = [IsAuthenticated]
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user_id')
            if user_id:
                qs = qs.filter(user_id=user_id)
            return qs
        
        qs = qs.filter(user=self.request.user)
        return qs
    
    class CategoryStatsSerializer(serializers.Serializer):
        total_count = serializers.IntegerField()
        total_products = serializers.IntegerField()
        avg_products_per_category = serializers.FloatField()
    
    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        if request.user.is_superuser:
            user_categories = Category.objects.all()
            user_products = Product.objects.all()
        else:
            user_categories = Category.objects.filter(user=request.user)
            user_products = Product.objects.filter(user=request.user)
        
        total_categories = user_categories.count()
        total_products = user_products.count()
        
        categories_with_products = user_categories.annotate(
            product_count=Count('product')
        )
        
        avg_products = categories_with_products.aggregate(
            avg=Avg('product_count')
        )['avg'] or 0
        
        stats = {
            'total_count': total_categories,
            'total_products': total_products,
            'avg_products_per_category': round(avg_products, 2)
        }
        
        serializer = self.CategoryStatsSerializer(instance=stats)
        return Response(serializer.data)
    
class CustomersViewset(
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin, 
    GenericViewSet
):
    permission_classes = [IsAuthenticated]
    
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user_id')
            if user_id:
                qs = qs.filter(user_id=user_id)
            return qs
        
        qs = qs.filter(user=self.request.user)
        return qs
    
    class CustomerStatsSerializer(serializers.Serializer):
        total_count = serializers.IntegerField()
        customers_with_orders = serializers.IntegerField()
        total_orders = serializers.IntegerField()
        avg_orders_per_customer = serializers.FloatField()
    
    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        if request.user.is_superuser:
            user_customers = Customer.objects.all()
            user_orders = Order.objects.all()
        else:
            user_customers = Customer.objects.filter(user=request.user)
            user_orders = Order.objects.filter(user=request.user)
        
        total_customers = user_customers.count()
        total_orders = user_orders.count()
        
        customers_with_orders = user_customers.filter(
            order__isnull=False
        ).distinct().count()
        
        avg_orders = total_orders / total_customers if total_customers > 0 else 0
        
        stats = {
            'total_count': total_customers,
            'customers_with_orders': customers_with_orders,
            'total_orders': total_orders,
            'avg_orders_per_customer': round(avg_orders, 2)
        }
        
        serializer = self.CustomerStatsSerializer(instance=stats)
        return Response(serializer.data)
    
class OrdersViewset(
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin, 
    GenericViewSet
):
    permission_classes = [IsAuthenticated]
    
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user_id')
            if user_id:
                qs = qs.filter(user_id=user_id)
            return qs
        
        qs = qs.filter(user=self.request.user)
        return qs
    
    class OrderStatsSerializer(serializers.Serializer):
        total_count = serializers.IntegerField()
        orders_today = serializers.IntegerField()
        orders_this_month = serializers.IntegerField()
        status_distribution = serializers.DictField()
    
    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        from django.utils import timezone
        
        if request.user.is_superuser:
            user_orders = Order.objects.all()
        else:
            user_orders = Order.objects.filter(user=request.user)
        
        total_orders = user_orders.count()
        
        today = timezone.now().date()
        orders_today = user_orders.filter(date=today).count()
        
        current_month = timezone.now().month
        current_year = timezone.now().year
        orders_this_month = user_orders.filter(
            date__month=current_month,
            date__year=current_year
        ).count()
        
        status_distribution = {}
        for status_value, status_label in Order._meta.get_field('status').choices:
            count = user_orders.filter(status=status_value).count()
            status_distribution[status_label] = count
        
        stats = {
            'total_count': total_orders,
            'orders_today': orders_today,
            'orders_this_month': orders_this_month,
            'status_distribution': status_distribution
        }
        
        serializer = self.OrderStatsSerializer(instance=stats)
        return Response(serializer.data)
    
class OrderDetailsViewset(
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin, 
    GenericViewSet
):
    permission_classes = [IsAuthenticated]
    
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        if self.request.user.is_superuser:
            user_id = self.request.query_params.get('user_id')
            if user_id:
                qs = qs.filter(user_id=user_id)
            return qs
        
        qs = qs.filter(user=self.request.user)
        return qs
    
    class OrderDetailStatsSerializer(serializers.Serializer):
        total_count = serializers.IntegerField()
        total_quantity = serializers.IntegerField()
        avg_quantity = serializers.FloatField()
        min_quantity = serializers.IntegerField()
        max_quantity = serializers.IntegerField()
    
    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        if request.user.is_superuser:
            user_order_details = OrderDetail.objects.all()
        else:
            user_order_details = OrderDetail.objects.filter(user=request.user)
        
        stats = user_order_details.aggregate(
            total_count=Count("id"),
            total_quantity=Sum("quantity"),
            avg_quantity=Avg("quantity"),
            min_quantity=Min("quantity"),
            max_quantity=Max("quantity")
        )
        
        serializer = self.OrderDetailStatsSerializer(instance=stats)
        return Response(serializer.data)