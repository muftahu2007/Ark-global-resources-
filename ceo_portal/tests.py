import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from ark_catalog.models import Product, Category, SourcingRequest, Inquiry
from ceo_portal.models import SecurityLog

@pytest.fixture
def ceo_user():
    return User.objects.create_superuser('ceo', 'ceo@example.com', 'password123')

@pytest.fixture
def normal_user():
    return User.objects.create_user('user', 'user@example.com', 'password123')

@pytest.fixture
def setup_data():
    category = Category.objects.create(name='Vault', slug='vault')
    Product.objects.create(name='Asset 1', category=category, sku='SKU123', description='Test')
    Inquiry.objects.create(customer_name='Lead 1', email='lead1@example.com')
    SourcingRequest.objects.create(customer_name='Source 1', email='source1@example.com', asset_class='Car')
    SecurityLog.objects.create(ip_address='127.0.0.1', attempted_username='admin')
    return category

@pytest.mark.django_db
class TestCEOPortalAuth:
    def test_ceo_login_get(self, client):
        User.objects.create_superuser('ceo', 'ceo@example.com', 'password123')
        url = reverse('ceo_login')
        response = client.get(url)
        assert response.status_code == 200
        assert 'ceo_portal/auth/login.html' in [t.name for t in response.templates]

    def test_ceo_login_post_valid(self, client, ceo_user):
        url = reverse('ceo_login')
        response = client.post(url, {'username': 'ceo', 'password': 'password123'})
        assert response.status_code == 302
        assert response.url == reverse('ceo_dashboard')

    def test_ceo_login_post_invalid(self, client, ceo_user):
        url = reverse('ceo_login')
        response = client.post(url, {'username': 'ceo', 'password': 'wrong'})
        assert response.status_code == 200  # Stays on login
        
    def test_ceo_login_post_not_superuser(self, client, normal_user):
        User.objects.create_superuser('ceo', 'ceo@example.com', 'password123') # Ensure a superuser exists so we don't redirect to signup
        url = reverse('ceo_login')
        response = client.post(url, {'username': 'user', 'password': 'password123'})
        assert response.status_code == 302
        assert response.url == reverse('ceo_login')

    def test_ceo_logout(self, client, ceo_user):
        client.force_login(ceo_user)
        url = reverse('ceo_logout')
        response = client.get(url)
        assert response.status_code == 302
        assert response.url == reverse('catalog')

@pytest.mark.django_db
class TestCEOPortalProtectedViews:
    def test_dashboard_unauthenticated(self, client):
        url = reverse('ceo_dashboard')
        response = client.get(url)
        assert response.status_code == 302
        assert reverse('ceo_login') in response.url

    def test_dashboard_authenticated(self, client, ceo_user, setup_data):
        client.force_login(ceo_user)
        url = reverse('ceo_dashboard')
        response = client.get(url)
        assert response.status_code == 200
        assert 'product_count' in response.context
        assert 'ceo_portal/dashboard.html' in [t.name for t in response.templates]

    def test_inventory_list(self, client, ceo_user, setup_data):
        client.force_login(ceo_user)
        url = reverse('ceo_inventory')
        response = client.get(url)
        assert response.status_code == 200
        assert len(response.context['products']) == 1

    def test_add_asset_get(self, client, ceo_user):
        client.force_login(ceo_user)
        url = reverse('ceo_add_asset')
        response = client.get(url)
        assert response.status_code == 200
        
    def test_add_asset_post_valid(self, client, ceo_user, setup_data):
        client.force_login(ceo_user)
        url = reverse('ceo_add_asset')
        image = SimpleUploadedFile("file.jpg", b"file_content", content_type="image/jpeg")
        data = {
            'name': 'New Asset',
            'category': setup_data.id,
            'sku': 'SKU456',
            'image': image
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert Product.objects.count() == 2

    def test_edit_asset(self, client, ceo_user, setup_data):
        client.force_login(ceo_user)
        product = Product.objects.first()
        url = reverse('ceo_edit_asset', kwargs={'pk': product.pk})
        response = client.post(url, {'name': 'Updated Asset', 'sku': 'SKU123', 'category': setup_data.id, 'description': 'Updated'})
        assert response.status_code == 302
        product.refresh_from_db()
        assert product.name == 'Updated Asset'

    def test_delete_asset(self, client, ceo_user, setup_data):
        client.force_login(ceo_user)
        product = Product.objects.first()
        url = reverse('ceo_delete_asset', kwargs={'pk': product.pk})
        response = client.post(url) # Assuming post or get doesn't matter, typically it should be POST but view accepts both
        assert Product.objects.count() == 0
        
    def test_threat_console(self, client, ceo_user, setup_data):
        client.force_login(ceo_user)
        url = reverse('ceo_threats')
        response = client.get(url)
        assert response.status_code == 200
        assert len(response.context['logs']) == 1
        
    def test_resolve_threat(self, client, ceo_user, setup_data):
        client.force_login(ceo_user)
        log = SecurityLog.objects.first()
        url = reverse('ceo_resolve_threat', kwargs={'pk': log.pk})
        client.post(url)
        log.refresh_from_db()
        assert log.resolved is True

    def test_sourcing_list(self, client, ceo_user, setup_data):
        client.force_login(ceo_user)
        url = reverse('ceo_sourcing_list')
        response = client.get(url)
        assert response.status_code == 200
        assert len(response.context['requests']) == 1

    def test_decoy_admin(self, client):
        url = reverse('decoy_admin')
        response = client.post(url, {'username': 'admin', 'password': '123'})
        assert response.status_code == 200
        assert SecurityLog.objects.count() == 1
