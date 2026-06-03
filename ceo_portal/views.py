from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from ark_catalog.models import Product, Inquiry, Category, SourcingRequest
from .forms import CEOSignupForm
import urllib.parse
from .models import SecurityLog
import time
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
import datetime

def is_ceo(user):
    return user.is_authenticated and user.is_superuser

def ceo_signup(request):
    # Redirect if already logged in as CEO
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('ceo_dashboard')

    # Lock signup if a CEO already exists
    if User.objects.filter(is_superuser=True).exists():
        messages.error(request, "The CEO role has already been claimed.")
        return redirect('ceo_login')
    
    if request.method == 'POST':
        form = CEOSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            login(request, user)
            messages.success(request, "Welcome, CEO. The Vault is now under your command.")
            return redirect('ceo_dashboard')
    else:
        form = CEOSignupForm()
    return render(request, 'ceo_portal/auth/signup.html', {'form': form})

def ceo_login(request):
    # Redirect to signup if no CEO exists in the system
    if not User.objects.filter(is_superuser=True).exists():
        messages.info(request, "No executive authority found. System initialization required.")
        return redirect('ceo_signup')

    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('ceo_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_superuser:
                login(request, user)
                return redirect('ceo_dashboard')
            else:
                messages.error(request, "Access Denied: High-level clearance required.")
                return redirect('ceo_login')
    else:
        form = AuthenticationForm()
    return render(request, 'ceo_portal/auth/login.html', {'form': form})

@login_required
def ceo_logout(request):
    logout(request)
    messages.info(request, "Logged out of CEO Command Center.")
    return redirect('catalog')

@login_required
@user_passes_test(is_ceo, login_url='ceo_login')
def dashboard(request):
    # Analytics: Lead Velocity (Last 14 days)
    from django.db.models import Count
    from django.db.models.functions import TruncDate
    
    today = datetime.date.today()
    fourteen_days_ago = today - datetime.timedelta(days=13)
    
    daily_leads = Inquiry.objects.filter(created_at__date__gte=fourteen_days_ago) \
        .annotate(date=TruncDate('created_at')) \
        .values('date') \
        .annotate(count=Count('id')) \
        .order_by('date')
    
    # Optimized gap filling using a dictionary
    leads_map = {entry['date']: entry['count'] for entry in daily_leads}
    lead_velocity_data = [
        {'date': (fourteen_days_ago + datetime.timedelta(days=i)).strftime('%b %d'),
         'count': leads_map.get(fourteen_days_ago + datetime.timedelta(days=i), 0)}
        for i in range(14)
    ]

    # Analytics: Category Distribution
    category_distribution = Category.objects.annotate(product_count=Count('products')).values('name', 'product_count')

    security_logs = SecurityLog.objects.all().order_by('-timestamp')[:5]
    threat_count = SecurityLog.objects.count()

    context = {
        'product_count': Product.objects.count(),
        'lead_count': Inquiry.objects.count(),
        'threat_count': threat_count,
        'security_logs': security_logs,
        'leads': Inquiry.objects.all().order_by('-created_at')[:5],
        'products': Product.objects.all().order_by('-created_at')[:4],
        'lead_velocity': lead_velocity_data,
        'category_distribution': list(category_distribution),
    }
    return render(request, 'ceo_portal/dashboard.html', context)

@login_required
@user_passes_test(is_ceo, login_url='ceo_login')
def inventory_list(request, category_slug=None):
    categories = Category.objects.all().order_by('name')
    q = request.GET.get('q', '')
    
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=current_category)
    else:
        products = Product.objects.all()
        current_category = None
        
    if q:
        products = products.filter(
            Q(name__icontains=q) | 
            Q(sku__icontains=q) | 
            Q(description__icontains=q)
        )
        
    products = products.order_by('-created_at')
    
    return render(request, 'ceo_portal/inventory.html', {
        'products': products, 
        'current_category': current_category,
        'categories': categories,
        'search_query': q
    })

@login_required
@user_passes_test(is_ceo, login_url='ceo_login')
def toggle_availability(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_available = not product.is_available
    product.save()
    
    # Handle AJAX requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'is_available': product.is_available,
            'product_name': product.name
        })
        
    messages.success(request, f"Status updated for {product.name}.")
    return redirect(request.META.get('HTTP_REFERER', 'ceo_inventory'))

@login_required
@user_passes_test(is_ceo, login_url='ceo_login')
def add_asset(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        new_category_name = request.POST.get('new_category')
        description = request.POST.get('description')
        sku = request.POST.get('sku')
        image = request.FILES.get('image')
        price_raw = request.POST.get('price', '').strip()
        price_unit = request.POST.get('price_unit', 'per piece')

        # Sanitise price – strip currency symbols / commas
        price = None
        if price_raw:
            try:
                price = float(price_raw.replace('₦', '').replace(',', '').replace('#', ''))
            except ValueError:
                price = None

        category = None
        if new_category_name and new_category_name.strip():
            category, _ = Category.objects.get_or_create(name=new_category_name.strip())
        elif category_id and category_id.strip():
            category = get_object_or_404(Category, id=category_id)

        if name and category and sku and image:
            Product.objects.create(
                name=name,
                category=category,
                description=description,
                sku=sku,
                image=image,
                price=price,
                price_unit=price_unit,
            )
            messages.success(request, f"Asset '{name}' successfully secured in the {category.name} Vault.")
            return redirect('ceo_inventory_category', category_slug=category.slug)
        else:
            missing = []
            if not name: missing.append("Designation")
            if not category: missing.append("Vault Directory")
            if not sku: missing.append("SKU")
            if not image: missing.append("Media Attachment")
            messages.error(request, f"Deployment failed. Missing: {', '.join(missing)}")

    categories = Category.objects.all().order_by('name')
    price_unit_choices = Product.PRICE_UNIT_CHOICES
    return render(request, 'ceo_portal/add_asset.html', {
        'categories': categories,
        'price_unit_choices': price_unit_choices,
    })

import uuid
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files import File

@login_required
@user_passes_test(is_ceo, login_url='ceo_login')
def bulk_add_assets(request):
    if request.method == 'POST':
        category_id = request.POST.get('category')
        new_category_name = request.POST.get('new_category')
        images = request.FILES.getlist('images')
        
        category = None
        if new_category_name and new_category_name.strip():
            category, _ = Category.objects.get_or_create(name=new_category_name.strip())
        elif category_id and category_id.strip():
            category = get_object_or_404(Category, id=category_id)

        if category and images:
            success_count = 0
            for image in images:
                try:
                    temp_sku = f"ARK-AUTO-{uuid.uuid4().hex[:8].upper()}"
                    Product.objects.create(
                        name=f"Classified Asset {temp_sku[-6:]}",
                        category=category,
                        description="Asset awaiting executive detailing.",
                        sku=temp_sku,
                        image=image,
                        is_available=False  # Saved as Archived by default
                    )
                    success_count += 1
                except Exception as e:
                    print(f"Error processing upload for {image.name}: {e}")
                    
            if success_count > 0:
                messages.success(request, f"Mass Deployment Complete: {success_count} assets securely added to The Vault.")
            else:
                messages.error(request, "Deployment failed: No assets could be processed.")
                
            return redirect('ceo_inventory_category', category_slug=category.slug)
        else:
            messages.error(request, "Deployment failed. Missing: Vault Directory or Media Attachments.")

    categories = Category.objects.all().order_by('name')
    return render(request, 'ceo_portal/bulk_add_assets.html', {'categories': categories})

@login_required
@user_passes_test(is_ceo, login_url='ceo_login')
def edit_asset(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.name = request.POST.get('name')
        category_id = request.POST.get('category')
        new_category_name = request.POST.get('new_category')
        product.description = request.POST.get('description')

        new_sku = request.POST.get('sku')
        if new_sku:
            product.sku = new_sku

        # Price handling
        price_raw = request.POST.get('price', '').strip()
        price_unit = request.POST.get('price_unit', 'per piece')
        if price_raw:
            try:
                product.price = float(price_raw.replace('₦', '').replace(',', '').replace('#', ''))
            except ValueError:
                product.price = None
        else:
            product.price = None
        product.price_unit = price_unit

        if request.FILES.get('image'):
            product.image = request.FILES.get('image')

        if new_category_name:
            category, _ = Category.objects.get_or_create(name=new_category_name)
            product.category = category
        elif category_id:
            product.category = get_object_or_404(Category, id=category_id)

        product.save()
        messages.success(request, f"Asset '{product.name}' updated.")
        return redirect('ceo_inventory_category', category_slug=product.category.slug)

    categories = Category.objects.all().order_by('name')
    price_unit_choices = Product.PRICE_UNIT_CHOICES
    return render(request, 'ceo_portal/edit_asset.html', {
        'product': product,
        'categories': categories,
        'price_unit_choices': price_unit_choices,
    })

@login_required
@user_passes_test(is_ceo, login_url='ceo_login')
def delete_asset(request, pk):
    product = get_object_or_404(Product, pk=pk)
    category_slug = product.category.slug
    product.delete()
    messages.warning(request, "Asset removed from The Vault.")
    return redirect('ceo_inventory_category', category_slug=category_slug)

@login_required
@user_passes_test(is_ceo, login_url='ceo_login')
def bulk_delete_assets(request):
    if request.method == 'POST':
        product_ids = request.POST.getlist('selected_assets')
        category_slug = request.POST.get('category_slug')
        
        if product_ids:
            count = len(product_ids)
            Product.objects.filter(id__in=product_ids).delete()
            messages.warning(request, f"Mass Purge Complete: {count} assets removed from The Vault.")
        else:
            messages.error(request, "No assets selected for deletion.")
            
        if category_slug:
            return redirect('ceo_inventory_category', category_slug=category_slug)
    
    return redirect('ceo_inventory')

@login_required
@user_passes_test(is_ceo, login_url='ceo_login')
def lead_tracker(request):
    leads = Inquiry.objects.all().order_by('-created_at')
    return render(request, 'ceo_portal/leads.html', {'leads': leads})

@login_required
@user_passes_test(is_ceo, login_url='ceo_login')
def ceo_settings(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'delete_account':
            request.user.delete()
            logout(request)
            messages.warning(request, "CEO account deleted. The portal is now open for a new successor.")
            return redirect('catalog')
    
    categories = Category.objects.all().order_by('name')
    return render(request, 'ceo_portal/settings.html', {'categories': categories})

@login_required
@user_passes_test(is_ceo, login_url='ceo_login')
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.get_or_create(name=name)
            messages.success(request, f"New Portal Directory '{name}' established.")
    return redirect('ceo_settings')

@login_required
@user_passes_test(is_ceo, login_url='ceo_login')
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            category.name = name
            category.save()
            messages.success(request, "Directory refinement complete.")
    return redirect('ceo_settings')

@login_required
@user_passes_test(is_ceo, login_url='ceo_login')
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    name = category.name
    category.delete()
    messages.warning(request, f"Directory '{name}' and all associated assets purged.")
    return redirect('ceo_settings')

def decoy_admin(request):
    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        
        # Determine client IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
            
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        
        # Log intrusion attempt in the decoy, masking the password to prevent accidental credential logging
        masked_password = '*' * len(password) if password else ''
        SecurityLog.objects.create(
            ip_address=ip,
            user_agent=user_agent,
            attempted_username=username,
            attempted_password=masked_password
        )
        
        # Smart Tarpit: Count logs from this IP in the last 15 minutes
        fifteen_mins_ago = timezone.now() - datetime.timedelta(minutes=15)
        consecutive_attempts = SecurityLog.objects.filter(ip_address=ip, timestamp__gte=fifteen_mins_ago).count()
        
        error_message = "Please enter the correct username and password for a staff account. Note that both fields may be case-sensitive."
        
    return render(request, 'ceo_portal/decoy_admin.html', {'error_message': error_message})

@login_required
@user_passes_test(is_ceo, login_url='ceo_login')
def threat_console(request):
    logs = SecurityLog.objects.all().order_by('-timestamp')
    q = request.GET.get('q', '')
    if q:
        logs = logs.filter(
            Q(ip_address__icontains=q) | 
            Q(attempted_username__icontains=q) | 
            Q(user_agent__icontains=q)
        )
    
    status_filter = request.GET.get('status', 'all')
    if status_filter == 'active':
        logs = logs.filter(resolved=False)
    elif status_filter == 'resolved':
        logs = logs.filter(resolved=True)
        
    active_threat_count = SecurityLog.objects.filter(resolved=False).count()
    resolved_threat_count = SecurityLog.objects.filter(resolved=True).count()
    
    return render(request, 'ceo_portal/threats.html', {
        'logs': logs,
        'active_threat_count': active_threat_count,
        'resolved_threat_count': resolved_threat_count,
        'status_filter': status_filter,
        'search_query': q
    })

@login_required
@user_passes_test(is_ceo, login_url='ceo_login')
def resolve_threat(request, pk):
    log = get_object_or_404(SecurityLog, pk=pk)
    log.resolved = not log.resolved
    log.save()
    messages.success(request, f"Security Log status updated for IP {log.ip_address}.")
    return redirect(request.META.get('HTTP_REFERER', 'ceo_threats'))

@login_required
@user_passes_test(is_ceo, login_url='ceo_login')
def purge_threats(request):
    if request.method == 'POST':
        purged_count, _ = SecurityLog.objects.filter(resolved=True).delete()
        messages.warning(request, f"Sanitization Complete: {purged_count} resolved security logs purged.")
    return redirect('ceo_threats')

@login_required
@user_passes_test(is_ceo, login_url='ceo_login')
def sourcing_list(request):
    requests = SourcingRequest.objects.all().order_by('-created_at')
    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        requests = requests.filter(status=status_filter)
    
    q = request.GET.get('q', '')
    if q:
        requests = requests.filter(
            Q(tracking_code__icontains=q) | 
            Q(customer_name__icontains=q) | 
            Q(asset_class__icontains=q)
        )
    return render(request, 'ceo_portal/sourcing_list.html', {
        'requests': requests,
        'status_filter': status_filter,
        'search_query': q
    })

@login_required
@user_passes_test(is_ceo, login_url='ceo_login')
def sourcing_detail(request, pk):
    s_req = get_object_or_404(SourcingRequest, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        new_notes = request.POST.get('broker_notes')
        
        if new_status:
            s_req.status = new_status
        if new_notes is not None:
            s_req.broker_notes = new_notes
            
        s_req.save()
        messages.success(request, f"Tracking Code {s_req.tracking_code} updated successfully.")
        return redirect('ceo_sourcing_detail', pk=pk)
        
    return render(request, 'ceo_portal/sourcing_detail.html', {'s_req': s_req})

@login_required
@user_passes_test(is_ceo, login_url='ceo_login')
def lead_dossier_print(request, pk):
    lead = get_object_or_404(Inquiry, pk=pk)
    return render(request, 'ceo_portal/dossier_print.html', {'type': 'lead', 'obj': lead})

@login_required
@user_passes_test(is_ceo, login_url='ceo_login')
def sourcing_dossier_print(request, pk):
    s_req = get_object_or_404(SourcingRequest, pk=pk)
    return render(request, 'ceo_portal/dossier_print.html', {'type': 'sourcing', 'obj': s_req})
