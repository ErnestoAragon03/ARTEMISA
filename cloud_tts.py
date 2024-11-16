from openai import OpenAI
import sounddevice as sd
import numpy as np
import main
import tempfile
from proxy import upload_audio_to_cloud, get_OpenAI_Key
import wave
import os

client = OpenAI(
    #Configurar API key de OpenAI
    api_key = get_OpenAI_Key()
)

is_tts_playing=False

def generate_audio_OpenAI(input_text, app):
    global is_tts_playing
    is_tts_playing = True
    response = client.audio.speech.create(
        model="tts-1",
        voice=app.master.current_voice.lower(),
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

    ### Obtener el correo del usuario actual###
    user_email = app.master.current_email
    ###Crear un archivo temporal para guardar el audio###
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav', prefix=f"{user_email}") as temp_wav_file:
        temp_wav_path = temp_wav_file.name

        #Guardar en formato Wav
        with wave.open(temp_wav_file, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit audio
            wav_file.setframerate(24000)  # 24 kHz sample rate
            wav_file.writeframes((audio_array * 32767).astype(np.int16).tobytes())  # Escribir el audio PCM

            print(f"Audio guardado en: {temp_wav_path}")
    ###Llamar función para subir el archivo al bucket
    upload_audio_to_cloud(temp_wav_path)

    is_tts_playing = False
    main.tts_interrupted = False
