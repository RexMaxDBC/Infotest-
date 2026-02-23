import streamlit as st
import numpy as np
from keras.models import load_model
from PIL import Image, ImageOps
from supabase import create_client, Client
import os
from datetime import datetime

# --- 1. SUPABASE SETUP (SECRETS) ---
# Streamlit zieht sich diese Werte aus den "Secrets" Einstellungen (Online oder .streamlit/secrets.toml)
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("❌ Fehler: Supabase Secrets nicht gefunden oder Verbindung fehlgeschlagen.")
    st.info("Bitte trage SUPABASE_URL und SUPABASE_KEY in den Streamlit Settings ein.")
    st.stop()

# --- 2. KI MODELL SETUP ---
@st.cache_resource
def setup_ai():
    try:
        model = load_model("keras_model.h5", compile=False)
        with open("labels.txt", "r") as f:
            class_names = f.readlines()
        return model, class_names
    except Exception as e:
        st.error(f"❌ KI-Modell konnte nicht geladen werden: {e}")
        return None, None

model, class_names = setup_ai()

def predict_category(image):
    # Bildvorbereitung für das Modell (224x224)
    size = (224, 224)
    image_resized = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    image_array = np.asarray(image_resized)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
    
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0] = normalized_image_array
    
    prediction = model.predict(data)
    index = np.argmax(prediction)
    # Entfernt "0 " am Anfang des Labels
    label = class_names[index].strip()[2:]
    return label, float(prediction[0][index])

# --- 3. UI LAYOUT ---
st.set_page_config(page_title="Fundbüro Katharineum", layout="wide", page_icon="🏫")
st.title("🏫 Digitales Fundbüro Katharineum")

tab1, tab2 = st.tabs(["🔍 Suchen", "📤 Fundstück melden"])

# --- TAB 1: SUCHEN (Datenbank abfragen) ---
with tab1:
    search_query = st.text_input("Wonach suchst du?", placeholder="z.B. Stift oder Jacke")
    
    try:
        # Abfrage an die Tabelle 'items'
        query = supabase.table("items").select("*")
        
        if search_query:
            query = query.ilike("category", f"%{search_query}%")
        
        result = query.execute()
        items = result.data

        if items:
            cols = st.columns(4)
            for i, item in enumerate(items):
                with cols[i % 4]:
                    st.image(item['image_url'], use_container_width=True)
                    st.write(f"**{item['category']}**")
                    # Falls du ein Datum in der DB hast:
                    if 'created_at' in item:
                        st.caption(f"Gefunden am: {item['created_at'][:10]}")
        else:
            st.info("Keine Fundstücke gefunden.")
    except Exception as e:
        st.error(f"Fehler beim Abrufen der Daten: {e}")

# --- TAB 2: MELDEN (Upload & KI Analyse) ---
with tab2:
    st.subheader("Neues Fundstück erfassen")
    uploaded_file = st.file_uploader("Bild des Gegenstands", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        img = Image.open(uploaded_file).convert("RGB")
        st.image(img, width=300, caption="Vorschau")
        
        if st.button("Analysieren & In Datenbank speichern"):
            if model is None:
                st.error("KI-Modell nicht bereit.")
            else:
                with st.spinner("KI analysiert Bild und lädt Daten hoch..."):
                    # 1. KI Vorhersage treffen
                    label, score = predict_category(img)
                    
                    # 2. Bild in Supabase Storage hochladen
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    file_name = f"{timestamp}.jpg"
