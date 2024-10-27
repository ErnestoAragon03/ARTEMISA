import socket

def check_internet_connection(host="8.8.8.8", port=53, timeout=3):
    """
        Esta función checa si el equipo tiene conexión a Intenet al intentar conectarse a un servidor

        Args:
            host: Dirección del servidor para verificar la conexión (por defecto es Google DNS 8.8.8.8).
            port (int): Puerto para la conexión (por defecto es 53 para DNS)
            timeout (int): Tiempo de espera en segundos para la conexión (por defecto 3 segundos)
        Returns:
            bool: True si hay conexión a Internet, False si no
    """
    try:
        socket.setdefaulttimeout(timeout)
        #Intenta conectarse al host y puertos especificados
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host,port))
        return True
    except OSError:
        return False
    
if __name__ == "__main__":
    if check_internet_connection():
        print("Conectado a Internet.")
    else:
        print("No hay conexión a Internet.")