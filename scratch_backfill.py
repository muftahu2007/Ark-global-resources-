import os
import django
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDate

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "global_ark.settings")
django.setup()

from ark_catalog.models import Inquiry, SourcingRequest
from ceo_portal.models import DailyMetric

def backfill():
    print("Backfilling inquiries...")
    inquiries = Inquiry.objects.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id'))
    for entry in inquiries:
        if entry['date']:
            metric, _ = DailyMetric.objects.get_or_create(date=entry['date'])
            metric.inquiries_count = entry['count']
            metric.save()

    print("Backfilling sourcing requests...")
    sourcing = SourcingRequest.objects.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id'))
    for entry in sourcing:
        if entry['date']:
            metric, _ = DailyMetric.objects.get_or_create(date=entry['date'])
            metric.sourcing_count = entry['count']
            metric.save()

    print("Backfill complete!")

if __name__ == '__main__':
    backfill()
