from rest_framework import serializers
from api.models import Favorite
from .sneaker_serializers import SneakerSerializer


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для избранных товаров.
    """
    sneaker = SneakerSerializer(read_only=True)
    
    class Meta:
        model = Favorite
        fields = ['id', 'sneaker', 'added_at']
        read_only_fields = ['id', 'added_at']


class FavoriteCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления товара в избранное.
    """
    class Meta:
        model = Favorite
        fields = ['sneaker']


class FavoriteCheckSerializer(serializers.Serializer):
    """
    Сериализатор для проверки наличия товара в избранном.
    """
    sneaker_id = serializers.IntegerField()
    is_favorite = serializers.BooleanField(read_only=True) 