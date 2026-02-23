import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, storage
import numpy as np
from keras.models import load_model
from PIL import Image, ImageOps
import os
from datetime import datetime

# --- 1. FIREBASE INITIALISIERUNG ---
def init_firebase():
    # Prüfen, ob die App bereits läuft (wichtig für Streamlit Re-runs)
    if not firebase_admin._apps:
        try:
            base_path = os.path.dirname(__file__)
            key_path = os.path.join(base_path, "firebase-key.json")
            
            if not os.path.exists(key_path):
                st.error(f"❌ Datei nicht gefunden: {key_path}")
                return False
                
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred, {
                'storageBucket': 'DEIN-PROJEKT-ID.appspot.com' # <--- HIER DEINE ID EINTRAGEN
            })
            return True
        except Exception as e:
            st.error(f"❌ Firebase Fehler: {e}")
            return False
    return True

# Initialisierung ausführen
if init_firebase():
    db = firestore.client()
    bucket = storage.bucket()
else:
    st.warning("Warte auf Firebase-Konfiguration...")
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
        st.error(f"❌ Fehler beim Laden des KI-Modells: {e}")
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
    # Entfernt "0 " oder "1 " vom Anfang des Labels
    label = class_names[index].strip()[2:]
    return label, float(prediction[0][index])

# --- 3. UI LAYOUT ---
st.set_page_config(page_title="Katharineum Fundbüro", layout="wide")
st.title("🏫 Digitales Fundbüro Katharineum")

tab1, tab2 = st.tabs(["🔍 Suchen", "📤 Neues Fundstück melden"])

# --- TAB 1: SUCHEN ---
with tab1:
    search_query = st.text_input("Wonach suchst du? (z.B. Stift)")
    
    try:
        items_ref = db.collection("fundsachen")
        docs = items_ref.stream()
        
        cols = st.columns(4)
        count = 0
        
        for doc in docs:
            item = doc.to_dict()
            kat = item.get('kategorie', 'Unbekannt')
            
            # Suche/Filter
            if not search_query or search_query.lower() in kat.lower():
                with cols[count % 4]:
                    st.image(item.get('bild_url'), use_container_width=True)
                    st.write(f"**{kat}**")
                    st.caption(f"Gefunden: {item.get('datum')}")
                count += 1
        
        if count == 0:
            st.info("Keine Fundstücke gefunden.")
    except Exception as e:
        st.error(f"Fehler beim Laden der Daten: {e}")

# --- TAB 2: MELDEN ---
with tab2:
    st.subheader("Gegenstand registrieren")
    uploaded_file = st.file_uploader("Bild auswählen", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        img = Image.open(uploaded_file).convert("RGB")
        st.image(img, width=300)
        
        if st.button("KI-Analyse & Speichern"):
            if model is None:
                st.error("KI-Modell nicht geladen.")
            else:
                with st.spinner("KI arbeitet..."):
                    # 1. KI Vorhersage
                    label, score = predict_category(img)
                    
                    # 2. Bild-Upload
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    file_name = f"images/{timestamp}.jpg"
                    blob = bucket.blob(file_name)
                    
                    img.save("temp_upload.jpg")
                    blob.upload_from_filename("temp_upload.jpg")
                    blob.make_public()
                    public_url = blob.public_url
                    
                    # 3. In Datenbank speichern
                    db.collection("fundsachen").add({
                        "kategorie": label,
                        "bild_url": public_url,
                        "datum": datetime.now().strftime("%d.%m.%Y, %H:%M"),
                        "sicherheit": score
                    })
                    
                    st.success(f"Erfolgreich als '{label}' gespeichert!")
                    if os.path.exists("temp_upload.jpg"):
                        os.remove("temp_upload.jpg")
