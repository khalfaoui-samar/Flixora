# movies/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import os
import json
from django.http import JsonResponse
import uuid
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import Movie, UserProfile, Favorite, Comment, Rating, WatchHistory,Episode

# Helper function pour obtenir ou créer un profil
def get_or_create_profile(user):
    try:
        return user.profile
    except UserProfile.DoesNotExist:
        # Créer le profil si non existant
        return UserProfile.objects.create(user=user)

# Pages principales
def movie_list(request):
    # Récupérer tous les films
    all_movies = Movie.objects.all().order_by('-created_at')  # ou '-id' si pas de created_at
    
    # Récupérer les films par type
    films = Movie.objects.filter(video_type='film').order_by('-created_at')[:8]
    animes = Movie.objects.filter(video_type='anime').order_by('-created_at')[:8]
    series = Movie.objects.filter(video_type='serie').order_by('-created_at')[:8]
    
    for movie in all_movies:
        movie.category_display = movie.get_category_display()
        movie.category_lower = movie.category.lower()
        movie.is_fav = movie.is_favorite_for_user(request.user)
    
    return render(request, 'movies/movie_list.html', {
        'movies': all_movies,
        'films': films,
        'animes': animes,
        'series': series,
    })
# views.py - REMPLACE ta fonction movie_detail existante par CELLE-CI :

def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    
    # ============ PARTIE POUR LES ÉPISODES ============
    episodes = []
    seasons = []
    current_episode = None
    
    # Récupérer les épisodes
    episodes = Episode.objects.filter(movie=movie).order_by('season_number', 'episode_number')
    
    if episodes.exists():  # Seulement si le film a des épisodes
        # Organiser par saisons
        seasons_dict = {}
        for episode in episodes:
            if episode.season_number not in seasons_dict:
                seasons_dict[episode.season_number] = []
            seasons_dict[episode.season_number].append(episode)
        
        # Convertir en liste de tuples pour le template
        seasons = sorted(seasons_dict.items())
        
        # Récupérer l'épisode demandé (depuis l'URL)
        episode_id = request.GET.get('episode')
        
        if episode_id:
            try:
                current_episode = Episode.objects.get(id=episode_id, movie=movie)
            except Episode.DoesNotExist:
                # Si l'épisode n'existe pas, prendre le premier
                current_episode = episodes.first()
        else:
            # Par défaut, premier épisode
            current_episode = episodes.first()
    # =================================================
    
    # Enregistrer automatiquement la visite dans l'historique
    if request.user.is_authenticated:
        profile = get_or_create_profile(request.user)
        WatchHistory.objects.get_or_create(
            user_profile=profile,
            movie=movie,
            defaults={
                'duration_watched': 0,
                'completed': False
            }
        )
    
    # Vérifier si le film est favori
    is_favorite = movie.is_favorite_for_user(request.user)
    
    # Récupérer les commentaires et évaluations
    comments = movie.comments.all().order_by('-created_at')
    user_rating = None
    if request.user.is_authenticated:
        profile = get_or_create_profile(request.user)
        try:
            user_rating = Rating.objects.get(user_profile=profile, movie=movie)
        except Rating.DoesNotExist:
            pass
    
    # AJOUTER les variables d'épisodes au context
    return render(request, 'movies/movie_detail.html', {
        'movie': movie,
        'current_episode': current_episode,
        'seasons': seasons,
        'episodes': episodes,
        'is_favorite': is_favorite,
        'comments': comments,
        'user_rating': user_rating
    })

# Pages filtrées par type
def movies_by_type(request, video_type):
    """Affiche les films filtrés par type (film, anime, serie)"""
    
    # Valider le type
    valid_types = ['film', 'anime', 'serie']
    if video_type not in valid_types:
        video_type = 'film'
    
    # Filtrer les films par type
    movies = Movie.objects.filter(video_type=video_type).order_by('-created_at')
    
    # Marquer les films favoris pour l'utilisateur connecté
    for movie in movies:
        movie.is_fav = movie.is_favorite_for_user(request.user)
    
    # Titre de la page selon le type
    page_titles = {
        'film': 'Films',
        'anime': 'Animes', 
        'serie': 'Séries'
    }
    
    return render(request, 'movies/movies_by_type.html', {
        'movies': movies,
        'video_type': video_type,
        'page_title': page_titles.get(video_type, 'Films')
    })

# Vues spécifiques pour chaque type
def films_view(request):
    return movies_by_type(request, 'film')

def animes_view(request):
    return movies_by_type(request, 'anime')

def series_view(request):
    return movies_by_type(request, 'serie')

# Authentification
def login_view(request):
    if request.user.is_authenticated:
        return redirect('movie_list')
    
    # Afficher un message personnalisé s'il est passé en paramètre
    message = request.GET.get('message', '')
    if message:
        messages.info(request, message)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Créer un profil si nécessaire
            get_or_create_profile(user)
            
            # Message de bienvenue personnalisé
            welcome_message = request.POST.get('welcome_message', f'Bienvenue {username} !')
            messages.success(request, welcome_message)
            
            # Redirection après connexion
            next_url = request.POST.get('next', 'movie_list')
            if next_url:
                return redirect(next_url)
            return redirect('movie_list')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    next_url = request.GET.get('next', 'movie_list')
    return render(request, 'movies/auth/login.html', {'next': next_url})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('movie_list')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validation
        errors = []
        
        if User.objects.filter(username=username).exists():
            errors.append('Ce nom d\'utilisateur est déjà pris.')
        
        if User.objects.filter(email=email).exists():
            errors.append('Cet email est déjà utilisé.')
        
        if password1 != password2:
            errors.append('Les mots de passe ne correspondent pas.')
        
        if len(password1) < 6:
            errors.append('Le mot de passe doit contenir au moins 6 caractères.')
        
        if not errors:
            # Créer l'utilisateur
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            # Créer automatiquement le profil
            get_or_create_profile(user)
            login(request, user)
            messages.success(request, f'Compte créé avec succès, bienvenue {username} !')
            return redirect('movie_list')
        else:
            for error in errors:
                messages.error(request, error)
    
    return render(request, 'movies/auth/register.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté.')
    return redirect('movie_list')

# Profil
@login_required
def profile_view(request):
    profile = get_or_create_profile(request.user)
    
    # Récupérer les films favoris
    favorite_movies_ids = Favorite.objects.filter(
        user_profile=profile
    ).values_list('movie__id', flat=True)
    
    favorite_movies = Movie.objects.filter(id__in=favorite_movies_ids)
    
    # Récupérer l'historique récent
    recent_history = WatchHistory.objects.filter(
        user_profile=profile
    ).order_by('-watched_at')[:10]
    
    # Compter les commentaires
    comment_count = Comment.objects.filter(user_profile=profile).count()
    
    return render(request, 'movies/profile.html', {
        'profile': profile,
        'favorite_movies': favorite_movies,
        'favorite_count': favorite_movies.count(),
        'recent_history': recent_history,
        'watch_history_count': WatchHistory.objects.filter(user_profile=profile).count(),
        'comment_count': comment_count,
    })

# Mise à jour de l'avatar
@login_required
@require_POST
@csrf_exempt
def update_avatar(request):
    """Mettre à jour l'avatar de l'utilisateur"""
    try:
        profile = get_or_create_profile(request.user)
        
        # Gérer l'avatar uploadé
        if 'avatar' in request.FILES:
            avatar_file = request.FILES['avatar']
            
            # Vérifier la taille (max 5MB)
            if avatar_file.size > 5 * 1024 * 1024:
                return JsonResponse({'success': False, 'error': 'Fichier trop volumineux (max 5MB)'})
            
            # Vérifier le type de fichier
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if avatar_file.content_type not in allowed_types:
                return JsonResponse({'success': False, 'error': 'Format de fichier non supporté. Utilisez JPG, PNG, GIF ou WebP.'})
            
            # Supprimer l'ancien avatar s'il existe
            if profile.avatar and os.path.isfile(profile.avatar.path):
                try:
                    os.remove(profile.avatar.path)
                except:
                    pass
            
            # Générer un nom de fichier unique
            filename = f'avatar_{request.user.id}_{uuid.uuid4().hex[:8]}.{avatar_file.name.split(".")[-1]}'
            
            # Sauvegarder le nouvel avatar
            profile.avatar.save(filename, avatar_file, save=True)
            
        # Gérer les avatars par défaut
        elif 'default_avatar' in request.POST:
            default_avatar = request.POST.get('default_avatar')
            
            # Supprimer l'ancien avatar s'il existe
            if profile.avatar and os.path.isfile(profile.avatar.path):
                try:
                    os.remove(profile.avatar.path)
                except:
                    pass
            
            # Définir l'avatar par défaut (stockage dans un champ séparé)
            profile.avatar = None
            # Si vous avez un champ default_avatar_type dans votre modèle UserProfile :
            # profile.default_avatar_type = default_avatar
            profile.save()
            
        else:
            return JsonResponse({'success': False, 'error': 'Aucune image fournie'})
        
        # Rafraîchir l'objet profile
        profile.refresh_from_db()
        
        # Construire l'URL de l'avatar
        avatar_url = profile.avatar.url if profile.avatar else None
        
        return JsonResponse({
            'success': True,
            'avatar_url': avatar_url,
            'message': 'Photo de profil mise à jour avec succès'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Mise à jour du profil
@login_required
@require_POST
@csrf_exempt
def update_profile(request):
    """Mettre à jour les informations du profil"""
    try:
        user = request.user
        profile = get_or_create_profile(user)
        
        # Récupérer les données du formulaire
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        bio = request.POST.get('bio', '').strip()
        
        # Valider les données
        if not username:
            return JsonResponse({'success': False, 'error': 'Le nom d\'utilisateur est requis'})
        
        if not email:
            return JsonResponse({'success': False, 'error': 'L\'email est requis'})
        
        # Vérifier si le nom d'utilisateur est unique (sauf pour l'utilisateur actuel)
        if username != user.username:
            if User.objects.filter(username=username).exclude(id=user.id).exists():
                return JsonResponse({'success': False, 'error': 'Ce nom d\'utilisateur est déjà pris'})
            user.username = username
        
        # Vérifier si l'email est unique (sauf pour l'utilisateur actuel)
        if email != user.email:
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                return JsonResponse({'success': False, 'error': 'Cet email est déjà utilisé'})
            user.email = email
        
        user.save()
        
        profile.bio = bio
        profile.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Profil mis à jour avec succès',
            'username': user.username,
            'email': user.email,
            'bio': bio
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Historique
@login_required
@require_POST
@csrf_exempt
def remove_from_history(request, history_id):
    """Retirer un film de l'historique"""
    try:
        history_item = get_object_or_404(WatchHistory, id=history_id, user_profile=request.user.profile)
        history_item.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Film retiré de l\'historique'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

# Favoris (AJAX)
@login_required
@require_POST
@csrf_exempt
def toggle_favorite(request, movie_id):
    try:
        movie = get_object_or_404(Movie, pk=movie_id)
        profile = get_or_create_profile(request.user)
        
        # Vérifier si le film est déjà en favori
        favorite_exists = Favorite.objects.filter(
            user_profile=profile,
            movie=movie
        ).exists()
        
        if favorite_exists:
            # Retirer des favoris
            Favorite.objects.filter(
                user_profile=profile,
                movie=movie
            ).delete()
            is_favorite = False
            action = 'removed'
            message = 'Film retiré des favoris'
        else:
            # Ajouter aux favoris
            Favorite.objects.create(
                user_profile=profile,
                movie=movie
            )
            is_favorite = True
            action = 'added'
            message = 'Film ajouté aux favoris !'
        
        # Compter les favoris
        favorite_count = Favorite.objects.filter(user_profile=profile).count()
        
        return JsonResponse({
            'success': True,
            'action': action,
            'is_favorite': is_favorite,
            'message': message,
            'favorite_count': favorite_count
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

# Vue pour récupérer les favoris (optionnel)
@login_required
def get_favorites(request):
    profile = get_or_create_profile(request.user)
    
    # Récupérer les films favoris via Favorite
    favorites = Favorite.objects.filter(user_profile=profile).select_related('movie')
    
    favorite_list = []
    for fav in favorites:
        favorite_list.append({
            'id': fav.movie.id,
            'title': fav.movie.title,
            'category': fav.movie.category
        })
    
    return JsonResponse({
        'favorites': favorite_list,
        'count': len(favorite_list)
    })

# Vue pour vider les favoris (optionnel)
@login_required
@require_POST
def clear_favorites(request):
    profile = get_or_create_profile(request.user)
    count = Favorite.objects.filter(user_profile=profile).count()
    
    # Supprimer tous les favoris
    Favorite.objects.filter(user_profile=profile).delete()
    
    messages.success(request, f'Tous les favoris ont été supprimés ({count} films).')
    return redirect('profile')

# Vues pour les commentaires et évaluations
@login_required
@require_POST
@csrf_exempt
def add_comment(request, movie_id):
    """Ajouter un commentaire"""
    try:
        movie = get_object_or_404(Movie, pk=movie_id)
        profile = get_or_create_profile(request.user)
        content = request.POST.get('content', '').strip()
        
        if not content:
            return JsonResponse({'success': False, 'error': 'Le commentaire ne peut pas être vide'})
        
        comment = Comment.objects.create(
            user_profile=profile,
            movie=movie,
            content=content
        )
        
        return JsonResponse({
            'success': True,
            'comment_id': comment.id,
            'content': comment.content,
            'username': request.user.username,
            'created_at': comment.created_at.strftime('%d/%m/%Y %H:%M'),
            'comment_count': movie.comments.count()
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
@csrf_exempt
def add_rating(request, movie_id):
    """Ajouter ou mettre à jour une évaluation"""
    try:
        movie = get_object_or_404(Movie, pk=movie_id)
        profile = get_or_create_profile(request.user)
        score = int(request.POST.get('score', 5))
        
        # Valider le score
        if score < 1 or score > 5:
            return JsonResponse({'success': False, 'error': 'Le score doit être entre 1 et 5'})
        
        # Créer ou mettre à jour l'évaluation
        rating, created = Rating.objects.update_or_create(
            user_profile=profile,
            movie=movie,
            defaults={'score': score}
        )
        
        # Recalculer la moyenne
        ratings = movie.ratings.all()
        if ratings.exists():
            average = sum(r.score for r in ratings) / ratings.count()
        else:
            average = 0
        
        return JsonResponse({
            'success': True,
            'created': created,
            'score': rating.score,
            'average_rating': round(average, 1),
            'rating_count': ratings.count(),
            'user_rating': rating.score
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
@csrf_exempt
def add_to_watch_history(request, movie_id):
    """Ajouter un film à l'historique de visionnage"""
    try:
        movie = get_object_or_404(Movie, pk=movie_id)
        profile = get_or_create_profile(request.user)
        completed = request.POST.get('completed', 'false').lower() == 'true'
        duration = int(request.POST.get('duration', 0))
        
        # Créer ou mettre à jour l'historique
        history, created = WatchHistory.objects.update_or_create(
            user_profile=profile,
            movie=movie,
            defaults={
                'duration_watched': duration,
                'completed': completed
            }
        )
        
        return JsonResponse({
            'success': True,
            'created': created,
            'movie_title': movie.title,
            'completed': history.completed
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def watch_history_view(request):
    """Page de l'historique de visionnage"""
    profile = get_or_create_profile(request.user)
    history = WatchHistory.objects.filter(user_profile=profile).order_by('-watched_at')
    
    # Calculer les statistiques
    completed_count = history.filter(completed=True).count()
    in_progress_count = history.filter(completed=False).count()
    
    return render(request, 'movies/watch_history.html', {
        'profile': profile,
        'watch_history': history,
        'history_count': history.count(),
        'completed_count': completed_count,
        'in_progress_count': in_progress_count,
    })

@login_required
@require_POST
def clear_watch_history(request):
    """Vider l'historique de visionnage"""
    profile = get_or_create_profile(request.user)
    count = WatchHistory.objects.filter(user_profile=profile).count()
    WatchHistory.objects.filter(user_profile=profile).delete()
    
    messages.success(request, f'Historique vidé ({count} films supprimés).')
    return redirect('watch_history')

# movies/views.py
from django.http import JsonResponse

@login_required
def check_watch_history(request, movie_id):
    """Vérifier si un film est dans l'historique de l'utilisateur"""
    try:
        movie = get_object_or_404(Movie, pk=movie_id)
        profile = get_or_create_profile(request.user)
        
        history_item = WatchHistory.objects.filter(
            user_profile=profile,
            movie=movie
        ).first()
        
        if history_item:
            return JsonResponse({
                'in_history': True,
                'completed': history_item.completed,
                'duration_watched': history_item.duration_watched,
                'last_watched': history_item.watched_at.strftime('%d/%m/%Y %H:%M')
            })
        else:
            return JsonResponse({
                'in_history': False
            })
    except Exception as e:
        return JsonResponse({
            'in_history': False,
            'error': str(e)
        })




