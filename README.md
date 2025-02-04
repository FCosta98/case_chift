# README

## Case technique : Récupération de données depuis Odoo et API FastAPI

Pour ce case, j'ai dû réaliser deux tâches :
1. Créer un script qui récupère les factures et les contacts d'une base de données Odoo via leur API.
2. Développer une API avec FastAPI.

## Exécution du projet

Il est recommandé de créer un environnement Python avant de lancer le projet.

---

## 1. L'API FastAPI

- **URL publique** : [https://case-chift.onrender.com/docs#/](https://case-chift.onrender.com/docs#/)
- **Exécution en local** (après installation des librairies) :
  ```bash
  uvicorn main:app --reload
  ```

### 1.1 Structure du projet

L'API est structurée comme suit :

- `models/` : contient les différents modèles (Facture et Contact).
- `schemas/` : définit les schémas utilisés comme arguments pour les endpoints POST.
- `controller/` : contient la logique des endpoints (un fichier pour les contacts et un pour les factures).
- `utils/` : regroupe les fichiers utilitaires.
- `tests/` : contient les tests unitaires (exécutables avec `pytest` depuis le dossier principal).
- `config.py` : gère les variables d'environnement.
- `db.py` : assure la connexion entre l'API et la base de données.
- `main.py` : crée une instance FastAPI et définit les routes vers les controllers.
- `requirements.txt` : liste des bibliothèques nécessaires au projet.
- `.env` : fichier contenant les clés secrètes et l'URL de la base de données (non versionné).

Exemple de clé secrète (pour tests) :
```ini
MYSECRET_API_KEY="supersecretkey"
```

### 1.2 Base de données

J'ai choisi PostgreSQL, une base de données avec laquelle j'ai l'habitude de travailler. Elle est déployée via Supabase. Les migrations sont gérées avec Alembic.

### 1.3 Sécurité de l'API

L'API est sécurisée avec une clé API placée dans le header des requêtes. Elle est vérifiée dans `utils.py`. L'authentification est persistante dans la documentation Swagger.

```python
app = FastAPI(swagger_ui_parameters={"persistAuthorization": True})
```

### 1.4 Modèles

- Le champ `email` du modèle Contact n'est ni unique ni obligatoire car l'API Odoo peut renvoyer plusieurs contacts avec le même email, voire sans email.

### 1.5 Déploiement

- **Base de données** : déployée sur Supabase (gratuitement).
- **API** : déployée avec Render (solution plus simple et rapide qu'un serveur AWS EC2).
- **CI/CD** : Render suit la branche `master` de mon dépôt GitHub. Toute modification de cette branche déclenche un déploiement automatique.
- **Tests** : Les tests unitaires doivent être validés avant qu'une pull request ne puisse être mergée dans `master` (via GitHub Actions).

---

## 2. Le script Odoo

### 2.1 Structure

- `utils.py` : fonctions utilitaires pour réduire la redondance du code.
- `script_odoo.py` : fichier principal du script.
- `.env` : contient les variables d'environnement (un fichier différent par projet).
- `Dockerfile` : pour la création de l'image Docker.
- `chift_case_key.pem` : clé SSH pour la connexion au serveur AWS EC2.
- `requirements.txt` : dépendances du projet.

### 2.2 Fonctionnement

1. Récupération des variables d'environnement pour Odoo et Supabase.
2. Connexion à la base de données.
3. Authentification et connexion à l'API Odoo.
4. Gestion des contacts et des factures :
   - Récupération des données depuis Odoo.
   - Traitement vectoriel avec Pandas.
   - Interaction avec la base de données.
5. Fermeture des connexions.

### 2.3 Choix d'implémentation

- **Pandas** : utile pour des opérations vectorielles sur de grandes quantités de données.
- **Insertion optimisée** : utilisation de `execute_values()` pour insérer plusieurs entrées en une seule requête.
- **Conservation des IDs Odoo** : permet de synchroniser facilement les données en supprimant les éléments obsolètes.

### 2.4 Exécution du script

#### En local

```bash
python3 script_odoo.py
```

#### Automatisation avec cron

1. Création de l'image Docker :

```bash
docker build -t odoo_sync .
```

2. Ajout d'une tâche cron (exécution toutes les minutes) :

```cron
*/1 * * * * /usr/local/bin/docker run --rm odoo_sync >> /Users/costa/Documents/Projets_Perso/Informatique/case_chift/scripts/cron.log 2>&1
```

#### Déploiement sur AWS EC2

1. Transfert de l'image Docker sur le serveur.
2. Modification du `crontab` du serveur :

```cron
*/1 * * * * /usr/bin/docker run --rm odoo_sync >> /home/ubuntu/cron.log 2>&1
```

(J'ai depuis arrêté l'automatisation.)

---

## 3. Conclusion

J'ai passé un agréable moment à réaliser ce case, que j'ai trouvé pertinent et intéressant. J'ai apprécié le lien avec votre activité, ainsi que la possibilité de découvrir Odoo et l'automatisation des tâches avec cron.

J'ai hâte de recevoir vos feedbacks !

