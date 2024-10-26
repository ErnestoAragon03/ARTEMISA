from openai import OpenAI
import sounddevice as sd
import numpy as np

client = OpenAI(
    #organization= 'org-BLKMXfWSb6Ytc2bIO4tIJ6EM',
    #project= 'proj_9mma3BD13IrvUCF1pmCHNHgc'
    #Configurar API key de OpenAI
    api_key = "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"

)

def generate_audio_OpenAI(input_text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=input_text,
        response_format="pcm"   #Usaremos formato pcm para poder reproducir el audio directamente
    )
    #Convertir la respuesta en pcm a un arreglo de numpy y reproducirlo
    pcm_data = response.read()
    # Convertir el audio PCM a un array numpy y reproducirlo
    audio_array = np.frombuffer(pcm_data, dtype=np.int16)
    sd.play(audio_array, samplerate=24000)  # Reproducir en 24 kHz
    sd.wait()  # Esperar a que termine la reproducción