import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'global_ark.settings')
django.setup()

from ark_catalog.models import Product, Category

def cleanup():
    # Car patterns
    car_ids = [
        '1778702738125', '1778702738155', '1778702738187', '1778702738219',
        '1778702738249', '1778702738279', '1778702736097', '1778702738470',
        '1778702736212', '1778702736251', '1778702736290', 'camry'
    ]
    
    # Shoe patterns
    shoe_ids = [
        '1778702737436', '1778702737473', '1778702737512', '1778702737553', 
        '1778702737591', '1778702736137'
    ]
    
    # Bag/Accessory patterns (Watches included)
    bag_ids = [
        '1778702737628', '1778702737665', '1778702737704', '1778702737738',
        '1778702736327', '1778702736362', '1778702736397', '1778702736437'
    ]
    all_products = Product.objects.all()
    count = 0
    
    for p in all_products:
        img_path = str(p.image)
        new_cat_name = None
        
        # Check for cars
        if any(cid in img_path for cid in car_ids):
            new_cat_name = 'Cars'
        # Check for shoes
        elif any(sid in img_path for sid in shoe_ids):
            new_cat_name = 'Shoes'
        # Check for bags
        elif any(bid in img_path for bid in bag_ids):
            new_cat_name = 'Bags'
        
        if new_cat_name:
            cat_obj, _ = Category.objects.get_or_create(name=new_cat_name)
            if p.category != cat_obj:
                print(f"Moving {p.name} from {p.category.name} to {new_cat_name}")
                p.category = cat_obj
                p.save()
                count += 1
            
    print(f"Cleanup complete. Updated {count} products.")

if __name__ == '__main__':
    cleanup()
