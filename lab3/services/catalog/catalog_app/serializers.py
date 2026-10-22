from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    # Compatibility: the old API calls this field "user", not "user_id".
    user = serializers.IntegerField(source="user_id", read_only=True)

    class Meta:
        model = Category
        fields = ("id", "name", "description", "user")

    def create(self, validated_data):
        validated_data["user_id"] = self.context["request"].user.pk
        return super().create(validated_data)


class ProductSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source="user_id", read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), allow_null=True)

    class Meta:
        model = Product
        fields = ("id", "name", "price", "description", "quantity", "category", "picture", "user")

    def validate_category(self, category):
        request = self.context["request"]
        if category is not None and not request.user.is_superuser and category.user_id != request.user.pk:
            raise serializers.ValidationError("Нельзя использовать чужую категорию")
        return category

    def create(self, validated_data):
        validated_data["user_id"] = self.context["request"].user.pk
        return super().create(validated_data)
