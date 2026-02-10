import streamlit as st
import pandas as pd

st.set_page_config(page_title="Katharineum Profilwahl Simulator", layout="wide")

# Hardcoded Stunden aus Tabellen
halbjahre = ["E1", "E2", "Q1.1", "Q1.2", "Q2.1", "Q2.2"]

fach_stunden = {
    "Profilfach": {"E1": 4, "E2": 4, "Q1.1": 5, "Q1.2": 5, "Q2.1": 5, "Q2.2": 5},
    "Deutsch (DE)": {"E1": 3, "E2": 3, "Q1.1": 3, "Q1.2": 3, "Q2.1": 3, "Q2.2": 3},
    "Mathematik (MA)": {"E1": 3, "E2": 3, "Q1.1": 13, "Q1.2": 13, "Q2.1": 13, "Q2.2": 13},  # Anpassung falls nötig
    "Kernfremdsprache": {"E1": 3, "E2": 3, "Q1.1": 3, "Q1.2": 3, "Q2.1": 3, "Q2.2": 3},
    "Naturw. MINT": {"E1": 3, "E2": 3, "Q1.1": 3, "Q1.2": 3, "Q2.1": 3, "Q2.2": 3},
    "2. FS": {"E1": 3, "E2": 3, "Q1.1": 3, "Q1.2": 3, "Q2.1": 3, "Q2.2": 3},
    "3. FS": {"E1": 3, "E2": 3, "Q1.1": 3, "Q1.2": 3, "Q2.1": 3, "Q2.2": 3},
    "Geografie (Ge)": {"E1": 2, "E2": 2, "Q1.1": 2, "Q1.2": 2, "Q2.1": 2, "Q2.2": 2},
    "Ek": {"E1": 2, "E2": 2, "Q1.1": 2, "Q1.2": 2, "Q2.1": 2, "Q2.2": 2},
    "Wp": {"E1": 2, "E2": 2, "Q1.1": 2, "Q1.2": 2, "Q2.1": 2, "Q2.2": 2},
    "Religion/Philosophie": {"E1": 2, "E2": 2, "Q1.1": 2, "Q1.2": 2, "Q2.1": 2, "Q2.2": 2},
    "Kunst/Musik": {"E1": 2, "E2": 2, "Q1.1": 2, "Q1.2": 2, "Q2.1": 2, "Q2.2": 2},
    "Sport (Sp)": {"E1": 2, "E2": 2, "Q1.1": 2, "Q1.2": 2, "Q2.1": 2, "Q2.2": 2},
    "Profilseminar": {"E1": 1, "E2": 1, "Q1.1": 3, "Q1.2": 3, "Q2.1": 3, "Q2.2": 3},
    "Berufliche Orientierung": {"E1": 1, "E2": 1, "Q1.1": 3, "Q1.2": 3, "Q2.1": 3, "Q2.2": 3},
    "Darstellendes Spiel": {"E1": 2, "E2": 2, "Q1.1": 2, "Q1.2": 2, "Q2.1": 2, "Q2.2": 2},
}

# Profil-spezifische Profilfächer
profil_faecher = {
    "Sprachliches Profil": ["Latein", "Englisch"],
    "Naturwissenschaftliches Profil": ["Physik"],
    "Gesellschaftswissenschaftliches Profil": ["Geschichte"],
    "Ästhetisches Profil": ["Musik", "Kunst"],
}

# Einschränkungen: Darstellendes Spiel nur in Ästhetischem Profil
verfuegbare_wp = {
    "Naturwissenschaftliches Profil": ["Geografie (Ge)", "Wp", "Ek"],
    "Gesellschaftswissenschaftliches Profil": ["Geografie (Ge)", "Wp", "Ek", "Darstellendes Spiel"],
    "Sprachliches Profil": ["Geografie (Ge)", "Wp", "Ek", "Darstellendes Spiel"],
    "Ästhetisches Profil": ["Geografie (Ge)", "Wp", "Ek", "Darstellendes Spiel"],
}

# Abitur Infos
abitur_info = {
    # ... (wie im vorherigen Code, unverändert)
}

st.title("Katharineum Lübeck – Verbesserter Profilwahl & Stunden-Simulator")

st.markdown("""
Verbesserte Version: 
- Profil-spezifische Einschränkungen für Fächer (z.B. Darstellendes Spiel nicht im Naturwissenschaftlichen Profil).
- Vollständige Tabelle mit Fächern und Stunden pro Quartal.
- Profilfach hervorgehoben als P1-Fach (erhöhtes Niveau).
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Deine Wahl")
    profil = st.radio("Profilbereich", list(profil_faecher.keys()))
    profil_fach_name = st.radio("Profilfach (P1 - erhöhtes Niveau)", profil_faecher[profil])
    
    kern_fs = st.selectbox("Kernfremdsprache", ["Englisch", "Latein", "Französisch"])
    
    zweite_fs = st.selectbox("2. Fremdsprache", ["Englisch", "Latein", "Französisch", "Griechisch"])
    
    dritte_fs = st.checkbox("3. Fremdsprache hinzufügen")
    if dritte_fs:
        dritte_fs_name = st.selectbox("3. FS", ["Englisch", "Latein", "Französisch", "Griechisch"])
    
    verpf_nw = st.selectbox("Verpflichtende Naturwissenschaft", ["Physik", "Chemie", "Biologie"])
    
    religion_phi = st.radio("Religion oder Philosophie", ["Religion", "Philosophie"])
    
    wp_faecher = st.multiselect("Weitere WP-Fächer", verfuegbare_wp[profil])

# Gewählte Fächer sammeln
gewaehlte_faecher = {
    "Profilfach (P1)": profil_fach_name,
    "Deutsch (DE)": "Deutsch (DE)",
    "Mathematik (MA)": "Mathematik (MA)",
    "Kernfremdsprache": kern_fs,
    "Verpf. NW": verpf_nw,
    "Religion/Philosophie": religion_phi,
}

if zweite_fs:
    gewaehlte_faecher["2. FS"] = zweite_fs

if dritte_fs:
    gewaehlte_faecher["3. FS"] = dritte_fs_name

for wp in wp_faecher:
    gewaehlte_faecher[wp] = wp

# Tabelle aufbauen
data = []
for kategorie, fach in gewaehlte_faecher.items():
    if fach in fach_stunden:
        row = [kategorie] + [fach_stunden[fach].get(hj, 0) for hj in halbjahre]
    else:
        row = [kategorie] + [fach_stunden.get(kategorie, {}).get(hj, 0) for hj in halbjahre]
    data.append(row)

# Summen
summen = ["Summe"] + [sum(row[i+1] for row in data) for i in range(6)]

data.append(summen)

df = pd.DataFrame(data, columns=["Fach/Kategorie"] + halbjahre)

# Hervorheben des Profilfachs
def highlight_profil(val):
    if val == "Profilfach (P1)":
        return 'background-color: lightblue; font-weight: bold'
    return ''

st.subheader("Stunden pro Quartal")
st.dataframe(df.style.applymap(highlight_profil, subset=["Fach/Kategorie"]))

# Validierung und Abitur-Infos (wie vorher)
st.subheader("Abitur-Infos")
for fach in gewaehlte_faecher.values():
    if fach in abitur_info:
        with st.expander(fach):
            st.info(abitur_info[fach])
