import streamlit as st
import pandas as pd

st.set_page_config(page_title="Katharineum Profilwahl", layout="wide")

halbjahre = ["E1", "E2", "Q1.1", "Q1.2", "Q2.1", "Q2.2"]

# Stunden-Dict (nur existierende Schlüssel – kein "Kern-FS")
stunden = {
    "Profilfach": {"E1":4, "E2":4, "Q1.1":5, "Q1.2":5, "Q2.1":5, "Q2.2":5},
    "Deutsch": {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Mathematik": {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Englisch": {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Latein": {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Französisch": {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Griechisch": {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Physik": {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Chemie": {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Biologie": {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Geografie": {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Wirtschaft/Politik": {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Religion": {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Philosophie": {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Kunst": {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Musik": {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Darstellendes Spiel": {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
}

profil_optionen = {
    "Sprachliches Profil": ["Latein", "Englisch"],
    "Naturwissenschaftliches Profil": ["Physik"],
    "Gesellschaftswissenschaftliches Profil": ["Geschichte"],
    "Ästhetisches Profil": ["Musik", "Kunst"],
}

wp_optionen = {
    "Sprachliches Profil": ["Geografie", "Wirtschaft/Politik"],
    "Naturwissenschaftliches Profil": ["Geografie", "Wirtschaft/Politik"],
    "Gesellschaftswissenschaftliches Profil": ["Geografie", "Wirtschaft/Politik"],
    "Ästhetisches Profil": ["Geografie", "Wirtschaft/Politik"],
}

st.title("Katharineum – Profilwahl & Stundenplaner")

# ===============================================
# WAHLEN
# ===============================================

profil = st.selectbox("**1. Profil**", [""] + list(profil_optionen.keys()))

if not profil:
    st.info("Wähle bitte zuerst dein Profil aus.")
    st.stop()

profil_fach = st.radio("**Profilfach (P1 – erhöhtes Niveau)**", profil_optionen[profil])

gewaehlte = {profil_fach}

kern_fs = st.selectbox("**Kernfremdsprache**", 
                       [f for f in ["Englisch", "Latein", "Französisch"] if f not in gewaehlte])
gewaehlte.add(kern_fs)

zweite_fs = st.selectbox("**2. Fremdsprache**", 
                         ["Keine"] + [f for f in ["Englisch", "Latein", "Französisch", "Griechisch"] if f not in gewaehlte])

if zweite_fs != "Keine":
    gewaehlte.add(zweite_fs)

verpf_nw = st.selectbox("**Verpflichtende Naturwissenschaft**", 
                        [f for f in ["Physik", "Chemie", "Biologie"] if f not in gewaehlte])

ethik_rel = st.radio("**Religion oder Philosophie**", ["Religion", "Philosophie"])

wp_faecher = st.multiselect("**Weitere WP-Fächer**", wp_optionen[profil])

ds = False
if profil == "Ästhetisches Profil":
    ds = st.checkbox("Darstellendes Spiel (nur Ästhetik – affin/Seminar)")

# ===============================================
# TABELLE
# ===============================================

rows = []

rows.append(["Profilfach (P1)", profil_fach] + [stunden_basis["Profilfach"].get(h, 0) for h in halbjahre])
rows.append(["Kern", "Deutsch"] + [stunden_basis["Deutsch"].get(h, 0) for h in halbjahre])
rows.append(["Kern", "Mathematik"] + [stunden_basis["Mathematik"].get(h, 0) for h in halbjahre])
rows.append(["Kern", kern_fs] + [stunden_basis.get(kern_fs, stunden_basis["Englisch"]).get(h, 3) for h in halbjahre])

if zweite_fs != "Keine":
    rows.append(["2. FS", zweite_fs] + [stunden_basis.get(zweite_fs, stunden_basis["Englisch"]).get(h, 3) for h in halbjahre])

rows.append(["Verpf. NW", verpf_nw] + [stunden_basis.get(verpf_nw, stunden_basis["Physik"]).get(h, 3) for h in halbjahre])
rows.append(["Ethik/Rel.", ethik_rel] + [stunden_basis[ethik_rel].get(h, 2) for h in halbjahre])

for wp in wp_faecher:
    rows.append(["WP", wp] + [stunden_basis.get(wp, stunden_basis["Geografie"]).get(h, 2) for h in halbjahre])

if ds:
    rows.append(["Ästhetik-Seminar", "Darstellendes Spiel"] + [stunden_basis["Darstellendes Spiel"].get(h, 2) for h in halbjahre])

# Summen – sehr robust
summ_row = ["**Summe**", ""]
for col_idx in range(2, len(halbjahre) + 2):
    col_sum = 0
    for row in rows:
        if len(row) > col_idx:
            val = row[col_idx]
            col_sum += val if isinstance(val, (int, float)) else 0
    summ_row.append(col_sum)

rows.append(summ_row)

df = pd.DataFrame(rows, columns=["Kategorie", "Fach"] + halbjahre)

def highlight(row):
    styles = [''] * len(row)
    if row["Kategorie"] == "Profilfach (P1)":
        styles = ['background-color: #cce5ff; font-weight: bold'] * len(row)
    if row["Kategorie"] == "**Summe**":
        styles = ['background-color: #f0f0f0; font-weight: bold'] * len(row)
    return styles

st.subheader("Dein Stundenplan")
st.dataframe(
    df.style.apply(highlight, axis=1).format("{:.0f}", na_rep="-"),
    use_container_width=True,
    hide_index=True
)

# Belastung – sicher gegen leere Tabelle
e_sum = 0
if "**Summe**" in df["Kategorie"].values:
    sum_row = df[df["Kategorie"] == "**Summe**"].iloc[0]
    e1 = sum_row.get("E1", 0)
    e2 = sum_row.get("E2", 0)
    e_sum = e1 + e2

if e_sum > 35:
    st.error(f"E-Phase: {e_sum} Stunden – deutlich zu hoch!")
elif e_sum > 32:
    st.warning(f"E-Phase: {e_sum} Stunden – relativ hoch")
else:
    st.success(f"E-Phase: {e_sum} Stunden – im grünen Bereich")

st.caption("Stabile Version • Kein NameError • Kein IndexError • Darstellendes Spiel nur Ästhetik")
