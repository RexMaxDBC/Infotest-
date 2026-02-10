import streamlit as st
import pandas as pd

st.set_page_config(page_title="Katharineum Profilwahl", layout="wide")

# Halbjahre
halbjahre = ["E1", "E2", "Q1.1", "Q1.2", "Q2.1", "Q2.2"]

# Stunden-Basis (exakt aus deinen Tabellen abgelesen, keine "13" mehr)
stunden_basis = {
    "Profilfach":          {"E1":4, "E2":4, "Q1.1":5, "Q1.2":5, "Q2.1":5, "Q2.2":5},
    "Deutsch":             {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Mathematik":          {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Englisch":            {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Latein":              {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Französisch":         {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Griechisch":          {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Physik":              {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Chemie":              {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Biologie":            {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Informatik":          {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Geografie":           {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Wirtschaft/Politik":  {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Religion":            {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Philosophie":         {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Kunst":               {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Musik":               {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Darstellendes Spiel": {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Profilseminar":       {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
}

# Profil → Profilfächer
profil_optionen = {
    "Sprachliches Profil": ["Latein", "Englisch"],
    "Naturwissenschaftliches Profil": ["Physik"],
    "Gesellschaftswissenschaftliches Profil": ["Geschichte"],
    "Ästhetisches Profil": ["Musik", "Kunst"],
}

# WP pro Profil – Darstellendes Spiel NUR Ästhetik + nicht als freies WP, sondern als Seminar-ähnlich
wp_optionen = {
    "Sprachliches Profil": ["Geografie", "Wirtschaft/Politik"],
    "Naturwissenschaftliches Profil": ["Geografie", "Wirtschaft/Politik"],
    "Gesellschaftswissenschaftliches Profil": ["Geografie", "Wirtschaft/Politik"],
    "Ästhetisches Profil": ["Geografie", "Wirtschaft/Politik"],  # DS nicht hier – siehe unten
}

st.title("Katharineum Lübeck – Profilwahl Simulator")

# ────────────────────────────────────────────────
# WAHL
# ────────────────────────────────────────────────
profil = st.selectbox("**Profil**", list(profil_optionen.keys()))

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
gewaehlte.add(verpf_nw)

ethik_rel = st.radio("**Religion oder Philosophie**", ["Religion", "Philosophie"])

wp = st.multiselect("**Weitere WP-Fächer**", wp_optionen[profil])

# Darstellendes Spiel nur im Ästhetischen Profil – als Seminar-Option, nicht normales WP
ds = False
if profil == "Ästhetisches Profil":
    ds = st.checkbox("Darstellendes Spiel (affines Fach / Seminar im Ästhetik-Profil)")

# ────────────────────────────────────────────────
# TABELLE
# ────────────────────────────────────────────────
rows = []

# Profilfach
rows.append(["Profilfach (P1)", profil_fach] + [stunden_basis["Profilfach"][h] for h in halbjahre])

# Kernfächer
rows.append(["Kern", "Deutsch"] + [stunden_basis["Deutsch"][h] for h in halbjahre])
rows.append(["Kern", "Mathematik"] + [stunden_basis["Mathematik"][h] for h in halbjahre])
rows.append(["Kern", "Fremdsprache"] + [stunden_basis["Kern-FS"][h] for h in halbjahre] if "Kern-FS" in stunden_basis else [3]*6)

# Ergänzungen
if zweite_fs != "Keine":
    rows.append(["2. FS", zweite_fs] + [stunden_basis.get(zweite_fs, stunden_basis["Englisch"])[h] for h in halbjahre])

rows.append(["Verpf. NW", verpf_nw] + [stunden_basis[verpf_nw][h] for h in halbjahre])
rows.append(["Ethik/Rel.", ethik_rel] + [stunden_basis[ethik_rel][h] for h in halbjahre])

for w in wp:
    rows.append(["WP", w] + [stunden_basis.get(w, stunden_basis["Geografie"])[h] for h in halbjahre])

if ds:
    rows.append(["Ästhetik-Seminar", "Darstellendes Spiel"] + [stunden_basis["Darstellendes Spiel"][h] for h in halbjahre])

# Summen – numpy-sicher
summ_row = ["**Summe**", ""]
for col_idx in range(2, len(rows[0])):
    col_sum = 0
    for row in rows:
        val = row[col_idx]
        if hasattr(val, 'item'):  # numpy.int64/float64
            col_sum += val.item()
        else:
            col_sum += val
    summ_row.append(col_sum)

rows.append(summ_row)

df = pd.DataFrame(rows, columns=["Kategorie", "Fach"] + halbjahre)

# Styling
def highlight(row):
    if row["Kategorie"] == "Profilfach (P1)":
        return ['background-color: #cce5ff; font-weight: bold'] * len(row)
    if row["Kategorie"] == "**Summe**":
        return ['background-color: #e8e8e8; font-weight: bold'] * len(row)
    return [''] * len(row)

st.subheader("Stundenplan")
st.dataframe(
    df.style.apply(highlight, axis=1).format("{:.0f}", na_rep="-"),
    use_container_width=True,
    hide_index=True
)

# Belastung
e_sum = df.iloc[-1]["E1"] + df.iloc[-1]["E2"] if "**Summe**" in df["Kategorie"].values else 0
if e_sum > 35:
    st.error(f"E-Phase Belastung: {e_sum} Stunden – deutlich zu hoch!")
elif e_sum > 32:
    st.warning(f"E-Phase Belastung: {e_sum} Stunden – relativ hoch")
else:
    st.success(f"E-Phase Belastung: {e_sum} Stunden – im guten Bereich")

st.caption("Darstellendes Spiel nur Ästhetik-Profil • Keine Fächer-Duplikate • Stunden direkt aus Tabellen")
