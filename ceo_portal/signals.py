from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from ark_catalog.models import Inquiry, SourcingRequest
from .models import DailyMetric

@receiver(post_save, sender=Inquiry)
def update_inquiry_metrics(sender, instance, created, **kwargs):
    if created:
        today = timezone.localdate(instance.created_at) if instance.created_at else timezone.localdate()
        metric, _ = DailyMetric.objects.get_or_create(date=today)
        metric.inquiries_count += 1
        metric.save()

@receiver(post_save, sender=SourcingRequest)
def update_sourcing_metrics(sender, instance, created, **kwargs):
    if created:
        today = timezone.localdate(instance.created_at) if instance.created_at else timezone.localdate()
        metric, _ = DailyMetric.objects.get_or_create(date=today)
        metric.sourcing_count += 1
        metric.save()
