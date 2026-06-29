from django.apps import AppConfig


class ArkCatalogConfig(AppConfig):
    name = 'ark_catalog'

    def ready(self):
        import ark_catalog.signals