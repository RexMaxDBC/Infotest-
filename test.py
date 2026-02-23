import streamlit as st
import numpy as np
from keras.models import load_model
from PIL import Image, ImageOps
from supabase import create_client, Client
import os

# --- SUPABASE SETUP ---
# Ersetze diese Werte mit deinen echten Supabase-Daten (aus den Settings)
url: str = "DEINE_SUPABASE_URL"
key: str = "DEIN_SUPABASE_ANON_KEY"
supabase: Client = create_client(url, key)

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
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    image_array = np.asarray(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0] = normalized_image_array
    
    prediction = model.predict(data)
    index = np.argmax(prediction)
    return class_names[index][2:].strip(), prediction[0][index]

# --- UI LAYOUT ---
st.set_page_config(page_title="Fundbüro Katharineum", page_icon="🏫")
st.title("🏫 Digitales Fundbüro Katharineum")

tab1, tab2 = st.tabs(["🔍 Suchen", "📤 Fundstück melden"])

# --- TAB 1: SUCHEN ---
with tab1:
    search_query = st.text_input("Nach was suchst du? (z.B. Stift, Jacke)")
    
    # Datenbank abfragen
    if search_query:
        response = supabase.table("items").select("*").ilike("category", f"%{search_query}%").execute()
    else:
        response = supabase.table("items").select("*").execute()
    
    items = response.data
    
    if items:
        cols = st.columns(3)
        for i, item in enumerate(items):
            with cols[i % 3]:
                st.image(item['image_url'], use_container_width=True)
                st.write(f"**Kategorie:** {item['category']}")
                st.caption(f"Gefunden am: {item['created_at'][:10]}")
    else:
        st.info("Keine passenden Fundstücke gefunden.")

# --- TAB 2: MELDEN (Hausmeister / Lehrer) ---
with tab2:
    st.subheader("Neues Fundstück erfassen")
    uploaded_file = st.file_uploader("Foto des Gegenstands", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, width=200)
        
        if st.button("KI-Analyse & Speichern"):
            # 1. KI erkennt Kategorie
            label, score = predict_category(image)
            st.write(f"KI erkennt: **{label}** ({round(score*100)}%)")
            
            # 2. Bild zu Supabase Storage hochladen
            # (Hinweis: Du musst einen Bucket namens 'images' in Supabase erstellen)
            file_name = f"found_{uploaded_file.name}"
            # In der Realität müsstest du hier den Upload-Befehl für den Storage nutzen
            # Der Einfachheit halber nehmen wir hier eine Dummy-URL an:
            fake_url = f"{url}/storage/v1/object/public/images/{file_name}"
            
            # 3. Daten in Tabelle 'items' speichern
            data = {
                "category": label,
                "image_url": fake_url
            }
            supabase.table("items").insert(data).execute()
            st.success(f"Erfolgreich als '{label}' im Fundbüro gespeichert!")
                })
                
                st.success(f"Gespeichert als: {label}!")
                os.remove("temp.jpg")
