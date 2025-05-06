from django.contrib import admin
from django.utils.html import format_html
from .models import Sneaker, Cart, CartItem, Favorite, Order, OrderItem, UserProfile

class SneakerAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price', 'image_preview', 'available', 'created_at')
    list_filter = ('available', 'created_at')
    search_fields = ('title', 'description')
    list_editable = ('price', 'available')
    readonly_fields = ('image_preview', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'price', 'image', 'image_preview', 'description')
        }),
        ('Статус', {
            'fields': ('available',)
        }),
        ('Техническая информация', {
            'fields': ('slug', 'image_url'),
            'classes': ('collapse',)
        })
    )
    
    def get_fieldsets(self, request, obj=None):
        """Динамически определяем набор полей в зависимости от создания/редактирования"""
        fieldsets = list(super().get_fieldsets(request, obj))
        
        # Добавляем поля дат только при редактировании существующего объекта
        if obj:  # Если это редактирование существующего объекта
            fieldsets.append(
                ('Даты', {
                    'fields': ('created_at', 'updated_at'),
                    'classes': ('collapse',)
                })
            )
        
        return fieldsets
    
    def image_preview(self, obj):
        """Отображение превью изображения в админке"""
        if obj.image:
            return format_html('<img src="{}" width="100" height="auto" />', obj.image.url)
        elif obj.image_url:
            return format_html('<img src="{}" width="100" height="auto" />', obj.image_url)
        return "Нет изображения"
    
    image_preview.short_description = 'Превью'
    
    def get_readonly_fields(self, request, obj=None):
        """Динамически определяем поля только для чтения"""
        if obj:  # редактирование существующего объекта
            return ('created_at', 'updated_at', 'image_preview')
        # создание нового объекта
        return ('image_preview',)
    
    def save_model(self, request, obj, form, change):
        """Дополнительные действия при сохранении модели"""
        if 'image' in form.changed_data and obj.image:
            # Установить image_url на основе загруженного изображения
            obj.image_url = obj.get_image_url()
        super().save_model(request, obj, form, change)

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('added_at',)
    
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_id', 'items_count', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'session_id')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CartItemInline]
    
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Кол-во товаров'
    
    def total_price(self, obj):
        return sum(item.quantity * item.sneaker.price for item in obj.items.all())
    total_price.short_description = 'Общая сумма'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at', 'total_price')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Покупатель', {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone', 'address')
        }),
        ('Информация о заказе', {
            'fields': ('status', 'total_price')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_id', 'sneaker', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'session_id', 'sneaker__title')
    
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')
    search_fields = ('user__username', 'user__email', 'phone')

# Регистрация моделей в админке
admin.site.register(Sneaker, SneakerAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
