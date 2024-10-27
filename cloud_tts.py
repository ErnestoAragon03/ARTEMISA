from openai import OpenAI
import sounddevice as sd
import numpy as np
import main
import time

client = OpenAI(
    #Configurar API key de OpenAI
    api_key = "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"
)

is_tts_playing=False

def generate_audio_OpenAI(input_text):
    global is_tts_playing
    is_tts_playing = True
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=input_text,
        response_format="pcm"   #Usaremos formato pcm para poder reproducir el audio directamente
    )
    #Convertir la respuesta en pcm a un arreglo de numpy y reproducirlo
    pcm_data = response.read()
    # Convertir el audio PCM a un array numpy y reproducirlo
    audio_array = np.frombuffer(pcm_data, dtype=np.int16).astype(np.float32) / 32768.0
    #sd.play(audio_array, samplerate=24000)  # Reproducir en 24 kHz
    #if main.tts_interrupted:
    #    sd.stop()

    # Crear el flujo de salida
    with sd.OutputStream(samplerate=24000, channels=1) as stream:
        # Dividir el audio en bloques
        for i in range(0, len(audio_array), 1024):
            if main.tts_interrupted:
                print("Reproducción interrumpida.")
                break
            block = audio_array[i:i + 1024]
            stream.write(block)  # Escribe el bloque en el stream
    is_tts_playing = False
    main.tts_interrupted = False
