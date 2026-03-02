import streamlit as st
import numpy as np
import os
from datetime import datetime
from PIL import Image, ImageOps
import requests

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
    
    # Debug: Zeige Verbindungsinfos (ohne den vollen Key zu zeigen)
    st.sidebar.write("✅ Supabase verbunden")
    st.sidebar.write(f"URL: {url[:30]}...")
    
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
                    temp_file = "temp.jpg"
                    
                    try:
                        # KI Vorhersage
                        label, score = predict_category(img)
                        st.info(f"KI erkannte: {label} ({score:.2%})")
                        
                        # Bild speichern
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        file_name = f"{timestamp}.jpg"
                        img.save(temp_file)
                        
                        # --- METHODE 1: Supabase Storage Upload (korrigiert) ---
                        try:
                            with open(temp_file, "rb") as f:
                                # WICHTIG: Storage-Bucket existiert? Prüfen!
                                storage = supabase.storage.from_("images")
                                
                                # Test: Liste vorhandene Dateien
                                try:
                                    files = storage.list()
                                    st.sidebar.write(f"📁 Dateien im Bucket: {len(files)}")
                                except Exception as e:
                                    st.sidebar.warning(f"Bucket-List Fehler: {e}")
                                
                                # Upload mit expliziten Parametern
                                storage.upload(
                                    path=file_name,
                                    file=f,
                                    file_options={"content-type": "image/jpeg", "upsert": "true"}
                                )
                                
                            # Öffentliche URL abrufen
                            public_url = storage.get_public_url(file_name)
                            st.sidebar.success(f"✅ Bild hochgeladen: {file_name}")
                            
                        except Exception as storage_error:
                            st.error(f"Storage Fehler: {storage_error}")
                            
                            # --- METHODE 2: Fallback - Direkter REST Upload ---
                            st.info("Versuche alternativen Upload...")
                            
                            headers = {
                                "apikey": key,
                                "Authorization": f"Bearer {key}",
                                "Content-Type": "image/jpeg"
                            }
                            
                            with open(temp_file, "rb") as f:
                                image_data = f.read()
                            
                            upload_url = f"{url}/storage/v1/object/images/{file_name}"
                            response = requests.post(upload_url, headers=headers, data=image_data)
                            
                            if response.status_code == 200:
                                public_url = f"{url}/storage/v1/object/public/images/{file_name}"
                                st.sidebar.success("✅ Alternativer Upload erfolgreich")
                            else:
                                st.error(f"❌ Alternativer Upload fehlgeschlagen: {response.status_code} - {response.text}")
                                raise Exception("Upload fehlgeschlagen")
                        
                        # --- In Datenbank speichern ---
                        try:
                            # Prüfe ob Tabelle existiert und schreibbar ist
                            insert_data = {
                                "category": label,
                                "image_url": public_url,
                                "created_at": datetime.now().isoformat(),
                                "confidence": score
                            }
                            
                            result = supabase.table("items").insert(insert_data).execute()
                            
                            if result.data:
                                st.success(f"✅ Erfolgreich als '{label}' gespeichert!")
                                st.balloons()
                            else:
                                st.warning("⚠️ Bild gespeichert, aber Datenbank-Eintrag fehlgeschlagen")
                                
                        except Exception as db_error:
                            st.error(f"❌ Datenbank Fehler: {db_error}")
                            
                            # Zeige die Datenbank-Struktur für Debugging
                            try:
                                # Test: Einfacher Select
                                test = supabase.table("items").select("*").limit(1).execute()
                                st.sidebar.write("✅ Datenbank lesbar")
                                if test.data:
                                    st.sidebar.write("Spalten:", list(test.data[0].keys()))
                            except Exception as select_error:
                                st.sidebar.error(f"❌ Datenbank nicht lesbar: {select_error}")
                            
                            # Manuellen Eintrag vorschlagen
                            st.info(f"""
                            **Manueller Datenbank-Eintrag:**
                            - Bild-URL: {public_url}
                            - Kategorie: {label}
                            
                            Füge diesen Eintrag manuell im Supabase Dashboard ein.
                            """)
                    
                    except Exception as e:
                        st.error(f"❌ Allgemeiner Fehler: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
                    
                    finally:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                            st.sidebar.write("🧹 Temporäre Datei gelöscht")
