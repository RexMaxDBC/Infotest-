import streamlit as st
import pandas as pd

st.set_page_config(page_title="Katharineum Profilwahl", layout="wide")

halbjahre = ["E1", "E2", "Q1.1", "Q1.2", "Q2.1", "Q2.2"]

stunden_basis = {
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
    "Informatik": {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Geografie": {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Wirtschaft/Politik": {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Religion": {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Philosophie": {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Kunst": {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Musik": {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Darstellendes Spiel": {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
}

profil_optionen = {
    "Sprachliches": ["Latein", "Englisch"],
    "Naturwissenschaftliches": ["Physik"],
    "Gesellschaftswissenschaftliches": ["Geschichte"],
    "Ästhetisches": ["Musik", "Kunst"],
}

wp_nach_profil = {
    "Sprachliches": ["Geografie", "Wirtschaft/Politik", "Darstellendes Spiel"],
    "Naturwissenschaftliches": ["Geografie", "Wirtschaft/Politik"],
    "Gesellschaftswissenschaftliches": ["Geografie", "Wirtschaft/Politik", "Darstellendes Spiel"],
    "Ästhetisches": ["Geografie", "Wirtschaft/Politik", "Darstellendes Spiel"],
}

st.title("Katharineum Profilwahl Simulator")

profil = st.selectbox("Profil", list(profil_optionen.keys()))
profil_fach = st.radio("Profilfach (P1)", profil_optionen[profil])

gewaehlte = {profil_fach}

kern_fs = st.selectbox("Kernfremdsprache", 
                       [f for f in ["Englisch", "Latein", "Französisch"] if f not in gewaehlte])
gewaehlte.add(kern_fs)

zweite_fs = st.selectbox("2. Fremdsprache", 
                         ["Keine"] + [f for f in ["Englisch", "Latein", "Französisch", "Griechisch"] if f not in gewaehlte])
if zweite_fs != "Keine": gewaehlte.add(zweite_fs)

verpf_nw = st.selectbox("Verpflichtende Naturwissenschaft", 
                        [f for f in ["Physik", "Chemie", "Biologie"] if f not in gewaehlte])
gewaehlte.add(verpf_nw)

ethik_rel = st.radio("Religion / Philosophie", ["Religion", "Philosophie"])

wp = st.multiselect("Weitere WP-Fächer", wp_nach_profil[profil])

# ────────────────────────────────────────────────
#  TABELLE
# ────────────────────────────────────────────────
rows = []

rows.append(["Profilfach (P1)", profil_fach] + [stunden["Profilfach"][h] for h in halbjahre])
rows.append(["Deutsch", "Deutsch"] + [stunden["Deutsch"][h] for h in halbjahre])
rows.append(["Mathematik", "Mathematik"] + [stunden["Mathematik"][h] for h in halbjahre])
rows.append(["Kern-FS", kern_fs] + [stunden["Kern-FS"][h] for h in halbjahre])

if zweite_fs != "Keine":
    rows.append(["2. FS", zweite_fs] + [stunden[zweite_fs][h] for h in halbjahre])

rows.append(["Verpf. NW", verpf_nw] + [stunden[verpf_nw][h] for h in halbjahre])
rows.append([ethik_rel, ethik_rel] + [stunden[ethik_rel][h] for h in halbjahre])

for w in wp:
    rows.append(["WP", w] + [stunden.get(w, stunden["Geografie"])[h] for h in halbjahre])

# Summen (numpy-sicher)
summ_row = ["**Summe**", ""]
for col in range(2, len(rows[0])):
    s = 0
    for r in rows:
        v = r[col]
        s += v.item() if hasattr(v, 'item') else v
    summ_row.append(s)
rows.append(summ_row)

df = pd.DataFrame(rows, columns=["Kategorie", "Fach"] + halbjahre)

def style_profil(row):
    if row["Kategorie"] == "Profilfach (P1)":
        return ['background-color: #d1e7ff; font-weight: bold'] * len(row)
    if row["Kategorie"] == "**Summe**":
        return ['background-color: #e0e0e0; font-weight: bold'] * len(row)
    return [''] * len(row)

st.dataframe(
    df.style.apply(style_profil, axis=1).format("{:.0f}", na_rep=""),
    use_container_width=True,
    hide_index=True
)

st.caption("Darstellendes Spiel nur in erlaubten Profilen • Keine Duplikate • Stunden aus deinen Tabellen")
