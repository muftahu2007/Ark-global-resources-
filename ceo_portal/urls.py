from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='ceo_dashboard'),
    path('auth/signup/', views.ceo_signup, name='ceo_signup'),
    path('auth/login/', views.ceo_login, name='ceo_login'),
    path('auth/logout/', views.ceo_logout, name='ceo_logout'),
    
    # Password Reset
    path('auth/password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html'
    ), name='password_reset'),
    path('auth/password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('auth/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('auth/reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),

    path('inventory/', views.inventory_list, name='ceo_inventory'),
    path('inventory/add/', views.add_asset, name='ceo_add_asset'),
    path('inventory/bulk-add/', views.bulk_add_assets, name='ceo_bulk_add_assets'),
    path('inventory/bulk-delete/', views.bulk_delete_assets, name='ceo_bulk_delete_assets'),
    path('inventory/edit/<int:pk>/', views.edit_asset, name='ceo_edit_asset'),
    path('inventory/delete/<int:pk>/', views.delete_asset, name='ceo_delete_asset'),
    path('inventory/toggle/<int:pk>/', views.toggle_availability, name='ceo_toggle_availability'),
    path('inventory/<slug:category_slug>/', views.inventory_list, name='ceo_inventory_category'),
    path('leads/', views.lead_tracker, name='ceo_leads'),
    path('leads/delete/<int:pk>/', views.lead_delete, name='ceo_lead_delete'),
    path('threats/', views.threat_console, name='ceo_threats'),
    path('threats/resolve/<int:pk>/', views.resolve_threat, name='ceo_resolve_threat'),
    path('threats/purge/', views.purge_threats, name='ceo_purge_threats'),
    path('settings/', views.ceo_settings, name='ceo_settings'),
    path('settings/category/add/', views.add_category, name='ceo_add_category'),
    path('settings/category/edit/<int:pk>/', views.edit_category, name='ceo_edit_category'),
    path('settings/category/delete/<int:pk>/', views.delete_category, name='ceo_delete_category'),
    path('sourcing/', views.sourcing_list, name='ceo_sourcing_list'),
    path('sourcing/<int:pk>/', views.sourcing_detail, name='ceo_sourcing_detail'),
    path('sourcing/delete/<int:pk>/', views.sourcing_delete, name='ceo_sourcing_delete'),
    path('leads/dossier/<int:pk>/', views.lead_dossier_print, name='ceo_lead_dossier_print'),
    path('sourcing/dossier/<int:pk>/', views.sourcing_dossier_print, name='ceo_sourcing_dossier_print'),
    path('help/', views.ceo_help, name='ceo_help'),
]
