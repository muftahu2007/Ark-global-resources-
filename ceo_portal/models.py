from django.db import models

class SecurityLog(models.Model):
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    attempted_username = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Security Logs"
        ordering = ['-timestamp'] 

    def __str__(self):     
        status = "Resolved" if self.resolved else "Active Alert"
        return f"Intrusion attempt from {self.ip_address} on {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - [{status}]"
