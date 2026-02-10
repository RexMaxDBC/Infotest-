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

st.title("Katharineum Lübeck – Profilwahl Simulator")

# ===============================================
#          WAHLEN – erst hier werden Variablen gesetzt
# ===============================================

profil = st.selectbox("**1. Profil wählen**", list(profil_optionen.keys()))

if profil:
    profil_fach = st.radio("**Profilfach (P1)**", profil_optionen[profil])
else:
    profil_fach = None
    st.info("Wähle zuerst ein Profil aus.")
    st.stop()  # ← verhindert, dass der Rest ausgeführt wird, bevor alles definiert ist

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

wp = st.multiselect("**Weitere WP-Fächer**", wp_optionen[profil])

ds = False
if profil == "Ästhetisches Profil":
    ds = st.checkbox("Darstellendes Spiel (nur Ästhetik-Profil, affin/Seminar)")

# ===============================================
#          ERST JETZT TABELLE BAUEN – alle Variablen sind definiert
# ===============================================

rows = []

# Profilfach
rows.append(["Profilfach (P1)", profil_fach] + [stunden_basis["Profilfach"][h] for h in halbjahre])

# Kernfächer
rows.append(["Kern", "Deutsch"] + [stunden_basis["Deutsch"][h] for h in halbjahre])
rows.append(["Kern", "Mathematik"] + [stunden_basis["Mathematik"][h] for h in halbjahre])
rows.append(["Kern", "Fremdsprache"] + [stunden_basis.get(kern_fs, stunden_basis["Englisch"])[h] for h in halbjahre])

if zweite_fs != "Keine":
    rows.append(["2. FS", zweite_fs] + [stunden_basis.get(zweite_fs, stunden_basis["Englisch"])[h] for h in halbjahre])

rows.append(["Verpf. NW", verpf_nw] + [stunden_basis[verpf_nw][h] for h in halbjahre])

rows.append(["Ethik/Rel.", ethik_rel] + [stunden_basis[ethik_rel][h] for h in halbjahre])

for w in wp:
    rows.append(["WP", w] + [stunden_basis.get(w, stunden_basis["Geografie"])[h] for h in halbjahre])

if ds:
    rows.append(["Ästhetik-Seminar", "Darstellendes Spiel"] + [stunden_basis["Darstellendes Spiel"][h] for h in halbjahre])

# Summenzeile – jetzt sicher
summ_row = ["**Summe**", ""]
num_halbjahre = len(halbjahre)
for col in range(2, 2 + num_halbjahre):
    col_sum = sum(row[col] for row in rows)
    summ_row.append(col_sum)

rows.append(summ_row)

df = pd.DataFrame(rows, columns=["Kategorie", "Fach"] + halbjahre)

def highlight(row):
    if row["Kategorie"] == "Profilfach (P1)":
        return ['background-color: lightblue; font-weight: bold'] * len(row)
    if row["Kategorie"] == "**Summe**":
        return ['background-color: #f0f0f0; font-weight: bold'] * len(row)
    return [''] * len(row)

st.subheader("Stundenplan")
st.dataframe(df.style.apply(highlight, axis=1).format("{:.0f}"), use_container_width=True, hide_index=True)

st.caption("Fehler behoben: Alle Variablen werden vor der Tabelle gesetzt • Darstellendes Spiel nur Ästhetik + nicht als WP")
    elif e_sum > 32:
        st.warning(f"E-Phase: {e_sum} Stunden – relativ hoch")
    else:
        st.success(f"E-Phase: {e_sum} Stunden – ok")
