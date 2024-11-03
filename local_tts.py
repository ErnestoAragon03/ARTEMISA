import TTS.api
import sounddevice as sd
import numpy as np
import librosa
import os
from logger_config import logger

#Inicializar modelo de Mozilla (css10)
def initialize_tts():
    try:
        logger.info("Llegando a local_tts.py")
        # Determina la ruta base, donde está ubicado el script actual
        base_path = os.path.dirname(os.path.abspath(__file__))
        # Rutas relativas al modelo y archivo de configuración
        model_path = os.path.join(base_path, 'TTS', 'Local', 'Models', 'tts_models--es--mai--tacotron2-DDC', 'model_file.pth')
        config_path = os.path.join(base_path, 'TTS', 'Local', 'Models', 'tts_models--es--mai--tacotron2-DDC', 'config.json')

        #Inicializar TTS
        tts = TTS.api.TTS(model_path=model_path, config_path=config_path, progress_bar=False)
        return tts
    except Exception as e:
        logger.error("Error en local_tts.py: %s", e)
#Función para generar el audio
def generate_audio(input_text,tts):
    #Generar el audio
    audio = tts.tts(input_text, speed=5)
    #Convertir la lista de audio a un array de numpy
    np_audio = np.array(audio)
    #Normalizar la señal para darle un sonido más natural
    filtered_audio = librosa.util.normalize(np_audio)
    #Reproducir el audio
    sd.play(filtered_audio, samplerate=22050)
    sd.wait()