import sounddevice as sd
import vosk
import json
import sys  # Importa la librería sys
import webrtcvad
import time
import queue

# Configura el modelo y el reconocimiento
#laptop_DELL = "C:\User\ernes\OneDrive\Documentos\Proyecto ARTEMISA\ASR\Local\Model\vosk-model-small-es-0.42"
#desktop = "C:\Users\Ernesto\Documents\Proyecto ARTEMISA\ASR\Local\Model\vosk-model-small-es-0.42"

#Path hacia la ubicación del modelo Vosk (Modificar más adelante para evitar problemas de compatibilidad)
model_path = r"C:\Users\Ernesto\Documents\Proyecto ARTEMISA\ASR\Local\Model\vosk-model-small-es-0.42"

#Parámetros del audio
samplerate = 16000  #Frecuencia de muestreo (Depende del micrófono)
blocksize = 8000     #Tamaño de los bloques de procesamiento
dtype = 'int16'     #Formato de los datos de audio
frame_duration = 30 #ms
frame_size = int(samplerate * frame_duration /1000)

#Incializar el modelo Vosk
model = vosk.Model(model_path)
rec = vosk.KaldiRecognizer(model, samplerate)

#Configuración detección de actividad vocal (VAD)
vad = webrtcvad.Vad(1)  #1 indica modo de detección normal
silence_threshold = 3 # Segundos de inactividad que esperará el modelo

#Iniciar los tiempos de espera
last_voice_time = time.time()
is_listening = True
last_detection_time = 0
detection_cooldown = 0.5    #Umbral para evitar repetir palabras

#Variable donde almacenar el texto transcrito por Vosk
recognized_text =""
conversation_active = False


def is_speech(frame):
    return vad.is_speech(frame, samplerate)

def start_asr_local():
    global recognized_text, conversation_active
    
    #Cola para almacenar los datos de audio
    audio_queue = queue.Queue()

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
    conversation_active = True
"""
        audio_data = indata.flatten()
        #Verificar si hay voz en cada frame
        for start in range(0, len(audio_data), frame_size):
            frame = audio_data[start:start + frame_size]

            if len(frame) < frame_size:
                #Ignorar frames muy pequeños
                continue
                    
            current_time =time.time()

            if is_speech(frame.tobytes()):
                #Evitar detecciones múltiples
                if current_time - last_detection_time > detection_cooldown:
                    print("Detectando voz...")
                    last_detection_time = current_time
                        
                if rec.AcceptWaveform(indata.tobytes()):
                    result = json.loads(rec.Result())
                    recognized_text= result.get('text', '')
                    print("Texto reconocido:", result.get('text', ''))

                last_voice_time = current_time

        if time.time() - last_voice_time > silence_threshold:
                    print("Usuario terminó de hablar")
                    stop_listening()

    def stop_listening():
        global is_listening 
        is_listening = False #Marcar que la escucha ha terminado
        print("Terminando la grabación...")
        print(recognized_text)
        sd.stop()

    #Selecciona el dispositivo de entrada (device) Si no se especifica usa el default que tiene el sistema
    #device_id = 10
    def start_listening():
        global is_listening
        is_listening = True
        print("Escuchando... Ctr+C para detener")
        # Iniciar la captura de audio
        with sd.InputStream(samplerate=samplerate, blocksize = blocksize, dtype=dtype, channels=1, callback=callback):
            while is_listening:
                sd.sleep(100)
                
    start_listening()

except KeyboardInterrupt:
    print("\nDone")
except Exception as e:
    print(f"Error inicializando InputStream: {e}")"""