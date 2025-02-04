# README

## Case technique : Récupération de données depuis Odoo et API FastAPI

Pour ce case j’ai du réaliser 2 taches, la première consistait à faire un script qui récupérait les factures et les contacts d’une base de données Odoo via leur API, et la seconde consistait à créer une API avec FastAPI.

## Exécution du projet

Il est recommandé de créer un environnement Python avant de lancer le projet.
J'ai également mis à votre disposition un fichier `commandes.txt` qui contient toutes les commandes que j'ai effectuées pour ce projet.

---

## 1. L’API FastAPI

- **URL publique** : [https://case-chift.onrender.com/docs#/](https://case-chift.onrender.com/docs)
- **Run en local** (installer les librairies au préalable) :
  ```bash
  uvicorn main:app --reload
  ```

### 1.1 La structure du projet

Pour cette API j’ai décidé de la structurer de la façon suivante :

- `models/` : comprend les différents modèles, dans notre cas Facture et Contact.
- `schemas/` : contient les schémas de mes modèles que j’utilise ensuite en argument de mes endpoints POST pour créer des contacts et factures.
- `controller/` : contient mes fichiers controller, c’est-à-dire les fichiers qui contiennent la logique de mes endpoints. J’ai fait un fichier controller pour les contacts et un pour les factures. Actuellement, les deux ont une logique identique, mais si à l’avenir on veut avoir des comportements différents pour les endpoints des différents modèles, ce sera plus clair de séparer leur logique.
- `utils/` : regroupe les fichiers utilitaires.
- `tests/` : contient mes fichiers de tests. J’utilise pytest. (Run `pytest` depuis le dossier principal pour les lancer)
- `config.py` : utilisé pour récupérer mes variables d’environnement.
- `db.py` : permet de faire le lien entre mon API et ma base de données.
- `main.py` : crée une instance de l’application FastAPI et définit les routes vers mes controllers.
- `requirements.txt` : liste des bibliothèques externes nécessaires au projet. Il est utilisé pour indiquer au serveur quelles librairies installer ainsi que leur version lors du déploiement et des tests effectués par les actions GitHub.
- `.env` : non présent sur GitHub car il contient toutes mes clés secrètes. Il contient l’URL de ma base de données. J’utilise une URL pour la base de données locale et une pour la base de production. J’ai également une clé secrète qui me permet de sécuriser mon API.

Exemple de clé secrète (pour tests) :
```ini
MYSECRET_API_KEY="supersecretkey"
```

### 1.2 La base de données

J’ai choisi de travailler avec une base de données PostgreSQL, c’est le type de base de données avec lequel j’ai l’habitude de bosser, c’est donc un choix que j’ai fait par facilité. Je savais que je n’allais pas rencontrer trop de problèmes lors de son déploiement avec Supabase. Pour gérer les migrations de la base de données, j’utilise Alembic.

### 1.3 La sécurité de l’API

Pour sécuriser mon API, j’ai fait le choix d’utiliser une clé API dans le header de mes requêtes.
Cela se manifeste lors de l’instanciation de mon application :
```python
app = FastAPI(
    swagger_ui_parameters={"persistAuthorization": True}
)
```
Mais c’est également précisé dans les dépendances de mes endpoints (voir `controller/`). Les détails sont dans le fichier `utils.py`.

### 1.4 Les modèles

En ce qui concerne les modèles, j’ai choisi de ne pas définir le champ `email` du modèle Contact comme unique, car j’ai vu que l’on pouvait récupérer plusieurs contacts avec le même email via l’API Odoo. J’ai également décidé qu’il pourrait être `null` car via l’API Odoo, je récupérais des contacts sans email. À part ça, je n’ai pas fait de choix particulier.

### 1.5 Le déploiement

- **Base de données** : déployée sur Supabase gratuitement.
- **API** : déployée avec Render. J’avais deux choix : soit déployer l’API via un serveur AWS EC2, soit utiliser Render, plus simple et rapide. Render permet de préciser la branche et le dossier du projet GitHub (ici `master` et `fast_api`), d’indiquer les variables d’environnement et de fournir un fichier `requirements.txt`. Si les opérations effectuées ne sont pas trop complexes, Render déploie gratuitement le serveur en HTTPS.
- **CI/CD** : Render suit la branche `master` de mon repo GitHub, donc à chaque fois que cette branche est modifiée, le déploiement du serveur est mis à jour.
- **Tests** : Les tests unitaires doivent être impérativement réussis pour pouvoir merger une pull request à la branche `master` grâce aux GitHub Actions.

---

## 2. Le script Odoo

### 2.1 La structure

- `utils.py` : contient des fonctions utilitaires qui réduisent la redondance du code, notamment pour les interactions avec la base de données.
- `script_odoo.py` : fichier principal du script.
- `.env` : chaque projet a son fichier car chaque fichier est déployé séparément.
- `Dockerfile` : utilisé lors de la création de l’image Docker.
- `chift_case_key.pem` : permet la connexion SSH à mon serveur AWS EC2 qui gère l’automatisation du cron job toutes les X minutes.
- `requirements.txt` : liste des dépendances du projet.

### 2.2 Comment le script fonctionne

1. Récupération des variables d’environnement propres à la base de données Odoo et à la base Supabase.
2. Connexion à la base de données.
3. Authentification et connexion à l’API Odoo.
4. Gestion des contacts et des factures :
   - Récupération des données depuis Odoo.
   - Traitement des données récupérées (avec Pandas pour des opérations vectorielles).
   - Interaction avec la base de données.
5. Fermeture des connexions à la base de données.

### 2.3 Mes choix d’implémentation

- **Utilisation de Pandas** : utile pour des opérations vectorielles sur de grandes quantités de données.
- **Insertion optimisée** : utilisation de `execute_values()` pour insérer plusieurs éléments en une seule requête.
- **Conservation des IDs Odoo** : permet de synchroniser facilement les données et de supprimer celles qui ne font plus partie de la base Odoo.

### 2.4 Exécution du script

#### En local

```bash
python3 script_odoo.py
```

#### Automatisation avec cron

1. Création de l’image Docker :

```bash
docker build -t odoo_sync .
```

2. Ajout d’une tâche cron (exécution toutes les minutes) :

```cron
*/1 * * * * /usr/local/bin/docker run --rm odoo_sync >> /Users/costa/Documents/Projets_Perso/Informatique/case_chift/scripts/cron.log 2>&1
```

#### Déploiement sur AWS EC2

1. Transfert de l’image Docker sur le serveur.
2. Modification du `crontab` du serveur :

```cron
*/1 * * * * /usr/bin/docker run --rm odoo_sync >> /home/ubuntu/cron.log 2>&1
```

(J’ai arrêté l’automatisation depuis.)

---

## 3. Conclusion

J’ai passé un agréablement moment à réaliser ce case, je l’ai trouvé pertinent et intéressant. J’ai bien aimé le fait qu’il soit lié à votre activité. Il m’a permis d’utiliser Odoo pour la première fois, ainsi que de découvrir l’automatisation de tâches avec cron. J’ai hâte de recevoir vos feedbacks !

