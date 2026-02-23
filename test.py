import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, storage
import numpy as np
from keras.models import load_model
from PIL import Image, ImageOps
import os
from datetime import datetime

# --- FIREBASE SETUP ---
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'DEIN-PROJEKT-ID.appspot.com' # Hier deine Storage-URL eintragen
    })

db = firestore.client()
bucket = storage.bucket()

# --- KI MODELL SETUP ---
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
    return class_names[index][2:].strip(), float(prediction[0][index])

# --- UI ---
st.set_page_config(page_title="Katharineum Fundbüro", layout="wide")
st.title("🏫 Digitales Fundbüro (Firebase Edition)")

tab1, tab2 = st.tabs(["🔍 Suchen", "📤 Neues Fundstück"])

# --- TAB 1: SUCHEN ---
with tab1:
    search = st.text_input("Wonach suchst du?")
    items_ref = db.collection("fundsachen")
    
    # Datenbank abfragen
    docs = items_ref.stream()
    
    cols = st.columns(4)
    found_any = False
    
    for i, doc in enumerate(docs):
        item = doc.to_dict()
        # Einfacher Filter
        if search.lower() in item['kategorie'].lower() or not search:
            with cols[i % 4]:
                st.image(item['bild_url'], use_container_width=True)
                st.write(f"**{item['kategorie']}**")
                st.caption(f"Gefunden: {item['datum']}")
            found_any = True
            
    if not found_any:
        st.info("Keine Fundstücke gefunden.")

# --- TAB 2: MELDEN ---
with tab2:
    st.subheader("Gegenstand registrieren")
    file = st.file_uploader("Foto machen/hochladen", type=["jpg", "png", "jpeg"])
    
    if file:
        img = Image.open(file).convert("RGB")
        st.image(img, width=250)
        
        if st.button("In Datenbank speichern"):
            with st.spinner("KI analysiert und speichert..."):
                # 1. KI Label
                label, score = predict_category(img)
                
                # 2. Bild in Firebase Storage hochladen
                image_path = f"images/{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                blob = bucket.blob(image_path)
                
                # Temporär lokal speichern für Upload
                img.save("temp.jpg")
                blob.upload_from_filename("temp.jpg")
                blob.make_public()
                url = blob.public_url
                
                # 3. Daten in Firestore speichern
                db.collection("fundsachen").add({
                    "kategorie": label,
                    "bild_url": url,
                    "datum": datetime.now().strftime("%d.%m.%Y %H:%M"),
                    "score": score
                })
                
                st.success(f"Gespeichert als: {label}!")
                os.remove("temp.jpg")
