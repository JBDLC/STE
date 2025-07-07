# 🚀 Guide de déploiement PostgreSQL sur Render

## 📋 Prérequis

- Compte Render.com
- Votre application Flask prête
- Données SQLite à migrer (optionnel)

## 🔧 Étapes de déploiement

### 1. Préparer votre code

Assurez-vous que votre `requirements.txt` contient :
```
psycopg2-binary>=2.9.0
```

### 2. Créer la base PostgreSQL sur Render

1. **Connectez-vous à Render**
2. **Cliquez sur "New" → "PostgreSQL"**
3. **Configurez :**
   - **Name** : `ste-releve-db`
   - **Database** : `ste_releve`
   - **User** : `ste_releve_user`
   - **Plan** : `Free` (1GB)

### 3. Déployer votre application

1. **Cliquez sur "New" → "Web Service"**
2. **Connectez votre repository GitHub**
3. **Configurez :**
   - **Name** : `ste-releve`
   - **Environment** : `Python 3`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn app:app`

### 4. Configurer les variables d'environnement

Dans votre service web, allez dans **Environment** et ajoutez :

```
RENDER=true
DATABASE_URL=postgresql://ste_releve_user:password@host/database
```

**Note** : L'URL DATABASE_URL est automatiquement fournie par Render.

### 5. Migrer vos données (si vous en avez)

Si vous avez des données SQLite à migrer :

```bash
# Localement, avec la base PostgreSQL configurée
python migrate_to_postgres.py
```

## 🔍 Vérification

1. **Vérifiez les logs** de votre application
2. **Testez la connexion** à la base de données
3. **Vérifiez que les données** sont bien présentes

## 🛡️ Avantages PostgreSQL

✅ **Persistance garantie** - Les données ne disparaissent jamais  
✅ **Sauvegardes automatiques** - Render gère les sauvegardes  
✅ **Performance** - Plus rapide pour de gros volumes  
✅ **Fiabilité** - Gestion des erreurs et récupération automatique  
✅ **Évolutivité** - Peut gérer des millions de relevés  

## 🔧 Configuration avancée

### Variables d'environnement recommandées

```
RENDER=true
SECRET_KEY=votre_cle_secrete_ici
FLASK_ENV=production
```

### Monitoring

- **Logs** : Disponibles dans le dashboard Render
- **Métriques** : Surveillez l'utilisation de la base
- **Sauvegardes** : Automatiques avec PostgreSQL

## 🆘 Dépannage

### Problème : Connexion refusée
- Vérifiez que la base PostgreSQL est créée
- Vérifiez l'URL de connexion
- Vérifiez les variables d'environnement

### Problème : Tables manquantes
- Vérifiez que `db.create_all()` est appelé
- Vérifiez les logs de l'application

### Problème : Migration échouée
- Vérifiez que la base SQLite existe
- Vérifiez les permissions
- Vérifiez la connexion PostgreSQL

## 📞 Support

- **Documentation Render** : https://render.com/docs
- **Documentation PostgreSQL** : https://www.postgresql.org/docs/
- **Logs de l'application** : Dashboard Render → Logs 