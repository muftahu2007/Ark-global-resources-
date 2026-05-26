import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'global_ark.settings')
django.setup()

from ark_catalog.models import Product

# Clear existing and re-seed with all categories
Product.objects.all().delete()

fleet_items = [
    # CARS
    {
        'name': '2024 Toyota Camry Executive',
        'category': 'Cars',
        'sku': 'ARK-FLEET-001',
        'image': 'products/camry.png',
        'description': 'Executive Edition. Sleek white exterior, luxury glass complex backdrop. 8k Cinematic quality.'
    },
    # SHOES
    {
        'name': 'Italian Oxford Corporate',
        'category': 'Shoes',
        'sku': 'ARK-SH-001',
        'image': 'products/leather_set.png',
        'description': 'Handcrafted Italian leather corporate shoes. Minimalist luxury aesthetic on marble.'
    },
    # FABRICS
    {
        'name': 'Atampa Gold-Leaf Wax',
        'category': 'Fabrics',
        'sku': 'ARK-TEX-001',
        'image': 'products/atampa.png',
        'description': 'Premium Atampa luxury African wax fabric. Intricate gold and deep blue patterns.'
    },
    # BAGS
    {
        'name': 'Executive Leather Briefcase',
        'category': 'Bags',
        'sku': 'ARK-BAG-001',
        'image': 'products/leather_set.png',
        'description': 'Professional black leather designer briefcase. Minimalist luxury for global voyagers.'
    }
]

for item in fleet_items:
    Product.objects.create(**item)

print("Full Category Fleet successfully seeded.")
