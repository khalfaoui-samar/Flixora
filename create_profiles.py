# create_profiles.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Flixora.settings')
django.setup()

from django.contrib.auth.models import User
from movies.models import UserProfile

print("Création des profils pour les utilisateurs existants...")

users_without_profile = []
for user in User.objects.all():
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        users_without_profile.append(user)
        UserProfile.objects.create(user=user)

if users_without_profile:
    print(f"Profils créés pour {len(users_without_profile)} utilisateurs:")
    for user in users_without_profile:
        print(f"  - {user.username}")
else:
    print("Tous les utilisateurs ont déjà un profil.")