import sqlite3
import pymysql
from logger_config import logger

###Función para sincronizar los usuarios de la DB online con la local (se sobreescribirá la local)###
def sync_users_to_local(local_db_path, cloud_db_config):
    local_conn = sqlite3.connect(local_db_path)
    local_cursor=local_conn.cursor()

    cloud_conn = pymysql.connect(**cloud_db_config)
    cloud_cursor = cloud_conn.cursor()

    #Obtener Usuarios locales
    local_cursor.execute("SELECT email FROM local_users")
    local_users = local_cursor.fetchall()
    for user in local_users:
        email = user

        #Verificar que el usuario esté en la base de datos
        cloud_cursor.execute("""SELECT email, username, password, voice, personality 
                                FROM users 
                                WHERE email = %s
                                """, (email))
        cloud_user = cloud_cursor.fetchone()

        if cloud_user:
            # Verificar si hay discrepancias
            if cloud_user != user:
                cloud_email, cloud_username, cloud_password, cloud_voice, cloud_personality = cloud_user
                #Si hay cambios actualizar la base local
                local_cursor.execute("""
                                     UPDATE local_users
                                     SET username = (?),
                                        password = (?),
                                        voice = (?),
                                        personality = (?)
                                     WHERE email = (?)
                                     """, (cloud_username, cloud_password, cloud_voice, cloud_personality, cloud_email))    
        #Si no existe significa que el usuario fue eliminado
        else:
            local_cursor.execute("""
                                 DELETE FROM local_users
                                 WHERE email = ?
                                 """, (email))
        
        local_conn.commit()

        #Cerrar conexiones
    local_conn.close()
    cloud_conn.close()
    

###Función para sincronizar los usuarios de la DB local con la cloud (se sobreescribirá la cloud)###
def sync_users_to_cloud(local_db_path, cloud_db_config):
    local_conn = sqlite3.connect(local_db_path)
    local_cursor=local_conn.cursor()

    cloud_conn = pymysql.connect(**cloud_db_config)
    cloud_cursor = cloud_conn.cursor()

    #Obtener Usuarios locales
    local_cursor.execute("SELECT email, username, password, voice, personality, logged FROM local_users")
    local_users = local_cursor.fetchall()

    for user in local_users:
        email, username, password, voice, personality, logged = user

        #Verificar que el usuario esté en la base de datos
        cloud_cursor.execute("SELECT email, username, password, voice, personality FROM users WHERE email = %s", (email,))
        cloud_user = cloud_cursor.fetchone()

        if cloud_user:
            # Verificar si hay discrepancias
            if cloud_user != user:
                #Si hay cambios actualizar la base online
                cloud_cursor.execute("""
                                     UPDATE users
                                     SET username = %s,
                                     password = %s,
                                     voice = %s,
                                     personality = %s
                                     WHERE email = %s
                                     """, (username, password, voice, personality, email))
                
        #Si no existe crearlo
        else:
            cloud_cursor.execute("""
                                    INSERT INTO users (email, username, password, voice, personality)
                                    VALUES (%s, %s, %s, %s, %s)
                                     """, (email, username, password, voice, personality))

    cloud_conn.commit()
    #Cerrar conexiones
    local_conn.close()
    cloud_conn.close()

###Función para verificar si ya hay un email registrado en la base online###
def email_alredy_exists(email, cloud_db_config):
    cloud_conn = pymysql.connect(**cloud_db_config)
    cloud_cursor = cloud_conn.cursor()
    cloud_cursor.execute("SELECT * FROM users WHERE email = %s", email)
    cloud_user = cloud_cursor.fetchone()

    cloud_conn.close()

    if cloud_user:
        return True
    else:
        return False
    
###Función para insertar un nuevo usuario en la base online###
def add_user_online(username, email, password, cloud_db_config):
    cloud_conn = pymysql.connect(**cloud_db_config)
    cloud_cursor = cloud_conn.cursor()
    cloud_cursor.execute("""
                                    INSERT INTO users (email, username, password, voice)
                                    VALUES (%s, %s, %s, %s)
                                     """, (email, username, password, "Nova"))

    cloud_conn.commit()
    cloud_conn.close()

###Función para autenticar un usuario de la base online, si es que existe###
def authenticate_user_online(email, password, cloud_db_config):
    logger.info("Llegando a authenticate user online")
    try:
        cloud_conn = pymysql.connect(**cloud_db_config)
        cloud_cursor = cloud_conn.cursor()

        cloud_cursor.execute("SELECT * FROM users WHERE email= %s AND password = %s", (email, password))
        user = cloud_cursor.fetchone()
        cloud_conn.close()
        logger.info("Usuario autenticado con éxito")
        return user
    except Exception as e:
        logger.error("Error al autenticar usuario: %s", e)

###Función para eliminar usuarios de la nube###
def delete_user_online(email, cloud_db_config):
    cloud_conn = pymysql.connect(**cloud_db_config)
    cloud_cursor = cloud_conn.cursor()

    cloud_cursor.execute("DELETE FROM users WHERE email = %s", (email,))
    cloud_conn.commit()
    cloud_conn.close()

###Función para cambiar la personalidad
def change_personality_online(new_personality, email, cloud_db_config):
    cloud_conn = pymysql.connect(**cloud_db_config)
    cloud_cursor = cloud_conn.cursor()

    cloud_cursor.execute("UPDATE users SET personality = %s WHERE email = %s", (new_personality, email))
    cloud_conn.commit()
    cloud_conn.close()

###Función para cmabiar la voz
def change_voice(voice, email, cloud_db_config):
    cloud_conn = pymysql.connect(**cloud_db_config)
    cloud_cursor = cloud_conn.cursor()

    cloud_cursor.execute("UPDATE users SET voice = %s WHERE email = %s", (voice, email))
    cloud_conn.commit()
    cloud_conn.close()