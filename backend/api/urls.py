from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import (
    SneakerViewSet, CartViewSet, FavoriteViewSet, OrderViewSet,
    AnonymousCartViewSet, AnonymousFavoriteViewSet
)
from api.views.user_views import UserViewSet

# Создаем router для автоматического создания URL
router = DefaultRouter()
router.register(r'sneakers', SneakerViewSet, basename='sneaker')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # Включаем URLs, созданные router'ом
    path('', include(router.urls)),
    
    # Маршруты для авторизованных пользователей
    path('cart/', CartViewSet.as_view({'get': 'list'}), name='cart'),
    path('cart/add/', CartViewSet.as_view({'post': 'add_item'}), name='cart-add'),
    path('cart/update/', CartViewSet.as_view({'post': 'update_item'}), name='cart-update'),
    path('cart/remove/', CartViewSet.as_view({'post': 'remove_item'}), name='cart-remove'),
    path('cart/clear/', CartViewSet.as_view({'post': 'clear'}), name='cart-clear'),
    
    path('favorites/', FavoriteViewSet.as_view({'get': 'list'}), name='favorites'),
    path('favorites/add/', FavoriteViewSet.as_view({'post': 'add'}), name='favorites-add'),
    path('favorites/remove/', FavoriteViewSet.as_view({'post': 'remove'}), name='favorites-remove'),
    path('favorites/check/', FavoriteViewSet.as_view({'get': 'check'}), name='favorites-check'),
    
    # Маршруты для анонимных пользователей
    path('anonymous/cart/', AnonymousCartViewSet.as_view({'get': 'list'}), name='anonymous-cart'),
    path('anonymous/cart/add/', AnonymousCartViewSet.as_view({'post': 'add_item'}), name='anonymous-cart-add'),
    path('anonymous/cart/update/', AnonymousCartViewSet.as_view({'post': 'update_item'}), name='anonymous-cart-update'),
    path('anonymous/cart/remove/', AnonymousCartViewSet.as_view({'post': 'remove_item'}), name='anonymous-cart-remove'),
    path('anonymous/cart/clear/', AnonymousCartViewSet.as_view({'post': 'clear'}), name='anonymous-cart-clear'),
    
    path('anonymous/favorites/', AnonymousFavoriteViewSet.as_view({'get': 'list'}), name='anonymous-favorites'),
    path('anonymous/favorites/add/', AnonymousFavoriteViewSet.as_view({'post': 'add'}), name='anonymous-favorites-add'),
    path('anonymous/favorites/remove/', AnonymousFavoriteViewSet.as_view({'post': 'remove'}), name='anonymous-favorites-remove'),
    path('anonymous/favorites/check/', AnonymousFavoriteViewSet.as_view({'get': 'check'}), name='anonymous-favorites-check'),
    
    # Маршруты для аутентификации (используем djoser)
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    
    # Другие URL-пути
    path('user/profile/', UserViewSet.as_view({'get': 'profile', 'put': 'profile', 'patch': 'profile'}), name='user-profile'),
    path('orders/create-from-cart/', OrderViewSet.as_view({'post': 'create_from_cart'}), name='order-create-from-cart'),
] 