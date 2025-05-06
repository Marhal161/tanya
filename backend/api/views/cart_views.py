from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from api.models import Cart, CartItem, Sneaker
from api.serializers.cart_serializers import CartSerializer, CartItemCreateSerializer, CartItemUpdateSerializer


class BaseCartViewSet(viewsets.ViewSet):
    """
    Базовый ViewSet с общей функциональностью для работы с корзиной.
    """
    
    def get_serializer_context(self):
        return {'request': self.request}
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """
        Добавление товара в корзину.
        """
        cart = self.get_cart(request)
        serializer = CartItemCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            sneaker = serializer.validated_data['sneaker']
            quantity = serializer.validated_data.get('quantity', 1)
            
            # Проверяем, есть ли уже такой товар в корзине
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                sneaker=sneaker,
                defaults={'quantity': quantity}
            )
            
            # Если товар уже есть, обновляем количество
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            return Response(CartSerializer(cart).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def update_item(self, request):
        """
        Обновление количества товара в корзине.
        """
        cart = self.get_cart(request)
        serializer = CartItemUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            sneaker_id = serializer.validated_data['sneaker_id']
            quantity = serializer.validated_data['quantity']
            
            try:
                cart_item = CartItem.objects.get(cart=cart, sneaker_id=sneaker_id)
                
                if quantity <= 0:
                    cart_item.delete()
                else:
                    cart_item.quantity = quantity
                    cart_item.save()
                
                return Response(CartSerializer(cart).data)
            except CartItem.DoesNotExist:
                return Response(
                    {'error': 'Товар не найден в корзине'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """
        Удаление товара из корзины.
        """
        cart = self.get_cart(request)
        sneaker_id = request.data.get('sneaker_id')
        
        if not sneaker_id:
            return Response(
                {'error': 'Необходимо указать ID товара'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart_item = CartItem.objects.get(cart=cart, sneaker_id=sneaker_id)
            cart_item.delete()
            
            return Response(CartSerializer(cart).data)
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Товар не найден в корзине'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """
        Очистка корзины.
        """
        cart = self.get_cart(request)
        CartItem.objects.filter(cart=cart).delete()
        
        return Response(CartSerializer(cart).data)


class CartViewSet(BaseCartViewSet):
    """
    ViewSet для работы с корзиной авторизованного пользователя.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_cart(self, request):
        """
        Получаем или создаем корзину для авторизованного пользователя.
        """
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart
    
    def list(self, request):
        """
        Получение корзины пользователя.
        """
        cart = self.get_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class AnonymousCartViewSet(BaseCartViewSet):
    """
    ViewSet для работы с корзиной анонимного пользователя.
    """
    
    def get_cart(self, request):
        """
        Получаем или создаем корзину для анонимного пользователя по ID сессии.
        """
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        
        cart, _ = Cart.objects.get_or_create(session_id=session_id)
        return cart
    
    def list(self, request):
        """
        Получение корзины анонимного пользователя.
        """
        cart = self.get_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data) 