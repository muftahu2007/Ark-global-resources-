"""
URL configuration for global_ark project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from ceo_portal import views as ceo_views

urlpatterns = [
    # Decoy Honeypot Door (Traps attacker bots)
    path('admin/', ceo_views.decoy_admin, name='decoy_admin'),
    
    # Real Secret Vault Door (Hides Django Admin)
    path(f"{settings.SECRET_ADMIN_PATH}/", admin.site.urls),
    
    path('', include('ark_catalog.urls')),
    path('ceo-portal/', include('ceo_portal.urls')),
]
    
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
