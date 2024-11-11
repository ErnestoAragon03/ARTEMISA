import pymysql
from syncCloud import sync_users_to_cloud, sync_users_to_local
from proxy import get_sql_credentials
import json
import threading 

###Definir evento para terminar threads
stop_event = threading.Event()

###Función para clonar el contenido de la base local a la online (Se sobreescribirá la online)###
def clone_to_cloud():
    #Path a la base local
    local_db_path = './artemisa_local_db'
    ###Conseguir credenciales de Cloud SQL###
    #Obtener secreto desde el SecretManager
    credentials = get_sql_credentials()
    #Parsear las credenciales desde un JSON a un diccionario
    cloud_db_config = json.loads(credentials)
    try:
        sync_users_to_cloud(local_db_path, cloud_db_config)
        print("Conexión exitosa a la base de datos en la nube.")
    except pymysql.MySQLError as e:
        print(f"Error al conectar: {e}")

###Función para clonar el contenido de la base online a la local (Se sobreescribirá la local)###
def clone_to_local(intervalo = 300):

    while not stop_event.is_set():
        #Path a la base local
        local_db_path = './artemisa_local_db'
        ###Conseguir credenciales de Cloud SQL###
        #Obtener secreto desde el SecretManager
        credentials = get_sql_credentials()
        #Parsear las credenciales desde un JSON a un diccionario
        cloud_db_config = json.loads(credentials)
        try:
            sync_users_to_local(local_db_path, cloud_db_config)
            print("Se clonó con éxito la base en la nube.")
        except pymysql.MySQLError as e:
            print(f"Error al conectar: {e}")

        stop_event.wait(intervalo)

def stop_clone():
    stop_event.set()

if __name__ == "__main__":
    #Path a la base local
    local_db_path = './artemisa_local_db'
    ###Conseguir credenciales de Cloud SQL###
    #Obtener secreto desde el SecretManager
    credentials = get_sql_credentials()
    #Parsear las credenciales desde un JSON a un diccionario
    cloud_db_config = json.loads(credentials)

    try:
        sync_users_to_cloud(local_db_path, cloud_db_config)
        print("Conexión exitosa a la base de datos en la nube.")
    except pymysql.MySQLError as e:
        print(f"Error al conectar: {e}")