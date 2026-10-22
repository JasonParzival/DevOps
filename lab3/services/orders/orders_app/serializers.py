from rest_framework import serializers
from .models import Order, OrderDetail
from .services import customer_info, product_info

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source="user_id", read_only=True)
    customer = serializers.IntegerField(source="customer_id", min_value=1)

    class Meta:
        model = Order
        fields = ("id", "order_number", "date", "status", "customer", "user")

    def validate_customer(self, value):
        customer_info(self.context["request"].user, value)
        return value

    def create(self, validated_data):
        validated_data["user_id"] = self.context["request"].user.pk
        return super().create(validated_data)


class OrderDetailSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source="user_id", read_only=True)
    product = serializers.IntegerField(source="product_id", min_value=1)
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    product_name = serializers.CharField(read_only=True)
    product_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderDetail
        fields = ("id", "order", "product", "quantity", "user", "product_name", "product_price")

    def validate_order(self, value):
        current = self.context["request"].user
        if not current.is_superuser and value.user_id != current.pk:
            raise serializers.ValidationError("Нельзя использовать чужой заказ")
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        requester = self.context["request"].user
        product_id = attrs.get("product_id", getattr(self.instance, "product_id", None))
        quantity = attrs.get("quantity", getattr(self.instance, "quantity", None))
        changing_product = self.instance is None or "product_id" in attrs
        changing_quantity = self.instance is None or "quantity" in attrs
        if changing_product or changing_quantity:
            product = product_info(requester, product_id)
            try:
                stock = int(product["quantity"])
                price = str(product["price"])
                name = str(product["name"])
                if stock < 0 or not name:
                    raise ValueError("Invalid product info")
            except (KeyError, ValueError, TypeError) as exc:
                from .services import UpstreamUnavailable
                raise UpstreamUnavailable("Некорректный ответ каталога") from exc
            if quantity > stock:
                raise serializers.ValidationError({"quantity": "Количество превышает текущий остаток"})
            if changing_product:
                attrs["product_name"] = name
                attrs["product_price"] = price
        return attrs

    def create(self, validated_data):
        validated_data["user_id"] = self.context["request"].user.pk
        return super().create(validated_data)
