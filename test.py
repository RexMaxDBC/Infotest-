import streamlit as st
import pandas as pd
from collections import defaultdict

st.set_page_config(page_title="Katharineum Profilwahl Simulator", layout="wide")

# ────────────────────────────────────────────────
#  HARD CODED STUNDEN aus deinen Tabellen (pro Halbjahr)
# ────────────────────────────────────────────────
halbjahre = ["E1", "E2", "Q1.1", "Q1.2", "Q2.1", "Q2.2"]

# Basis-Stunden pro Fach (unabhängig vom Profil – grobe Annäherung aus Bildern)
fach_stunden = {
    # Profilfächer (immer 4 in E, 5 in Q)
    "Profilfach":          {"E1":4, "E2":4, "Q1.1":5, "Q1.2":5, "Q2.1":5, "Q2.2":5},
    
    # Kernfächer (meist 3)
    "Deutsch":             {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Mathematik":          {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Kernfremdsprache":    {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    
    # Naturwissenschaften / MINT (meist 3)
    "Physik":              {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Chemie":              {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Biologie":            {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Informatik":          {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    
    # Fremdsprachen 2./3. (meist 3)
    "Englisch":            {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Latein":              {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Französisch":         {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    "Griechisch":          {"E1":3, "E2":3, "Q1.1":3, "Q1.2":3, "Q2.1":3, "Q2.2":3},
    
    # Gesellschaftswiss. & WP (meist 2)
    "Geschichte":          {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Geografie":           {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Wirtschaft/Politik":  {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Religion":            {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Philosophie":         {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    
    # Ästhetisch & Sport (meist 2)
    "Musik":               {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Kunst":               {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Darstellendes Spiel": {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    
    # Seminare (variabel, meist 2)
    "Profilseminar":       {"E1":2, "E2":2, "Q1.1":2, "Q1.2":2, "Q2.1":2, "Q2.2":2},
    "Berufliche Orient.":  {"E1":1, "E2":1, "Q1.1":3, "Q1.2":3, "Q2.1":0, "Q2.2":0},
}

# ────────────────────────────────────────────────
#  Abitur-Info-Texte (geprüft nach OAPVO SH 2025+)
# ────────────────────────────────────────────────
abitur_info = {
    "Profilfach": "Immer auf erhöhtem Niveau (5 h in Q) → eines der zwei schriftlichen Prüfungsfächer möglich. Doppelt gewichtet in der Abiturnote.",
    "Deutsch": "Kernfach. Kann auf erhöhtem Niveau (5 h) gewählt werden → schriftliche Prüfung möglich. Muss eingebracht werden.",
    "Mathematik": "Kernfach. Kann auf erhöhtem Niveau gewählt werden → schriftliche Prüfung möglich. Muss eingebracht werden.",
    "Kernfremdsprache": "Kernfach. Kann auf erhöhtem Niveau gewählt werden → schriftliche Prüfung möglich. Muss eingebracht werden.",
    "Physik": "Kann auf erhöhtem Niveau sein (wenn Profil). Ansonsten grundlegend. Muss mindestens eine NW eingebracht werden.",
    "Chemie": "Grundlegendes Niveau (meist). Kann mündlich geprüft werden.",
    "Biologie": "Grundlegendes Niveau (meist). Kann mündlich geprüft werden.",
    "Informatik": "Grundlegendes Niveau. Kann mündlich oder als Projekt eingebracht werden.",
    "Englisch": "Kann als 2./3. FS oder Kern gewählt werden. Mündlich oder schriftlich möglich.",
    "Latein": "Kann als 2./3. FS oder Kern gewählt werden. Mündlich oder schriftlich möglich.",
    "Französisch": "Kann als 2./3. FS oder Kern gewählt werden. Mündlich oder schriftlich möglich.",
    "Griechisch": "Meist 3. FS. Mündlich möglich.",
    "Geschichte": "Grundlegendes Niveau. Mündlich möglich.",
    "Geografie": "Grundlegendes Niveau. Mündlich möglich.",
    "Wirtschaft/Politik": "Grundlegendes Niveau. Mündlich möglich.",
    "Religion": "Grundlegendes Niveau. Mündlich möglich.",
    "Philosophie": "Grundlegendes Niveau. Mündlich möglich.",
    "Musik": "Grundlegendes Niveau. Praktische/mündliche Prüfung möglich.",
    "Kunst": "Grundlegendes Niveau. Praktische/mündliche Prüfung möglich.",
    "Darstellendes Spiel": "Grundlegendes Niveau. Praktische/mündliche Prüfung möglich.",
    "Profilseminar": "Kann als Besondere Lernleistung oder mündliche Prüfung eingebracht werden.",
}

# ────────────────────────────────────────────────
#  SESSION STATE
# ────────────────────────────────────────────────
if "wahl" not in st.session_state:
    st.session_state.wahl = defaultdict(bool)

# ────────────────────────────────────────────────
#  TITEL & INFO
# ────────────────────────────────────────────────
st.title("Katharineum Lübeck – Profilwahl & Stunden-Simulator")
st.markdown("""
Diese App simuliert deine **Wochenstunden** pro Halbjahr und zeigt dir, wie sich deine Wahl auf die Belastung auswirkt.  
Die Zahlen stammen aus den Tabellen des Katharineums (2024/25).  
Ab 2025 gilt: **nur noch zwei Fächer auf erhöhtem Niveau** (Profil + ein Kernfach).
""")

# ────────────────────────────────────────────────
#  WAHL-BEREICH
# ────────────────────────────────────────────────
col1, col2 = st.columns([1,2])

with col1:
    st.subheader("Deine Wahl")

    profil = st.radio("**A – Profilbereich** (genau eines)", 
                      ["Sprachliches Profil", "Naturwissenschaftliches Profil", 
                       "Gesellschaftswissenschaftliches Profil", "Ästhetisches Profil"])

    if profil == "Sprachliches Profil":
        profil_fach = st.radio("Profilfach", ["Latein", "Englisch"])
    elif profil == "Ästhetisches Profil":
        profil_fach = st.radio("Profilfach", ["Musik", "Kunst"])
    else:
        profil_fach = profil.split()[0]   # Physik, Geschichte

    st.markdown("---")

    kern_fs = st.selectbox("**Kernfremdsprache** (B – abiturrelevant)", 
                           ["Englisch", "Latein", "Französisch"])

    zweite_fs = st.multiselect("**2. Fremdsprache** oder MINT (kann auch MINT sein)", 
                               ["Englisch", "Latein", "Französisch", "Griechisch", 
                                "Biologie", "Chemie", "Physik", "Informatik"], 
                               max_selections=1)

    dritte_fs = st.multiselect("**3. Fremdsprache** (freiwillig)", 
                               ["Englisch", "Latein", "Französisch", "Griechisch", 
                                "Biologie", "Chemie", "Physik", "Informatik"], 
                               max_selections=1)

    verpf_nw = st.selectbox("**Verpflichtende Naturwissenschaft**", 
                            ["Physik", "Chemie", "Biologie"])

    zusaetz_mint = st.checkbox("Zusätzliches MINT-Fach (falls erlaubt)")

    if profil != "Ästhetisches Profil":
        aesthetik = st.checkbox("Ästhetisches Fach (Musik oder Kunst)")
        if aesthetik:
            aest_fach = st.radio("Welches?", ["Musik", "Kunst"])
    else:
        aesthetik = False

    ethik_rel = st.radio("**Religion oder Philosophie**", ["Religion", "Philosophie"])

    weitere_wp = st.multiselect("**Weitere WP-Fächer** (Ge, Ek, Wp, Sp, …)", 
                                ["Geografie", "Wirtschaft/Politik", "Darstellendes Spiel"])

    seminar = st.checkbox("Profilseminar / fächerübergreifendes Projekt")

# ────────────────────────────────────────────────
#  BERECHNUNG
# ────────────────────────────────────────────────
stunden_pro_halbjahr = defaultdict(float)

# Profilfach
stunden_pro_halbjahr.update(fach_stunden["Profilfach"])

# Kernfächer (fest)
for f in ["Deutsch", "Mathematik", "Kernfremdsprache"]:
    stunden_pro_halbjahr.update(fach_stunden[f])

# Gewählte Fächer
ausgewaehlte = set()

if kern_fs:
    ausgewaehlte.add(kern_fs)

for f in zweite_fs + dritte_fs:
    if f in fach_stunden:
        stunden_pro_halbjahr.update(fach_stunden[f])
        ausgewaehlte.add(f)

# Verpflichtende NW
if verpf_nw:
    stunden_pro_halbjahr.update(fach_stunden[verpf_nw])
    ausgewaehlte.add(verpf_nw)

# Zusätzliches MINT
if zusaetz_mint:
    stunden_pro_halbjahr.update(fach_stunden["Informatik"])  # Beispiel

# Ästhetik
if aesthetik and aest_fach:
    stunden_pro_halbjahr.update(fach_stunden[aest_fach])
    ausgewaehlte.add(aest_fach)

# Religion/Phil.
if ethik_rel:
    stunden_pro_halbjahr.update(fach_stunden[ethik_rel])
    ausgewaehlte.add(ethik_rel)

# Weitere WP
for f in weitere_wp:
    if f in fach_stunden:
        stunden_pro_halbjahr.update(fach_stunden[f])
        ausgewaehlte.add(f)

# Seminar
if seminar:
    stunden_pro_halbjahr.update(fach_stunden["Profilseminar"])

# Summen
summen = {hj: round(stunden_pro_halbjahr[hj],1) for hj in halbjahre}

# ────────────────────────────────────────────────
#  ANZEIGE
# ────────────────────────────────────────────────
st.subheader("Deine Wochenstunden pro Halbjahr")

df = pd.DataFrame({
    "Halbjahr": halbjahre,
    "Stunden": [summen[h] for h in halbjahre]
})

df["Bewertung"] = df["Stunden"].apply(
    lambda x: "🟢 OK" if 28 <= x <= 34 else "🟡 Hoch" if x <= 36 else "🔴 Zu hoch"
)

st.dataframe(df.style.format({"Stunden": "{:.1f}"}), use_container_width=True)

if max(summen.values()) > 35:
    st.warning("Achtung: In der Einführungsphase (E-Phase) sind mehr als 35 Wochenstunden sehr belastend!")

# ────────────────────────────────────────────────
#  ABITUR-INFO
# ────────────────────────────────────────────────
st.subheader("Welche Fächer können wie ins Abitur eingebracht werden?")

with st.expander("Allgemeine Regeln (OAPVO SH ab 2025 / Abitur 2027)"):
    st.info("""
    • Nur **zwei** Fächer auf erhöhtem Niveau (5 h in Q):  
      → dein **Profilfach** + **ein** Kernfach (Deutsch, Mathematik oder Kernfremdsprache)  
    • Mindestens **ein** Fach pro Aufgabenfeld muss eingebracht werden  
    • Mindestens **zwei** Fremdsprachen insgesamt  
    • Mindestens **eine** Naturwissenschaft  
    • 36 Halbjahresnoten aus Q1–Q2 + 4 Prüfungen (3 schriftlich, 1 mündlich oder Bes.LL)
    """)

for fach in sorted(ausgewaehlte):
    if fach in abitur_info:
        with st.expander(f"{fach}"):
            st.info(abitur_info[fach])

st.caption("Stand: Februar 2026 – basierend auf OAPVO SH & Katharineum-Tabellen 2024/25")
