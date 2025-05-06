from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from api.models import Favorite, Sneaker
from api.serializers.favorite_serializers import FavoriteSerializer, FavoriteCreateSerializer


class BaseFavoriteViewSet(viewsets.ViewSet):
    """
    Базовый ViewSet с общей функциональностью для работы с избранным.
    """
    
    def get_serializer_context(self):
        return {'request': self.request}
    
    @action(detail=False, methods=['post'])
    def add(self, request):
        """
        Добавление товара в избранное.
        """
        serializer = FavoriteCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            sneaker = serializer.validated_data['sneaker']
            
            # Получаем данные пользователя или сессии
            user, session_id = self.get_user_or_session(request)
            
            # Проверяем, есть ли уже такой товар в избранном
            favorite, created = Favorite.objects.get_or_create(
                user=user,
                session_id=session_id,
                sneaker=sneaker
            )
            
            if created:
                return Response({'status': 'Товар добавлен в избранное'})
            return Response({'status': 'Товар уже в избранном'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def remove(self, request):
        """
        Удаление товара из избранного.
        """
        sneaker_id = request.data.get('sneaker_id')
        
        if not sneaker_id:
            return Response(
                {'error': 'Необходимо указать ID товара'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Получаем данные пользователя или сессии
        user, session_id = self.get_user_or_session(request)
        
        # Формируем фильтр для поиска избранного
        filter_params = {'sneaker_id': sneaker_id}
        if user:
            filter_params['user'] = user
        else:
            filter_params['session_id'] = session_id
        
        try:
            favorite = Favorite.objects.get(**filter_params)
            favorite.delete()
            
            return Response({'status': 'Товар удален из избранного'})
        except Favorite.DoesNotExist:
            return Response(
                {'error': 'Товар не найден в избранном'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def check(self, request):
        """
        Проверка, находится ли товар в избранном.
        """
        sneaker_id = request.query_params.get('sneaker_id')
        
        if not sneaker_id:
            return Response(
                {'error': 'Необходимо указать ID товара'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Получаем данные пользователя или сессии
        user, session_id = self.get_user_or_session(request)
        
        # Формируем фильтр для поиска избранного
        filter_params = {'sneaker_id': sneaker_id}
        if user:
            filter_params['user'] = user
        else:
            filter_params['session_id'] = session_id
        
        is_favorite = Favorite.objects.filter(**filter_params).exists()
        
        return Response({'is_favorite': is_favorite})


class FavoriteViewSet(BaseFavoriteViewSet):
    """
    ViewSet для работы с избранным авторизованного пользователя.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_user_or_session(self, request):
        """
        Возвращает пользователя и None вместо session_id.
        """
        return request.user, None
    
    def list(self, request):
        """
        Получение списка избранных товаров пользователя.
        """
        favorites = Favorite.objects.filter(user=request.user)
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data)


class AnonymousFavoriteViewSet(BaseFavoriteViewSet):
    """
    ViewSet для работы с избранным анонимного пользователя.
    """
    
    def get_user_or_session(self, request):
        """
        Возвращает None вместо пользователя и session_id.
        """
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        
        return None, session_id
    
    def list(self, request):
        """
        Получение списка избранных товаров анонимного пользователя.
        """
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        
        favorites = Favorite.objects.filter(session_id=session_id)
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data) 