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
    
    # Debug: Zeige Verbindungsinfos
    st.sidebar.success("✅ Supabase verbunden")
    
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
            st.write(f"📊 {len(items)} Fundstücke gefunden")
            cols = st.columns(4)
            for i, item in enumerate(items):
                with cols[i % 4]:
                    st.image(item['image_url'], use_container_width=True)
                    st.write(f"**{item['category']}**")
                    st.caption(f"ID: {item['id']}")  # Zeige ID für Debug
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
                        st.info(f"🤖 KI erkannte: **{label}** ({score:.2%} Wahrscheinlichkeit)")
                        
                        # Bild speichern
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        file_name = f"{timestamp}.jpg"
                        img.save(temp_file)
                        
                        # --- STORAGE UPLOAD ---
                        try:
                            # Prüfe ob Bucket existiert und zugänglich ist
                            storage = supabase.storage.from_("images")
                            
                            # Versuche zuerst zu listen (testet Berechtigung)
                            try:
                                files = storage.list()
                                st.sidebar.write(f"📁 {len(files)} Dateien im Bucket")
                            except:
                                st.sidebar.warning("Bucket existiert vielleicht nicht")
                            
                            # Bild hochladen
                            with open(temp_file, "rb") as f:
                                storage.upload(
                                    path=file_name,
                                    file=f,
                                    file_options={"content-type": "image/jpeg"}
                                )
                            
                            public_url = storage.get_public_url(file_name)
                            st.sidebar.success(f"✅ Bild hochgeladen: {file_name}")
                            
                        except Exception as storage_error:
                            st.error(f"❌ Storage Fehler: {storage_error}")
                            
                            # Alternative: Direkter REST Upload
                            try:
                                headers = {
                                    "apikey": key,
                                    "Authorization": f"Bearer {key}",
                                }
                                
                                with open(temp_file, "rb") as f:
                                    files = {"file": (file_name, f, "image/jpeg")}
                                    
                                upload_url = f"{url}/storage/v1/object/images/{file_name}"
                                response = requests.post(upload_url, headers=headers, files=files)
                                
                                if response.status_code == 200:
                                    public_url = f"{url}/storage/v1/object/public/images/{file_name}"
                                    st.sidebar.success("✅ Alternativer Upload erfolgreich")
                                else:
                                    st.error(f"Upload fehlgeschlagen: {response.text}")
                                    raise Exception("Upload fehlgeschlagen")
                                    
                            except Exception as e:
                                st.error(f"❌ Auch alternativer Upload fehlgeschlagen: {e}")
                                raise
                        
                        # --- DATENBANK EINTRAG (mit id als SERIAL PRIMARY KEY) ---
                        try:
                            # WICHTIG: id wird automatisch von der Datenbank vergeben
                            # Wir lassen id einfach weg - das ist korrekt!
                            insert_data = {
                                "category": label,
                                "image_url": public_url,
                                "created_at": datetime.now().isoformat()
                            }
                            
                            # Optional: confidence nur wenn die Spalte existiert
                            # Prüfe zuerst ob die confidence Spalte existiert
                            try:
                                # Test mit einem Select um Spalten zu sehen
                                sample = supabase.table("items").select("*").limit(1).execute()
                                if sample.data:
                                    columns = list(sample.data[0].keys())
                                    st.sidebar.write("📋 Tabellenspalten:", columns)
                                    
                                    # Füge confidence nur hinzu wenn die Spalte existiert
                                    if 'confidence' in columns:
                                        insert_data['confidence'] = score
                            except:
                                pass  # Ignoriere Fehler beim Spalten-Check
                            
                            # Insert durchführen
                            result = supabase.table("items").insert(insert_data).execute()
                            
                            if result.data:
                                new_id = result.data[0].get('id')
                                st.success(f"✅ Erfolgreich als '{label}' gespeichert! (ID: {new_id})")
                                st.balloons()
                            else:
                                st.warning("⚠️ Bild gespeichert, aber Datenbank-Eintrag lieferte keine Daten")
                                
                        except Exception as db_error:
                            st.error(f"❌ Datenbank Fehler: {db_error}")
                            
                            # Zeige detaillierte Fehlerinformationen
                            st.info("""
                            **Mögliche Ursachen:**
                            1. Die Tabelle 'items' existiert nicht
                            2. Die Spaltennamen stimmen nicht überein
                            3. Ein Pflichtfeld fehlt
                            
                            **Erwartete Tabellenstruktur:**
                            - id (bigserial, PRIMARY KEY) - wird automatisch vergeben
                            - category (text)
                            - image_url (text)
                            - created_at (timestamp)
                            - confidence (float, optional)
                            """)
                            
                            # Zeige den Versuchten Insert
                            st.code(f"Versuchter Insert: {insert_data}", language="json")
                            
                            # Biete manuellen Eintrag an
                            st.markdown("---")
                            st.subheader("📝 Manueller Eintrag")
                            st.markdown(f"""
                            **Falls der automatische Eintrag nicht klappt:**
                            
                            1. Gehe zum [Supabase Dashboard]({url})
                            2. Öffne den Table Editor
                            3. Füge diesen Eintrag manuell ein:
                            
                            ```json
                            {{
                              "category": "{label}",
                              "image_url": "{public_url}",
                              "created_at": "{datetime.now().isoformat()}"
                            }}
""")
