import streamlit as st
import numpy as np
from keras.models import load_model
from PIL import Image, ImageOps
from supabase import create_client, Client
import os
from datetime import datetime

# --- 1. SUPABASE SETUP ---
# Ersetze diese mit deinen echten Daten aus den Supabase Settings (API)
SUPABASE_URL = "DEINE_SUPABASE_URL"
SUPABASE_KEY = "DEIN_SUPABASE_ANON_KEY"

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase: Client = init_supabase()
except Exception as e:
    st.error(f"Supabase Verbindung fehlgeschlagen: {e}")
    st.stop()

# --- 2. KI MODELL SETUP ---
@st.cache_resource
def setup_ai():
    model = load_model("keras_model.h5", compile=False)
    with open("labels.txt", "r") as f:
        class_names = f.readlines()
    return model, class_names

model, class_names = setup_ai()

def predict_category(image):
    size = (224, 224)
    image_resized = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    image_array = np.asarray(image_resized)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
    
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0] = normalized_image_array
    
    prediction = model.predict(data)
    index = np.argmax(prediction)
    label = class_names[index].strip()[2:]
    return label, float(prediction[0][index])

# --- 3. UI LAYOUT ---
st.set_page_config(page_title="Katharineum Fundbüro", layout="wide")
st.title("🏫 Digitales Fundbüro (Supabase)")

tab1, tab2 = st.tabs(["🔍 Suchen", "📤 Neues Fundstück melden"])

# --- TAB 1: SUCHEN ---
with tab1:
    search_query = st.text_input("Suchen nach...")
    
    # Daten aus Supabase abrufen
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
    else:
        st.info("Keine Fundstücke gefunden.")

# --- TAB 2: MELDEN ---
with tab2:
    st.subheader("Gegenstand erfassen")
    file = st.file_uploader("Bild hochladen", type=["jpg", "png", "jpeg"])
    
    if file:
        img = Image.open(file).convert("RGB")
        st.image(img, width=250)
        
        if st.button("Speichern"):
            with st.spinner("KI analysiert..."):
                # 1. KI Label
                label, score = predict_category(img)
                
                # 2. Bild-Upload in Storage
                file_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                img.save("temp.jpg")
                
                with open("temp.jpg", "rb") as f:
                    supabase.storage.from_("images").upload(file_name, f)
                
                # Public URL generieren
                public_url = supabase.storage.from_("images").get_public_url(file_name)
                
                # 3. Datenbank-Eintrag
                supabase.table("items").insert({
                    "category": label,
                    "image_url": public_url
                }).execute()
                
                st.success(f"Gespeichert als: {label}")
                os.remove("temp.jpg")
