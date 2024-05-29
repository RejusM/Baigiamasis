from django.apps import AppConfig


class TrailoappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "trailoapp"

    def ready(self):
        import trailoapp.signals
