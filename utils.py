import hashlib
from pathlib import Path

def SHA256_encription(input):
    print(input)
    sha256_hash = hashlib.sha256()

    # Convertir el texto en bytes y actualizar el objeto hash
    sha256_hash.update(input.encode('utf-8'))
    
    print(sha256_hash)
    # Devolver el hash en formato hexadecimal
    return sha256_hash.hexdigest()

if __name__ == "__main__":
    encripted = SHA256_encription("Prueba123@")
    print(encripted)

def get_desktop_path():
    """
    Obtiene la ruta del Escritorio del usuario, compatible con Windows, macOS y Linux.
    
    :return: La ruta completa al directorio del Escritorio.
    """
    # Obtener la ruta del hogar del usuario
    home = Path.home()
    
    # Definir el nombre del directorio del Escritorio dependiendo del sistema operativo
    desktop_path = home / 'Desktop'  # Esto funciona en la mayoría de sistemas, incluyendo Windows y macOS
    
    # En algunos casos específicos (por ejemplo, configuraciones locales) el Escritorio podría tener otro nombre
    if not desktop_path.exists():
        # Intentar con la traducción del Escritorio para otros idiomas (común en algunos Windows)
        desktop_path = home / 'Escritorio'
    
    # Asegurarse de que la ruta existe
    if desktop_path.exists():
        return str(desktop_path)
    else:
        # Si no se encuentra el Escritorio, usar la carpeta de inicio del usuario como alternativa
        return str(home)