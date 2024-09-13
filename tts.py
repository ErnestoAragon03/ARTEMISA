import sounddevice as sd
import numpy as np
from TTS.api import TTS

#Inicializar modelo de Mozilla (css10)
def initialize_tts():
    #Nombre del modelo que se usará
    model_name="tts_models/es/mai/tacotron2-DDC"
    #Inicializar TTS
    tts = TTS(model_name=model_name, progress_bar=False)
    return tts

#Función para generar el audio
def generate_audio(input_text,tts):
    #Generar el audio
    audio = tts.tts(input_text)
    #Convertir la lista de audio a un array de numpy
    np_audio = np.array(audio)
    #Reproducir el audio
    sd.play(np_audio, samplerate=22050)
    sd.wait()