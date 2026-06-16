from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View, TemplateView
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import subprocess
from .models import Product, Inquiry, Category, SourcingRequest
import urllib.parse

class ProductListView(ListView):
    """Home view showing category boxes."""
    model = Product
    template_name = 'ark_catalog/catalog.html'     
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Unique categories from the Category model
        context['categories'] = Category.objects.all().order_by('name')
        return context

class CategoryProductView(ListView):
    """View showing products within a specific category."""
    model = Product
    template_name = 'ark_catalog/category_products.html'
    context_object_name = 'products'

    def get_queryset(self):
        self.category_slug = self.kwargs.get('category')
        self.category = get_object_or_404(Category, slug=self.category_slug)
        return Product.objects.filter(category=self.category, is_available=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_name'] = self.category.name
        return context

class FleetManagementView(ListView):
    """Dynamic view showing all available cars."""
    model = Product
    template_name = 'ark_catalog/fleet.html'
    context_object_name = 'fleet_cars'

    def get_queryset(self):
        from django.db.models import Q
        # We query by category name dynamically, matching common names for the fleet
        return Product.objects.filter(
            Q(category__name__icontains='Car') | 
            Q(category__name__icontains='Fleet') | 
            Q(category__name__icontains='Vehicle'),
            is_available=True
        )

class ToggleSelectionView(View):
    def post(self, request, product_id):
        action = request.POST.get('action', 'add')
        
        # Directly fetch and append, explicitly telling Django to save
        if 'selection' not in request.session:
            request.session['selection'] = []
            
        selection = request.session['selection']
        product_id_str = str(product_id)
        
        if action == 'remove':
            if product_id_str in selection:
                selection.remove(product_id_str)
            status = 'removed'
        else:
            selection.append(product_id_str)
            status = 'added'
            
        request.session['selection'] = selection
        # We MUST NOT call request.session.save() explicitly here because it resets
        # request.session.modified to False, which causes SessionMiddleware to skip
        # sending the Set-Cookie header if a new session was created!
        # Re-assigning to request.session automatically marks it as modified.
        # Check if it's an AJAX request
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', '')
        if is_ajax:
            return JsonResponse({
                'status': status,
                'selection_count': len(selection),
                'session_key': request.session.session_key
            })
            
        return redirect(request.META.get('HTTP_REFERER', 'catalog'))

from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

@method_decorator(never_cache, name='dispatch')
class InquiryFormView(View):
    def get(self, request):
        if not request.session.session_key:
            request.session.create()
            
        selection_ids = request.session.get('selection', [])
        
        products_dict = {str(p.id): p for p in Product.objects.filter(id__in=selection_ids)}
        selected_products = [products_dict[i] for i in selection_ids if i in products_dict]
        
        return render(request, 'ark_catalog/inquiry_form.html', {
            'selected_products': selected_products,
            'raw_selection_ids': selection_ids,
            'session_key': request.session.session_key,
        })

    def post(self, request):
        name = request.POST.get('name', '')
        phone = request.POST.get('phone', '')
        email = request.POST.get('email', '')
        message = request.POST.get('message', '')
        method = request.POST.get('method', 'whatsapp')
        
        selection_ids = request.session.get('selection', [])
        if not selection_ids:
            messages.error(request, "Your selection is empty.")
            return redirect('catalog')
        
        products_dict = {str(p.id): p for p in Product.objects.filter(id__in=selection_ids)}
        products = [products_dict[i] for i in selection_ids if i in products_dict]
        
        inquiry = Inquiry.objects.create(
            customer_name=name, phone=phone, email=email, message=message
        )
        inquiry.items_requested.set(set(products))
        
        from collections import defaultdict
        grouped_email_products = defaultdict(list)
        for p in products:
            cat_name = p.category.name if p.category else "General Selection"
            grouped_email_products[cat_name].append(p)
            
        email_items_str = ""
        for cat_name, items in grouped_email_products.items():
            email_items_str += f"\n📂 {cat_name}\n"
            for idx, p in enumerate(items, 1):
                sku_str = f" [SKU: {p.sku}]" if p.sku else ""
                email_items_str += f"   {idx}. {p.name}{sku_str}\n"
        
        if method == 'email':
            # Handle Executive Email Transmission
            subject = f"🏛️ NEW EXECUTIVE INQUIRY: {name}"
            email_body = f"""
=========================================
ARK GLOBAL RESOURCES - NEW LEAD
=========================================

CUSTOMER PROFILE:
-----------------
Name:    {name}
Phone:   {phone}
Email:   {email}

SELECTED INVENTORY:
-------------------{email_items_str}

CLIENT MESSAGE:
---------------
"{message if message else 'No additional notes provided.'}"

=========================================
Sent via Ark Catalog Executive Portal
=========================================
"""
            try:
                send_mail(
                    subject,
                    email_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [getattr(settings, 'ARK_EXECUTIVE_EMAIL', 'admin@example.com')],
                    fail_silently=False,
                )
                request.session['selection'] = []
                return render(request, 'ark_catalog/success.html', {'method': 'email'})
            except Exception as e:
                messages.error(request, f"Email delivery failed. Please use WhatsApp. Error: {e}")
                return redirect('inquiry_form') 

        else:
            # Handle WhatsApp Transmission (Shopping Assistant Format)
            grouped_products = {}
            for p in products:
                cat_name = p.category.name if p.category else "Other Items"
                if cat_name not in grouped_products:
                    grouped_products[cat_name] = []
                grouped_products[cat_name].append(p)

            wa_lines = [
                f"👋 Hello Ark Global, my name is {name}.",
                "I'm interested in these items:\n"
            ]
            
            counter = 1
            for cat_name, items in grouped_products.items():
                wa_lines.append(f"✨ * {cat_name}*")
                for p in items:
                    num_emoji = f"{counter}️⃣" if counter <= 9 else f"{counter}."
                    wa_lines.append(f"   {num_emoji} {p.name}")
                    counter += 1
                wa_lines.append("") # Empty line for spacing
                
            if message:
                wa_lines.append(f"💬 *Notes:* {message}\n")
                
            wa_lines.append("Reply with a number to continue! 🏛️")
            
            wa_text = "\n".join(wa_lines)
            encoded_message = urllib.parse.quote(wa_text)
            request.session['selection'] = []
            wa_link = f"https://wa.me/{getattr(settings, 'WHATSAPP_NUMBER', '')}?text={encoded_message}"
            return render(request, 'ark_catalog/success.html', {'wa_link': wa_link, 'method': 'whatsapp'})

class PrivateSourcingView(View):
    def get(self, request):
        categories = Category.objects.all().order_by('name')
        return render(request, 'ark_catalog/sourcing.html', {
            'categories': categories
        })

    def post(self, request):
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        asset_type = request.POST.get('asset_type', '')
        budget = request.POST.get('budget', '')
        timeline = request.POST.get('timeline', '')
        details = request.POST.get('details', '')
        method = request.POST.get('method', 'whatsapp')

        full_message = f"Asset Type: {asset_type}\nBudget: {budget}\nTimeline: {timeline}\n\nDetails:\n{details}"

        # Create SourcingRequest record instead of general inquiry
        sourcing_request = SourcingRequest.objects.create(
            customer_name=name, phone=phone, email=email, 
            asset_class=asset_type, budget=budget, timeline=timeline, details=details
        )
        t_code = sourcing_request.tracking_code

        # --- SEND LUXURY HTML CONFIRMATION EMAIL TO CLIENT ---
        if email:
            try:
                client_subject = f"Sourcing Request Received - Ref: {t_code} | Global Ark Resources"
                
                # Context for the email
                context = {
                    'name': name,
                    'tracking_code': t_code,
                    'asset_type': asset_type,
                    'budget': budget,
                    'timeline': timeline,
                    'details': details,
                }
                
                # Render HTML and plain text versions
                html_content = render_to_string('emails/sourcing_confirmation.html', context)
                text_content = f"""Dear {name},

Thank you for choosing Global Ark Resources. We have successfully received your private sourcing request. A dedicated concierge is currently reviewing your dossier and will reach out to you shortly.

Request Summary:
Tracking Code: {t_code}
Asset Class: {asset_type}
Budget: {budget}
Timeline: {timeline}
Additional Directives: {details}

Sincerely,
The Executive Concierge Team
Global Ark Resources Ltd."""
                
                msg = EmailMultiAlternatives(
                    client_subject,
                    text_content,
                    settings.DEFAULT_FROM_EMAIL,
                    [email]
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send(fail_silently=True)
            except Exception as e:
                # We fail silently for the client email so it doesn't break the submission flow
                pass

        # --- SEND NOTIFICATION TO EXECUTIVE ---

        if method == 'email':
            subject = f"🏛️ NEW PRIVATE SOURCING: {name} [{t_code}]"
            email_body = f"""
=========================================
ARK GLOBAL RESOURCES - PRIVATE SOURCING
=========================================
TRACKING CODE: {t_code}

CLIENT PROFILE:
---------------
Name:    {name}
Phone:   {phone}
Email:   {email}

SOURCING REQUIREMENTS:
----------------------
Asset Class: {asset_type}
Budget:      {budget}
Timeline:    {timeline}

ADDITIONAL SPECIFICATIONS:
--------------------------
"{details if details else 'No additional details provided.'}"

=========================================
Sent via Ark Catalog Executive Portal
=========================================
"""
            try:
                send_mail(
                    subject,
                    email_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [getattr(settings, 'ARK_EXECUTIVE_EMAIL', 'admin@example.com')],
                    fail_silently=False,
                )
                return render(request, 'ark_catalog/success.html', {'method': 'email', 'tracking_code': t_code})
            except Exception as e:
                messages.error(request, f"Email delivery failed. Please use WhatsApp. Error: {e}")
                return redirect('private_sourcing')
        else:
            # Handle WhatsApp Transmission (Shopping Assistant Format)
            wa_lines = [
                f"👋 Hello Ark Global, my name is {name}.",
                "I am submitting a new private sourcing request:\n",
                f"✨ *Asset:* {asset_type}",
                f"💰 *Budget:* {budget}",
                f"⏱️ *Timeline:* {timeline}"
            ]
            
            if details:
                wa_lines.append(f"\n💬 *Details:* {details}")
                
            wa_lines.append(f"\n_Ref: {t_code}_")
            wa_lines.append("\nPlease review my request and reply to continue our consultation! 🏛️")
            
            wa_text = "\n".join(wa_lines)
            encoded_message = urllib.parse.quote(wa_text)
            wa_link = f"https://wa.me/{getattr(settings, 'WHATSAPP_NUMBER', '')}?text={encoded_message}"
            return render(request, 'ark_catalog/success.html', {'wa_link': wa_link, 'method': 'whatsapp', 'tracking_code': t_code})

class SourcingTrackView(View):
    def get(self, request):
        return render(request, 'ark_catalog/sourcing_track.html')

    def post(self, request):
        email = request.POST.get('email', '')
        tracking_code = request.POST.get('tracking_code', '')
        
        try:
            sourcing_request = SourcingRequest.objects.get(email__iexact=email, tracking_code__iexact=tracking_code)
            return render(request, 'ark_catalog/sourcing_track.html', {
                'sourcing_request': sourcing_request,
                'email': email,
                'tracking_code': tracking_code
            })
        except SourcingRequest.DoesNotExist:
            messages.error(request, "No sourcing request found matching that email and tracking code combination.")
            return render(request, 'ark_catalog/sourcing_track.html')

class AboutUsView(View):
    def get(self, request):
        return render(request, 'ark_catalog/about.html')

def check_disk_space(request):
    try:
        # Run the standard Linux disk-free command
        result = subprocess.run(['df', '-h'], capture_output=True, text=True)
        
        # Print it to your Render Logs so you can see it there too
        print(result.stdout)
        
        # Wrap the output in a <pre> tag so the columns line up perfectly in the browser
        return HttpResponse(f"<pre>{result.stdout}</pre>")
        
    except Exception as e:
        return HttpResponse(f"Error checking disk space: {str(e)}")
