from django.contrib import admin
from .models import ClothingItem

@admin.register(ClothingItem)
class ClothingItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'sold', 'is_featured', 'posted_at')
    list_filter = ('category', 'sold', 'is_featured')
    search_fields = ('title', 'description')
    list_editable = ('is_featured',)

