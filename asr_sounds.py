import soundfile as sf
import sounddevice as sd


#Path hacia efectos de sonido
activation_sound_path = "./ASR/SoundEffects/start_beep.mp3"
deactivation_sound_path = "./ASR/SoundEffects/stop_beep.mp3"

#Reproduce un sonido cuando se activa el ASR
def play_activation_sound():
    try:
        data, samplerate = sf.read(activation_sound_path)
        sd.play(data, samplerate)
        sd.wait()
    except Exception as e:
        print(f"Error al reproducir sonido: {e}")

#Reproduce un sonido cuando se desactiva el ASR
def play_deactivation_sound():
    try:
        data, samplerate = sf.read(deactivation_sound_path)
        sd.play(data, samplerate)
        sd.wait()
    except Exception as e:
        print(f"Error al reproducir sonido: {e}")