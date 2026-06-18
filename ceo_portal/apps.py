from django.apps import AppConfig
from django.db.backends.signals import connection_created
from django.dispatch import receiver
from django.conf import settings
import os

@receiver(connection_created)
def configure_sqlite(sender, connection, **kwargs):
    if connection.vendor == 'sqlite':
        cursor = connection.cursor()
        cursor.execute('PRAGMA journal_mode=WAL;')
        cursor.execute('PRAGMA synchronous=NORMAL;')

class CeoPortalConfig(AppConfig):
    name = 'ceo_portal'

    def ready(self):
        # Cleanup orphaned temp uploads on startup
        try:
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_uploads')
            if os.path.exists(temp_dir):
                for f in os.listdir(temp_dir):
                    path = os.path.join(temp_dir, f)
                    if os.path.isfile(path):
                        os.remove(path)
        except Exception:
            pass

        import ceo_portal.signals
