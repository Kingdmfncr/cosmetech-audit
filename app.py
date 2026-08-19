"""CosmeTech Audit : dashboard d'analyse de conformité ingrédients (secteur
cosmétique). Données réelles Open Beauty Facts, allergènes réglementaires
UE (Annexe III, règlement CE 1223/2009).
"""
import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

SRC_DIR = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(SRC_DIR))

import conformite
import ingest

C_PRIMARY = "#0071E3"
C_GOOD    = "#34C759"
C_WARNING = "#FF9F0A"
C_DANGER  = "#FF3B30"
C_SURF    = "#F5F5F7"
C_TEXT    = "#1D1D1F"
C_MUTED   = "#6E6E73"
C_BORDER  = "#E8E8ED"

CHART_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=C_TEXT, family="Inter, -apple-system, sans-serif", size=13),
    margin=dict(l=20, r=20, t=40, b=20),
)

st.set_page_config(page_title="CosmeTech Audit", page_icon="🧴",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
html, body, [class*="css"] { font-family:'Inter',-apple-system,sans-serif; }
div[data-testid="stMetricValue"] { font-size: 1.6rem; font-weight: 700; }
.stTabs [aria-selected="true"] { font-weight: 700; }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=86400, show_spinner="Récupération de produits cosmétiques réels (Open Beauty Facts)...")
def load_all():
    produits = ingest.telecharger_produits()
    df = ingest.vers_dataframe(produits)
    df = conformite.auditer_dataframe(df)
    return df


df = load_all()

with st.sidebar:
    st.markdown(
        "<div style='text-align:center;padding:12px 0;'>"
        "<div style='font-size:1.8rem;'>🧴</div>"
        f"<div style='color:{C_PRIMARY};font-size:1.0rem;font-weight:700;'>CosmeTech Audit</div>"
        f"<div style='color:{C_MUTED};font-size:0.72rem;'>Conformité ingrédients, données réelles</div>"
        "</div>", unsafe_allow_html=True)
    st.markdown(f"<hr style='border-color:{C_BORDER};'>", unsafe_allow_html=True)

    categories = ["Toutes"] + sorted(df["categorie"].unique().tolist())
    categorie_choisie = st.selectbox("Catégorie", categories)

    st.markdown(f"<hr style='border-color:{C_BORDER};'>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='background:{C_SURF};border-radius:8px;padding:10px;font-size:0.75rem;color:{C_MUTED};'>"
        "📖 <strong>Données réelles, licence ouverte</strong><br>"
        "Produits cosmétiques réels (Open Beauty Facts, licence ODbL). "
        "Liste des 26 allergènes de parfum : Annexe III, règlement (CE) "
        "n°1223/2009. Un allergène détecté signale une présence à vérifier, "
        "pas un verdict de non-conformité : la déclaration obligatoire dépend "
        "d'un seuil de concentration non visible dans la liste d'ingrédients."
        "</div>", unsafe_allow_html=True)
    st.caption("Construit avec l'IA, Gisèle Metouck")
    st.caption("[GitHub](https://github.com/Kingdmfncr)")

df_filtre = df if categorie_choisie == "Toutes" else df[df["categorie"] == categorie_choisie]

st.title("CosmeTech Audit")
st.caption("Détection des allergènes de parfum à déclaration obligatoire sur de vrais produits cosmétiques (Open Beauty Facts).")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Produits analysés", len(df_filtre))
c2.metric("Avec allergène détecté", int((df_filtre["nb_allergenes"] > 0).sum()))
taux = round(100 * (df_filtre["nb_allergenes"] > 0).mean(), 1) if len(df_filtre) else 0
c3.metric("Part concernée", f"{taux}%")
c4.metric("Moyenne allergènes/produit", round(df_filtre["nb_allergenes"].mean(), 1) if len(df_filtre) else 0)

tabs = st.tabs(["Vue d'ensemble", "Produits à vigilance", "Explorer les produits"])

with tabs[0]:
    top = conformite.top_allergenes(df_filtre)
    if top:
        noms, comptes = zip(*top)
        fig = go.Figure(go.Bar(x=list(comptes)[::-1], y=list(noms)[::-1], orientation="h", marker_color=C_PRIMARY))
        fig.update_layout(title="Allergènes les plus fréquents (sur les produits analysés)", height=420, **CHART_DEFAULTS)
        st.plotly_chart(fig, use_container_width=True, key="chart_top_allergenes")
    else:
        st.info("Aucun allergène détecté sur cette sélection.")

    rep_categorie = df_filtre["categorie"].value_counts()
    fig2 = go.Figure(go.Pie(labels=rep_categorie.index, values=rep_categorie.values, hole=0.55,
                            marker=dict(colors=[C_PRIMARY, C_GOOD, C_WARNING, C_DANGER, C_MUTED, "#A855F7"])))
    fig2.update_layout(title="Répartition par catégorie", height=340, **CHART_DEFAULTS)
    st.plotly_chart(fig2, use_container_width=True, key="chart_categories")

with tabs[1]:
    st.caption("Produits avec le plus grand nombre d'allergènes de la liste réglementaire détectés dans leur liste d'ingrédients.")
    vigilance = df_filtre.sort_values("nb_allergenes", ascending=False).head(30)
    st.dataframe(
        vigilance[["nom_produit", "marque", "categorie", "nb_allergenes", "allergenes_detectes"]],
        use_container_width=True, hide_index=True,
    )

with tabs[2]:
    recherche = st.text_input("Filtrer par nom de produit ou marque")
    df_affiche = df_filtre
    if recherche:
        masque = (df_affiche["nom_produit"].str.contains(recherche, case=False, na=False)
                  | df_affiche["marque"].str.contains(recherche, case=False, na=False))
        df_affiche = df_affiche[masque]
    st.dataframe(
        df_affiche[["nom_produit", "marque", "categorie", "nb_allergenes", "ingredients_text"]],
        use_container_width=True, hide_index=True,
    )
    st.caption(f"{len(df_affiche)} produit(s) affiché(s).")
