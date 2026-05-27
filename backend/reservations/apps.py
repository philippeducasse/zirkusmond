from django.apps import AppConfig


class ReservationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "reservations"

    def ready(self):
        import reservations.payments.admin  # noqa: F401
        import reservations.payments.signals  # noqa: F401
