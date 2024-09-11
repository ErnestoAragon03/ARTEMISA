import sounddevice as sd
import numpy as np
import vosk
import json
import sys  # Importa la librería sys

# Configura el modelo y el reconocimiento
#laptop_DELL = "C:\User\ernes\OneDrive\Documentos\Proyecto ARTEMISA\env\ASR\Local\Model\vosk-model-small-es-0.42"
#desktop = "C:\Users\Ernesto\OneDrive\Documentos\Proyecto ARTEMISA\env\ASR\Local\Model\vosk-model-small-es-0.42"

model_path = r"C:\Users\Ernesto\OneDrive\Documentos\Proyecto ARTEMISA\env\ASR\Local\Model\vosk-model-small-es-0.42"
model = vosk.Model(model_path)
rec = vosk.KaldiRecognizer(model, 16000)

print(sd.query_devices())
# Función de callback para el flujo de audio
def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    if rec.AcceptWaveform(indata.tobytes()):
        result = json.loads(rec.Result())
        print("Texto reconocido:", result.get('text', ''))
    else:
        print(rec.PartialResult())
#Selecciona el dispositivo de entrada (device) Si no se especifica usa el default que tiene el sistema
#device_id = 10

# Configuración del flujo de audio
with sd.InputStream(samplerate=16000, blocksize = 8000, dtype="int16", channels=1, callback=callback):
    print("Iniciando reconocimiento de voz...")
    sd.sleep(10000)  # Mantén el script en ejecución
