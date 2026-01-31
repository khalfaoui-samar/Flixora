# movies/signals.py
from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crée automatiquement un profil utilisateur lorsqu'un nouvel utilisateur est créé
    """
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Sauvegarde automatiquement le profil utilisateur
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        # Créer le profil si non existant
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_migrate)
def create_profiles_for_existing_users(sender, **kwargs):
    """
    Crée des profils pour tous les utilisateurs existants après les migrations
    """
    if sender.name == 'movies':
        for user in User.objects.all():
            UserProfile.objects.get_or_create(user=user)