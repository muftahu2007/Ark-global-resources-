from .models import SecurityLog

def security_context(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return {
            'active_threats_count': SecurityLog.objects.filter(resolved=False).count()
        }
    return {}
