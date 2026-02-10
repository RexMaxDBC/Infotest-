# ────────────────────────────────────────────────
# TABELLE AUFBAUEN – mit expliziter Längen-Kontrolle
# ────────────────────────────────────────────────
rows = []

# Profilfach
rows.append(["Profilfach (P1)", profil_fach] + [stunden_basis["Profilfach"][h] for h in halbjahre])

# Kernfächer
rows.append(["Kern", "Deutsch"] + [stunden_basis["Deutsch"][h] for h in halbjahre])
rows.append(["Kern", "Mathematik"] + [stunden_basis["Mathematik"][h] for h in halbjahre])
rows.append(["Kern", "Fremdsprache"] + [stunden_basis.get(kern_fs, stunden_basis["Englisch"])[h] for h in halbjahre])

# 2. FS
if zweite_fs != "Keine":
    rows.append(["2. FS", zweite_fs] + [stunden_basis.get(zweite_fs, stunden_basis["Englisch"])[h] for h in halbjahre])

# Verpf. NW
rows.append(["Verpf. NW", verpf_nw] + [stunden_basis[verpf_nw][h] for h in halbjahre])

# Ethik/Rel.
rows.append(["Ethik/Rel.", ethik_rel] + [stunden_basis[ethik_rel][h] for h in halbjahre])

# WP-Fächer
for w in wp:
    rows.append(["WP", w] + [stunden_basis.get(w, stunden_basis["Geografie"])[h] for h in halbjahre])

# Darstellendes Spiel – nur Ästhetik + als eigene Kategorie
if profil == "Ästhetisches Profil" and ds:
    rows.append(["Ästhetik-Seminar", "Darstellendes Spiel"] + [stunden_basis["Darstellendes Spiel"][h] for h in halbjahre])

# ────────────────────────────────────────────────
# Summen – jetzt LÄNGEN-SICHER
# ────────────────────────────────────────────────
num_cols = len(halbjahre) + 2  # Kategorie + Fach + 6 Halbjahre

# Alle Zeilen auf korrekte Länge bringen (sicherheitshalber)
for row in rows:
    while len(row) < num_cols:
        row.append(0)   # fehlende Werte mit 0 auffüllen

# Jetzt Summen berechnen
summ_row = ["**Summe**", ""]
for col_idx in range(2, num_cols):
    col_sum = 0
    for row in rows:
        val = row[col_idx]
        # numpy.int64 / int / float robust behandeln
        if hasattr(val, 'item'):
            col_sum += val.item()
        elif isinstance(val, (int, float)):
            col_sum += val
        else:
            col_sum += 0  # fallback
    summ_row.append(col_sum)

rows.append(summ_row)

# DataFrame erstellen
df = pd.DataFrame(rows, columns=["Kategorie", "Fach"] + halbjahre)

# Styling-Funktion (angepasst)
def highlight(row):
    styles = [''] * len(row)
    if row["Kategorie"] == "Profilfach (P1)":
        for i in range(len(styles)):
            styles[i] = 'background-color: #cce5ff; font-weight: bold'
    if row["Kategorie"] == "**Summe**":
        for i in range(len(styles)):
            styles[i] = 'background-color: #e8e8e8; font-weight: bold'
    return styles

# Anzeige
st.subheader("Stundenplan")
st.dataframe(
    df.style.apply(highlight, axis=1)
            .format("{:.0f}", na_rep="-"),
    use_container_width=True,
    hide_index=True
)

# Belastungshinweis
if "**Summe**" in df["Kategorie"].values:
    e1 = df[df["Kategorie"] == "**Summe**"]["E1"].iloc[0]
    e2 = df[df["Kategorie"] == "**Summe**"]["E2"].iloc[0]
    e_sum = e1 + e2
    if e_sum > 35:
        st.error(f"E-Phase: {e_sum} Stunden – deutlich zu hoch!")
    elif e_sum > 32:
        st.warning(f"E-Phase: {e_sum} Stunden – relativ hoch")
    else:
        st.success(f"E-Phase: {e_sum} Stunden – ok")
