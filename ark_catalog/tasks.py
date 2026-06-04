import os
from io import BytesIO
from PIL import Image
from django.core.files import File

def optimize_product_image_task(product_id):
    # Import locally to avoid circular imports during setup
    from .models import Product
    
    try:
        product = Product.objects.get(id=product_id)
        if not product.image:
            return "No image to optimize"
            
        img = Image.open(product.image)
        
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
        filename = os.path.basename(product.image.name)
        filename_no_ext = os.path.splitext(filename)[0]
        
        if not filename_no_ext.endswith('_optimized'):
            new_filename = f"{filename_no_ext}_optimized.jpg"
            
            product.image = File(output, name=new_filename)
            product.save(update_fields=['image'])
            
        return f"Successfully optimized image for {product.name}"
    except Exception as e:
        return f"Failed to optimize image for product {product_id}: {str(e)}"
