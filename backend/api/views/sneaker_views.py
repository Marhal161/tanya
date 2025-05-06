from rest_framework import viewsets, permissions
from api.models import Sneaker
from api.serializers.sneaker_serializers import (
    SneakerSerializer, 
    SneakerListSerializer, 
    SneakerDetailSerializer,
    SneakerCreateUpdateSerializer
)
from rest_framework.parsers import MultiPartParser, FormParser


class SneakerViewSet(viewsets.ModelViewSet):
    """
    ViewSet для отображения и управления кроссовками.
    
    Позволяет получать список кроссовок, отдельную пару, создавать,
    обновлять и удалять товары (только для администраторов).
    """
    queryset = Sneaker.objects.filter(available=True)
    serializer_class = SneakerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]  # Для обработки загрузки файлов
    
    def get_serializer_context(self):
        """
        Добавляем request в контекст сериализатора для генерации полных URL
        """
        context = super().get_serializer_context()
        return context
    
    def get_serializer_class(self):
        """
        Возвращает соответствующий сериализатор в зависимости от действия.
        """
        if self.action == 'list':
            return SneakerListSerializer
        elif self.action == 'retrieve':
            return SneakerDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return SneakerCreateUpdateSerializer
        return SneakerSerializer
    
    def get_permissions(self):
        """
        Изменять данные могут только администраторы.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()
    
    def get_queryset(self):
        """
        Получаем кроссовки с возможностью фильтрации.
        """
        queryset = Sneaker.objects.filter(available=True)
        
        # Фильтрация по минимальной цене
        min_price = self.request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        
        # Фильтрация по максимальной цене
        max_price = self.request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Поиск по названию
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)
            
        return queryset 