from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Product, Category

@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def invalidate_product_cache(sender, instance, **kwargs):
    cache.delete('public_catalog_categories')
    # Use pattern matching or explicit clearing if we cache individual categories
    # For simplicity, we can just call cache.clear() which is very safe for this app 
    # to ensure all product lists and fleet lists are refreshed.
    cache.clear()

@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def invalidate_category_cache(sender, instance, **kwargs):
    cache.delete('public_catalog_categories')
    cache.clear()
