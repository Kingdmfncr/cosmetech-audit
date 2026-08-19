"""Ingestion de produits cosmétiques réels via l'API Open Beauty Facts
(projet sœur d'Open Food Facts, licence ODbL, données déclarées par les
marques et enrichies par une communauté de contributeurs).

Source : world.openbeautyfacts.org. Aucune donnée inventée : chaque produit,
chaque liste d'ingrédients vient d'un vrai code-barres réel.
"""
import json
import time
from pathlib import Path

import pandas as pd
import requests

API_URL = "https://world.openbeautyfacts.org/api/v2/search"
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
CACHE_FILE = RAW_DIR / "produits_cosmetiques.json"

CATEGORIES = ["creams", "shampoos", "lipsticks", "deodorants", "shower-gels", "face-care"]
CHAMPS = "code,product_name,brands,categories_tags,ingredients_text,countries_tags"


def _requete_categorie(categorie, page_size=60):
    reponse = requests.get(API_URL, params={
        "categories_tags": categorie, "countries_tags": "france",
        "fields": CHAMPS, "page_size": page_size,
    }, timeout=20, headers={"User-Agent": "PortfolioPoC-CosmeTechAudit/1.0"})
    reponse.raise_for_status()
    return reponse.json().get("products", [])


def telecharger_produits(force=False):
    """Récupère de vrais produits cosmétiques sur plusieurs catégories,
    déduplique par code-barres, met en cache local (le jeu réel change peu
    d'un jour à l'autre, pas besoin de re-télécharger à chaque run)."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if not force and CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))

    produits = {}
    for categorie in CATEGORIES:
        for p in _requete_categorie(categorie):
            code = p.get("code")
            if code and code not in produits and p.get("ingredients_text"):
                p["_categorie_recherchee"] = categorie
                produits[code] = p
        time.sleep(0.3)  # ne pas marteler l'API publique

    liste = list(produits.values())
    CACHE_FILE.write_text(json.dumps(liste, ensure_ascii=False), encoding="utf-8")
    return liste


def vers_dataframe(produits):
    lignes = []
    for p in produits:
        lignes.append({
            "code_barre": p.get("code", ""),
            "nom_produit": p.get("product_name", "") or "(nom non renseigné)",
            "marque": p.get("brands", "") or "(marque non renseignée)",
            "categorie": p.get("_categorie_recherchee", ""),
            "ingredients_text": p.get("ingredients_text", "") or "",
        })
    df = pd.DataFrame(lignes)
    df = df[df["ingredients_text"].str.len() > 5]  # écarte les fiches sans liste d'ingrédients exploitable
    return df.reset_index(drop=True)


def main():
    produits = telecharger_produits()
    df = vers_dataframe(produits)
    print(f"{len(produits)} produits récupérés (Open Beauty Facts, France, {len(CATEGORIES)} catégories).")
    print(f"{len(df)} produits avec une liste d'ingrédients exploitable.")
    print(df[["nom_produit", "marque", "categorie"]].head(5).to_string())


if __name__ == "__main__":
    main()
