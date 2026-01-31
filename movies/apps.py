# movies/apps.py
from django.apps import AppConfig

class MoviesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'movies'
    
    def ready(self):
        # Importez les signaux
        import movies.signals
        print("Signals importés")