# STE Relevés - Application de Gestion des Stations de Traitement des Eaux

## Description

Application web moderne et responsive pour la gestion des relevés de débits et consommations de réactifs dans les stations de traitement des eaux SMP et LPZ. L'application permet aux opérateurs de saisir quotidiennement les données avec validation dynamique et historique.

## Fonctionnalités principales

### 📊 Relevés quotidiens
- **Saisie dynamique** avec affichage du relevé précédent
- **Validation en temps réel** des données
- **Sauvegarde automatique** après saisie
- **Interface responsive** optimisée pour mobile

### 📈 Indicateurs et graphiques
- **Graphiques interactifs** avec Plotly.js
- **Calculs automatiques** des débits journaliers pour les totalisateurs
- **Statistiques** (moyenne, min, max, total)
- **Filtres par période** (7 jours, 30 jours, 3 mois, 1 an)

### 📋 Historique et export
- **Consultation historique** avec filtres avancés
- **Export Excel** avec formatage professionnel
- **Modification** des relevés existants
- **Recherche** par date, site, type de relevé

### 📸 Relevé du 20
- **Prise de photos** des débitmètres
- **Galerie photos** avec filtres
- **Téléchargement** des images
- **Historique visuel** des équipements

### 🔐 Sécurité
- **Authentification** des utilisateurs
- **Gestion des rôles** (opérateur, chef d'équipe, admin)
- **Sauvegarde** automatique des données

## Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner le projet**
```bash
git clone <url-du-repo>
cd ste_releve
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
```

3. **Activer l'environnement virtuel**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

5. **Lancer l'application**
```bash
python app.py
```

6. **Accéder à l'application**
Ouvrez votre navigateur et allez sur : `http://localhost:5000`

### Identifiants par défaut
- **Utilisateur** : `admin`
- **Mot de passe** : `admin123`

## Structure du projet

```
ste_releve/
├── app.py                 # Application principale Flask
├── requirements.txt       # Dépendances Python
├── templates/            # Templates HTML
│   ├── base.html         # Template de base
│   ├── login.html        # Page de connexion
│   ├── index.html        # Tableau de bord
│   ├── releve_site.html  # Page de relevés
│   ├── historique.html   # Page d'historique
│   ├── indicateurs.html  # Page des graphiques
│   ├── releve_20.html    # Page du relevé du 20
│   └── photos.html       # Galerie photos
├── uploads/              # Dossier des photos uploadées
└── ste_releve.db         # Base de données SQLite
```

## Utilisation

### Relevés quotidiens

1. **Accéder aux relevés**
   - Cliquez sur "Relevés SMP" ou "Relevés LPZ" dans le menu
   - L'interface affiche tous les types de relevés du site

2. **Saisir les données**
   - Entrez les valeurs dans les champs correspondants
   - Le relevé précédent est affiché pour comparaison
   - La différence est calculée automatiquement

3. **Sauvegarde**
   - Les données sont sauvegardées automatiquement
   - Un indicateur de statut confirme la sauvegarde

### Indicateurs et graphiques

1. **Sélectionner un indicateur**
   - Choisissez le type de relevé dans la liste
   - Sélectionnez la période d'analyse

2. **Visualiser les données**
   - Graphiques interactifs avec zoom et pan
   - Statistiques détaillées
   - Export des données

### Historique et export

1. **Filtrer les données**
   - Sélectionnez le site
   - Définissez la période
   - Utilisez la recherche textuelle

2. **Exporter en Excel**
   - Cliquez sur "Export Excel"
   - Le fichier est téléchargé automatiquement

### Relevé du 20

1. **Prendre une photo**
   - Sélectionnez le site et le débitmètre
   - Prenez la photo avec votre appareil
   - Ajoutez un commentaire optionnel

2. **Consulter la galerie**
   - Accédez à "Photos" dans le menu
   - Filtrez par site, date ou nom
   - Téléchargez ou supprimez les photos

## Configuration

### Base de données
L'application utilise SQLite par défaut. La base de données est créée automatiquement au premier lancement.

### Sites et types de relevés
Les sites (SMP, LPZ) et types de relevés sont initialisés automatiquement :

**SMP** : 28 types de relevés (Exhaures, Surpresseurs, pH, température, etc.)
**LPZ** : 23 types de relevés

### Types de mesures
- **Totalisateur** : Calcul automatique du débit journalier
- **Basique** : Valeur directe sans calcul
- **Hebdomadaire** : Affichage uniquement le lundi

## Déploiement en production

### Configuration serveur
```bash
# Installer gunicorn
pip install gunicorn

# Lancer en production
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Variables d'environnement
```bash
export FLASK_ENV=production
export SECRET_KEY=votre_cle_secrete_ici
```

### Base de données
Pour la production, considérez l'utilisation de PostgreSQL ou MySQL au lieu de SQLite.

## Maintenance

### Sauvegarde
- Sauvegardez régulièrement le fichier `ste_releve.db`
- Sauvegardez le dossier `uploads/` contenant les photos

### Logs
Les logs de l'application sont affichés dans la console. Pour la production, configurez un système de logging approprié.

### Mise à jour
1. Arrêtez l'application
2. Sauvegardez la base de données
3. Mettez à jour le code
4. Relancez l'application

## Support

Pour toute question ou problème :
- Vérifiez les logs de l'application
- Consultez la documentation Flask
- Contactez l'équipe de développement

## Licence

Ce projet est développé pour un usage interne. Tous droits réservés. 