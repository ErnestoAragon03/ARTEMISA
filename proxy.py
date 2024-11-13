import os
import subprocess
import tempfile
from google.oauth2 import service_account
from google.cloud import secretmanager
from logger_config import logger
import sys

###Variable para almacenar el proceso del proxy###
proxy_process = None

###Recupera las credenciales de SQL almacenadas en Secret Manager usando las credenciales de GCP###
def get_sql_credentials():
    logger.info("Llegando a get_sql_credentials")
    try:
        ###Cargar credenciales de GCP###
        # Verifica si la aplicación está empaquetada
        if getattr(sys, 'frozen', False):
            # Si está empaquetada, utiliza el directorio de PyInstaller
            base_path = sys._MEIPASS
        else:
            # Si está en desarrollo, utiliza el directorio actual
            base_path = os.path.abspath(".")
        credentials_path = os.path.join(base_path, 'credentials', 'GCP_credentials.json')

        GCP_credentials = service_account.Credentials.from_service_account_file(credentials_path)
        ###Crear cliente de secret manager###
        client = secretmanager.SecretManagerServiceClient(credentials=GCP_credentials)
        # Nombre completo del secreto en Secret Manager con la versión especificada
        secret_name = "projects/593380392756/secrets/CLOUD_SQL_CREDENTIALS/versions/latest"
        ###Accede a la última versión del proyecto###
        response = client.access_secret_version(name=secret_name)
        logger.info("SQL Credentials recuperadas")
        ###Obtener el archivo de credenciales###
        return response.payload.data.decode('UTF-8')
    except Exception as e:
        logger.error("Error al recuperar las credenciales SQL: %s", e)
###Inicia el proxy de Cloud SQL y guarda el proceso globalmente
def start_cloud_proxy():
    global proxy_process
    logger.info("Llegando a start_cloud_proxy")
    try:
        ###Iniciar el proxy de cloud###
        try:
            # Obtén el path absoluto del archivo de credenciales
            # Verifica si la aplicación está empaquetada
            if getattr(sys, 'frozen', False):
                # Si está empaquetada, utiliza el directorio de PyInstaller
                base_path = sys._MEIPASS
            else:
                # Si está en desarrollo, utiliza el directorio actual
                base_path = os.path.abspath(".")
            credentials_path = os.path.join(base_path, 'credentials', 'GCP_credentials.json')
            proxy_executable = os.path.join(base_path, 'credentials', 'cloud-sql-proxy.exe')
            logger.info("credentials_path :%s",credentials_path)
            logger.info("Proxy ejecutable path: %s", proxy_executable)
            proxy_process = subprocess.Popen([
                proxy_executable,
                f"--credentials-file={credentials_path}",
                "proyecto-artemisa-440806:us-central1:artemisa-cloud-db"
            ], creationflags=subprocess.CREATE_NO_WINDOW)
            print("Proxy de Cloud Iniciado con éxito.")
            logger.info("Proxy iniciado con éxito")
        except Exception as e:
            print("Error al iniciar el proxy: ",e)
            logger.error("Error al intentar iniciar el proxy:, %s", e)
    except Exception as e:
        logger.error("Error al iniciar el proxy: %s", e)

###Detiene el proxy con la nube usando el PID (Process ID)###
def stop_cloud_proxy():
    global proxy_process
    if proxy_process is not None:
        #Enviar terminación al proceso
        proxy_process.terminate()
        #Esperar a que se cierre el proceso
        proxy_process.wait()
        print("Proxy de Cloud terminado con éxito")
        proxy_process = None
    else:
        print("El proxy no está en ejecución")

###Llamar a la función de iniciar el proxy###
if __name__ == "__main__":
    try:
        start_cloud_proxy()
    except Exception as e:
        print("Error al inicializar el Proxy: ",e)
    finally:
        stop_cloud_proxy()