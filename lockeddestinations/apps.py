from django.apps import AppConfig


class LockeddestinationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "lockeddestinations"

    def ready(self):
        import lockeddestinations.signals  # noqa: F401