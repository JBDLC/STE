#!/usr/bin/env python3
"""
Script de migration des données de SQLite vers PostgreSQL
Utilisez ce script pour transférer vos données existantes
"""

import os
import sys
from datetime import datetime

# Configuration pour SQLite (source)
SQLITE_DB_PATH = 'ste_releve.db'
if os.path.exists('instance/ste_releve.db'):
    SQLITE_DB_PATH = 'instance/ste_releve.db'

def migrate_data():
    """Migre les données de SQLite vers PostgreSQL"""
    
    print("🔄 Début de la migration SQLite → PostgreSQL")
    print(f"📁 Base SQLite source: {SQLITE_DB_PATH}")
    
    if not os.path.exists(SQLITE_DB_PATH):
        print(f"❌ Erreur: Base SQLite non trouvée à {SQLITE_DB_PATH}")
        return False
    
    try:
        # Importer les modèles et créer les connexions
        from app import app, db, User, Site, TypeReleve, Releve, PhotoReleve, FormulaireRoutine, QuestionRoutine, ReponseRoutine, UserPageAccess
        
        with app.app_context():
            # Créer les tables PostgreSQL
            print("📋 Création des tables PostgreSQL...")
            db.create_all()
            
            # Connexion SQLite
            import sqlite3
            sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
            sqlite_cursor = sqlite_conn.cursor()
            
            # Migrer les utilisateurs
            print("👥 Migration des utilisateurs...")
            sqlite_cursor.execute("SELECT id, username, password_hash, role FROM user")
            users = sqlite_cursor.fetchall()
            for user_data in users:
                user = User.query.get(user_data[0])
                if not user:
                    user = User(
                        id=user_data[0],
                        username=user_data[1],
                        password_hash=user_data[2],
                        role=user_data[3]
                    )
                    db.session.add(user)
            
            # Migrer les sites
            print("🏭 Migration des sites...")
            sqlite_cursor.execute("SELECT id, nom, description FROM site")
            sites = sqlite_cursor.fetchall()
            for site_data in sites:
                site = Site.query.get(site_data[0])
                if not site:
                    site = Site(
                        id=site_data[0],
                        nom=site_data[1],
                        description=site_data[2]
                    )
                    db.session.add(site)
            
            # Migrer les types de relevé
            print("📊 Migration des types de relevé...")
            sqlite_cursor.execute("SELECT id, nom, site_id, type_mesure, unite, frequence, jour_specifique FROM type_releve")
            types_releve = sqlite_cursor.fetchall()
            for type_data in types_releve:
                type_releve = TypeReleve.query.get(type_data[0])
                if not type_releve:
                    type_releve = TypeReleve(
                        id=type_data[0],
                        nom=type_data[1],
                        site_id=type_data[2],
                        type_mesure=type_data[3],
                        unite=type_data[4],
                        frequence=type_data[5],
                        jour_specifique=type_data[6]
                    )
                    db.session.add(type_releve)
            
            # Migrer les relevés
            print("📈 Migration des relevés...")
            sqlite_cursor.execute("SELECT id, date, type_releve_id, valeur, utilisateur_id, commentaire, created_at FROM releve")
            releves = sqlite_cursor.fetchall()
            for releve_data in releves:
                releve = Releve.query.get(releve_data[0])
                if not releve:
                    releve = Releve(
                        id=releve_data[0],
                        date=datetime.strptime(releve_data[1], '%Y-%m-%d').date() if isinstance(releve_data[1], str) else releve_data[1],
                        type_releve_id=releve_data[2],
                        valeur=releve_data[3],
                        utilisateur_id=releve_data[4],
                        commentaire=releve_data[5],
                        created_at=datetime.fromisoformat(releve_data[6]) if releve_data[6] else datetime.utcnow()
                    )
                    db.session.add(releve)
            
            # Migrer les photos
            print("📸 Migration des photos...")
            sqlite_cursor.execute("SELECT id, date, site_id, nom_debitmetre, fichier_photo, utilisateur_id, commentaire, session_id, created_at FROM photo_releve")
            photos = sqlite_cursor.fetchall()
            for photo_data in photos:
                photo = PhotoReleve.query.get(photo_data[0])
                if not photo:
                    photo = PhotoReleve(
                        id=photo_data[0],
                        date=datetime.strptime(photo_data[1], '%Y-%m-%d').date() if isinstance(photo_data[1], str) else photo_data[1],
                        site_id=photo_data[2],
                        nom_debitmetre=photo_data[3],
                        fichier_photo=photo_data[4],
                        utilisateur_id=photo_data[5],
                        commentaire=photo_data[6],
                        session_id=photo_data[7] or f"migrated_{photo_data[0]}",
                        created_at=datetime.fromisoformat(photo_data[8]) if photo_data[8] else datetime.utcnow()
                    )
                    db.session.add(photo)
            
            # Migrer les formulaires de routine
            print("📝 Migration des formulaires de routine...")
            sqlite_cursor.execute("SELECT id, nom, created_at FROM formulaire_routine")
            formulaires = sqlite_cursor.fetchall()
            for form_data in formulaires:
                formulaire = FormulaireRoutine.query.get(form_data[0])
                if not formulaire:
                    formulaire = FormulaireRoutine(
                        id=form_data[0],
                        nom=form_data[1],
                        created_at=datetime.fromisoformat(form_data[2]) if form_data[2] else datetime.utcnow()
                    )
                    db.session.add(formulaire)
            
            # Migrer les questions de routine
            print("❓ Migration des questions de routine...")
            sqlite_cursor.execute("SELECT id, formulaire_id, id_question, lieu, question, ordre, created_at FROM question_routine")
            questions = sqlite_cursor.fetchall()
            for question_data in questions:
                question = QuestionRoutine.query.get(question_data[0])
                if not question:
                    question = QuestionRoutine(
                        id=question_data[0],
                        formulaire_id=question_data[1],
                        id_question=question_data[2],
                        lieu=question_data[3],
                        question=question_data[4],
                        ordre=question_data[5],
                        created_at=datetime.fromisoformat(question_data[6]) if question_data[6] else datetime.utcnow()
                    )
                    db.session.add(question)
            
            # Migrer les réponses de routine
            print("✅ Migration des réponses de routine...")
            sqlite_cursor.execute("SELECT id, formulaire_id, question_id, reponse, commentaire, photo_path, date_creation, heure_creation, utilisateur_id, created_at FROM reponse_routine")
            reponses = sqlite_cursor.fetchall()
            for reponse_data in reponses:
                reponse = ReponseRoutine.query.get(reponse_data[0])
                if not reponse:
                    reponse = ReponseRoutine(
                        id=reponse_data[0],
                        formulaire_id=reponse_data[1],
                        question_id=reponse_data[2],
                        reponse=reponse_data[3],
                        commentaire=reponse_data[4],
                        photo_path=reponse_data[5],
                        date_creation=datetime.strptime(reponse_data[6], '%Y-%m-%d').date() if isinstance(reponse_data[6], str) else reponse_data[6],
                        heure_creation=datetime.strptime(reponse_data[7], '%H:%M:%S').time() if isinstance(reponse_data[7], str) else reponse_data[7],
                        utilisateur_id=reponse_data[8],
                        created_at=datetime.fromisoformat(reponse_data[9]) if reponse_data[9] else datetime.utcnow()
                    )
                    db.session.add(reponse)
            
            # Migrer les droits d'accès
            print("🔐 Migration des droits d'accès...")
            sqlite_cursor.execute("SELECT id, user_id, page_name, can_access FROM user_page_access")
            accesses = sqlite_cursor.fetchall()
            for access_data in accesses:
                access = UserPageAccess.query.get(access_data[0])
                if not access:
                    access = UserPageAccess(
                        id=access_data[0],
                        user_id=access_data[1],
                        page_name=access_data[2],
                        can_access=bool(access_data[3])
                    )
                    db.session.add(access)
            
            # Valider toutes les migrations
            print("💾 Sauvegarde des données migrées...")
            db.session.commit()
            
            # Fermer la connexion SQLite
            sqlite_conn.close()
            
            print("✅ Migration terminée avec succès !")
            print(f"📊 Données migrées :")
            print(f"   - {len(users)} utilisateurs")
            print(f"   - {len(sites)} sites")
            print(f"   - {len(types_releve)} types de relevé")
            print(f"   - {len(releves)} relevés")
            print(f"   - {len(photos)} photos")
            print(f"   - {len(formulaires)} formulaires de routine")
            print(f"   - {len(questions)} questions de routine")
            print(f"   - {len(reponses)} réponses de routine")
            print(f"   - {len(accesses)} droits d'accès")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return False

if __name__ == "__main__":
    success = migrate_data()
    sys.exit(0 if success else 1) 