from groq import Groq
from dotenv import load_dotenv
import os
import json
from mistralai import Mistral
import requests
import plotly.express as px
import pandas as pd
# Load environment variables from .env file
load_dotenv()



# Specify the path to the audio file
audio_path = "../Enregistrement.m4a"

def read_file(file_path):

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()
    

def speech_to_text(audio_path, language="fr"):

    # Initialize the Groq client
    client = Groq(api_key=os.environ["GROQ_API_KEY"])  # Ensure you have set your API key in the .env file

    # Open the audio file
    with open(audio_path, "rb") as file:
        # Create a transcription of the audio file
        transcription       = client.audio.transcriptions.create(
            file=file,  # Required audio file
            model="whisper-large-v3-turbo",  # Required model to use for transcription
            prompt="Extrait le texte de l'audio de la maniére factuelle",  # Optional
            response_format="verbose_json",  # Optional
            timestamp_granularities=["word", "segment"],  # Optional (must set response_format to "json" to use and can specify "word", "segment" (default), or both)
            language=language,  # Optional
            temperature=0.0  # Optional
        )
    return transcription.text  # Return the transcription text


def text_analysis(text):
    client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

    chat_response = client.chat.complete(
        model="mistral-large-latest",
        messages=[
            {
                "role": "system",
                "content": read_file("context_analysis.txt"),  # Load the prompt from the file
            },
            {
                "role": "user",
                "content": f"Analyse le texte {text} et renvoie un JSON.",
            },
        ],
        response_format={"type": "json_object",}
    )

    json_str = chat_response.choices[0].message.content
    result_dict = json.loads(json_str)  # conversion JSON string -> dict Python

    return result_dict

import matplotlib.pyplot as plt

def create_emotion_chart(emotions_data):
    if not emotions_data:
        return None
    
    labels = list(emotions_data.keys())
    sizes = list(emotions_data.values())
    
    fig, ax = plt.subplots(figsize=(7,7))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    ax.set_title("Analyse Émotionnelle du Rêve")
    ax.axis('equal')  # Pour un cercle parfait
    
    return fig


####
def text_to_image(text):
    """
    Convert a text description of a dream into an image using the ClipDrop API.
    """
    # Assure-toi que la clé API est définie dans le fichier .env
    if "CLIPDROP_API_KEY" not in os.environ:
        raise ValueError("CLIPDROP_API_KEY is not set in the environment variables.")

    # Requête vers l'API ClipDrop
    r = requests.post('https://clipdrop-api.co/text-to-image/v1',
                      files={
                          'prompt': (None, text, 'text/plain')
    },
    headers={
        'x-api-key': os.environ["CLIPDROP_API_KEY"]  # Assure-toi que la clé est bien définie
    }
    )

    # Vérifie si la requête a fonctionné
    if r.ok:
        return r.content  # Renvoie directement les données de l'image (bytes)
    else:
        r.raise_for_status()



if __name__ == "__main__":
    # Call the speech_to_text function and print the result
    print('extracting text from audio...')
    transcription_dream_text = speech_to_text(audio_path)
    print(transcription_dream_text)

    # Call the text_analysis function and print the result
    print('analysing text...')
    analysis_emotions_results = text_analysis(transcription_dream_text)
    print(analysis_emotions_results)

    # Call the text_to_image function to generate an image from the dream description
    print('generating image from dream description...') 
    text_to_image(transcription_dream_text)
    print('Image generation complete.')

    # Show the pie chart using matplotlib
    print('showing pie chart...')
    fig = create_emotion_chart(analysis_emotions_results)
    fig.show()
    print('Pie chart displayed successfully.')
