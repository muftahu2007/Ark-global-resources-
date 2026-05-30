from django.db import models
from django.utils.text import slugify
from django.core.files import File
from io import BytesIO
from PIL import Image, ImageFile
import os

# Fix for "image file is truncated" errors on large bulk uploads
ImageFile.LOAD_TRUNCATED_IMAGES = True

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to='products/')
    description = models.TextField()
    sku = models.CharField(max_length=50, unique=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        # Image Optimization Engine
        if self.image:
            is_new_image = False
            if self.pk is None:
                is_new_image = True
            else:
                try:
                    old_obj = Product.objects.get(pk=self.pk)
                    if old_obj.image != self.image:
                        is_new_image = True
                except Product.DoesNotExist:
                    is_new_image = True

            if is_new_image:
                img = Image.open(self.image)
                
                # Enforce consistent color mode
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Cinematic resizing (Max 1600px width/height for high-res web displays)
                max_size = (1600, 1600)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Compress and format
                output = BytesIO()
                img.save(output, format='JPEG', quality=85, optimize=True)
                output.seek(0)
                
                # Extract filename without extension
                filename = os.path.splitext(self.image.name)[0]
                new_filename = f"{filename}_optimized.jpg"
                
                # Replace the image file
                self.image = File(output, name=new_filename)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Inquiry(models.Model):
    customer_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
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
