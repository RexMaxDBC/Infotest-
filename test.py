import streamlit as st
import pandas as pd

st.set_page_config(page_title="Katharineum Profilwahl", layout="wide")

# ────────────────────────────────────────────────
#  STUNDEN aus deinen Tabellen (exakt übernommen)
# ────────────────────────────────────────────────
halbjahre = ["E1", "E2", "Q1.1", "Q1.2", "Q2.1", "Q2.2"]

stunden = {
    # Profilfach – immer 4 in E, 5 in Q
    "Profilfach":          {"E1":4, "E2":4, "Q1.1":5, "Q1.2":5, "Q2.1":5, "Q2.2":5},
    
    # Kernfächer DE/MA/FS – fast immer 3
    "Deutsch":             {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Mathematik":          {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Kern-FS":             {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    
    # FS / MINT / NW – 3
    "Englisch":            {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Latein":              {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Französisch":         {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Griechisch":          {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Physik":              {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Chemie":              {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Biologie":            {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Informatik":          {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    
    # WP / Ge / Re/Phi / Ku/Mu / Sp – 2
    "Geografie":           {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Wirtschaft/Politik":  {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Religion":            {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Philosophie":         {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Kunst":               {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Musik":               {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Darstellendes Spiel": {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    
    # Seminare
    "Profilseminar":       {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
}

# Profil → mögliche Profilfächer
profil_optionen = {
    "Sprachliches Profil": ["Latein", "Englisch"],
    "Naturwissenschaftliches Profil": ["Physik"],
    "Gesellschaftswissenschaftliches Profil": ["Geschichte"],
    "Ästhetisches Profil": ["Musik", "Kunst"],
}

# ────────────────────────────────────────────────
#  BENUTZERWAHL
# ────────────────────────────────────────────────
st.title("Katharineum – Profilwahl & Stundenplaner")

profil = st.selectbox("**1. Wähle dein Profil**", list(profil_optionen.keys()))

profil_fach = st.radio("**Profilfach (P1 – erhöhtes Niveau)**", profil_optionen[profil])

gewaehlte_faecher = {profil_fach}  # für Duplikat-Filter

kern_fs = st.selectbox("**Kernfremdsprache**", 
                       [f for f in ["Englisch", "Latein", "Französisch"] if f not in gewaehlte_faecher])
gewaehlte_faecher.add(kern_fs)

zweite_fs = st.selectbox("**2. Fremdsprache**", 
                         ["Keine"] + [f for f in ["Englisch", "Latein", "Französisch", "Griechisch"] if f not in gewaehlte_faecher])
if zweite_fs != "Keine":
    gewaehlte_faecher.add(zweite_fs)

verpf_nw = st.selectbox("**Verpflichtende Naturwissenschaft**", 
                        [f for f in ["Physik", "Chemie", "Biologie"] if f not in gewaehlte_faecher])
gewaehlte_faecher.add(verpf_nw)

religion_phi = st.radio("**Religion oder Philosophie**", ["Religion", "Philosophie"])

wp_faecher = st.multiselect("**Weitere WP-Fächer**", 
                            ["Geografie", "Wirtschaft/Politik", "Darstellendes Spiel"])

# ────────────────────────────────────────────────
#  TABELLE AUFBAUEN
# ────────────────────────────────────────────────
daten = []

# Profilfach
daten.append(["Profilfach (P1)", profil_fach] + [stunden["Profilfach"][hj] for hj in halbjahre])

# Kernfächer
daten.append(["Kernfach", "Deutsch"] + [stunden["Deutsch"][hj] for hj in halbjahre])
daten.append(["Kernfach", "Mathematik"] + [stunden["Mathematik"][hj] for hj in halbjahre])
daten.append(["Kernfach", "Fremdsprache"] + [stunden["Kern-FS"][hj] for hj in halbjahre])

# Gewählte Ergänzungsfächer
if zweite_fs != "Keine":
    daten.append(["2. FS", zweite_fs] + [stunden[zweite_fs][hj] for hj in halbjahre])

daten.append(["Verpf. NW", verpf_nw] + [stunden[verpf_nw][hj] for hj in halbjahre])

daten.append(["Ethik/Rel.", religion_phi] + [stunden[religion_phi][hj] for hj in halbjahre])

for wp in wp_faecher:
    daten.append(["WP-Fach", wp] + [stunden.get(wp, stunden["Geografie"])[hj] for hj in halbjahre])

# Summenzeile
summen = ["**Summe**", ""] + [sum(zeile[i+2] for zeile in daten) for i in range(6)]

daten.append(summen)

df = pd.DataFrame(daten, columns=["Kategorie", "Fach"] + halbjahre)

# ────────────────────────────────────────────────
#  STYLING & ANZEIGE
# ────────────────────────────────────────────────
def highlight_profil(row):
    if row["Kategorie"] == "Profilfach (P1)":
        return ['background-color: #cce5ff; font-weight: bold'] * len(row)
    if row["Kategorie"] == "**Summe**":
        return ['background-color: #f0f0f0; font-weight: bold'] * len(row)
    return [''] * len(row)

st.subheader("Dein Stundenplan")

st.dataframe(
    df.style.apply(highlight_profil, axis=1)
             .format(precision=0, na_rep="-"),
    use_container_width=True,
    hide_index=True
)

# Belastungshinweis
max_e = max(df.loc[df["Kategorie"] != "**Summe**", "E1":"E2"].max().max())
if max_e > 35:
    st.error(f"**Achtung**: E-Phase mit {max_e} Stunden – sehr hoch (OAPVO max. ~35 empfohlen)")
elif max_e > 32:
    st.warning(f"E-Phase mit {max_e} Stunden – relativ hoch")
else:
    st.success(f"E-Phase mit {max_e} Stunden – im grünen Bereich")

st.caption("Basierend auf deinen Tabellen + OAPVO SH. Keine Duplikate, einheitliche Auswahl.")
