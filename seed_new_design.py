import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'global_ark.settings')
django.setup()

from ark_catalog.models import Product

# Clear existing and re-seed with NEW designed categories
Product.objects.all().delete()

items = [
    {
        'name': 'Italian Oxford Executive',
        'category': 'Shoes',
        'sku': 'ARK-SH-NEW-01',
        'image': 'products/shoe.png',
        'description': 'Handcrafted Italian black leather Oxford shoes. Minimalist luxury aesthetic on marble. High-end fashion photography.'
    },
    {
        'name': 'Elite Designer Briefcase',
        'category': 'Bags',
        'sku': 'ARK-BAG-NEW-01',
        'image': 'products/bag.png',
        'description': 'Top-grain black leather designer briefcase with brushed silver hardware. Professional corporate aesthetic.'
    },
    {
        'name': 'Architectural Kitchen Suite',
        'category': 'Kitchen',
        'sku': 'ARK-KIT-NEW-01',
        'image': 'products/kitchen.png',
        'description': 'Ultra-modern kitchen accessories including a matte black espresso machine and stainless steel cookware.'
    },
    {
        'name': 'Titanium Vanguard Smartphone',
        'category': 'Phones',
        'sku': 'ARK-PH-NEW-01',
        'image': 'products/phone.png', # Even if not yet generated, object will be created
        'description': 'Minimalist smartphone with titanium frame and seamless glass display. The pinnacle of high-end mobile tech.'
    }
]

for item in items:
    Product.objects.create(**item)

print("Successfully seeded with NEW luxury designs.")
