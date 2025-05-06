from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from api.models import UserProfile, Cart, Favorite
from api.serializers.user_serializers import UserSerializer, UserProfileSerializer, UserRegistrationSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с пользователями.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        """
        Установка разрешений в зависимости от действия.
        """
        if self.action == 'create':
            return [permissions.AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy', 'profile', 'update_profile']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]
    
    def get_serializer_class(self):
        """
        Выбор сериализатора в зависимости от действия.
        """
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Создание нового пользователя (регистрация).
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Перенос корзины и избранного из сессии в аккаунт пользователя
        session_id = request.session.session_key
        if session_id:
            self._transfer_session_data_to_user(session_id, user)
        
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    
    def _transfer_session_data_to_user(self, session_id, user):
        """
        Переносит данные из сессии (корзина, избранное) в аккаунт пользователя.
        """
        # Перенос корзины
        session_cart = Cart.objects.filter(session_id=session_id).first()
        user_cart, _ = Cart.objects.get_or_create(user=user)
        
        if session_cart:
            for cart_item in session_cart.items.all():
                # Проверяем, есть ли такой товар в корзине пользователя
                user_cart_item = user_cart.items.filter(sneaker=cart_item.sneaker).first()
                if user_cart_item:
                    user_cart_item.quantity += cart_item.quantity
                    user_cart_item.save()
                else:
                    cart_item.cart = user_cart
                    cart_item.save()
            
            # Удаляем корзину сессии
            session_cart.delete()
        
        # Перенос избранного
        session_favorites = Favorite.objects.filter(session_id=session_id)
        for fav in session_favorites:
            # Проверяем, есть ли такой товар в избранном пользователя
            if not Favorite.objects.filter(user=user, sneaker=fav.sneaker).exists():
                fav.user = user
                fav.session_id = None
                fav.save()
            else:
                fav.delete()  # Удаляем дубликат
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def profile(self, request):
        """
        Получение и обновление профиля текущего пользователя.
        """
        user = request.user
        
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data)
        
        serializer = UserSerializer(user, data=request.data, partial=request.method == 'PATCH')
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Обновляем профиль, если есть данные
        profile_data = request.data.get('profile', {})
        if profile_data:
            profile_serializer = UserProfileSerializer(user.profile, data=profile_data, partial=True)
            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save()
        
        return Response(UserSerializer(user).data) 