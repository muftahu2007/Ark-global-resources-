from django.urls import path
from django.views.generic import TemplateView
from .views import ProductListView, CategoryProductView, ToggleSelectionView, InquiryFormView, FleetManagementView, PrivateSourcingView, AboutUsView, SourcingTrackView

urlpatterns = [
    path('', ProductListView.as_view(), name='catalog'),
    path('category/<slug:category>/', CategoryProductView.as_view(), name='category_products'),
    path('toggle-selection/<int:product_id>/', ToggleSelectionView.as_view(), name='toggle_selection'),
    path('inquiry/', InquiryFormView.as_view(), name='inquiry_form'),
    path('fleet-management/', FleetManagementView.as_view(), name='fleet_management'),
    path('private-sourcing/', PrivateSourcingView.as_view(), name='private_sourcing'),
    path('private-sourcing/track/', SourcingTrackView.as_view(), name='sourcing_track'),
    path('about/', AboutUsView.as_view(), name='about'),
]
