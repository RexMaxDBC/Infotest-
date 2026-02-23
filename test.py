import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, storage
import numpy as np
from keras.models import load_model
from PIL import Image, ImageOps
import os
from datetime import datetime

# --- FIREBASE SETUP ---
# Wir prüfen, ob die App bereits initialisiert ist, um Fehler bei Re-runs zu vermeiden
if not firebase_admin._apps:
    try:
        # Sucht den Key im aktuellen Verzeichnis
        base_path = os.path.dirname(__file__)
        key_path = os.path.join(base_path, "firebase-key.json")
        
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'DEIN-PROJEKT-ID.appspot.com'  # <-- HIER ANPASSEN
        })
    except Exception as e:
        st.error(f"Fehler beim Laden von Firebase: {e}")

db = firestore.client()
bucket = storage.bucket()

# --- KI MODELL SETUP ---
@st.cache_resource
def setup_ai():
    # Wir laden das Modell und die Labels
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
    # Entfernt die Nummer am Anfang des Labels (z.B. "0 ")
    label = class_names[index].strip()[2:]
    return label, float(prediction[0][index])

# --- UI LAYOUT ---
st.set_page_config(page_title="Katharineum Fundbüro", layout="wide")
st.title("🏫 Digitales Fundbüro Katharineum")

tab1, tab2 = st.tabs(["🔍 Suchen", "📤 Neues Fundstück melden"])

# --- TAB 1: SUCHEN ---
with tab1:
    search_query = st.text_input("Wonach suchst du? (Leer lassen für alle)")
    
    # Alle Dokumente aus der Sammlung "fundsachen" holen
    items_ref = db.collection("fundsachen")
    docs = items_ref.stream()
    
    cols = st.columns(4)
    item_count = 0
    
    for doc in docs:
        item = doc.to_dict()
        kat = item.get('kategorie', 'Unbekannt')
        
        # Filter-Logik
        if not search_query or search_query.lower() in kat.lower():
            with cols[item_count % 4]:
                st.image(item.get('bild_url'), use_container_width=True)
                st.write(f"**{kat}**")
                st.caption(f"Gefunden: {item.get('datum')}")
            item_count += 1
            
    if item_count == 0:
        st.info("Keine Fundstücke vorhanden.")

# --- TAB 2: MELDEN ---
with tab2:
    st.subheader("Neuen Gegenstand erfassen")
    uploaded_file = st.file_uploader("Bild hochladen", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        img = Image.open(uploaded_file).convert("RGB")
        st.image(img, width=300)
        
        if st.button("KI-Analyse & in Firebase speichern"):
            with st.spinner("Verarbeite..."):
                # 1. KI Vorhersage
                label, score = predict_category(img)
                
                # 2. Bild-Upload in Firebase Storage
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                file_name = f"images/{timestamp}.jpg"
                blob = bucket.blob(file_name)
                
                # Temporäres Speichern für den Upload
                img.save("temp_upload.jpg")
                blob.upload_from_filename("temp_upload.jpg")
                
                # Bild öffentlich zugänglich machen
                blob.make_public()
                public_url = blob.public_url
                
                # 3. Daten in Firestore speichern (DATENBANK)
                # Hier muss die Einrückung absolut exakt sein:
                db.collection("fundsachen").add({
                    "kategorie": label,
                    "bild_url": public_url,
                    "datum": datetime.now().strftime("%d.%m.%Y, %H:%M"),
                    "sicherheit": score
                })
                
                st.success(f"Erfolgreich als '{label}' gespeichert!")
                
                # Aufräumen
                if os.path.exists("temp_upload.jpg"):
                    os.remove("temp_upload.jpg")
