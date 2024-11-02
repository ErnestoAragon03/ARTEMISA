import pvporcupine
import sounddevice as sd
import numpy as np
import queue
import main

#Configurar cola de audio
q = queue.Queue()

dtype = 'int16'     #Formato de los datos de audio
access_key = 'NTgoUMMTKQaczZNY4Jm2Gbxr9H67fwuXvco/r0uvTTsIwNtO+8KwRg=='

keyword_paths = [r'C:\Users\Ernesto\Documents\Proyecto ARTEMISA\Wake_Words\Artemisa_es_windows_v3_0_0.ppn']    #Path hacia las wake words
model_path = r'C:\Users\Ernesto\Documents\Proyecto ARTEMISA\Wake_Words\porcupine_params_es.pv'

#Cargar múltiples wake words predefinidas 
porcupine = pvporcupine.create(access_key=access_key,
                                keyword_paths=keyword_paths,
                                model_path=model_path)

#Función callback que captura el audio
def constant_callback(indata,frames,time,status):
    q.put(indata.copy())

#Función que reconoce las wake words
def recognize_wake_word():
    with sd.InputStream(callback=constant_callback, channels=1, samplerate=porcupine.sample_rate, blocksize=porcupine.frame_length, dtype=dtype):
        print("Listening...")
        while main.running:
            pcm = q.get().flatten()
            pcm = np.frombuffer(pcm, dtype=np.int16)

            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                print(f"Wake word detected!")
                return True 
        print("Muted")
        return False