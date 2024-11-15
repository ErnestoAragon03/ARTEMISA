import os
import subprocess
import tempfile
from google.oauth2 import service_account
from google.cloud import secretmanager
from google.cloud import storage
from logger_config import logger
import sys
import json
from utils import get_desktop_path

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

def get_storage_credentials():
    logger.info("Llegando a get_storage_credentials")
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
        secret_name = "projects/593380392756/secrets/CLOUD_STORAGE_CREDENTIALS/versions/latest"
        ###Accede a la última versión del proyecto###
        response = client.access_secret_version(name=secret_name)
        logger.info("SQL Credentials recuperadas")
        ###Obtener el archivo de credenciales###
        return response.payload.data.decode('UTF-8')
    except Exception as e:
        logger.error("Error al recuperar las credenciales de storage: %s", e)

def get_OpenAI_Key():
    logger.info("Llegando a get_OpenAI_Key")
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
        secret_name = "projects/593380392756/secrets/OPENAI_API_KEY/versions/latest"
        ###Accede a la última versión del proyecto###
        response = client.access_secret_version(name=secret_name)
        logger.info("API KEY recuperada")
        ###Obtener el archivo de credenciales###
        return response.payload.data.decode('UTF-8')
    except Exception as e:
        logger.error("Error al recuperar la API KEY: %s", e)

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

def upload_audio_to_cloud(audio_file_path):
    bucket_name = "audios_generados"
    try:
        ###Recuperar credenciales desde Secret Manager###
        storage_credentials_json = get_storage_credentials()

        if storage_credentials_json:
            # Decodificar el JSON en un diccionario
            storage_credentials = json.loads(storage_credentials_json)
            
            # Crear credenciales a partir del diccionario decodificado
            credentials = service_account.Credentials.from_service_account_info(storage_credentials)
            
            # Crear el cliente de Google Cloud Storage con las credenciales cargadas
            storage_client = storage.Client(credentials=credentials)
            
            # Obtener el bucket donde se almacenará el archivo
            bucket = storage_client.bucket(bucket_name)
            
            # Nombre del archivo en el bucket (puede ser el mismo nombre del archivo local)
            blob_name = os.path.basename(audio_file_path)
            blob = bucket.blob(blob_name)
            
            # Subir el archivo al bucket
            blob.upload_from_filename(audio_file_path)
            logger.info(f"Archivo {audio_file_path} subido exitosamente al bucket {bucket_name} como {blob_name}.")

            # Eliminar el archivo local después de subirlo
            os.remove(audio_file_path)
            print(f"Archivo {audio_file_path} eliminado del sistema local.")
        else:
            print("Error al recuperar las credenciales")
            logger.error("Error al recuperar las credenciales")
    except Exception as e:
        print("Ocurrió un error mientras se subía el audio: ", e)

###Descarga todos los archivos de audio del usuario actual###
def download_user_audios(user_email):
    bucket_name = "audios_generados"
    try:
        ###Recuperar credenciales desde Secret Manager###
        storage_credentials_json = get_storage_credentials()

        if storage_credentials_json:
            # Decodificar el JSON en un diccionario
            storage_credentials = json.loads(storage_credentials_json)
            
            # Crear credenciales a partir del diccionario decodificado
            credentials = service_account.Credentials.from_service_account_info(storage_credentials)
            
            # Crear el cliente de Google Cloud Storage con las credenciales cargadas
            storage_client = storage.Client(credentials=credentials)
            
            # Obtener el bucket donde de donde se descargarán los archivos
            bucket = storage_client.bucket(bucket_name)
            
            # Prefijo que corresponde al usuario actual
            prefix = f"{user_email}"

            ###Obtener ruta del escritorio del usuario
            desktop_path = get_desktop_path()
            download_folder = os.path.join(desktop_path, 'audios_descargados')

             # Crear la carpeta de descarga si no existe
            if not os.path.exists(download_folder):
                os.makedirs(download_folder)
            
            ###Listar todos los blobs (archivos) que comienzan con el prefijo del usuario
            blobs = bucket.list_blobs(prefix=prefix)
            print(blobs)

            ###Descargar cada archivo en la carpeta especificada
            for blob in blobs:
                print("Entró al for")
                # Ruta completa del archivo local
                local_file_path = os.path.join(download_folder, blob.name)
                
                # Crear directorios necesarios si no existen
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                
                # Descargar el archivo
                blob.download_to_filename(local_file_path)
                
                logger.info(f"Archivo descargado exitosamente: {blob.name} a {local_file_path}")
        else:
            print("Error al recuperar las credenciales")
            logger.error("Error al recuperar las credenciales")
    except Exception as e:
        print("Ocurrió un error mientras se descargaban los audios: ", e)

###Llamar a la función de iniciar el proxy###
if __name__ == "__main__":
    try:
        start_cloud_proxy()
        download_user_audios("ernesto.aragon888@gmail.com")
    except Exception as e:
        print("Error al inicializar el Proxy: ",e)
    finally:
        stop_cloud_proxy()