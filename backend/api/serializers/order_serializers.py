from rest_framework import serializers
from api.models import Order, OrderItem, Sneaker
from .sneaker_serializers import SneakerSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор для элементов заказа.
    """
    sneaker = SneakerSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'sneaker', 'price', 'quantity', 'total_price']
        read_only_fields = ['id', 'price']
    
    def get_total_price(self, obj):
        """
        Вычисляет общую стоимость элемента заказа.
        """
        return obj.price * obj.quantity


class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка заказов.
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'status', 'status_display', 'total_price', 
            'items_count', 'created_at'
        ]
        read_only_fields = ['id', 'total_price', 'created_at']
    
    def get_items_count(self, obj):
        """
        Вычисляет общее количество товаров в заказе.
        """
        return sum(item.quantity for item in obj.items.all())


class OrderDetailSerializer(serializers.ModelSerializer):
    """
    Детальный сериализатор для заказа.
    """
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone', 
            'address', 'total_price', 'status', 'status_display',
            'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_price', 'created_at', 'updated_at']


class OrderItemCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания элемента заказа.
    """
    class Meta:
        model = OrderItem
        fields = ['sneaker', 'quantity']


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания заказа.
    """
    items = OrderItemCreateSerializer(many=True)
    
    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'email', 'phone', 
            'address', 'items'
        ]
    
    def create(self, validated_data):
        """
        Создание заказа с элементами.
        """
        items_data = validated_data.pop('items')
        
        # Рассчитываем общую сумму заказа
        total_price = sum(
            Sneaker.objects.get(id=item_data['sneaker'].id).price * item_data['quantity']
            for item_data in items_data
        )
        
        # Создаем заказ
        order = Order.objects.create(
            **validated_data,
            total_price=total_price
        )
        
        # Создаем элементы заказа
        for item_data in items_data:
            sneaker = item_data['sneaker']
            OrderItem.objects.create(
                order=order,
                sneaker=sneaker,
                price=sneaker.price,
                quantity=item_data['quantity']
            )
        
        return order 