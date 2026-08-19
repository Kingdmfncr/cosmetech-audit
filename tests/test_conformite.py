"""Tests unitaires : détection des allergènes réglementaires et agrégation."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import conformite


def test_detecter_allergenes_trouve_un_ingredient_present():
    texte = "AQUA, GLYCERIN, LINALOOL, PARFUM"
    resultats = conformite.detecter_allergenes(texte)
    assert "Linalool" in resultats


def test_detecter_allergenes_insensible_a_la_casse():
    texte = "aqua, linalool, geraniol"
    resultats = conformite.detecter_allergenes(texte)
    assert "Linalool" in resultats and "Geraniol" in resultats


def test_detecter_allergenes_ne_trouve_rien_si_absent():
    texte = "AQUA, GLYCERIN, SODIUM CHLORIDE"
    assert conformite.detecter_allergenes(texte) == []


def test_detecter_allergenes_texte_vide():
    assert conformite.detecter_allergenes("") == []
    assert conformite.detecter_allergenes(None) == []


def test_liste_officielle_contient_26_substances():
    assert len(conformite.ALLERGENES_UE_26) == 26
    assert len(set(conformite.ALLERGENES_UE_26)) == 26  # pas de doublon


def test_auditer_dataframe_ajoute_les_colonnes():
    df = pd.DataFrame({
        "nom_produit": ["A", "B"],
        "ingredients_text": ["AQUA, LINALOOL, LIMONENE", "AQUA, GLYCERIN"],
    })
    resultat = conformite.auditer_dataframe(df)
    assert resultat.loc[0, "nb_allergenes"] == 2
    assert resultat.loc[1, "nb_allergenes"] == 0
    assert set(resultat.loc[0, "allergenes_detectes"]) == {"Linalool", "Limonene"}


def test_top_allergenes_classe_par_frequence():
    df = pd.DataFrame({
        "allergenes_detectes": [
            ["Linalool", "Limonene"],
            ["Linalool"],
            ["Coumarin"],
        ]
    })
    resultat = conformite.top_allergenes(df, n=5)
    assert resultat[0] == ("Linalool", 2)
