from django.apps import AppConfig


class BachelorpointappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bachelorPointApp'
    
    def ready(self):
        import bachelorPointApp.signals