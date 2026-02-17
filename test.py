import streamlit as st
from PIL import Image, ImageOps
import numpy as np
import tensorflow as tf

# Konfiguration der Seite
st.set_page_config(page_title="Rene Schmock Detector", page_icon="📸")

def load_model():
    # Hier den Pfad zu deinem exportierten Modell anpassen
    # Falls du noch kein Modell hast, ist dies der Platzhalter
    try:
        model = tf.keras.models.load_model("keras_model.h5", compile=False)
        return model
    except:
        st.error("Modell-Datei 'keras_model.h5' nicht gefunden! Bitte lade dein Modell hoch.")
        return None

def predict(image, model):
    # Bild für das Modell vorbereiten (Größe 224x224 ist Standard für viele KIs)
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    
    # Bild in Array umwandeln
    image_array = np.asarray(image)
    # Normalisierung
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
    
    # Daten-Array erstellen
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0] = normalized_image_array

    # Vorhersage treffen
    prediction = model.predict(data)
    index = np.argmax(prediction)
    
    # Basierend auf deiner labels.txt: 0 = Rene Schmock, 1 = Random 
    class_names = ["Rene Schmock", "Nicht Rene Schmock (Random)"]
    confidence_score = prediction[0][index]
    
    return class_names[index], confidence_score

# --- UI Layout ---
st.title("📸 Rene Schmock Erkennung")
st.write("Lade ein Bild hoch, um zu prüfen, ob es sich um den Creator Rene Schmock handelt.")

uploaded_file = st.file_uploader("Wähle ein Bild...", type=["jpg", "jpeg", "png"])

model = load_model()

if uploaded_file is not None and model is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Hochgeladenes Bild', use_container_width=True)
    
    st.write("---")
    with st.spinner('KI analysiert...'):
        label, score = predict(image, model)
        
        # Ergebnis-Anzeige
        if label == "Rene Schmock":
            st.success(f"Ergebnis: **{label}**")
        else:
            st.warning(f"Ergebnis: **{label}**")
            
        st.info(f"Sicherheit: {round(score * 100, 2)}%")

elif model is None:
    st.info("Hinweis: Du musst ein trainiertes Modell (keras_model.h5) im Verzeichnis haben.")
