import threading
import time
import socket
from tkinter import messagebox

class InternetChecker:
    def __init__(self):
        self.internet_status = True
        self.checking = True
        self.thread = threading.Thread(target=self.check_internet_connection, daemon=True)
        self.thread.start()
    def check_internet_connection(self, host="8.8.8.8", port=53, timeout=3):
        """
            Esta función checa si el equipo tiene conexión a Intenet al intentar conectarse a un servidor

            Args:
                host: Dirección del servidor para verificar la conexión (por defecto es Google DNS 8.8.8.8).
                port (int): Puerto para la conexión (por defecto es 53 para DNS)
                timeout (int): Tiempo de espera en segundos para la conexión (por defecto 3 segundos)
            Returns:
                bool: True si hay conexión a Internet, False si no
        """
        while self.checking:
            try:
                socket.setdefaulttimeout(timeout)
                #Intenta conectarse al host y puertos especificados
                socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host,port))
                new_status = True
            except OSError:
                new_status = False
            
            #Solo se muestra el messagebox si hay un cambio en el estado
            if new_status != self.internet_status:
                self.internet_status = new_status
                self.show_connection_status()
            #Esperar 5 segundos antes de volver a verificar
            time.sleep(5)

    def show_connection_status(self):
        print("Advirtió aquí")
        #Mostrar mensaje de desconexión o reconexión
        if self.internet_status:
            messagebox.showinfo("Conexión reestablecida", "Se ha recuperado la conexión a Internet, Artemisa pasará al modo online")
        else:
            messagebox.showwarning("Sin conexión a Internet", "Actualmente se encuentra en modo desconectado, Artemisa se transformará a su versión offline...")

    def stop_checking(self):
        print("Se terminó un thread")
        self.checking = False
    
if __name__ == "__main__":
    if check_internet_connection():
        print("Conectado a Internet.")
    else:
        print("No hay conexión a Internet.")