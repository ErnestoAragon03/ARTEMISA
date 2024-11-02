# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files("pvporcupine", includes=["resources/keyword_files/windows/*"])


a = Analysis(
    ['Artemisa.py'],
    pathex=['C:\\Users\\Ernesto\\Documents\\Proyecto ARTEMISA'],
    binaries=[
        ('C:\\Users\\Ernesto\\Documents\\Proyecto ARTEMISA\\env\\Lib\\site-packages\\vosk\\*.dll', 'vosk'),
        ('C:\\Users\\Ernesto\\Documents\\Proyecto ARTEMISA\\env\\Lib\\site-packages\\pvporcupine\\lib\windows\\amd64\\libpv_porcupine.dll', 'pvporcupine/lib/windows/amd64')],
    hiddenimports=['local_tts', 'inflect', 'typeguard', 'TTS'],
    datas=[
        ('C:\\Users\\Ernesto\\Documents\\Proyecto ARTEMISA\\ASR\\Local\\Model\\vosk-model-small-es-0.42', 'vosk-model-small-es-0.42'),
        ('C:\\Users\\Ernesto\\Documents\\Proyecto ARTEMISA\\local_tts.py', 'local_tts'),
        ('C:\\Users\\Ernesto\\AppData\\Local\\tts\\tts_models--es--mai--tacotron2-DDC\\model_file.pth','.'),
        ('C:\\Users\\Ernesto\\AppData\\Local\\tts\\tts_models--es--mai--tacotron2-DDC\\config.json','.'),
        ('C:\\Users\\Ernesto\\Documents\\Proyecto ARTEMISA\\env\\Lib\\site-packages\\TTS','TTS'),
        ('C:\\Users\\Ernesto\\Documents\\Proyecto ARTEMISA\\env\\Lib\\site-packages\\TTS\\VERSION', 'trainer'),
        ('C:\\Users\\Ernesto\\Documents\\Proyecto ARTEMISA\\env\\Lib\\site-packages\\inflect\\*', 'inflect'),
        ('C:\\Users\\Ernesto\\Documents\\Proyecto ARTEMISA\\env\\Lib\\site-packages\\typeguard\\*', 'typeguard'),
        ('C:\\Users\\Ernesto\\Documents\\Proyecto ARTEMISA\\env\\Lib\\site-packages\\gruut\VERSION', 'gruut'),
        ('C:\\Users\\Ernesto\\Documents\\Proyecto ARTEMISA\\env\\Lib\\site-packages\\jamo\\data\\*.json', 'jamo/data'),
        ('C:\\Users\\Ernesto\\Documents\\Proyecto ARTEMISA\\env\\Lib\\site-packages\\pypinyin\\*', 'pypinyin'),
        ('C:\\Users\\Ernesto\\Documents\\Proyecto ARTEMISA\\env\\Lib\\site-packages\\pvporcupine\\resources\\keyword_files\\windows', 'pvporcupine/resources/keyword_files/windows'),
        ('C:\\Users\\Ernesto\\Documents\\Proyecto ARTEMISA\\Wake_Words', 'Wake_Words'),
        ('C:\\Users\\Ernesto\\Documents\\Proyecto ARTEMISA\\wake_up.py', 'wake_up')],
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
