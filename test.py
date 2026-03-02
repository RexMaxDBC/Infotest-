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

# --- 1. KOMPATIBILITÄTS-FIX FÜR KERAS ---
class FixedDepthwiseConv2D(DepthwiseConv2D):
    def __init__(self, **kwargs):
        if 'groups' in kwargs:
            del kwargs['groups']
        super().__init__(**kwargs)

# --- 2. SUPABASE SETUP (SECRETS) ---
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
    
    # OPTION 1: Mit Service Role Key (für Backend-Operationen)
    # Falls du einen Service Role Key in den Secrets hast:
    # service_key: str = st.secrets["SUPABASE_SERVICE_KEY"]
    # supabase = create_client(url, service_key)
    
except Exception as e:
    st.error("❌ Fehler: Supabase Secrets nicht gefunden.")
    st.info("Bitte trage SUPABASE_URL und SUPABASE_KEY in den Streamlit Settings ein.")
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
        st.error(f"❌ KI-Modell Fehler: {e}")
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
    label = class_names[index].strip()[2:]  # Entfernt "0 " am Anfang
    return label, float(prediction[0][index])

# --- 4. UI LAYOUT ---
st.set_page_config(page_title="Fundbüro Katharineum", layout="wide", page_icon="🏫")
st.title("🏫 Digitales Fundbüro Katharineum")

tab1, tab2 = st.tabs(["🔍 Suchen", "📤 Fundstück melden"])

# --- TAB 1: SUCHEN ---
with tab1:
    search_query = st.text_input("Wonach suchst du?", placeholder="z.B. Stift")
    
    try:
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
    except Exception as e:
        st.error(f"Fehler beim Abrufen: {e}")

# --- TAB 2: MELDEN ---
with tab2:
    st.subheader("Neues Fundstück erfassen")
    uploaded_file = st.file_uploader("Bild auswählen", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        img = Image.open(uploaded_file).convert("RGB")
        st.image(img, width=300)
        
        if st.button("KI-Analyse & Speichern"):
            if model is None:
                st.error("KI konnte nicht geladen werden.")
            else:
                with st.spinner("Verarbeite..."):
                    try:
                        # KI Vorhersage
                        label, score = predict_category(img)
                        
                        # Bild-Upload
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        file_name = f"{timestamp}.jpg"
                        img.save("temp.jpg")
                        
                        # Bild in Supabase Storage hochladen
                        with open("temp.jpg", "rb") as f:
                            # WICHTIG: Korrekte Parameter-Reihenfolge
                            supabase.storage.from_("images").upload(
                                path=file_name,
                                file=f,
                                file_options={"content-type": "image/jpeg"}
                            )
                        
                        # Öffentliche URL generieren
                        public_url = supabase.storage.from_("images").get_public_url(file_name)
                        
                        # In Datenbank speichern - MIT AUTHENTIFIZIERUNG
                        # OPTION 2: Anonymen User erstellen (falls RLS für anonyme inserts erlaubt)
                        # Oder: RLS vorübergehend deaktivieren (nur für Entwicklung)
                        
                        # Versuche mit Insert
                        data = supabase.table("items").insert({
                            "category": label,
                            "image_url": public_url,
                            "created_at": datetime.now().isoformat()
                        }).execute()
                        
                        st.success(f"✅ Als '{label}' gespeichert!")
                        
                    except Exception as e:
                        st.error(f"❌ Fehler beim Speichern: {str(e)}")
                        st.info("""
                        **Lösungsmöglichkeiten:**
                        1. **RLS Policy in Supabase erstellen** (empfohlen):
                           - Gehe zu Authentication → Policies
                           - Erstelle eine INSERT Policy für "items" Tabelle
                           - Erlaube INSERT für "anon" oder "authenticated" users
                        
                        2. **Service Role Key verwenden**:
                           - Füge SUPABASE_SERVICE_KEY zu den Secrets hinzu
                           - Verwende diesen Key statt dem anon key
                        
                        3. **RLS temporär deaktivieren** (nur für Tests):
                           - In Supabase Dashboard → Authentication → Policies
                           - Bei der "items" Tabelle "Disable RLS" wählen
                        """)
                    finally:
                        if os.path.exists("temp.jpg"):
                            os.remove("temp.jpg")
