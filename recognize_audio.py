import sounddevice as sd
import numpy as np
import vosk
import json
import sys  # Importa la librería sys

# Configura el modelo y el reconocimiento
#laptop_DELL = "C:\User\ernes\OneDrive\Documentos\Proyecto ARTEMISA\ASR\Local\Model\vosk-model-small-es-0.42"
#desktop = "C:\Users\Ernesto\OneDrive\Documentos\Proyecto ARTEMISA\ASR\Local\Model\vosk-model-small-es-0.42"

#Path hacia la ubicación del modelo Vosk (Modificar más adelante para evitar problemas de compatibilidad)
model_path = r"C:\Users\Ernesto\OneDrive\Documentos\Proyecto ARTEMISA\ASR\Local\Model\vosk-model-small-es-0.42"
samplerata = 16000  #Frecuencia de muestreo (Depende del micrófono)
blocksize = 8000     #Tamaño de los bloques de procesamiento
dtype = 'int16'     #Formato de los datos de audio
#Incializar el modelo Vosk
model = vosk.Model(model_path)
rec = vosk.KaldiRecognizer(model, samplerata)

#Variable donde almacenar el texto transcrito por Vosk
recognized_text =""



print(sd.query_devices())
# Función de callback para el flujo de audio
def callback(indata, frames, time, status):
    global recognized_text
    if status:
        print(status, flush=True, file=sys.stderr)
    
    if rec.AcceptWaveform(indata.tobytes()):
        result = json.loads(rec.Result())
        recognized_text = result.get('text', '')
        print("Texto reconocido:", result.get('text', ''))
    else:
        print(rec.PartialResult())

#Selecciona el dispositivo de entrada (device) Si no se especifica usa el default que tiene el sistema
#device_id = 10

# Iniciar la captura de audio
with sd.InputStream(samplerate=samplerata, blocksize = blocksize, dtype=dtype, channels=1, callback=callback):
    print("Escuchando... Ctr+C para detener")
    while True:
        pass
