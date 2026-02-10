import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Notenschnitt-Rechner", layout="wide")

# ─────────────────────────────────────────────
# Hilfsfunktion: Punkte → Note
# ─────────────────────────────────────────────
def punkte_zu_note(punkte: int) -> float:
    if not 0 <= punkte <= 15:
        return 6.0
    return round((17 - punkte) / 3, 2)

# ─────────────────────────────────────────────
# Session State – Initialisierung
# ─────────────────────────────────────────────
if "noten_eintraege" not in st.session_state:
    st.session_state.noten_eintraege = [{"note": 2.0, "gewicht": 1.0}]

if "punkte_eintraege" not in st.session_state:
    st.session_state.punkte_eintraege = [{"punkte": 11, "gewicht": 1.0}]

# ─────────────────────────────────────────────
# Haupt-Layout
# ─────────────────────────────────────────────
st.title("Notenschnitt-Rechner")
st.markdown("**Nur ein System pro Berechnung** – entweder Noten oder Punkte")

tab_noten, tab_punkte = st.tabs(["Schulnoten  •  1,0 – 6,0", "Notenpunkte  •  0 – 15"])

# ─────────────────────────────────────────────
# TAB 1: Nur Schulnoten
# ─────────────────────────────────────────────
with tab_noten:
    st.subheader("Gesamtschnitt – nur Schulnoten")

    cols = st.columns([5, 4, 3, 1])
    cols[0].markdown("**Note**")
    cols[1].markdown("**Gewichtung**")
    cols[2].markdown("**2-fach**")
    cols[3].markdown("")

    neue_liste = []

    for i, e in enumerate(st.session_state.noten_eintraege):
        c1, c2, c3, c4 = st.columns([5, 4, 3, 1])

        note = c1.number_input(
            "", 1.0, 6.0, float(e["note"]), 0.1, format="%.1f",
            key=f"note_val_{i}"
        )

        gewicht_sel = c2.selectbox(
            "", [0.5, 1.0, 2.0, 3.0],
            index=[0.5,1,2,3].index(e["gewicht"]) if e["gewicht"] in [0.5,1,2,3] else 1,
            format_func=lambda x: f"×{x:.1f}" if x != 1 else "normal",
            key=f"note_gewicht_sel_{i}"
        )

        ist_2fach = c3.checkbox("", value=(e["gewicht"] >= 2.0), key=f"note_2fach_{i}")
        gewicht = 2.0 if ist_2fach else gewicht_sel

        if c4.button("×", key=f"del_note_{i}", help="entfernen"):
            st.session_state.noten_eintraege.pop(i)
            st.rerun()

        neue_liste.append({"note": note, "gewicht": gewicht})

    st.session_state.noten_eintraege = neue_liste

    st.divider()

    col_a, col_b, col_c = st.columns([2, 2, 1])

    col_a.button(
        "➕ Note hinzufügen",
        use_container_width=True,
        key="btn_add_note",
        on_click=lambda: st.session_state.noten_eintraege.append({"note": 2.0, "gewicht": 1.0})
    )

    col_b.button(
        "↺ Liste löschen",
        use_container_width=True,
        key="btn_reset_note",
        on_click=lambda: setattr(st.session_state, "noten_eintraege", [{"note": 2.0, "gewicht": 1.0}])
    )

    # Export CSV – Noten
    if st.session_state.noten_eintraege:
        df_export = pd.DataFrame([
            {
                "Note": round(e["note"], 1),
                "Gewichtung": e["gewicht"],
                "Beitrag": round(e["note"] * e["gewicht"], 2)
            }
            for e in st.session_state.noten_eintraege
        ])
        csv = df_export.to_csv(index=False).encode('utf-8')
        col_c.download_button(
            "CSV exportieren",
            csv,
            "noten_schnitt.csv",
            "text/csv",
            use_container_width=True,
            key="download_noten_csv"
        )

        summe = sum(e["note"] * e["gewicht"] for e in st.session_state.noten_eintraege)
        ges_gew = sum(e["gewicht"] for e in st.session_state.noten_eintraege)
        if ges_gew > 0:
            st.metric("**Gesamtnotenschnitt**", f"{summe / ges_gew:.2f}")

# ─────────────────────────────────────────────
# TAB 2: Nur Notenpunkte
# ─────────────────────────────────────────────
with tab_punkte:
    st.subheader("Gesamtschnitt – nur Notenpunkte")

    cols = st.columns([4, 4, 4, 3, 1])
    cols[0].markdown("**Punkte**")
    cols[1].markdown("**→ Note**")
    cols[2].markdown("**Gewichtung**")
    cols[3].markdown("**2-fach**")
    cols[4].markdown("")

    neue_liste = []

    for i, e in enumerate(st.session_state.punkte_eintraege):
        c1, c2, c3, c4, c5 = st.columns([4, 4, 4, 3, 1])

        punkte = c1.number_input(
            "", 0, 15, int(e["punkte"]), 1,
            key=f"punkte_val_{i}"
        )

        note = punkte_zu_note(punkte)
        c2.markdown(f"**{note:.2f}**" if note <= 4.0 else f"{note:.2f}")

        gewicht_sel = c3.selectbox(
            "", [0.5, 1.0, 2.0, 3.0],
            index=[0.5,1,2,3].index(e["gewicht"]) if e["gewicht"] in [0.5,1,2,3] else 1,
            format_func=lambda x: f"×{x:.1f}" if x != 1 else "normal",
            key=f"punkte_gewicht_sel_{i}"
        )

        ist_2fach = c4.checkbox("", value=(e["gewicht"] >= 2.0), key=f"punkte_2fach_{i}")
        gewicht = 2.0 if ist_2fach else gewicht_sel

        if c5.button("×", key=f"del_punkte_{i}", help="entfernen"):
            st.session_state.punkte_eintraege.pop(i)
            st.rerun()

        neue_liste.append({"punkte": punkte, "gewicht": gewicht, "note": note})

    st.session_state.punkte_eintraege = neue_liste

    st.divider()

    col_a, col_b, col_c = st.columns([2, 2, 1])

    col_a.button(
        "➕ Punkte hinzufügen",
        use_container_width=True,
        key="btn_add_punkte",
        on_click=lambda: st.session_state.punkte_eintraege.append({"punkte": 11, "gewicht": 1.0})
    )

    col_b.button(
        "↺ Liste löschen",
        use_container_width=True,
        key="btn_reset_punkte",
        on_click=lambda: setattr(st.session_state, "punkte_eintraege", [{"punkte": 11, "gewicht": 1.0}])
    )

    # Export CSV – Punkte
    if st.session_state.punkte_eintraege:
        df_export = pd.DataFrame([
            {
                "Punkte": e["punkte"],
                "Note": round(e["note"], 2),
                "Gewichtung": e["gewicht"],
                "Beitrag": round(e["note"] * e["gewicht"], 2)
            }
            for e in st.session_state.punkte_eintraege
        ])
        csv = df_export.to_csv(index=False).encode('utf-8')
        col_c.download_button(
            "CSV exportieren",
            csv,
            "punkte_schnitt.csv",
            "text/csv",
            use_container_width=True,
            key="download_punkte_csv"
        )

        summe = sum(e["note"] * e["gewicht"] for e in st.session_state.punkte_eintraege)
        ges_gew = sum(e["gewicht"] for e in st.session_state.punkte_eintraege)
        if ges_gew > 0:
            st.metric("**Gesamtnotenschnitt**", f"{summe / ges_gew:.2f}")

    # ─── Umrechnungstabelle ────────────────────────────────
    with st.expander("Vollständige Umrechnungstabelle (Punkte → Note)", expanded=False):
        table_data = [{"Punkte": p, "Note": f"{punkte_zu_note(p):.2f}"} for p in range(15, -1, -1)]
        st.dataframe(pd.DataFrame(table_data), hide_index=True, use_container_width=True)

st.caption("• (17 – Punkte) ÷ 3 • Gewichtung 0,5–3,0× • CSV-Export enthält Beiträge")
