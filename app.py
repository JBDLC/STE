from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
import matplotlib
matplotlib.use('Agg')  # Backend non-interactif pour de meilleures performances
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime, timedelta
import hashlib
import pickle
from functools import lru_cache
import json

app = Flask(__name__)

FICHIER = "mesures.xlsx"
CACHE_DIR = "cache"
CACHE_DURATION = 3600  # 1 heure en secondes
RAPPORTS_JSON = "rapports.json"

# Créer le dossier cache s'il n'existe pas
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# Configuration matplotlib pour de meilleures performances
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 100
plt.rcParams['figure.figsize'] = (10, 5)
plt.rcParams['font.size'] = 10

def get_cache_key(site, parametre, semaine=None, annee=None, type_graph="default"):
    """Génère une clé de cache unique pour un graphique"""
    key_data = f"{site}_{parametre}_{semaine}_{annee}_{type_graph}"
    return hashlib.md5(key_data.encode()).hexdigest()

def get_cache_path(cache_key):
    """Retourne le chemin du fichier de cache"""
    return os.path.join(CACHE_DIR, f"{cache_key}.png")

def is_cache_valid(cache_path):
    """Vérifie si le cache est encore valide"""
    if not os.path.exists(cache_path):
        return False
    file_age = datetime.now().timestamp() - os.path.getmtime(cache_path)
    return file_age < CACHE_DURATION

def save_to_cache(cache_key, image_data):
    """Sauvegarde une image en cache"""
    cache_path = get_cache_path(cache_key)
    with open(cache_path, 'wb') as f:
        f.write(image_data)

def load_from_cache(cache_key):
    """Charge une image depuis le cache"""
    cache_path = get_cache_path(cache_key)
    if is_cache_valid(cache_path):
        with open(cache_path, 'rb') as f:
            return f.read()
    return None

# Définition des mesures pour chaque site
mesures_smp = [
    "Exhaure 1", "Exhaure 2", "Exhaure 3", "Exhaure 4", "Retour dessableur", "Retour Orage",
    "Rejet à l'Arc", "Surpresseur 4 pompes", "Surpresseur 7 pompes", "Entrée STE CAB",
    "Alimentation CAB", "Eau potable", "Forage", "Boue STE", "Boue STE CAB",
    "pH entrée", "pH sortie", "Température entrée", "Température sortie",
    "Conductivité sortie", "MES entrée", "MES sortie", "Coagulant", "Floculant", "CO2"
]

mesures_lpz = [
    "Exhaure 1", "Exhaure 2", "Retour dessableur", "Surpresseur BP", "Surpresseur HP",
    "Rejet à l'Arc", "Entrée STE CAB", "Alimentation CAB", "Eau de montagne", "Boue STE",
    "Boue STE CAB", "pH entrée", "pH sortie", "Température entrée", "Température sortie",
    "Conductivité sortie", "MES entrée", "MES sortie", "Coagulant", "Floculant", "CO2"
]

sites = {"SMP": mesures_smp, "LPZ": mesures_lpz}

parametres_compteurs = {
    "SMP": ["Exhaure 1", "Exhaure 2", "Exhaure 3", "Exhaure 4", "Retour dessableur", "Retour Orage",
            "Rejet à l'Arc", "Surpresseur 4 pompes", "Surpresseur 7 pompes", "Entrée STE CAB",
            "Alimentation CAB", "Eau potable", "Forage"],
    "LPZ": ["Exhaure 1", "Exhaure 2", "Retour dessableur", "Surpresseur BP", "Surpresseur HP",
            "Rejet à l'Arc", "Entrée STE CAB", "Alimentation CAB", "Eau de montagne"]
}

parametres_directs = {
    "SMP": ["Boue STE", "Boue STE CAB", "pH entrée", "pH sortie", "Température entrée", "Température sortie",
            "Conductivité sortie", "MES entrée", "MES sortie", "CO2"],
    "LPZ": ["Boue STE", "Boue STE CAB", "pH entrée", "pH sortie", "Température entrée", "Température sortie",
            "Conductivité sortie", "MES entrée", "MES sortie", "CO2"]
}

def initialiser_fichier():
    if not os.path.exists(FICHIER):
        with pd.ExcelWriter(FICHIER) as writer:
            for site, mesures in sites.items():
                pd.DataFrame(columns=["Date", "Statut"] + mesures).to_excel(writer, sheet_name=site, index=False)

@lru_cache(maxsize=10)
def charger_donnees_cached(site, timestamp):
    """Version cachée de charger_donnees avec timestamp pour invalidation"""
    if not os.path.exists(FICHIER):
        initialiser_fichier()
    try:
        return pd.read_excel(FICHIER, sheet_name=site, engine="openpyxl")
    except Exception as e:
        print(f"Erreur lors du chargement des données pour {site}: {e}")
        return pd.DataFrame(columns=["Date", "Statut"] + sites[site])

def charger_donnees(site):
    """Charge les données avec cache intelligent"""
    # Utiliser le timestamp de modification du fichier pour invalider le cache
    if os.path.exists(FICHIER):
        timestamp = int(os.path.getmtime(FICHIER))
    else:
        timestamp = 0
    return charger_donnees_cached(site, timestamp)

def nettoyer_cache_expire():
    """Nettoie automatiquement les fichiers de cache expirés"""
    try:
        for filename in os.listdir(CACHE_DIR):
            file_path = os.path.join(CACHE_DIR, filename)
            if os.path.isfile(file_path) and not is_cache_valid(file_path):
                os.remove(file_path)
    except Exception as e:
        print(f"Erreur lors du nettoyage automatique du cache: {e}")

def invalider_cache_site(site):
    """Invalide tous les caches liés à un site spécifique"""
    try:
        for filename in os.listdir(CACHE_DIR):
            if filename.startswith(hashlib.md5(site.encode()).hexdigest()[:8]):
                file_path = os.path.join(CACHE_DIR, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
    except Exception as e:
        print(f"Erreur lors de l'invalidation du cache pour {site}: {e}")

def sauvegarder_donnees(df_modifie, site):
    dfs = {}
    if os.path.exists(FICHIER):
        with pd.ExcelFile(FICHIER, engine="openpyxl") as xls:
            for sheet in xls.sheet_names:
                dfs[sheet] = xls.parse(sheet)
    else:
        initialiser_fichier()
        for s in sites:
            dfs[s] = pd.DataFrame(columns=["Date", "Statut"] + sites[s])

    dfs[site] = df_modifie

    with pd.ExcelWriter(FICHIER, engine="openpyxl", mode="w") as writer:
        for sheet, data in dfs.items():
            data.to_excel(writer, sheet_name=sheet, index=False)
    
    # Invalider le cache après sauvegarde
    charger_donnees_cached.cache_clear()
    invalider_cache_site(site)

def enregistrer_rapport(semaine, annee, site):
    """Enregistre un rapport généré dans un fichier JSON"""
    rapports = []
    if os.path.exists(RAPPORTS_JSON):
        with open(RAPPORTS_JSON, "r", encoding="utf-8") as f:
            try:
                rapports = json.load(f)
            except Exception:
                rapports = []
    # On évite les doublons exacts
    for r in rapports:
        if r["semaine"] == semaine and r["annee"] == annee and r["site"] == site:
            return
    rapports.append({
        "semaine": semaine,
        "annee": annee,
        "site": site,
        "timestamp": datetime.now().isoformat()
    })
    with open(RAPPORTS_JSON, "w", encoding="utf-8") as f:
        json.dump(rapports, f, ensure_ascii=False, indent=2)

@app.route("/rapport", methods=["GET", "POST"])
def rapport():
    sites_list = list(sites.keys())
    rapports = []
    all_rapports = []
    if os.path.exists(RAPPORTS_JSON):
        with open(RAPPORTS_JSON, "r", encoding="utf-8") as f:
            try:
                all_rapports = json.load(f)
            except Exception:
                all_rapports = []
    # Construction de la table croisée année/semaine/sites
    index = set()
    for r in all_rapports:
        index.add((int(r["annee"]), int(r["semaine"])) )
    index = sorted(index, reverse=True)
    # Pour chaque (année, semaine), on regarde si un rapport existe pour SMP et LPZ
    table_rapports = []
    for annee, semaine in index:
        ligne = {"annee": annee, "semaine": semaine}
        for site in sites_list:
            found = next((r for r in all_rapports if int(r["annee"]) == annee and int(r["semaine"]) == semaine and r["site"] == site), None)
            ligne[site] = found
        table_rapports.append(ligne)
    # Affichage d'un rapport existant via GET
    if request.method == "GET" and request.args.get("semaine") and request.args.get("annee") and request.args.get("site"):
        semaine = int(request.args.get("semaine"))
        annee = int(request.args.get("annee"))
        site = request.args.get("site")
        rapports_result = []
        mesures = sites.get(site, [])
        df = charger_donnees(site)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df[df["Statut"] == "Validé"]
        df["Annee"] = df["Date"].dt.year
        df["Semaine"] = df["Date"].dt.isocalendar().week
        for parametre in mesures:
            cache_key = get_cache_key(site, parametre, semaine, annee, "rapport")
            cached_image = load_from_cache(cache_key)
            if cached_image:
                plot_url = base64.b64encode(cached_image).decode()
                rapports_result.append({"site": site, "parametre": parametre, "plot": plot_url})
                continue
        return render_template("rapport_resultat.html", rapports=rapports_result, semaine=semaine, annee=annee)
    # Génération d'un rapport via POST
    if request.method == "POST":
        semaine = int(request.form["semaine"])
        annee = int(request.form["annee"])
        site = request.form["site"]
        rapports_result = []
        for s, mesures in sites.items():
            if s != site:
                continue
            df = charger_donnees(site)
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df = df[df["Statut"] == "Validé"]
            df["Annee"] = df["Date"].dt.year
            df["Semaine"] = df["Date"].dt.isocalendar().week
            for parametre in mesures:
                cache_key = get_cache_key(site, parametre, semaine, annee, "rapport")
                cached_image = load_from_cache(cache_key)
                if cached_image:
                    plot_url = base64.b64encode(cached_image).decode()
                    rapports_result.append({"site": site, "parametre": parametre, "plot": plot_url})
                    continue
                img = io.BytesIO()
                if parametre in ["Coagulant", "Eau potable"]:
                    df_annuel = df[(df["Date"].dt.year == datetime.now().year) & (df["Date"].dt.weekday == 0)]
                    df_annuel["Semaine"] = df_annuel["Date"].dt.isocalendar().week
                    valeurs = pd.to_numeric(df_annuel[parametre], errors="coerce").fillna(0)
                    semaines = df_annuel["Semaine"]
                    plt.figure(figsize=(8, 4))
                    plt.plot(semaines, valeurs, marker="o")
                    plt.title(f"{site} - {parametre} (année en cours)")
                    plt.xlabel("Semaine")
                    plt.xticks(semaines, ["S" + str(s) for s in semaines])
                    plt.tight_layout()
                elif parametre == "Floculant":
                    df_floc = df[df["Date"].dt.year == datetime.now().year]
                    df_floc["Semaine"] = df_floc["Date"].dt.isocalendar().week
                    df_floc[parametre] = pd.to_numeric(df_floc[parametre], errors="coerce").fillna(0)
                    df_floc = df_floc.groupby("Semaine")[parametre].sum().reset_index()
                    plt.figure(figsize=(8, 4))
                    plt.plot(df_floc["Semaine"], df_floc[parametre], marker="o")
                    plt.title(f"{site} - Floculant hebdo (année en cours)")
                    plt.xlabel("Semaine")
                    plt.xticks(df_floc["Semaine"], ["S" + str(s) for s in df_floc["Semaine"]])
                    plt.tight_layout()
                elif parametre in parametres_compteurs[site]:
                    df_semaine = df[(df["Annee"] == annee) & (df["Semaine"] == semaine)]
                    valeurs = pd.to_numeric(df_semaine[parametre], errors="coerce").fillna(0).diff().fillna(0)
                    dates = df_semaine["Date"].dt.date
                    plt.figure(figsize=(8, 4))
                    plt.plot(dates, valeurs, marker="o")
                    plt.title(f"{site} - Delta {parametre}")
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                elif parametre in parametres_directs[site]:
                    df_semaine = df[(df["Annee"] == annee) & (df["Semaine"] == semaine)]
                    valeurs = pd.to_numeric(df_semaine[parametre], errors="coerce").fillna(0)
                    dates = df_semaine["Date"].dt.date
                    plt.figure(figsize=(8, 4))
                    plt.plot(dates, valeurs, marker="o")
                    plt.title(f"{site} - {parametre}")
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                else:
                    continue
                plt.savefig(img, format="png", dpi=100, bbox_inches='tight')
                img.seek(0)
                image_data = img.read()
                save_to_cache(cache_key, image_data)
                plot_url = base64.b64encode(image_data).decode()
                plt.close()
                rapports_result.append({"site": site, "parametre": parametre, "plot": plot_url})
        enregistrer_rapport(semaine, annee, site)
        # Après génération, recharger la table croisée
        if os.path.exists(RAPPORTS_JSON):
            with open(RAPPORTS_JSON, "r", encoding="utf-8") as f:
                try:
                    all_rapports = json.load(f)
                except Exception:
                    all_rapports = []
            index = set()
            for r in all_rapports:
                index.add((int(r["annee"]), int(r["semaine"])) )
            index = sorted(index, reverse=True)
            table_rapports = []
            for annee_, semaine_ in index:
                ligne = {"annee": annee_, "semaine": semaine_}
                for site_ in sites_list:
                    found = next((r for r in all_rapports if int(r["annee"]) == annee_ and int(r["semaine"]) == semaine_ and r["site"] == site_), None)
                    ligne[site_] = found
                table_rapports.append(ligne)
        return render_template("rapport_form.html", table_rapports=table_rapports, sites=sites_list, just_generated=True, semaine=semaine, annee=annee)
    return render_template("rapport_form.html", table_rapports=table_rapports, sites=sites_list)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/saisie/<site>", methods=["GET", "POST"])
def saisie(site):
    mesures = sites[site]
    df = charger_donnees(site)
    today_date = datetime.now()
    today_str = today_date.strftime("%Y-%m-%d")

    yesterday = (today_date - timedelta(days=1)).strftime("%Y-%m-%d")
    veille = df[(df["Date"] == yesterday) & (df["Statut"] == "Validé")]

    valeurs_veille = {}
    for m in mesures:
        valeurs_veille[m] = ""
        if not veille.empty:
            valeurs_veille[m] = veille[m].iloc[-1]

    brouillon = df[(df["Date"] == today_str) & (df["Statut"] == "Brouillon")]
    valide = df[(df["Date"] == today_str) & (df["Statut"] == "Validé")]

    if request.method == "POST":
        if "choix" in request.form:
            choix = request.form["choix"]
            if choix == "annuler":
                return redirect("/")
            elif choix == "ecraser":
                valid_today = df[(df["Date"] == today_str) & (df["Statut"] == "Validé")]
                if not valid_today.empty:
                    last_idx = valid_today.index[-1]
                    df = df.drop(last_idx)
                sauvegarder_donnees(df, site)
                return redirect(url_for("saisie", site=site))
            elif choix == "nouveau":
                ligne = {"Date": today_str, "Statut": "Brouillon"}
                for m in mesures:
                    ligne[m] = ""
                df.loc[len(df)] = ligne
                sauvegarder_donnees(df, site)
                return redirect(url_for("saisie", site=site))
            elif choix == "modifier":
                valid_today = df[(df["Date"] == today_str) & (df["Statut"] == "Validé")]
                if not valid_today.empty:
                    last_idx = valid_today.index[-1]
                    df.loc[last_idx, "Statut"] = "Brouillon"
                    sauvegarder_donnees(df, site)
                return redirect(url_for("saisie", site=site))

        ligne = {"Date": today_str, "Statut": "Brouillon"}
        for m in mesures:
            if m in ["Coagulant", "Eau potable"] and today_date.weekday() != 0:
                ligne[m] = ""
            else:
                ligne[m] = request.form.get(m) or ""

        if not brouillon.empty:
            idx = brouillon.index[0]
            for k, v in ligne.items():
                if k in ["Coagulant", "Eau potable"] and today_date.weekday() != 0:
                    df.loc[idx, k] = ""
                else:
                    df.loc[idx, k] = v
        else:
            df.loc[len(df)] = ligne

        if "finaliser" in request.form:
            df.loc[(df["Date"] == today_str) & (df["Statut"] == "Brouillon"), "Statut"] = "Validé"

        sauvegarder_donnees(df, site)
        message = "Mesure validée." if "finaliser" in request.form else "Brouillon sauvegardé."
        return render_template("confirmation.html", message=message)

    valeurs = {}
    if not brouillon.empty:
        valeurs = brouillon.iloc[0].fillna("").to_dict()
    elif not valide.empty:
        n = len(valide) + 1
        return render_template("alerte.html", site=site, n=n)

    valeurs_diff = {}
    for m in mesures:
        try:
            veille_val = float(valeurs_veille.get(m, 0)) or 0
            saisie_val = float(valeurs.get(m, 0)) or 0
            valeurs_diff[m] = saisie_val - veille_val
        except:
            valeurs_diff[m] = ""

    is_monday = today_date.weekday() == 0
    return render_template("saisie.html", site=site, mesures=mesures, valeurs=valeurs,
                           valeurs_veille=valeurs_veille, valeurs_diff=valeurs_diff, is_monday=is_monday)

@app.route("/visualisation", methods=["GET", "POST"])
def visualisation():
    sites_list = list(sites.keys())
    mesures_par_site = sites
    plot_url = None

    if request.method == "POST":
        site = request.form["site"]
        parametre = request.form["parametre"]
        semaine = request.form.get("semaine")
        annee = request.form.get("annee")

        # Générer une clé de cache unique pour ce graphique
        cache_key = get_cache_key(site, parametre, semaine, annee, "visualisation")
        
        # Vérifier si le graphique est en cache
        cached_image = load_from_cache(cache_key)
        if cached_image:
            plot_url = base64.b64encode(cached_image).decode()
        else:
            df = charger_donnees(site)
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df = df.dropna(subset=["Date"])
            df = df[df["Statut"] == "Validé"]
            df = df.sort_values("Date")

            # Filtrer par année si spécifiée, sinon utiliser l'année courante
            if annee:
                df = df[df["Date"].dt.year == int(annee)]
            else:
                current_year = datetime.now().year
                df = df[df["Date"].dt.year == current_year]

            # Filtrer par semaine si spécifiée
            if semaine and parametre not in ["Coagulant", "Eau potable", "Floculant"]:
                df["Semaine"] = df["Date"].dt.isocalendar().week
                df = df[df["Semaine"] == int(semaine)]

            if parametre in ["Coagulant", "Eau potable"]:
                df = df[df["Date"].dt.weekday == 0]
                df["Semaine"] = df["Date"].dt.isocalendar().week
                semaines = df["Semaine"].tolist()
                valeurs = pd.to_numeric(df[parametre], errors="coerce").fillna(0).tolist()
                titre = f"{parametre} hebdomadaire ({site})"

                plt.figure(figsize=(10, 5))
                plt.plot(semaines, valeurs, marker="o")
                plt.title(titre)
                plt.xlabel("Semaine")
                plt.ylabel(parametre)
                plt.xticks(semaines, ["S" + str(s) for s in semaines])
                plt.tight_layout()

            elif parametre == "Floculant":
                df["Semaine"] = df["Date"].dt.isocalendar().week
                df[parametre] = pd.to_numeric(df[parametre], errors="coerce").fillna(0)
                df_semaine = df.groupby("Semaine")[parametre].sum().reset_index()
                semaines = df_semaine["Semaine"].tolist()
                valeurs = df_semaine[parametre].tolist()
                titre = f"Consommation hebdomadaire de {parametre} ({site})"

                plt.figure(figsize=(10, 5))
                plt.plot(semaines, valeurs, marker="o")
                plt.title(titre)
                plt.xlabel("Semaine")
                plt.ylabel("Consommation")
                plt.xticks(semaines, ["S" + str(s) for s in semaines])
                plt.tight_layout()

            elif parametre in parametres_compteurs.get(site, []):
                df[parametre] = pd.to_numeric(df[parametre], errors='coerce').fillna(0)
                df["Delta"] = df[parametre].diff().fillna(0)
                dates = df["Date"].dt.date.tolist()
                valeurs = df["Delta"].tolist()
                titre = f"Variation journalière de {parametre} - {site}"

                plt.figure(figsize=(10, 5))
                plt.plot(dates, valeurs, marker="o")
                plt.title(titre)
                plt.xticks(rotation=45)
                plt.tight_layout()

            else:
                dates = df["Date"].dt.date.tolist()
                valeurs = pd.to_numeric(df[parametre], errors="coerce").fillna(0).tolist()
                titre = f"Mesure de {parametre} - {site}"

                plt.figure(figsize=(10, 5))
                plt.plot(dates, valeurs, marker="o")
                plt.title(titre)
                plt.xticks(rotation=45)
                plt.tight_layout()

            img = io.BytesIO()
            plt.savefig(img, format="png", dpi=100, bbox_inches='tight')
            img.seek(0)
            image_data = img.read()
            
            # Sauvegarder en cache
            save_to_cache(cache_key, image_data)
            
            plot_url = base64.b64encode(image_data).decode()
            plt.close()

    return render_template("visualisation.html", 
                           sites=sites_list, 
                           mesures_par_site=mesures_par_site,
                           plot_url=plot_url)

@app.route("/nettoyer_cache")
def nettoyer_cache():
    """Route pour nettoyer manuellement le cache"""
    try:
        for filename in os.listdir(CACHE_DIR):
            file_path = os.path.join(CACHE_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        return "Cache nettoyé avec succès"
    except Exception as e:
        return f"Erreur lors du nettoyage du cache: {e}"

@app.route("/rapports")
def rapports_liste():
    rapports = []
    if os.path.exists(RAPPORTS_JSON):
        with open(RAPPORTS_JSON, "r", encoding="utf-8") as f:
            try:
                rapports = json.load(f)
            except Exception:
                rapports = []
    # Tri par année, semaine, site
    rapports = sorted(rapports, key=lambda r: (r["annee"], r["semaine"], r["site"]))
    return render_template("rapports.html", rapports=rapports)

@app.route("/supprimer_rapport")
def supprimer_rapport():
    site = request.args.get("site")
    semaine = request.args.get("semaine")
    annee = request.args.get("annee")
    if not (site and semaine and annee):
        return redirect(url_for("rapport"))
    # Charger et filtrer la bibliothèque
    if os.path.exists(RAPPORTS_JSON):
        with open(RAPPORTS_JSON, "r", encoding="utf-8") as f:
            try:
                rapports = json.load(f)
            except Exception:
                rapports = []
        rapports = [r for r in rapports if not (str(r["site"]) == str(site) and str(r["semaine"]) == str(semaine) and str(r["annee"]) == str(annee))]
        with open(RAPPORTS_JSON, "w", encoding="utf-8") as f:
            json.dump(rapports, f, ensure_ascii=False, indent=2)
    # (Optionnel) supprimer le cache associé
    # Rediriger vers la page rapport avec le site sélectionné
    return redirect(url_for("rapport", site=site))

if __name__ == "__main__":
    # Nettoyer le cache expiré au démarrage
    nettoyer_cache_expire()
    
    # Configuration pour la production
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 3600  # Cache statique 1 heure
    
    app.run(debug=True, host='0.0.0.0', port=5000)
