import soundfile as sf
import sounddevice as sd
import os
from logger_config import logger

#Determina la ruta base, donde está ubicado el script actual
base_path = os.path.dirname(os.path.abspath(__file__))
logger.info("Base_path: %s", base_path)
#Path hacia efectos de sonido
activation_sound_path = os.path.join(base_path, 'ASR', 'SoundEffects', 'start_beep.mp3')
deactivation_sound_path = os.path.join(base_path, 'ASR', 'SoundEffects', 'stop_beep.mp3')

#Reproduce un sonido cuando se activa el ASR
def play_activation_sound():
    logger.info("Se llamó a play_activation_sound")
    try:
        data, samplerate = sf.read(activation_sound_path)
        sd.play(data, samplerate)
        sd.wait()
    except Exception as e:
        print(f"Error al reproducir sonido: {e}")
        logger.error("Error al reproducir activation sound: %s", e)

#Reproduce un sonido cuando se desactiva el ASR
def play_deactivation_sound():
    logger.info("Se llamó a play_deactivation_sound")
    try:
        data, samplerate = sf.read(deactivation_sound_path)
        sd.play(data, samplerate)
        sd.wait()
    except Exception as e:
        print(f"Error al reproducir sonido: {e}")
        logger.error("Error al reproducir deactivation sound: %s", e)