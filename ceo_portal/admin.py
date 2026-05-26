from django.contrib import admin
from .models import SecurityLog

@admin.register(SecurityLog)
class SecurityLogAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'attempted_username', 'attempted_password', 'timestamp', 'resolved')
    list_filter = ('resolved', 'timestamp')
    search_fields = ('ip_address', 'attempted_username', 'user_agent')
    # Keep historical logs immutable except for the resolved flag
    readonly_fields = ('ip_address', 'user_agent', 'attempted_username', 'attempted_password', 'timestamp')
    ordering = ('-timestamp',)
