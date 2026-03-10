import streamlit as st
import numpy as np
import os
from datetime import datetime
from PIL import Image, ImageOps
import tensorflow as tf
from keras.models import load_model
from keras.layers import DepthwiseConv2D
from supabase import create_client, Client

# --- 1. KOMPATIBILITÄTS-FIX ---
class FixedDepthwiseConv2D(DepthwiseConv2D):
    def __init__(self, **kwargs):
        if 'groups' in kwargs: del kwargs['groups']
        super().__init__(**kwargs)

# --- 2. SUPABASE SETUP ---
try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except Exception:
    st.error("❌ Supabase Verbindung fehlgeschlagen.")
    st.stop()

# --- 3. KI MODELL SETUP ---
@st.cache_resource
def setup_ai():
    try:
        model = load_model("keras_model.h5", compile=False, custom_objects={'DepthwiseConv2D': FixedDepthwiseConv2D})
        with open("labels.txt", "r") as f: class_names = f.readlines()
        return model, class_names
    except: return None, None

model, class_names = setup_ai()

def predict_category(image):
    size = (224, 224)
    image_resized = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    image_array = np.asarray(image_resized)
    normalized = (image_array.astype(np.float32) / 127.5) - 1
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0] = normalized
    prediction = model.predict(data)
    index = np.argmax(prediction)
    return class_names[index].strip()[2:], float(prediction[0][index])

# --- 4. MODERN UI DESIGN (CSS) ---
st.set_page_config(page_title="Fundbüro Katharineum", layout="wide", page_icon="🏫")

st.markdown("""
    <style>
    /* Hintergrund und Schrift */
    .main { background-color: #f8f9fa; }
    
    /* Karten-Design für Fundstücke */
    .item-card {
        background-color: white;
        border-radius: 15px;
        padding: 15px;
        border: 1px solid #e0e0e0;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        transition: 0.3s;
    }
    .item-card:hover { box-shadow: 5px 5px 15px rgba(0,0,0,0.1); }
    
    /* Header-Styling */
    .main-header {
        color: #003366;
        font-family: 'serif';
        font-weight: bold;
        text-align: center;
        margin-bottom: 10px;
    }
    
    /* Stats-Box */
    .stats-container {
        background: linear-gradient(90deg, #003366 0%, #00509d 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER & STATS ---
st.markdown("<h1 class='main-header'>🏫 Digitales Fundbüro Katharineum</h1>", unsafe_allow_html=True)

# Kurze Statistik abrufen
try:
    total_items = supabase.table("items").select("*", count="exact").execute().count
except:
    total_items = 0

st.markdown(f"""
    <div class='stats-container'>
        <h3 style='margin:0; color:white;'>Aktuell gelistete Fundstücke: {total_items}</h3>
        <p style='margin:0; opacity:0.8;'>Hilf mit, verlorene Gegenstände zurückzugeben!</p>
    </div>
    """, unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 Fundstücke durchsuchen", "📤 Neues Fundstück melden"])

# ===============================
# TAB 1 – SUCHEN & KATALOG
# ===============================
with tab1:
    search_col, filter_col = st.columns([3, 1])
    with search_col:
        search_query = st.text_input("🔍 Suchbegriff eingeben...", placeholder="z.B. Jacke, Schlüssel, Tasche")
    with filter_col:
        sort_order = st.selectbox("Sortierung", ["Neueste zuerst", "Älteste zuerst"])

    try:
        query = supabase.table("items").select("*")
        if search_query:
            if search_query.isdigit(): query = query.eq("id", int(search_query))
            else: query = query.ilike("category", f"%{search_query}%")
        
        # Sortierung
        query = query.order("created_at", descending=(sort_order == "Neueste zuerst"))
        items = query.execute().data

        if items:
            # Grid-System für die Karten
            cols = st.columns(4)
            for i, item in enumerate(items):
                with cols[i % 4]:
                    st.markdown(f"""
                        <div class="item-card">
                            <img src="{item['image_url']}" style="width:100%; height:180px; object-fit:cover; border-radius:10px; margin-bottom:10px;">
                            <span style="background-color:#e1ecf4; color:#003366; padding:2px 8px; border-radius:5px; font-size:12px;">#{item['id']}</span>
                            <h4 style="margin:5px 0;">{item['category']}</h4>
                            <p style="color:gray; font-size:13px; margin:0;">📅 {datetime.fromisoformat(item['created_at']).strftime('%d.%m.%Y')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    if st.button(f"Details zu #{item['id']}", key=f"btn_{item['id']}"):
                        st.info(f"Bitte melde dich im Sekretariat mit der ID #{item['id']}, um diesen Gegenstand abzuholen.")
        else:
            st.info("Keine Fundstücke gefunden. Probier es mit einem anderen Suchbegriff.")
    except Exception as e:
        st.error(f"Katalog konnte nicht geladen werden.")

# ===============================
# TAB 2 – MELDEN (AI UNTERSTÜTZT)
# ===============================
with tab2:
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.subheader("📸 Foto aufnehmen / hochladen")
        uploaded_file = st.file_uploader("Bild des Gegenstands", type=["jpg", "png", "jpeg"])
        if uploaded_file:
            img = Image.open(uploaded_file).convert("RGB")
            st.image(img, use_container_width=True, caption="Vorschau")

    with col_b:
        st.subheader("📋 Erfassung")
        if uploaded_file:
            if st.button("🚀 Gegenstand analysieren & speichern", use_container_width=True):
                if model is None:
                    st.error("KI-System offline.")
                else:
                    try:
                        with st.spinner("KI analysiert das Bild..."):
                            label, score = predict_category(img)
                            
                            # Speicher-Logik
                            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                            file_name = f"{ts}.jpg"
                            img.save("temp.jpg")

                            with open("temp.jpg", "rb") as f:
                                supabase.storage.from_("images").upload(file_name, f)
                            
                            url = supabase.storage.from_("images").get_public_url(file_name)
                            
                            res = supabase.table("items").insert({
                                "category": label, "image_url": url
                            }).execute()

                            if res.data:
                                st.balloons()
                                st.success(f"Erfolgreich erfasst!")
                                st.markdown(f"""
                                    **Ergebnis der KI-Analyse:**
                                    - Kategorie: `{label}`
                                    - Sicherheit: `{score*100:.1f}%`
                                    - Registrierte ID: `{res.data[0]['id']}`
                                """)
                                st.warning("Bitte lege den Gegenstand jetzt in den Fund-Schrank im Erdgeschoss.")
                    except Exception as e:
                        st.error(f"Fehler: {e}")
        else:
            st.info("Lade ein Bild hoch, um die automatische Erfassung zu starten.")

# --- FOOTER ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>© 2024 Katharineum zu Lübeck - Digitales Fundbüro Projekt</p>", unsafe_allow_html=True)
