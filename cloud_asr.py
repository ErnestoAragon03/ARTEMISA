from openai import OpenAI
import sounddevice as sd
import soundfile as sf
import numpy as np
import scipy.io.wavfile as wav
import io
import time 
from asr_sounds import play_activation_sound, play_deactivation_sound

client = OpenAI(
    #Configurar API key de OpenAI
    api_key = "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"
)

SAMPLERATE = 16000          #Frecuencia de muestreo (Hz)
CHANNELS = 1                #Número de canales (mono)
SILENCE_THRESHOLD = 100     # Nivel de silencio para detener (Ajustable según entorno)
SILENCE_DURATION = 2        # Segundos de silencio antes de detener la grabación
#Iniciar los tiempos de espera
last_voice_time = time.time()
is_listening = True
last_detection_time = 0
#Variable donde guardar la respuesta de Whisper
recognized_text =""
conversation_active = False

#Captura el audio
def capture_audio():
    #Almacenar audio detectado un un buffer temporal
    audio_data = []         #Almacena los bloques de audio grabados
    silence_chunks = 0      #Conteo bloques con silencio 

    def callback(indata, frames, time, status):
        nonlocal silence_chunks, audio_data
        volume_norm = np.linalg.norm(indata) * 10
        
        if volume_norm < SILENCE_THRESHOLD:
            silence_chunks += 1 #Agregar al conteo de silencio
        else:
            silence_chunks = 0  #Reiniciar el conteo de silencio
        
        #Guardar el audio en cada llamada a callback
        audio_data.extend(indata.copy())

        #Terminar grabación si el silencio supera el Silence Duration
        if silence_chunks > SILENCE_DURATION * SAMPLERATE / frames:
            raise sd.CallbackStop()
    
    #Reproducir sonido de activación
    play_activation_sound()
    #Iniciar grabación
    print("Artemisa está escuchando...")
    #Captura de audio
    with sd.InputStream(callback=callback, samplerate=SAMPLERATE, channels=CHANNELS):
        last_voice_time = time.time()

    #Convertir a un array de numpy
    audio_np = np.array(audio_data, dtype=np.float32)
    play_deactivation_sound()
    print("Grabación terminada")
    return audio_np

def save_and_transcribe(audio_np):
    #Guardar el audio en un archivo .wav temporal
    temp_file = "temp_audio.wav"
    wav.write(temp_file, SAMPLERATE, audio_np)

    #Enviar a Whisper
    with open(temp_file, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    transcription_text = transcription["text"]
    print("Texto final reconocido: ", transcription_text)
    return transcription_text

def transcribe():
    try:
        audio_np = capture_audio()
        transcription = save_and_transcribe(audio_np=audio_np)
        return transcription
    except Exception as e:
        print("Error: ", e)