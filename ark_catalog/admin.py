from django.contrib import admin
from .models import Product, Inquiry, Category, SourcingRequest

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_available', 'created_at')
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_available',)

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'phone', 'email', 'created_at')
    readonly_fields = ('created_at',)
    list_filter = ('created_at',)
    search_fields = ('customer_name', 'phone', 'email', 'message')
    
    # Show products requested in the admin detail view
    filter_horizontal = ('items_requested',)

@admin.register(SourcingRequest)
class SourcingRequestAdmin(admin.ModelAdmin):
    list_display = ('tracking_code', 'customer_name', 'email', 'asset_class', 'status', 'created_at')
    readonly_fields = ('tracking_code', 'created_at', 'updated_at')
    list_filter = ('status', 'asset_class', 'created_at')
    search_fields = ('tracking_code', 'customer_name', 'email', 'phone', 'details', 'broker_notes')
    ordering = ('-created_at',)

