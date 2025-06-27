from django.apps import AppConfig


class PmcApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pmc_api'

    def ready(self):
        print("💡 pmc_api is ready and signals are loaded.")
        from simple_history import register
        from django.contrib.auth import get_user_model

        # Register your User model for history
        register(get_user_model())  # ✅ Safe way to register auth.User

        # Import signals here too (if any)
        import pmc_api.signals
