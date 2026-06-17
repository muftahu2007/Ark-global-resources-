from django.db import models
from django.utils.text import slugify
from django.core.files import File
from io import BytesIO
from PIL import Image, ImageFile
import os
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

# Fix for "image file is truncated" errors on large bulk uploads
ImageFile.LOAD_TRUNCATED_IMAGES = True

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    poster_image = models.ImageField(upload_to='categories/', blank=True, null=True, help_text='Optional: Pin a custom poster image to this category card on the main portal page.')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Product(models.Model):
    PRICE_UNIT_CHOICES = [
        ('per piece',  'Per Piece'),
        ('per yard',   'Per Yard'),
        ('per set',    'Per Set'),
        ('per pair',   'Per Pair')
    ]


    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to='products/')
    description = models.TextField()
    sku = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(
        max_digits=14, decimal_places=2,
        null=True, blank=True,
        help_text='Price in Nigerian Naira (₦). Leave blank to hide pricing.'
    )
    price_unit = models.CharField(
        max_length=20, choices=PRICE_UNIT_CHOICES,
        default='per piece', blank=True,
        help_text='Unit of measurement for the quoted price.'
    )
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        # Determine if image optimization is needed
        is_new_image = False
        update_fields = kwargs.get('update_fields', None)
        
        # If we are only updating specific fields (like from the async task itself), skip optimization check
        if update_fields and 'image' in update_fields:
            super().save(*args, **kwargs)
            return

        if self.image:
            if self.pk is None:
                is_new_image = True
            else:
                try:
                    old_obj = Product.objects.get(pk=self.pk)
                    if old_obj.image != self.image:
                        is_new_image = True
                except Product.DoesNotExist:
                    is_new_image = True

        super().save(*args, **kwargs)

        if is_new_image:
            from django_q.tasks import async_task
            async_task('ark_catalog.tasks.optimize_product_image_task', self.pk)

    def __str__(self):
        return self.name

class Inquiry(models.Model):
    customer_name = models.CharField(max_length=200)
    email = models.EmailField()
    country = CountryField(blank=True, null=True)
    phone = PhoneNumberField(blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    lga = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    full_address = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField(blank=True)
    items_requested = models.ManyToManyField(Product, related_name='inquiries')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Inquiries"

    def __str__(self):
        return f"Inquiry from {self.customer_name} - {self.created_at.strftime('%Y-%m-%d')}"

class SourcingRequest(models.Model):
    STATUS_CHOICES = [
        ('Received', 'Request Received'),
        ('Researching', 'Market Researching'),
        ('Inspecting', 'Inspecting Assets'),
        ('Secured', 'Asset Secured'),
        ('Acquired', 'Acquired & Delivered'),
        ('Cancelled', 'Cancelled/Archived'),
    ]
    tracking_code = models.CharField(max_length=20, unique=True, editable=False)
    customer_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    asset_class = models.CharField(max_length=100)
    budget = models.CharField(max_length=100)
    timeline = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Received')
    broker_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            import uuid
            self.tracking_code = f"ARK-SRC-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.tracking_code} - {self.customer_name} ({self.status})"
