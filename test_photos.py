#!/usr/bin/env python3
"""
Script de test pour vérifier les photos du relevé du 20
"""

from app import app, db, PhotoReleve, Site, User

def test_photos():
    with app.app_context():
        print("=== TEST DES PHOTOS DU RELEVE DU 20 ===")
        
        # Vérifier le nombre total de photos
        total_photos = PhotoReleve.query.count()
        print(f"Nombre total de photos en base: {total_photos}")
        
        # Lister toutes les photos
        photos = PhotoReleve.query.order_by(PhotoReleve.date.desc()).all()
        print("\nDétails des photos:")
        for photo in photos:
            # Gérer les deux formats : site_id comme entier ou comme chaîne
            site = None
            if isinstance(photo.site_id, int):
                # Nouveau format : site_id est un entier
                site = db.session.get(Site, photo.site_id)
            else:
                # Ancien format : site_id est une chaîne (nom du site)
                site = Site.query.filter_by(nom=photo.site_id).first()
            
            user = db.session.get(User, photo.utilisateur_id)
            print(f"  - ID: {photo.id}")
            print(f"    Site: {site.nom if site else 'Inconnu'}")
            print(f"    Débitmètre: {photo.nom_debitmetre}")
            print(f"    Date: {photo.date}")
            print(f"    Utilisateur: {user.username if user else 'Inconnu'}")
            print(f"    Session: {photo.session_id}")
            print(f"    Fichier: {photo.fichier_photo}")
            print()
        
        # Grouper par session
        sessions = {}
        for photo in photos:
            if photo.session_id not in sessions:
                sessions[photo.session_id] = []
            sessions[photo.session_id].append(photo)
        
        print("=== RELEVES PAR SESSION ===")
        for session_id, session_photos in sessions.items():
            if session_photos:
                first_photo = session_photos[0]
                
                # Gérer les deux formats : site_id comme entier ou comme chaîne
                site = None
                if isinstance(first_photo.site_id, int):
                    # Nouveau format : site_id est un entier
                    site = db.session.get(Site, first_photo.site_id)
                else:
                    # Ancien format : site_id est une chaîne (nom du site)
                    site = Site.query.filter_by(nom=first_photo.site_id).first()
                
                user = db.session.get(User, first_photo.utilisateur_id)
                print(f"Session: {session_id}")
                print(f"  Date: {first_photo.date}")
                print(f"  Site: {site.nom if site else 'Inconnu'}")
                print(f"  Utilisateur: {user.username if user else 'Inconnu'}")
                print(f"  Nombre de photos: {len(session_photos)}")
                print(f"  Débitmètres: {[p.nom_debitmetre for p in session_photos]}")
                print()

if __name__ == "__main__":
    test_photos() 