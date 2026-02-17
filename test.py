import streamlit as st
import numpy as np
from keras.models import load_model
from PIL import Image, ImageOps

# Seiteneinstellungen
st.set_page_config(page_title="Rene Schmock Detector", layout="centered")

# Modell und Labels laden (gecached, damit es schnell geht)
@st.cache_resource
def load_ai_model():
    model = load_model("keras_model.h5", compile=False)
    with open("labels.txt", "r") as f:
        class_names = f.readlines()
    return model, class_names

model, class_names = load_ai_model()

st.title("📸 Rene Schmock Erkennung")
st.write("Lade ein Bild hoch, um zu prüfen, ob es Rene Schmock ist oder nicht.")

# File Uploader ersetzt den statischen Pfad
uploaded_file = st.file_uploader("Wähle ein Bild...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Bild anzeigen
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Hochgeladenes Bild", use_container_width=True)
    
    with st.spinner("KI analysiert..."):
        # Bildvorbereitung (genau wie in deinem Skript)
        size = (224, 224)
        image_resized = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
        image_array = np.asarray(image_resized)
        
        # Normalisierung
        normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
        
        # Daten-Array für Vorhersage
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        data[0] = normalized_image_array

        # Vorhersage treffen
        prediction = model.predict(data)
        index = np.argmax(prediction)
        
        # Label extrahieren (aus deiner labels.txt) 
        # class_names[0] ist "rene schmock", class_names[1] ist "random" 
        label = class_names[index].strip()[2:] 
        confidence_score = prediction[0][index]

        # Ergebnis-Ausgabe
        st.divider()
        if index == 0:
            st.success(f"### Ergebnis: {label}")
        else:
            st.warning(f"### Ergebnis: {label}")
            
        st.write(f"**Sicherheit:** {round(confidence_score * 100, 2)}%")
