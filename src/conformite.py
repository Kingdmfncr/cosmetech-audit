"""Détection des allergènes de parfum à déclaration obligatoire (Annexe III,
Règlement (CE) n°1223/2009 relatif aux produits cosmétiques).

Important, pour rester honnête sur ce que ce POC mesure réellement : la
présence d'un allergène de cette liste dans les ingrédients n'est PAS une
non-conformité en soi. Le règlement impose de le DÉCLARER sur l'étiquette
au-delà d'un seuil de concentration (0,001% produits sans rinçage, 0,01%
produits à rincer) que la liste d'ingrédients seule ne permet pas de
vérifier. Ce module signale une présence à vérifier, jamais un verdict de
conformité ou de non-conformité définitif.

Note de veille réglementaire (non couverte par ce POC) : le règlement (UE)
2023/1545 étend cette liste à environ 80 substances, application prévue à
partir de juillet 2026. Seule la liste des 26 actuellement en vigueur est
implémentée ici, faute d'avoir pu vérifier la liste complète et exacte de
l'extension à date de construction de ce projet.
"""

# 26 allergènes, noms INCI, Annexe III du règlement CE 1223/2009.
ALLERGENES_UE_26 = [
    "Alpha-Isomethyl Ionone", "Amyl Cinnamal", "Amylcinnamyl Alcohol", "Anise Alcohol",
    "Benzyl Alcohol", "Benzyl Benzoate", "Benzyl Cinnamate", "Benzyl Salicylate",
    "Butylphenyl Methylpropional", "Cinnamal", "Cinnamyl Alcohol", "Citral", "Citronellol",
    "Coumarin", "Eugenol", "Evernia Prunastri Extract", "Evernia Furfuracea Extract",
    "Farnesol", "Geraniol", "Hexyl Cinnamal", "Hydroxycitronellal",
    "Hydroxyisohexyl 3-Cyclohexene Carboxaldehyde", "Isoeugenol", "Limonene", "Linalool",
    "Methyl 2-Octynoate",
]


def detecter_allergenes(ingredients_text):
    """Recherche par sous-chaîne insensible à la casse sur le texte brut des
    ingrédients (format INCI, liste séparée par virgules). Retourne la liste
    des allergènes de la liste réglementaire trouvés dans ce produit."""
    if not ingredients_text:
        return []
    texte = ingredients_text.upper()
    return [a for a in ALLERGENES_UE_26 if a.upper() in texte]


def auditer_dataframe(df):
    """Ajoute une colonne 'allergenes_detectes' (liste) et 'nb_allergenes' à
    chaque produit, sans rien filtrer ni exclure : l'audit expose, il ne
    décide pas à la place de l'utilisateur."""
    df = df.copy()
    df["allergenes_detectes"] = df["ingredients_text"].apply(detecter_allergenes)
    df["nb_allergenes"] = df["allergenes_detectes"].apply(len)
    return df


def top_allergenes(df, n=15):
    """Fréquence des allergènes détectés sur l'ensemble du jeu de produits."""
    compteur = {}
    for liste in df["allergenes_detectes"]:
        for a in liste:
            compteur[a] = compteur.get(a, 0) + 1
    return sorted(compteur.items(), key=lambda kv: kv[1], reverse=True)[:n]
