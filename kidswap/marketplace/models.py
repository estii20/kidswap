from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class ClothingItem(models.Model):
    CATEGORY_CHOICES = [
        ('tops', 'Tops'),
        ('bottoms', 'Bottoms'),
        ('shoes', 'Shoes'),
        ('outerwear', 'Outerwear'),
        ('accessories', 'Accessories'),
    ]

    CONDITION_CHOICES = [
        ('new', 'New with tags'),
        ('like_new', 'Like New'),
        ('gently_used', 'Gently Used'),
        ('worn', 'Worn'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    size = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='item_images/')
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    posted_at = models.DateTimeField(auto_now_add=True)
    sold = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(ClothingItem, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.title} in {self.user.username}'s cart"


class ItemImage(models.Model):
    item = models.ForeignKey(ClothingItem, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='item_images/')

    def __str__(self):
        return f"Image for {self.item.title}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"