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

# --- 4. UI DESIGN (CSS) ---
st.set_page_config(page_title="Fundbüro Katharineum", layout="wide", page_icon="🏫")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .main-title {
        color: #1e3a8a;
        text-align: center;
        font-weight: 800;
        padding: 10px;
    }
    /* Karten-Design für Fundstücke */
    .item-container {
        background: white;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🏫 Digitales Fundbüro Katharineum</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 KATALOG DURCHSUCHEN", "📤 NEUES FUNDSTÜCK MELDEN"])

# ===============================
# TAB 1 – KATALOG
# ===============================
with tab1:
    search_query = st.text_input("Suche nach Gegenstand oder ID", placeholder="z.B. Tasche...")
    
    try:
        query = supabase.table("items").select("*")
        if search_query:
            if search_query.isdigit():
                query = query.eq("id", int(search_query))
            else:
                query = query.ilike("category", f"%{search_query}%")

        result = query.order("created_at", descending=True).execute()
        items = result.data

        if items:
            # Grid mit 4 Spalten
            for i in range(0, len(items), 4):
                cols = st.columns(4)
                chunk = items[i:i + 4]
                for idx, item in enumerate(chunk):
                    with cols[idx]:
                        st.markdown('<div class="item-container">', unsafe_allow_html=True)
                        st.image(item['image_url'], use_container_width=True)
                        st.markdown(f"**{item['category']}**")
                        st.caption(f"🆔 ID: {item['id']} | 📅 {datetime.fromisoformat(item['created_at']).strftime('%d.%m.')}")
                        st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Keine Fundstücke gefunden.")
    except Exception as e:
        st.error(f"Fehler beim Laden: {e}")

# ===============================
# TAB 2 – MELDEN
# ===============================
with tab2:
    st.subheader("Neues Fundstück erfassen")
    col_img, col_info = st.columns([1, 1])
    
    with col_img:
        uploaded_file = st.file_uploader("Bild hochladen", type=["jpg", "png", "jpeg"])
        if uploaded_file:
            img = Image.open(uploaded_file).convert("RGB")
            st.image(img, use_container_width=True, caption="Vorschau")

    with col_info:
        if uploaded_file:
            if st.button("🚀 ANALYSIEREN & SPEICHERN", use_container_width=True):
                if model is None:
                    st.error("KI-Modell nicht geladen.")
                else:
                    try:
                        with st.spinner("KI analysiert..."):
                            # 1. Analyse
                            label, score = predict_category(img)
                            
                            # 2. Temporär speichern
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            file_name = f"{timestamp}.jpg"
                            img.save("temp_upload.jpg")

                            # 3. Supabase Upload
                            with open("temp_upload.jpg", "rb") as f:
                                supabase.storage.from_("images").upload(file_name, f)

                            # 4. Datenbank Eintrag
                            public_url = supabase.storage.from_("images").get_public_url(file_name)
                            response = supabase.table("items").insert({
                                "category": label, 
                                "image_url": public_url
                            }).execute()

                            if response.data:
                                st.success(f"Erfolgreich als '{label}' gespeichert!")
                                st.balloons()
                            
                            if os.path.exists("temp_upload.jpg"):
                                os.remove("temp_upload.jpg")
                    except Exception as e:
                        st.error(f"Fehler: {e}")
        else:
            st.info("Bitte lade ein Foto hoch, um zu beginnen.")
