# movies/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Pages principales
    path('', views.movie_list, name='movie_list'),
    path('movie/<int:pk>/', views.movie_detail, name='movie_detail'),

    # Pages par type
    path('films/', views.films_view, name='films'),
    path('animes/', views.animes_view, name='animes'),
    path('series/', views.series_view, name='series'),
    path('type/<str:video_type>/', views.movies_by_type, name='movies_by_type'),

    # Authentification
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profil
    path('profile/', views.profile_view, name='profile'),
    path('profile/update-avatar/', views.update_avatar, name='update_avatar'),
    path('profile/update/', views.update_profile, name='update_profile'),
    
    # Favoris
    path('toggle-favorite/<int:movie_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.get_favorites, name='get_favorites'),
    path('clear-favorites/', views.clear_favorites, name='clear_favorites'),

    # Commentaires et évaluations
    path('movie/<int:movie_id>/comment/', views.add_comment, name='add_comment'),
    path('movie/<int:movie_id>/rate/', views.add_rating, name='add_rating'),
    path('movie/<int:movie_id>/watch/', views.add_to_watch_history, name='add_to_watch_history'),

    # Historique
    path('watch-history/', views.watch_history_view, name='watch_history'),
    path('clear-watch-history/', views.clear_watch_history, name='clear_watch_history'),
    path('remove-from-history/<int:history_id>/', views.remove_from_history, name='remove_from_history'),
    # urls.py
    path('api/check-watch-history/<int:movie_id>/', views.check_watch_history, name='check_watch_history'),


    #path('movie/<int:movie_id>/add-episode/', views.add_episode, name='add_episode'),
]