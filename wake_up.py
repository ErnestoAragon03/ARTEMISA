import pvporcupine
import sounddevice as sd
import numpy as np
import queue
import main
from logger_config import logger
import os

#Configurar cola de audio
q = queue.Queue()

dtype = 'int16'     #Formato de los datos de audio
access_key = 'NTgoUMMTKQaczZNY4Jm2Gbxr9H67fwuXvco/r0uvTTsIwNtO+8KwRg=='

#Determina la ruta base, donde está ubicado el script actual
base_path = os.path.dirname(os.path.abspath(__file__))

keyword_paths = [os.path.join(base_path, 'Wake_Words', 'Artemisa_es_windows_v3_0_0.ppn')] #Path hacia las wake words
model_path = os.path.join(base_path, 'Wake_Words', 'porcupine_params_es.pv')

#Cargar múltiples wake words predefinidas 
porcupine = pvporcupine.create(access_key=access_key,
                                keyword_paths=keyword_paths,
                                model_path=model_path)

#Función callback que captura el audio
def constant_callback(indata,frames,time,status):
    q.put(indata.copy())

#Función que reconoce las wake words
def recognize_wake_word():
    try:
        logger.info("Llegando a wake_up-py")
        with sd.InputStream(callback=constant_callback, channels=1, samplerate=porcupine.sample_rate, blocksize=porcupine.frame_length, dtype=dtype):
            logger.info("Esperando Wake Word...")
            print("Listening...")
            while main.running:
                pcm = q.get().flatten()
                pcm = np.frombuffer(pcm, dtype=np.int16)

                keyword_index = porcupine.process(pcm)
                if keyword_index >= 0:
                    logger.info("Wake word detectada")
                    print(f"Wake word detected!")
                    return True 
            print("Muted")
            return False
    except Exception as e:
        logger.error("Error en wake_up.py: %s", e)