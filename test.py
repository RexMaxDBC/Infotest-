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

# --- 4. ADVANCED UI DESIGN (CSS) ---
st.set_page_config(page_title="Fundbüro Katharineum", layout="wide", page_icon="🏫")

st.markdown("""
    <style>
    /* Hintergrund der App */
    .stApp { background-color: #fdfdfd; }
    
    /* Titel-Styling */
    .main-title {
        font-family: 'Helvetica Neue', sans-serif;
        color: #1e3a8a;
        text-align: center;
        padding: 20px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* Karte für Fundstücke */
    div[data-testid="stVerticalBlock"] > div.stColumn > div {
        background: white;
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #eee;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    
    div[data-testid="stVerticalBlock"] > div.stColumn > div:hover {
        transform: translateY(-5px);
        border-color: #3b82f6;
    }

    /* Tab-Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f1f5f9;
        border-radius: 10px;
        padding: 10px 25px;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] { background-color: #3b82f6 !important; color: white !important; }

    /* Bild-Rahmen */
    .stImage img { border-radius: 10px; object-fit: cover; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🏫 Digitales Fundbüro Katharineum</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 KATALOG DURCHSUCHEN", "📤 NEUES FUNDSTÜCK MELDEN"])

# ===============================
# TAB 1 – KATALOG (GRID LAYOUT)
# ===============================
with tab1:
    col1, col2 = st.columns([2,1])
    with col1:
        search_query = st.text_input("", placeholder="Suche nach Kategorie oder ID...", label_visibility="collapsed")
    
    try:
        query = supabase.table("items").select("*")
        if search_query:
            if search_query.isdigit(): query = query.eq("id", int(search_query))
            else: query = query.ilike("category", f"%{search_query}%")

        result = query.order("created_at", descending=True).execute()
        items = result.data

        if items:
            # Erstellt ein Raster (4 Spalten)
            rows = [items[i:i + 4] for i in range(0, len(items), 4)]
            for row in rows:
