from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Category

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'daily'

    def items(self):
        return ['catalog', 'fleet_management', 'private_sourcing', 'about', 'inquiry_form']

    def location(self, item):
        return reverse(item)

class CategorySitemap(Sitemap):
    priority = 0.9
    changefreq = 'daily'

    def items(self):
        return Category.objects.all()

    def location(self, item):
        return reverse('category_products', kwargs={'category': item.slug})
