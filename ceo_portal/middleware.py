from django.conf import settings
from django.http import Http404, HttpResponseRedirect

class GatekeeperMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Retrieve path and key from settings
        secret_path = getattr(settings, 'SECRET_ADMIN_PATH', 'vault-console')
        secret_key = getattr(settings, 'SECRET_ADMIN_KEY', 'ArkVanguard2026')

        # Check if the path targets the secret admin page
        # Django paths are standard with slashes (e.g., /vault-console/)
        normalized_path = request.path.strip('/')
        
        if normalized_path.startswith(secret_path):
            # 1. Check if the user is passing the gatekeeper key in the query string
            gatekeeper_param = request.GET.get('gatekeeper')
            
            if gatekeeper_param == secret_key:
                # Key is correct! Set a secure, signed cookie and redirect to clear the query string from URL
                response = HttpResponseRedirect(request.path)
                response.set_signed_cookie(
                    'vault_gatekeeper_token',
                    secret_key,
                    max_age=30 * 24 * 60 * 60,  # 30 days
                    httponly=True,
                    secure=not settings.DEBUG,
                    samesite='Lax'
                )
                return response
            
            # 2. Check if the signed cookie is present and matches the secret key
            try:
                cookie_token = request.get_signed_cookie('vault_gatekeeper_token', default=None)
            except Exception:
                # Handle cookie tampering gracefully
                cookie_token = None

            if cookie_token == secret_key:
                # Valid cookie found! Proceed normally
                return self.get_response(request)
            
            # 3. No valid authentication. Hide the door!
            # We raise a standard 404 error, simulating that this path does not exist.
            raise Http404("Page not found")

        # For all other paths, continue processing normal middleware
        return self.get_response(request)
