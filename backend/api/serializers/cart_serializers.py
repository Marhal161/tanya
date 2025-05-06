from rest_framework import serializers
from api.models import Cart, CartItem
from .sneaker_serializers import SneakerSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор для элементов корзины.
    """
    sneaker = SneakerSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'sneaker', 'quantity', 'total_price', 'added_at']
        read_only_fields = ['id', 'added_at']
    
    def get_total_price(self, obj):
        """
        Вычисляет общую стоимость элемента корзины.
        """
        return obj.quantity * obj.sneaker.price


class CartSerializer(serializers.ModelSerializer):
    """
    Сериализатор для корзины.
    """
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'items_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_price(self, obj):
        """
        Вычисляет общую стоимость корзины.
        """
        return sum(item.quantity * item.sneaker.price for item in obj.items.all())
    
    def get_items_count(self, obj):
        """
        Вычисляет общее количество товаров в корзине.
        """
        return sum(item.quantity for item in obj.items.all())


class CartItemCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания элемента корзины.
    """
    class Meta:
        model = CartItem
        fields = ['sneaker', 'quantity']
        

class CartItemUpdateSerializer(serializers.Serializer):
    """
    Сериализатор для обновления элемента корзины.
    """
    sneaker_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=0)
    
    def validate_quantity(self, value):
        """
        Проверка количества товара.
        """
        if value < 0:
            raise serializers.ValidationError("Количество не может быть отрицательным.")
        return value 