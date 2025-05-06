from rest_framework import serializers
from api.models import Sneaker
from django.conf import settings


class SneakerSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Sneaker (кроссовки).
    """
    image_url = serializers.SerializerMethodField()
    imageUrl = serializers.SerializerMethodField()  # Дублируем поле в camelCase для React
    
    class Meta:
        model = Sneaker
        fields = [
            'id', 'title', 'price', 'image', 'image_url', 'imageUrl', 'description', 
            'available', 'slug', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_image_url(self, obj):
        """
        Возвращает полный URL для изображения
        """
        if obj.image:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            else:
                # Если нет request, используем домен из настроек
                return f"http://localhost:8000{obj.image.url}"
        if obj.image_url:
            # Если это уже полный URL, возвращаем как есть
            if obj.image_url.startswith('http'):
                return obj.image_url
            # Иначе добавляем домен
            return f"http://localhost:8000{obj.image_url}"
        return None
    
    def get_imageUrl(self, obj):
        """
        Дублирует get_image_url для совместимости с React (camelCase)
        """
        return self.get_image_url(obj)


class SneakerListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка кроссовок (с меньшим количеством полей).
    """
    image_url = serializers.SerializerMethodField()
    imageUrl = serializers.SerializerMethodField()  # Дублируем поле в camelCase для React
    
    class Meta:
        model = Sneaker
        fields = ['id', 'title', 'price', 'image_url', 'imageUrl', 'available']
        read_only_fields = ['id']
    
    def get_image_url(self, obj):
        """
        Возвращает полный URL для изображения
        """
        if obj.image:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            else:
                # Если нет request, используем домен из настроек
                return f"http://localhost:8000{obj.image.url}"
        if obj.image_url:
            # Если это уже полный URL, возвращаем как есть
            if obj.image_url.startswith('http'):
                return obj.image_url
            # Иначе добавляем домен
            return f"http://localhost:8000{obj.image_url}"
        return None
    
    def get_imageUrl(self, obj):
        """
        Дублирует get_image_url для совместимости с React (camelCase)
        """
        return self.get_image_url(obj)


class SneakerDetailSerializer(serializers.ModelSerializer):
    """
    Расширенный сериализатор для детальной информации о кроссовках.
    """
    image_url = serializers.SerializerMethodField()
    imageUrl = serializers.SerializerMethodField()  # Дублируем поле в camelCase для React
    
    class Meta:
        model = Sneaker
        fields = [
            'id', 'title', 'price', 'image', 'image_url', 'imageUrl', 'description', 
            'available', 'slug', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_image_url(self, obj):
        """
        Возвращает полный URL для изображения
        """
        if obj.image:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            else:
                # Если нет request, используем домен из настроек
                return f"http://localhost:8000{obj.image.url}"
        if obj.image_url:
            # Если это уже полный URL, возвращаем как есть
            if obj.image_url.startswith('http'):
                return obj.image_url
            # Иначе добавляем домен
            return f"http://localhost:8000{obj.image_url}"
        return None
    
    def get_imageUrl(self, obj):
        """
        Дублирует get_image_url для совместимости с React (camelCase)
        """
        return self.get_image_url(obj)


class SneakerCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления кроссовок.
    """
    class Meta:
        model = Sneaker
        fields = ['title', 'price', 'image', 'description', 'available'] 