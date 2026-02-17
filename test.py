import streamlit as st
from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np

# 1. Seite konfigurieren
st.set_page_config(page_title="Rene Schmock Detector")
st.title("KI Bild-Erkennung")

# 2. Modell und Labels laden
# Wir nutzen @st.cache_resource, damit das Modell nicht bei jedem Klick neu geladen wird
@st.cache_resource
def setup_model():
    model = load_model("keras_model.h5", compile=False)
    class_names = open("labels.txt", "r").readlines()
    return model, class_names

model, class_names = setup_model()

# 3. Benutzeroberfläche für den Upload
uploaded_file = st.file_uploader("Lade ein Bild hoch...", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # Bild öffnen
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption='Hochgeladenes Bild', use_container_width=True)
    
    # --- Deine Logik beginnt hier ---
    # Array erstellen
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

    # Bild vorbereiten (Resizing & Cropping)
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    image_array = np.asarray(image)

    # Normalisierung
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
    data[0] = normalized_image_array

    # Vorhersage
    prediction = model.predict(data)
    index = np.argmax(prediction)
    
    # Labels aus deiner Datei verwenden 
    # Index 0: rene schmock, Index 1: random 
    class_name = class_names[index]
    confidence_score = prediction[0][index]
    # --- Ende deiner Logik ---

    # Ergebnis anzeigen
    st.write("---")
    label_clean = class_name[2:].strip() # Entfernt die Zahl "0 " oder "1 " am Anfang 
    st.subheader(f"Ergebnis: {label_clean}")
    st.info(f"Wahrscheinlichkeit: {round(confidence_score * 100, 2)}%")
