import sounddevice as sd
import numpy as np
from TTS.api import TTS
import librosa

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
    audio = tts.tts(input_text, speed=5)
    #Convertir la lista de audio a un array de numpy
    np_audio = np.array(audio)
    #Normalizar la señal para darle un sonido más natural
    filtered_audio = librosa.util.normalize(np_audio)
    #Reproducir el audio
    sd.play(filtered_audio, samplerate=22050)
    sd.wait()