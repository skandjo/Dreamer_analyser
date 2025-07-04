import streamlit as st
import os
import tempfile
from io import BytesIO
import plotly.express as px
import pandas as pd
from PIL import Image

# Import des fonctions du backend
from main import speech_to_text, text_analysis, text_to_image

# Configuration de la page
st.set_page_config(
    page_title="🌙 Synthétiseur de Rêve",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .main-header h1, .main-header p {
        color: #222222;
        margin: 0;
    }
    .section-header {
        background: #f8f9fa;
        padding: 0.5rem 1rem;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
        border-radius: 5px;
        color: #222222;
    }
    .dream-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
        color: #222222;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

import pandas as pd
import plotly.express as px

def display_emotion_pie_chart(emotions_data):
    if not emotions_data:
        st.write("Aucune donnée d'émotions à afficher.")
        return

    # Convertir les valeurs en float, 0 si échec
    converted_data = {}
    for k, v in emotions_data.items():
        try:
            converted_data[k] = float(v)
        except (ValueError, TypeError):
            converted_data[k] = 0.0

    df = pd.DataFrame(list(converted_data.items()), columns=['Emotion', 'Intensité'])

    fig = px.pie(df, values='Intensité', names='Emotion',
                 title="",
                 color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=True, height=400)

    st.plotly_chart(fig, use_container_width=True)



def main():
    st.markdown("""
    <div class="main-header">
        <h1>🌙 Synthétiseur de Rêve</h1>
        <p>Découvrez les secrets de vos rêves à travers l'IA</p>
    </div>
    """, unsafe_allow_html=True)

    # Vérification des clés API
    required_keys = ["GROQ_API_KEY", "MISTRAL_API_KEY", "CLIPDROP_API_KEY"]
    missing_keys = [key for key in required_keys if not os.environ.get(key)]
    if missing_keys:
        st.error(f"⚠️ Clés API manquantes: {', '.join(missing_keys)}")
        st.info("Veuillez configurer toutes les clés API dans votre fichier .env")
        st.stop()

    # Sidebar
    with st.sidebar:
        st.markdown("### 📖 Instructions")
        st.markdown("""
        1. **Uploadez** un fichier audio de votre rêve
        2. **Attendez** la transcription automatique
        3. **Découvrez** l'analyse émotionnelle
        4. **Admirez** l'image générée de votre rêve
        """)
        st.markdown("### ⚙️ Paramètres")
        language = st.selectbox("Langue de transcription", ["fr", "en"], index=0)
        st.markdown("### 💡 Conseils")
        st.info("Pour de meilleurs résultats, décrivez votre rêve de manière détaillée et claire.")

    st.markdown('<div class="section-header"><h2>🎤 Upload Audio</h2></div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Choisissez un fichier audio de votre rêve",
        type=['wav', 'mp3', 'm4a', 'flac', 'ogg'],
        help="Formats supportés: WAV, MP3, M4A, FLAC, OGG"
    )

    if uploaded_file is not None:
        st.success(f"✅ Fichier uploadé: {uploaded_file.name} ({uploaded_file.size} bytes)")

        if st.button("🚀 Analyser mon rêve", key="analyze_button"):
            if 'transcription' not in st.session_state:
                st.session_state.transcription = None
            if 'analysis' not in st.session_state:
                st.session_state.analysis = None
            if 'dream_image' not in st.session_state:
                st.session_state.dream_image = None

            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            try:
                with st.spinner("🎯 Transcription de l'audio en cours..."):
                    transcription = speech_to_text(tmp_file_path, language)
                    st.session_state.transcription = transcription

                if transcription:
                    st.markdown('<div class="section-header"><h2>📝 Transcription</h2></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="dream-card">{transcription}</div>', unsafe_allow_html=True)

                    with st.spinner("🧠 Analyse émotionnelle en cours..."):
                        analysis = text_analysis(transcription)
                        st.session_state.analysis = analysis

                    if analysis:
                        st.markdown('<div class="section-header"><h2>📊 Analyse émotionnelle</h2></div>', unsafe_allow_html=True)
                        display_emotion_pie_chart(analysis)

                    with st.spinner("🎨 Génération de l'image de votre rêve..."):
                        image_data = text_to_image(transcription)
                        st.session_state.dream_image = image_data

                    if image_data:
                        st.markdown('<div class="section-header"><h2>🖼️ Représentation Visuelle</h2></div>', unsafe_allow_html=True)
                        image = Image.open(BytesIO(image_data))
                        st.image(image, caption="Représentation visuelle de votre rêve", use_container_width=True)
                        st.download_button(
                            label="💾 Télécharger l'image",
                            data=image_data,
                            file_name="mon_reve.png",
                            mime="image/png"
                        )
                else:
                    st.error("❌ Erreur lors de la transcription. Veuillez réessayer.")

            except Exception as e:
                st.error(f"❌ Erreur lors du traitement: {str(e)}")

            finally:
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)

    if 'transcription' in st.session_state and st.session_state.transcription:
        if not uploaded_file:
            st.markdown('<div class="section-header"><h2>📝 Dernière Transcription</h2></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="dream-card">{st.session_state.transcription}</div>', unsafe_allow_html=True)

    if 'analysis' in st.session_state and st.session_state.analysis:
        if not uploaded_file:
            st.markdown('<div class="section-header"><h2>📊 Dernière Analyse</h2></div>', unsafe_allow_html=True)
            display_emotion_pie_chart(st.session_state.analysis)

    if 'dream_image' in st.session_state and st.session_state.dream_image:
        if not uploaded_file:
            st.markdown('<div class="section-header"><h2>🖼️ Dernière Image</h2></div>', unsafe_allow_html=True)
            image = Image.open(BytesIO(st.session_state.dream_image))
            st.image(image, caption="Représentation visuelle de votre rêve", use_column_width=True)

if __name__ == "__main__":
    main()
