import pymysql
from syncCloud import sync_users_to_cloud
from syncCloud import sync_users_to_local

if __name__ == "__main__":
    local_db_path = './artemisa_local_db'
    cloud_db_config = {
        'host': 'localhost',
        'user': 'main',
        'password': 'Judgment',
        'database': 'Artemisas_long_term_memory',
        'port': 3306,
    }
    sync_users_to_cloud(local_db_path, cloud_db_config)
    try:
        connection = pymysql.connect(**cloud_db_config)
        print("Conexión exitosa a la base de datos en la nube.")
    except pymysql.MySQLError as e:
        print(f"Error al conectar: {e}")