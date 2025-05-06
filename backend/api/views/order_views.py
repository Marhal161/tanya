from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from api.models import Order, OrderItem, Cart, CartItem
from api.serializers.order_serializers import OrderSerializer, OrderCreateSerializer, OrderDetailSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с заказами пользователя.
    
    Позволяет получать список заказов, создавать новые заказы,
    просматривать детали заказа и отменять заказы.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Получаем только заказы текущего пользователя.
        """
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_serializer_class(self):
        """
        Выбираем сериализатор в зависимости от действия.
        """
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return OrderDetailSerializer
        return OrderSerializer
    
    def get_serializer_context(self):
        """
        Добавляем request в контекст сериализатора.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @transaction.atomic
    def perform_create(self, serializer):
        """
        Создание заказа и очистка корзины.
        """
        # Сохраняем заказ
        order = serializer.save(user=self.request.user)
        
        # После создания заказа очищаем корзину пользователя
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        CartItem.objects.filter(cart=cart).delete()
        
        return order
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Отмена заказа.
        """
        order = self.get_object()
        
        # Проверяем, можно ли отменить заказ
        if order.status in ['delivered', 'canceled']:
            return Response(
                {'error': 'Невозможно отменить заказ в статусе "Доставлен" или "Отменен"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Меняем статус заказа на "Отменен"
        order.status = 'canceled'
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def create_from_cart(self, request):
        """
        Создание заказа на основе текущей корзины пользователя.
        """
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        
        if not cart_items.exists():
            return Response(
                {'error': 'Корзина пуста'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Создаем данные для сериализатора
        order_data = {
            'first_name': request.data.get('first_name', ''),
            'last_name': request.data.get('last_name', ''),
            'email': request.data.get('email', ''),
            'phone': request.data.get('phone', ''),
            'address': request.data.get('address', ''),
            'items': [
                {
                    'sneaker': item.sneaker.id,
                    'quantity': item.quantity
                }
                for item in cart_items
            ]
        }
        
        serializer = OrderCreateSerializer(data=order_data, context=self.get_serializer_context())
        
        if serializer.is_valid():
            order = self.perform_create(serializer)
            return Response(OrderDetailSerializer(order).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 