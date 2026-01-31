# movies/admin.py
from django.contrib import admin
from .models import Movie, Episode

class EpisodeInline(admin.TabularInline):  # ou admin.StackedInline pour un affichage vertical
    model = Episode
    extra = 1  # Nombre de formulaires d'épisodes vides à afficher
    fields = ('season_number', 'episode_number', 'title', 'video', 'duration', 'release_year')
    ordering = ('season_number', 'episode_number')

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'video_type', 'category', 'release_year', 'duration')
    list_filter = ('video_type', 'category', 'release_year')
    search_fields = ('title', 'description', 'director')
    
    # AJOUTE CETTE LIGNE :
    inlines = [EpisodeInline]  
    

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('movie', 'season_number', 'episode_number', 'title', 'duration')
    list_filter = ('movie', 'season_number')
    search_fields = ('title', 'movie__title')
    ordering = ('movie', 'season_number', 'episode_number')