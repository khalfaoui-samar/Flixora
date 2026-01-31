Flixora – Site de streaming de films, séries et animes



Description du projet

Flixora est une plateforme web de streaming inspirée de Netflix. Elle permet aux utilisateurs de :

- Parcourir et rechercher des films, séries et animes.
- Filtrer les contenus par catégories (comédie, action, horreur…).
- Regarder des films en ligne, écrire des commentaires, noter les films, télécharger ou partager le lien sur WhatsApp, Facebook ou Twitter.
- Gérer un compte utilisateur : profil, bio, photo de profil, liste de favoris, historique et corbeille.

L’objectif du projet est de fournir une expérience utilisateur complète pour la gestion et la visualisation de contenus multimédias, tout en intégrant des fonctionnalités sociales et de personnalisation.




✨ Fonctionnalités

1️⃣ Accueil / Interface principale

Liste des films, séries et animes.
Barre de recherche par titre ou mot-clé.
Filtrage par catégories.
Options au survol d’un film :
Regarder le film (lecture directe sans connexion).
Ajouter aux favoris (connexion obligatoire).

2️⃣ Lecture du contenu

Lecture en streaming.
Ajouter des commentaires.
Mettre une note (rating).
Télécharger le film.
Partager via WhatsApp, Facebook ou Twitter.

3️⃣ Gestion du profil utilisateur

Liste des favoris.
Modifier profil : photo et bio.
Voir l’historique des films visionnés.
vider l’historique ou supprimer certains éléments.

4️⃣ Authentification

Connexion / Inscription.
Seuls les utilisateurs connectés peuvent ajouter des favoris et gérer leur profil.


---


## Aperçu du site

### Page d'accueil
![Page d'accueil](screenshots/accueil.png)

### Interface pour les films
![Interface films](screenshots/Interface_film.png)

### Interface pour les animes
![Interface animes](screenshots/Interface_Anime.png)

### Interface pour les séries
![Interface séries](screenshots/Interface_Series.png)

### Authentification
![Login](screenshots/login.png)
![Register](screenshots/register.png)

### Lecture d'un film
![Lecture 1](screenshots/1.png)
![Lecture 2](screenshots/2.png)

### Profil
![Profil](screenshots/profile.png)

### Historique
![Historique](screenshots/historique.png)

---

💻 Technologies utilisées

Python 3.x
Django 6.x
HTML / CSS / JavaScript
SQLite / PostgreSQL (selon configuration)
Bootstrap (pour le design)

---

## 🚀 Installation et lancement

1. Cloner le projet :

```bash
git clone https://github.com/ton-utilisateur/Flixora.git
cd Flixora
```

2. Créer un environnement virtuel et installer Django :

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install django
```

3. Appliquer les migrations :
```bash
python manage.py migrate
```

4. Créer un super utilisateur :
```bash
python manage.py createsuperuser
```

5. Lancer le serveur :

```bash
python manage.py runserver
```
Ouvrir le navigateur sur : http://127.0.0.1:8000/

---

✨ Auteur

Samar Khalfaoui Email : khalfaouisamar86@gmail.com github : https://github.com/khalfaoui-samar