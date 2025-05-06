from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.core.files.storage import default_storage
import os
import uuid
from django.conf import settings

# Create your models here.

def sneaker_image_path(instance, filename):
    """Функция для определения пути загрузки изображения"""
    # Получаем расширение файла
    ext = filename.split('.')[-1]
    # Формируем имя файла на основе slug и случайного UUID для уникальности
    filename = f"{instance.slug}-{uuid.uuid4()}.{ext}"
    # Возвращаем путь для сохранения
    return os.path.join('sneakers', filename)

class Sneaker(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image_url = models.URLField(blank=True, null=True, verbose_name="URL изображения")
    image = models.ImageField(upload_to=sneaker_image_path, blank=True, null=True, verbose_name="Изображение")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    available = models.BooleanField(default=True, verbose_name="В наличии")
    slug = models.SlugField(max_length=255, blank=True, unique=True, verbose_name="URL-slug")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Кроссовки"
        verbose_name_plural = "Кроссовки"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Автоматически генерируем slug при создании
        if not self.slug:
            self.slug = slugify(self.title)
            # Если slug уже существует, добавляем случайное число
            if Sneaker.objects.filter(slug=self.slug).exists():
                self.slug = f"{self.slug}-{uuid.uuid4().hex[:6]}"
        
        # Если изображение загружено, сохраняем его URL
        if self.image and not self.image_url:
            self.image_url = self.get_image_url()
        
        super(Sneaker, self).save(*args, **kwargs)
    
    def get_image_url(self):
        if self.image:
            return self.image.url
        return self.image_url
    
    def delete(self, *args, **kwargs):
        # Удаляем файл изображения при удалении записи
        if self.image:
            if os.path.isfile(self.image.path):
                default_storage.delete(self.image.path)
        super(Sneaker, self).delete(*args, **kwargs)


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Пользователь")
    session_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID сессии")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
    
    def __str__(self):
        return f"Корзина {self.user.username if self.user else self.session_id}"
    
    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE, verbose_name="Корзина")
    sneaker = models.ForeignKey(Sneaker, on_delete=models.CASCADE, verbose_name="Кроссовки")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    
    class Meta:
        verbose_name = "Товар в корзине"
        verbose_name_plural = "Товары в корзине"
        unique_together = ['cart', 'sneaker']
    
    def __str__(self):
        return f"{self.sneaker.title} ({self.quantity}) в корзине {self.cart}"
    
    @property
    def total_price(self):
        return self.sneaker.price * self.quantity


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Пользователь")
    session_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID сессии")
    sneaker = models.ForeignKey(Sneaker, on_delete=models.CASCADE, verbose_name="Кроссовки")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    
    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        unique_together = [['user', 'sneaker'], ['session_id', 'sneaker']]
    
    def __str__(self):
        return f"{self.sneaker.title} в избранном у {self.user.username if self.user else self.session_id}"


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'В обработке'),
        ('paid', 'Оплачено'),
        ('shipped', 'Отправлено'),
        ('delivered', 'Доставлено'),
        ('canceled', 'Отменено'),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Пользователь")
    session_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID сессии")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    address = models.TextField(verbose_name="Адрес доставки")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая сумма")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заказ №{self.id} от {self.created_at.strftime('%d.%m.%Y')}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name="Заказ")
    sneaker = models.ForeignKey(Sneaker, on_delete=models.CASCADE, verbose_name="Кроссовки")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    
    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказе"
    
    def __str__(self):
        return f"{self.sneaker.title} ({self.quantity}) в заказе №{self.order.id}"
    
    @property
    def total_price(self):
        return self.price * self.quantity


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Пользователь")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон")
    address = models.TextField(blank=True, null=True, verbose_name="Адрес")
    
    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"
    
    def __str__(self):
        return f"Профиль пользователя {self.user.username}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
