import sounddevice as sd
import soundfile as sf
import vosk
import json
import sys  # Importa la librería sys
import webrtcvad
import time
import queue
from asr_sounds import play_activation_sound, play_deactivation_sound
import main

#Path hacia la ubicación del modelo Vosk (Modificar más adelante para evitar problemas de compatibilidad)
model_path = r".\ASR\Local\Model\vosk-model-small-es-0.42"

#Parámetros del audio
samplerate = 16000  #Frecuencia de muestreo (Depende del micrófono)
blocksize = 8000     #Tamaño de los bloques de procesamiento
dtype = 'int16'     #Formato de     los datos de audio
frame_duration = 30 #ms
frame_size = int(samplerate * frame_duration /1000)

#Incializar el modelo Vosk
model = vosk.Model(model_path)
rec = vosk.KaldiRecognizer(model, samplerate)

#Configuración detección de actividad vocal (VAD)
vad = webrtcvad.Vad(1)  #1 indica modo de detección normal
silence_threshold = 1 # Segundos de inactividad que esperará el modelo

#Iniciar los tiempos de espera
last_voice_time = time.time()
is_listening = True
last_detection_time = 0
detection_cooldown = 0.5    #Umbral para evitar repetir palabras

def start_asr_local(app_instance):
    global recognized_text
    recognized_text = ""
    #Cola para almacenar los datos de audio
    audio_queue = queue.Queue()

    #Reproducir sonido de activación
    play_activation_sound()
    #print(sd.query_devices())       #Imprime la lista de todos los dispositivos conectados a la computadora
    # Función de callback para el flujo de audio
    def callback(indata, frames, callback_time, status):
        if status:
            print(status, file=sys.stderr)
        audio_queue.put(bytes(indata))

        #Comienza la escucha
    with sd.InputStream(samplerate=samplerate, blocksize = blocksize, dtype=dtype, channels=1, callback=callback):
        print("Escuchando...")

        #Objeto de reconocimiento de Vosk
        recognizer = vosk.KaldiRecognizer(model, samplerate)
        
        last_voice_time = time.time()
        
        while True:
            data = audio_queue.get()
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                text = json.loads(result).get('text', '')
                if text:
                    recognized_text += text + " "
                    last_voice_time = time.time()  #Reiniciar contador de silencio
            else:
                #Manejar datos parciales
                partial_result = recognizer.PartialResult()
                partial_text = json.loads(partial_result).get('partial', '')

                if partial_text:
                    last_voice_time = time.time()   #Reiniciar contador de silencio
            #Verificar si se ha superado el umbral de silencio
            if time.time() - last_voice_time > silence_threshold:  
                print("Usuario terminó de hablar")
                break
            if recognized_text != (partial_text + " "):
                print(f"Escuchando: {recognized_text+partial_text}")
    #Resultado final
    print(f"Texto final reconocido: {recognized_text}")
    main.conversation_active = True  
    play_deactivation_sound()
    return recognized_text