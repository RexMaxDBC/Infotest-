import streamlit as st
import numpy as np
import os
from datetime import datetime
from PIL import Image, ImageOps

# TensorFlow/Keras Imports
import tensorflow as tf
from keras.models import load_model
from keras.layers import DepthwiseConv2D
from supabase import create_client, Client

# --- 1. KOMPATIBILITÄTS-FIX ---
class FixedDepthwiseConv2D(DepthwiseConv2D):
    def __init__(self, **kwargs):
        if 'groups' in kwargs:
            del kwargs['groups']
        super().__init__(**kwargs)

# --- 2. SUPABASE SETUP ---
# Stelle sicher, dass die Secrets in Streamlit hinterlegt sind!
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"❌ Supabase Verbindung fehlerhaft: {e}")
    st.stop()

# --- 3. KI MODELL SETUP ---
@st.cache_resource
def setup_ai():
    try:
        model = load_model(
            "keras_model.h5",
            compile=False,
            custom_objects={'DepthwiseConv2D': FixedDepthwiseConv2D}
        )
        with open("labels.txt", "r") as f:
            class_names = f.readlines()
        return model, class_names
    except Exception as e:
        st.error(f"❌ KI-Modell konnte nicht geladen werden: {e}")
        return None, None

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

# --- 4. UI ---
st.set_page_config(page_title="Fundbüro Katharineum", layout="wide", page_icon="🏫")

# Custom CSS für schönes Design ohne die Logik zu brechen
st.markdown("""
    <style>
    .item-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #ddd;
        margin-bottom: 20px;
    }
    .main-title {
        color: #003366;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🏫 Digitales Fundbüro Katharineum</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 Suchen", "📤 Fundstück melden"])

# ===============================
# TAB 1 – SUCHEN
# ===============================
with tab1:
    search_query = st.text_input("Wonach suchst du?", placeholder="z.B. Stift oder ID")

    try:
        query = supabase.table("items").select("*")

        if search_query:
            if search_query.isdigit():
                query = query.eq("id", int(search_query))
            else:
                query = query.ilike("category", f"%{search_query}%")

        # Sortierung: Neueste zuerst
        result = query.order("created_at", descending=True).execute()
        items = result.data

        if items:
            cols = st.columns(4)
            for i, item in enumerate(items):
                with cols[i % 4]:
                    st.markdown('<div class="item-card">', unsafe_allow_html=True)
                    st.image(item['image_url'], use_container_width=True)
                    st.write(f"🆔 **ID: {item['id']}**")
                    st.write(f"📂 {item['category']}")
                    st.caption(f"📅 {datetime.fromisoformat(item['created_at']).strftime('%d.%m.%Y %H:%M')}")
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Keine Fundstücke gefunden.")
    except Exception as e:
        st.error(f"Fehler beim Abrufen der Daten: {e}")

# ===============================
# TAB 2 – MELDEN
# ===============================
with tab2:
    st.subheader("Neues Fundstück erfassen")
    uploaded_file = st.file_uploader("Bild auswählen", type=["jpg", "png", "jpeg"])

    if uploaded_file:
        img = Image.open(uploaded_file).convert("RGB")
        st.image(img, width=300, caption="Vorschau")

        if st.button("KI-Analyse & Speichern"):
            if model is None:
                st.error("KI-Modell nicht verfügbar.")
            else:
                try:
                    with st.spinner("Wird verarbeitet..."):
                        # 1. KI Analyse
                        label, score = predict_category(img)

                        # 2. Bild temporär zwischenspeichern
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        file_name = f"{timestamp}.jpg"
                        img.save("temp_upload.jpg")

                        # 3. Upload zu Supabase Storage
                        with open("temp_upload.jpg", "rb") as f:
                            supabase.storage.from_("images").upload(file_name, f)

                        # 4. Öffentliche URL abrufen
                        public_url = supabase.storage.from_("images").get_public_url(file_name)

                        # 5. In Datenbank speichern
                        response = supabase.table("items").insert({
                            "category": label,
                            "image_url": public_url
                        }).execute()

                        # 6. Erfolg melden
                        if response.data:
                            new_item = response.data[0]
                            st.success(f"✅ Als '{label}' gespeichert! (ID: {new_item['id']})")
                            st.balloons()
                        
                        # Temporäre Datei löschen
                        if os.path.exists("temp_upload.jpg"):
                            os.remove("temp_upload.jpg")

                except Exception as e:
                    st.error(f"Fehler beim Speichern: {e}")
                    st.info("Falls Fehler 403 erscheint: Prüfe die SQL-Policies im Dashboard!")
