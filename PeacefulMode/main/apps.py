from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        # Импорт должен быть внутри метода, чтобы избежать циклической зависимости
        import main.signals
