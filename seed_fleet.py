import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'global_ark.settings')
django.setup()

from ark_catalog.models import Product

# Clear existing products to ensure clean fleet look
Product.objects.all().delete()

fleet_items = [
    {
        'name': '2024 Toyota Camry Executive',
        'category': 'Cars',
        'sku': 'ARK-FLEET-001',
        'image': 'products/camry.png',
        'description': 'A hyper-realistic, cinematic presentation of the 2024 Toyota Camry Executive Edition. Featuring sleek white exterior styling, parked before a modern luxury glass complex in Lagos. High-end performance meets corporate elegance.'
    },
    {
        'name': 'Premium Atampa Gold-Leaf Fabric',
        'category': 'Fabrics',
        'sku': 'ARK-TEX-002',
        'image': 'products/atampa.png',
        'description': 'Hand-selected premium Atampa African wax fabric. Intricate patterns in gold and deep indigo blue, draped with architectural precision. The pinnacle of West African luxury textiles.'
    },
    {
        'name': 'Italian Leather Corporate Suite',
        'category': 'Shoes',
        'sku': 'ARK-ACC-003',
        'image': 'products/leather_set.png',
        'description': 'A masterclass in minimalist luxury. Professional black leather designer briefcase paired with matching handcrafted Italian corporate shoes. Presented on a pristine marble surface.'
    }
]

for item in fleet_items:
    Product.objects.create(**item)

print("Luxury Fleet successfully docked in the database.")
