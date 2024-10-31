from openai import OpenAI
import sounddevice as sd
import soundfile as sf
import webrtcvad
import numpy as np
import time
import queue
import io
import tempfile
import wave
import main
import cloud_tts
import os

from asr_sounds import play_activation_sound, play_deactivation_sound

client = OpenAI(
    #Configurar API key de OpenAI
    api_key = "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"
)

samplerate = 16000          #Frecuencia de muestreo (Hz)
frame_duration = 30          #Duración de frame (ms)
frame_size = int (samplerate * frame_duration / 1000)
silence_threshold = 2    #Segundos de silencio antes de detener la grabación
vad = webrtcvad.Vad(1)     #Nivel de sensibilidad (VAD)

# Inicialización de la cola de audio y tiempos de espera
audio_queue = queue.Queue()
last_voice_time = time.time()
audio_buffer = io.BytesIO()  # Buffer de audio para almacenar los datos grabados


# Función de callback para la captura de audio
def callback(indata, frames, time, status):
    if status:
        print(status)
    audio_queue.put(indata.copy())

# Función para dividir el audio en frames de tamaño adecuado para VAD
def frame_generator(frame_size, audio_data):
    for i in range(0, len(audio_data), frame_size):
        yield audio_data[i:i + frame_size]

# Función para procesar y verificar la actividad de voz en frames de audio
def process_voice_activity(data):
    global last_voice_time
    for frame in frame_generator(frame_size, data):
        is_speech = vad.is_speech(frame.tobytes(), samplerate)
        if is_speech:
            last_voice_time = time.time()
            return True
    return False

#Captura el audio
def capture_audio():
    global last_voice_time
    while cloud_tts.is_tts_playing:
        time.sleep(2)
    #Reproducir sonido de activación
    play_activation_sound() 
    #Iniciar grabación
    print("Artemisa está escuchando...")
    #Captura de audio
    with sd.InputStream(samplerate=samplerate, blocksize=frame_size, channels=1, callback=callback, dtype='int16'):
        print("Escuchando:")

        #Procesar datos de audio
        while True:
            data = audio_queue.get()
            
            audio_buffer.write(data)
            #Verificar la actividad de voz en frame actual
            if not(process_voice_activity(data)):
                if time.time() - last_voice_time > silence_threshold:
                    print("Usuario terminó de hablar")
                    break   #Finalizar captura
    
    play_deactivation_sound()
    print("Grabación terminada")
    audio_buffer.seek(0)    #Reiniciar Buffer
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=".\ASR\Online\Temp") as temp_audio_file:
        with wave.open(temp_audio_file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 2 bytes para int16
            wf.setframerate(samplerate)
            wf.writeframes(audio_buffer.read())
        temp_audio_file_name = temp_audio_file.name
    audio_buffer.truncate(0)
    audio_buffer.seek(0)
    print("Llegó a save_and_transcribe")
    transcription_text = []
        #Enviar a Whisper
    with open(temp_audio_file_name, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="es"
            )
    transcription_text = transcription.text
    print("Texto final reconocido: ", transcription_text)
    directory_path = "./ASR/Online/Temp/"
    audio_file_path = os.path.join(directory_path, temp_audio_file_name)
    print(audio_file_path)  
    #Borrar el archivo temporal
    if os.path.exists(audio_file_path):
        os.remove(audio_file_path)
        print(f"Archivo {audio_file_path} eliminado.")
    else:
        print("El archivo no existe.")

    if transcription_text:
        main.conversation_active = True
        return transcription_text


def transcribe():
    transcription = ""
    try:
        transcription = capture_audio()
        return transcription
    except ConnectionError:
        main.alert_No_Connection()
    except Exception as e:
        print("Error: ", e)