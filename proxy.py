import os
import subprocess
import tempfile
from google.oauth2 import service_account
from google.cloud import secretmanager
import signal

###Variable para almacenar el proceso del proxy###
proxy_process = None

###Recupera las credenciales de SQL almacenadas en Secret Manager usando las credenciales de GCP###
def get_sql_credentials():
    ###Cargar credenciales de GCP###
    GCP_credentials = service_account.Credentials.from_service_account_file("./credentials/GCP_credentials.json")
    ###Crear cliente de secret manager###
    client = secretmanager.SecretManagerServiceClient(credentials=GCP_credentials)
    # Nombre completo del secreto en Secret Manager con la versión especificada
    secret_name = "projects/593380392756/secrets/CLOUD_SQL_CREDENTIALS/versions/latest"
    ###Accede a la última versión del proyecto###
    response = client.access_secret_version(name=secret_name)
    ###Obtener el archivo de credenciales###
    return response.payload.data.decode('UTF-8')

###Inicia el proxy de Cloud SQL y guarda el proceso globalmente
def start_cloud_proxy():
    global proxy_process
    ###Obtener las credenciales desde el secret manager###
    #credentials = get_sql_credentials()
    ###Crear un archivo temporal para almacenar las credenciales###
    with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".json") as tmp_credentials:
        tmp_credentials.write(credentials)
        tmp_credentials_path = tmp_credentials.name

    ###Iniciar el proxy de cloud###
    try:
        proxy_process = subprocess.Popen([
            "./env/Scripts/cloud-sql-proxy",
            f"--credentials-file=./credentials/GCP_credentials.json",
            "proyecto-artemisa-440806:us-central1:artemisa-cloud-db"
        ])
        print("Proxy de Cloud Iniciado con éxito.")
    except Exception as e:
        print("Error al iniciar el proxy: ",e)
    finally:
        ###Limpiar el archivo###
        os.remove(tmp_credentials_path)

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
    start_cloud_proxy()