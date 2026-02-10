import streamlit as st
import pandas as pd
from collections import defaultdict

st.set_page_config(page_title="Katharineum Profilwahl Simulator", layout="wide")

# ────────────────────────────────────────────────
#  STUNDEN-DICT aus deinen Tabellen (exakt übernommen, keine "13")
# ────────────────────────────────────────────────
halbjahre = ["E1", "E2", "Q1.1", "Q1.2", "Q2.1", "Q2.2"]

stunden_basis = {
    # Profilfach (immer 4 in E, 5 in Q – blau in allen Tabellen)
    "Profilfach":          {"E1":4, "E2":4, "Q1.1":5, "Q1.2":5, "Q2.1":5, "Q2.2":5},
    
    # Kernfächer DE/MA/FS (meist 3 durchgängig – gelb/orange/rot)
    "Deutsch":             {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Mathematik":          {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Kernfremdsprache":    {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    
    # FS / MINT / NW (orange/gelb – fast immer 3)
    "Englisch":            {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Latein":              {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Französisch":         {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Griechisch":          {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Physik":              {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Chemie":              {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Biologie":            {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Informatik":          {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    
    # WP / Ge / Ek / Re/Phi / Ku/Mu / Sp (grün/rot – meist 2)
    "Geografie":           {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Wirtschaft/Politik":  {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Religion":            {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Philosophie":         {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Kunst":               {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Musik":               {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Darstellendes Spiel": {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    
    # Seminare (variabel – aus Summen abgeleitet)
    "Profilseminar":       {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Berufliche Orient.":  {"E1":1, "E2":1, "Q1.1":3, "Q1.2":3, "Q2.1":0, "Q2.2":0},
}

# Profil-spezifische Profilfächer
profil_faecher = {
    "Sprachliches Profil": ["Latein", "Englisch"],
    "Naturwissenschaftliches Profil": ["Physik"],
    "Gesellschaftswissenschaftliches Profil": ["Geschichte"],
    "Ästhetisches Profil": ["Musik", "Kunst"],
}

# Verfügbare WP-Fächer pro Profil (kein DS im Physik-Profil)
wp_optionen = {
    "Sprachliches Profil": ["Geografie", "Wirtschaft/Politik", "Darstellendes Spiel"],
    "Naturwissenschaftliches Profil": ["Geografie", "Wirtschaft/Politik"],
    "Gesellschaftswissenschaftliches Profil": ["Geografie", "Wirtschaft/Politik", "Darstellendes Spiel"],
    "Ästhetisches Profil": ["Geografie", "Wirtschaft/Politik", "Darstellendes Spiel"],
}

st.title("Katharineum Lübeck – Profilwahl-Simulator")

st.markdown("**Wähle dein Profil und Fächer – Duplikate werden verhindert**")

# ────────────────────────────────────────────────
#  WAHL
# ────────────────────────────────────────────────
profil = st.radio("**Profil**", list(profil_faecher.keys()))

profil_fach = st.radio("**Profilfach (P1 – erhöhtes Niveau)**", profil_faecher[profil])

gewaehlte = {profil_fach}  # Set für Duplikat-Prüfung

kern_fs = st.selectbox("**Kernfremdsprache**", [f for f in ["Englisch", "Latein", "Französisch"] if f not in gewaehlte])
gewaehlte.add(kern_fs)

zweite_fs = st.selectbox("**2. Fremdsprache**", ["Keine"] + [f for f in ["Englisch", "Latein", "Französisch", "Griechisch"] if f not in gewaehlte])
if zweite_fs != "Keine":
    gewaehlte.add(zweite_fs)

verpf_nw = st.selectbox("**Verpflichtende NW**", [f for f in ["Physik", "Chemie", "Biologie"] if f not in gewaehlte])
gewaehlte.add(verpf_nw)

religion_phi = st.radio("**Religion oder Philosophie**", ["Religion", "Philosophie"])

wp_liste = st.multiselect("**Weitere WP-Fächer**", wp_optionen[profil])

# ────────────────────────────────────────────────
#  Stunden sammeln
# ────────────────────────────────────────────────
stunden = defaultdict(int)

# Profilfach
for hj in halbjahre:
    stunden[hj] += stunden_basis["Profilfach"][hj]

# Kernfächer (fest 3 h)
for f in ["Deutsch", "Mathematik", "Kernfremdsprache"]:
    for hj in halbjahre:
        stunden[hj] += stunden_basis[f][hj]

# Gewählte
if kern_fs: 
    for hj in halbjahre: stunden[hj] += stunden_basis.get(kern_fs, stunden_basis["Kernfremdsprache"])[hj]

if zweite_fs != "Keine":
    for hj in halbjahre: stunden[hj] += stunden_basis[zweite_fs][hj]

for hj in halbjahre: stunden[hj] += stunden_basis[verpf_nw][hj]

for hj in halbjahre: stunden[hj] += stunden_basis[religion_phi][hj]

for wp in wp_liste:
    for hj in halbjahre: stunden[hj] += stunden_basis.get(wp, stunden_basis["Geografie"])[hj]  # Default 2 h

# ────────────────────────────────────────────────
#  Tabelle
# ────────────────────────────────────────────────
st.subheader("Wochenstunden pro Halbjahr")

df = pd.DataFrame({
    "Halbjahr": halbjahre,
    "Stunden": [stunden[hj] for hj in halbjahre],
    "Status": ["🟢 OK" if 28 <= stunden[hj] <= 34 else "🟡 Hoch" if stunden[hj] <= 36 else "🔴 Zu hoch" for hj in halbjahre]
})

st.dataframe(df.style.format({"Stunden": "{:.0f}"}), use_container_width=True)

if any(stunden[hj] > 35 for hj in ["E1", "E2"]):
    st.warning("**E-Phase >35 h** – das ist sehr hoch (OAPVO empfiehlt max. 35 h)")

st.caption("Stunden aus deinen Tabellen + OAPVO SH. Profilfach immer 4/5 h, Kern 3 h, WP 2 h, etc.")
st.subheader("Abitur-Infos")
for fach in set(fach for _, fach in fach_kategorie.values()):
    if fach in abitur_info:
        with st.expander(fach):
            st.info(abitur_info[fach])

st.caption("Basierend auf OAPVO SH und Katharineum-Tabellen. Stand: Februar 2026.")
