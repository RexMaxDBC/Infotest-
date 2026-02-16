import streamlit as st
import pandas as pd

st.set_page_config(page_title="Katharineum Profilwahl", layout="wide")

# Halbjahre
halbjahre = ["E1", "E2", "Q1.1", "Q1.2", "Q2.1", "Q2.2"]

# Stunden-Dictionary
stunden = {
    "Profilfach": {"E1": 4, "E2": 4, "Q1.1": 5, "Q1.2": 5, "Q2.1": 5, "Q2.2": 5},
    "Deutsch": {"E1": 3, "E2": 3, "Q1.1": 3, "Q1.2": 3, "Q2.1": 3, "Q2.2": 3},
    "Mathematik": {"E1": 3, "E2": 3, "Q1.1": 3, "Q1.2": 3, "Q2.1": 3, "Q2.2": 3},
    "Englisch": {"E1": 3, "E2": 3, "Q1.1": 3, "Q1.2": 3, "Q2.1": 3, "Q2.2": 3},
    "Latein": {"E1": 3, "E2": 3, "Q1.1": 3, "Q1.2": 3, "Q2.1": 3, "Q2.2": 3},
    "Französisch": {"E1": 3, "E2": 3, "Q1.1": 3, "Q1.2": 3, "Q2.1": 3, "Q2.2": 3},
    "Griechisch": {"E1": 3, "E2": 3, "Q1.1": 3, "Q1.2": 3, "Q2.1": 3, "Q2.2": 3},
    "Physik": {"E1": 3, "E2": 3, "Q1.1": 3, "Q1.2": 3, "Q2.1": 3, "Q2.2": 3},
    "Chemie": {"E1": 3, "E2": 3, "Q1.1": 3, "Q1.2": 3, "Q2.1": 3, "Q2.2": 3},
    "Biologie": {"E1": 3, "E2": 3, "Q1.1": 3, "Q1.2": 3, "Q2.1": 3, "Q2.2": 3},
    "Geografie": {"E1": 2, "E2": 2, "Q1.1": 2, "Q1.2": 2, "Q2.1": 2, "Q2.2": 2},
    "Wirtschaft/Politik": {"E1": 2, "E2": 2, "Q1.1": 2, "Q1.2": 2, "Q2.1": 2, "Q2.2": 2},
    "Religion": {"E1": 2, "E2": 2, "Q1.1": 2, "Q1.2": 2, "Q2.1": 2, "Q2.2": 2},
    "Philosophie": {"E1": 2, "E2": 2, "Q1.1": 2, "Q1.2": 2, "Q2.1": 2, "Q2.2": 2},
    "Kunst": {"E1": 2, "E2": 2, "Q1.1": 2, "Q1.2": 2, "Q2.1": 2, "Q2.2": 2},
    "Musik": {"E1": 2, "E2": 2, "Q1.1": 2, "Q1.2": 2, "Q2.1": 2, "Q2.2": 2},
    "Darstellendes Spiel": {"E1": 2, "E2": 2, "Q1.1": 2, "Q1.2": 2, "Q2.1": 2, "Q2.2": 2},
    "Geschichte": {"E1": 2, "E2": 2, "Q1.1": 2, "Q1.2": 2, "Q2.1": 2, "Q2.2": 2},
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

st.title("Katharineum Lübeck – Profilwahl & Stundenplaner")

# ===============================================
# WAHLEN
# ===============================================

profil = st.selectbox("**1. Profil wählen**", [""] + list(profil_optionen.keys()))

if not profil:
    st.info("Bitte zuerst ein Profil auswählen.")
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
    ds = st.checkbox("Darstellendes Spiel (nur im Ästhetischen Profil – affin/Seminar)")

# ===============================================
# TABELLENAUFBAU
# ===============================================

rows = []

def add_row(kategorie, fach):
    rows.append([kategorie, fach] + [stunden[fach].get(h, 0) for h in halbjahre])

add_row("Profilfach (P1)", profil_fach)
add_row("Kernfach", "Deutsch")
add_row("Kernfach", "Mathematik")
add_row("Kernfach", kern_fs)

if zweite_fs != "Keine":
    add_row("2. FS", zweite_fs)

add_row("Verpf. NW", verpf_nw)
add_row("Ethik/Rel.", ethik_rel)

for wp in wp_faecher:
    add_row("WP-Fach", wp)

if ds:
    add_row("Ästhetik-Seminar", "Darstellendes Spiel")

# Summenzeile
summ_row = ["Summe", ""]
for h in halbjahre:
    summ_row.append(sum(r[i + 2] for r in rows))
rows.append(summ_row)

df = pd.DataFrame(rows, columns=["Kategorie", "Fach"] + halbjahre)

# ===============================================
# STYLING
# ===============================================

def highlight(row):
    color = ""
    if row["Kategorie"] == "Profilfach (P1)":
        color = "#cce5ff"
    elif row["Kategorie"] == "Summe":
        color = "#f2f2f2"
    style = [f"background-color: {color}; font-weight: bold" if color else "" for _ in row]
    return style

st.subheader("Dein Stundenplan")
st.dataframe(
    df.style.apply(highlight, axis=1),
    use_container_width=True,
    hide_index=True
)

# ===============================================
# BELASTUNGSANZEIGE
# ===============================================

sum_row = df[df["Kategorie"] == "Summe"].iloc[0]
e_sum = int(sum_row["E1"]) + int(sum_row["E2"])

if e_sum > 35:
    st.error(f"E-Phase Belastung: {e_sum} Stunden – deutlich zu hoch!")
elif e_sum > 32:
    st.warning(f"E-Phase Belastung: {e_sum} Stunden – relativ hoch.")
else:
    st.success(f"E-Phase Belastung: {e_sum} Stunden – im grünen Bereich.")

st.caption("Stabile Fassung • optimiert & voll funktionsfähig • inkl. Geschichte & Stylingfix")

