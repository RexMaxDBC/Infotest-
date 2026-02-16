import streamlit as st
import pandas as pd

st.set_page_config(page_title="Katharineum Profilwahl", layout="wide")

# Halbjahre
halbjahre = ["E1", "E2", "Q1.1", "Q1.2", "Q2.1", "Q2.2"]

# Stunden-Dictionary
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

wp_optionen = ["Geografie", "Wirtschaft/Politik", "Chemie", "Biologie", "Physik"]

st.title("Katharineum Lübeck – Profilwahl & Stundenplaner")

# --- WAHLEN ---
profil = st.selectbox("**1. Profil wählen**", [""] + list(profil_optionen.keys()))

if not profil:
    st.info("Bitte zuerst ein Profil auswählen.")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    profil_fach = st.radio("**Profilfach (P1 – erhöhtes Niveau)**", profil_optionen[profil])
    gewaehlte = {profil_fach}

    kern_fs = st.selectbox("**Kernfremdsprache**", 
                           [f for f in ["Englisch", "Latein", "Französisch"] if f not in gewaehlte])
    gewaehlte.add(kern_fs)

    zweite_fs = st.selectbox("**2. Fremdsprache**", 
                             ["Keine"] + [f for f in ["Englisch", "Latein", "Französisch", "Griechisch"] if f not in gewaehlte])
    if zweite_fs != "Keine": gewaehlte.add(zweite_fs)

with col2:
    verpf_nw = st.selectbox("**Verpflichtende Naturwissenschaft**", 
                            [f for f in ["Physik", "Chemie", "Biologie"] if f not in gewaehlte])
    gewaehlte.add(verpf_nw)

    ethik_rel = st.radio("**Religion oder Philosophie**", ["Religion", "Philosophie"])
    
    wp_faecher = st.multiselect("**Weitere WP-Fächer**", [f for f in wp_optionen if f not in gewaehlte])

ds = False
if profil == "Ästhetisches Profil":
    ds = st.checkbox("Darstellendes Spiel (Zusatzfach)")

# --- TABELLE ERSTELLEN ---
rows = []

def get_stunden(fach_name, ist_profilfach=False):
    key = "Profilfach" if ist_profilfach else fach_name
    # Fallback, falls ein Fach nicht im Dictionary ist (z.B. Geschichte)
    data = stunden.get(key, {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2})
    return [data.get(h, 0) for h in halbjahre]

rows.append(["Profilfach (P1)", profil_fach] + get_stunden(profil_fach, True))
rows.append(["Kernfach", "Deutsch"] + get_stunden("Deutsch"))
rows.append(["Kernfach", "Mathematik"] + get_stunden("Mathematik"))
rows.append(["Kernfach", kern_fs] + get_stunden(kern_fs))

if zweite_fs != "Keine":
    rows.append(["2. FS", zweite_fs] + get_stunden(zweite_fs))

rows.append(["Verpf. NW", verpf_nw] + get_stunden(verpf_nw))
rows.append(["Ethik/Rel.", ethik_rel] + get_stunden(ethik_rel))

for wp in wp_faecher:
    rows.append(["WP-Fach", wp] + get_stunden(wp))

if ds:
    rows.append(["Zusatz", "Darstellendes Spiel"] + get_stunden("Darstellendes Spiel"))

# DataFrame erstellen
df = pd.DataFrame(rows, columns=["Kategorie", "Fach"] + halbjahre)

# Summenzeile berechnen
summen = df[halbjahre].sum()
sum_row = pd.DataFrame([["**SUMME**", "Gesamt"] + summen.tolist()], columns=df.columns)
df = pd.concat([df, sum_row], ignore_index=True)

# Styling Funktion
def highlight_rows(row):
    if row["Kategorie"] == "Profilfach (P1)":
        return ['background-color: #e6f3ff'] * len(row)
    if row["Kategorie"] == "**SUMME**":
        return ['background-color: #f0f2f6; font-weight: bold'] * len(row)
    return [''] * len(row)

st.subheader("Dein voraussichtlicher Stundenplan")

# Visualisierung
st.dataframe(
    df.style.apply(highlight_rows, axis=1),
    use_container_width=True,
    hide_index=True
)

# Belastungs-Check (E-Phase Durchschnitt)
e_stunden = (summen["E1"] + summen["E2"]) / 2
if e_stunden > 34:
    st.error(f"⚠️ Hohe Belastung: Durchschnittlich {e_stunden:.1f} Stunden in der E-Phase.")
elif e_stunden < 30:
    st.warning(f"ℹ️ Wenig Stunden: {e_stunden:.1f}. Prüfe, ob du alle Belegungspflichten erfüllst.")
else:
    st.success(f"✅ Ausgewogener Plan: {e_stunden:.1f} Stunden in der E-Phase.")

st.caption("Hinweis: Dies ist eine Planungshilfe. Maßgeblich ist die offizielle Oberstufenverordnung.")
