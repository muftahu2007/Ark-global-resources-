import pytest
from django.urls import reverse
from django.core.cache import cache
from ark_catalog.models import Product, Category, SourcingRequest, Inquiry

@pytest.fixture
def setup_data():
    category = Category.objects.create(name='Cars', slug='cars')
    from django.core.files.uploadedfile import SimpleUploadedFile
    image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
    Product.objects.create(name='Test Car', category=category, is_available=True, price=100.0, description='Test', sku='SKU1', image=image)
    Product.objects.create(name='Hidden Car', category=category, is_available=False, price=200.0, description='Test', sku='SKU2', image=image)
    return category

@pytest.mark.django_db
class TestArkCatalogViews:
    
    def test_product_list_view(self, client, setup_data):
        url = reverse('catalog')
        response = client.get(url)
        assert response.status_code == 200
        assert 'ark_catalog/catalog.html' in [t.name for t in response.templates]
        assert 'categories' in response.context
        # Check cache
        assert cache.get('public_catalog_categories') is not None
        
    def test_category_product_view_valid(self, client, setup_data):
        url = reverse('category_products', kwargs={'category': 'cars'})
        response = client.get(url)
        assert response.status_code == 200
        assert 'ark_catalog/category_products.html' in [t.name for t in response.templates]
        assert len(response.context['products']) == 1  # Only available ones
        assert response.context['category_name'] == 'Cars'
        
    def test_category_product_view_invalid(self, client):
        url = reverse('category_products', kwargs={'category': 'nonexistent'})
        response = client.get(url)
        assert response.status_code == 404
        
    def test_fleet_management_view(self, client, setup_data):
        url = reverse('fleet_management')
        response = client.get(url)
        assert response.status_code == 200
        assert 'ark_catalog/fleet.html' in [t.name for t in response.templates]
        assert len(response.context['fleet_cars']) == 1
        
    def test_toggle_selection_view_add_remove(self, client, setup_data):
        product = Product.objects.first()
        url = reverse('toggle_selection', kwargs={'product_id': product.id})
        
        # Add
        response = client.post(url, {'action': 'add'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        assert response.status_code == 200
        assert response.json()['status'] == 'added'
        assert str(product.id) in client.session['selection']
        
        # Remove
        response = client.post(url, {'action': 'remove'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        assert response.status_code == 200
        assert response.json()['status'] == 'removed'
        assert str(product.id) not in client.session['selection']
        
    def test_inquiry_form_get(self, client, setup_data):
        url = reverse('inquiry_form')
        response = client.get(url)
        assert response.status_code == 200
        assert 'ark_catalog/inquiry_form.html' in [t.name for t in response.templates]
        
    def test_inquiry_form_post_empty_selection(self, client):
        url = reverse('inquiry_form')
        data = {
            'customer_name': 'John Doe',
            'email': 'john@example.com',
            'message': 'Test'
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert response.url == reverse('catalog')
        
    def test_inquiry_form_post_valid_selection(self, client, setup_data):
        product = Product.objects.first()
        session = client.session
        session['selection'] = [str(product.id)]
        session.save()
        
        url = reverse('inquiry_form')
        data = {
            'customer_name': 'John Doe',
            'email': 'john@example.com',
            'message': 'Test',
            'method': 'whatsapp'
        }
        response = client.post(url, data)
        assert response.status_code == 200
        assert 'ark_catalog/success.html' in [t.name for t in response.templates]
        
        # Check if inquiry created
        assert Inquiry.objects.count() == 1
        
    def test_private_sourcing_get(self, client):
        url = reverse('private_sourcing')
        response = client.get(url)
        assert response.status_code == 200
        assert 'ark_catalog/sourcing.html' in [t.name for t in response.templates]
        
    def test_private_sourcing_post(self, client):
        url = reverse('private_sourcing')
        data = {
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'asset_type': 'Private Jet',
            'budget': '10M',
            'timeline': 'ASAP',
            'method': 'whatsapp'
        }
        response = client.post(url, data)
        assert response.status_code == 200
        assert 'ark_catalog/success.html' in [t.name for t in response.templates]
        assert SourcingRequest.objects.count() == 1
        
    def test_sourcing_track_get(self, client):
        url = reverse('sourcing_track')
        response = client.get(url)
        assert response.status_code == 200
        assert 'ark_catalog/sourcing_track.html' in [t.name for t in response.templates]
        
    def test_sourcing_track_post_valid(self, client):
        sr = SourcingRequest.objects.create(email='test@example.com')
        url = reverse('sourcing_track')
        response = client.post(url, {'email': sr.email, 'tracking_code': sr.tracking_code})
        assert response.status_code == 200
        assert response.context['sourcing_request'] == sr
        
    def test_sourcing_track_post_invalid(self, client):
        url = reverse('sourcing_track')
        response = client.post(url, {'email': 'invalid@test.com', 'tracking_code': 'WRONG'})
        assert response.status_code == 200
        assert 'sourcing_request' not in response.context
        
    def test_about_us_view(self, client):
        url = reverse('about')
        response = client.get(url)
        assert response.status_code == 200
        assert 'ark_catalog/about.html' in [t.name for t in response.templates]

    def test_check_disk_space(self, client):
        url = reverse('check_disk')
        response = client.get(url)
        assert response.status_code == 200
