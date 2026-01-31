# movies/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='thumbnails/')
    video = models.FileField(upload_to='videos/')
    release_year = models.IntegerField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)  # en minutes
    director = models.CharField(max_length=100, null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    CATEGORY_CHOICES = [
        ('action', 'Action'),
        ('drama', 'Drame'),
        ('comedy', 'Comédie'),
        ('romance', 'Romance'),
        ('horror', 'Horreur'),

    ]

    VIDEO_TYPE_CHOICES = [
        ('film', 'Film'),
        ('anime', 'Anime'),
        ('serie', 'Série'),
    ]
    
    video_type = models.CharField(
        max_length=10,
        choices=VIDEO_TYPE_CHOICES,
        default='film'
    )

    
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='action'
    )
    
    def __str__(self):
        return self.title
    
    # AJOUTEZ CETTE MÉTHODE pour vérifier si un utilisateur a favorisé ce film
    def is_favorite_for_user(self, user):
        """Vérifie si le film est favori pour un utilisateur donné."""
        if not user.is_authenticated:
            return False
        try:
            profile = user.profile
            return Favorite.objects.filter(user_profile=profile, movie=self).exists()
        except UserProfile.DoesNotExist:
            return False

    @property
    def average_rating(self):
        """Retourne la note moyenne du film"""
        ratings = self.ratings.all()
        if ratings.exists():
            return sum(r.score for r in ratings) / ratings.count()
        return 0
    
    @property
    def rating_count(self):
        """Retourne le nombre d'évaluations"""
        return self.ratings.count()
    
    @property
    def comment_count(self):
        """Retourne le nombre de commentaires"""
        return self.comments.filter(is_approved=True).count()
    
    def get_recent_comments(self, limit=5):
        """Retourne les commentaires récents"""
        return self.comments.filter(is_approved=True).order_by('-created_at')[:limit]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    
    def __str__(self):
        return self.user.username
    
    @property
    def favorite_movies(self):
        """Retourne les films favoris de l'utilisateur."""
        return Movie.objects.filter(favorite__user_profile=self)
    
    # AJOUTEZ CETTE MÉTHODE pour vérifier si un film est favori
    def has_favorite(self, movie):
        """Vérifie si un film est dans les favoris de l'utilisateur."""
        return Favorite.objects.filter(user_profile=self, movie=movie).exists()

    @property
    def watch_history_movies(self):
        """Retourne les films de l'historique"""
        return Movie.objects.filter(watched_by__user_profile=self).order_by('-watched_by__watched_at')
    
    @property
    def recently_watched(self, limit=10):
        """Retourne les films récemment regardés"""
        return self.watch_history.all().order_by('-watched_at')[:limit]


class Favorite(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='favorites')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user_profile', 'movie')  # Empêche les doublons
        verbose_name = "Favori"
        verbose_name_plural = "Favoris"
        ordering = ['-added_at']  # Les plus récents d'abord
    
    def __str__(self):
        return f"{self.user_profile.user.username} - {self.movie.title}"
    
    # AJOUTEZ CETTE MÉTHODE pour un accès facile à l'utilisateur
    @property
    def user(self):
        """Retourne l'utilisateur associé à ce favori."""
        return self.user_profile.user


class Rating(models.Model):
    """Modèle pour les évaluations (1-5 étoiles)"""
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='ratings')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings')
    score = models.IntegerField(
        choices=[(1, '1 étoile'), (2, '2 étoiles'), (3, '3 étoiles'), 
                (4, '4 étoiles'), (5, '5 étoiles')],
        default=5
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user_profile', 'movie')
        verbose_name = "Évaluation"
        verbose_name_plural = "Évaluations"
    
    def __str__(self):
        return f"{self.user_profile.user.username} - {self.movie.title}: {self.score}/5"


class Comment(models.Model):
    """Modèle pour les commentaires"""
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='comments')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)  # Pour modération
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
    
    def __str__(self):
        return f"{self.user_profile.user.username} sur {self.movie.title}"


class WatchHistory(models.Model):
    """Modèle pour l'historique de visionnage"""
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='watch_history')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='watched_by')
    watched_at = models.DateTimeField(auto_now_add=True)
    duration_watched = models.IntegerField(default=0)  # en secondes
    completed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-watched_at']
        verbose_name = "Historique de visionnage"
        verbose_name_plural = "Historiques de visionnage"
        unique_together = ('user_profile', 'movie')  # Un seul enregistrement par film
    
    def __str__(self):
        status = "Terminé" if self.completed else "En cours"
        return f"{self.user_profile.user.username} - {self.movie.title} ({status})"



# models.py - AJOUTE CETTE CLASSE À LA FIN DU FICHIER

class Episode(models.Model):
    """Modèle pour les épisodes"""
    movie = models.ForeignKey(
        Movie, 
        on_delete=models.CASCADE, 
        related_name='episodes'
    )
    season_number = models.IntegerField(default=1)
    episode_number = models.IntegerField()
    title = models.CharField(max_length=200)
    video = models.FileField(upload_to='episodes/')
    thumbnail = models.ImageField(upload_to='episode_thumbnails/', null=True, blank=True)
    description = models.TextField(blank=True)
    duration = models.IntegerField(null=True, blank=True)
    release_year = models.DateField(null=True, blank=True)
    release_year = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['season_number', 'episode_number']
        unique_together = ['movie', 'season_number', 'episode_number']
        verbose_name = "Épisode"
        verbose_name_plural = "Épisodes"
    
    def __str__(self):
        return f"{self.movie.title} - S{self.season_number:02d}E{self.episode_number:02d}: {self.title}"
    
    @property
    def full_episode_title(self):
        """Retourne le titre complet avec saison et épisode"""
        return f"Saison {self.season_number} - Épisode {self.episode_number}: {self.title}"