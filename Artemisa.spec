# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files("pvporcupine", includes=["resources/keyword_files/windows/*"])


a = Analysis(
    ['Artemisa.py'],
    pathex=['C:\\Users\\Ernesto\\Documents\\Proyecto ARTEMISA'],
    binaries=[
        ('./env/Lib/site-packages/vosk/*.dll', 'vosk'),
        ('./Wake_Words/pvporcupine/lib/windows/amd64/libpv_porcupine.dll', 'pvporcupine/lib/windows/amd64')],
    hiddenimports=['local_tts', 'TTS'],
    datas=[
        ('./ASR/Local/Model/vosk-model-small-es-0.42', 'vosk-model-small-es-0.42'),
        ('./ASR/Online/Temp','ASR/Online/Temp'),
        ('./local_tts.py', 'local_tts'),
        ('./TTS/Local/Models/tts_models--es--mai--tacotron2-DDC','TTS/Local/Models/tts_models--es--mai--tacotron2-DDC'),
        ('./LLM/Local/models--mrm8488--distill-bert-base-spanish-wwm-cased-finetuned-spa-squad2-es/snapshots/dcadd98e59cd7ce8efd00cb4c61a024e2895b4c1','LLM/Local/models--mrm8488--distill-bert-base-spanish-wwm-cased-finetuned-spa-squad2-es'),
        ('./env/Lib/site-packages/TTS','TTS'),
        ('./env/Lib/site-packages/TTS/VERSION', 'trainer'),
        ('./env/Lib/site-packages/inflect/*', 'inflect'),
        ('./env/Lib/site-packages/typeguard/*', 'typeguard'),
        ('./env/Lib/site-packages/gruut/VERSION', 'gruut'),
        ('./env/Lib/site-packages/jamo/data/*.json', 'jamo/data'),
        ('./env/Lib/site-packages/pypinyin/*', 'pypinyin'),
        ('./env/Lib/site-packages/pvporcupine/resources/keyword_files/windows', 'pvporcupine/resources/keyword_files/windows'),
        ('./Wake_Words', 'Wake_Words'),
        ('./wake_up.py', 'wake_up'),
        ('./ASR/SoundEffects/start_beep.mp3','ASR/SoundEffects'),
        ('./ASR/SoundEffects/stop_beep.mp3','ASR/SoundEffects')],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Artemisa',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['Icons\\ArtemisaLogo.ico'],
)
