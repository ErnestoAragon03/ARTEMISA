import sqlite3

def init_db():
    conn = sqlite3.connect('artemisa_local_db')    #Se contecta o crea la base de datos
    cursor = conn.cursor()

     #Crear tabla de cuentas
    cursor.execute('''CREATE TABLE IF NOT EXISTS local_users(
                   email TEXT NOT NULL PRIMARY KEY,
                   username TEXT NOT NULL,
                   password TEXT NOT NULL,
                   voice TEXT,
                   logged BOOLEAN)''')
    
    #Crear tabla de consultas recientes
    cursor.execute('''CREATE TABLE IF NOT EXISTS recent_consults(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                timestamp DATATIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def insertar_consulta(question, answer, email):
    conn = sqlite3.connect('artemisa_local_db')
    cursor  = conn.cursor()
    cursor.execute("INSERT INTO recent_consults (question, answer, email) VALUES (?, ?, ?)", (question, answer, email))
    conn.commit()
    conn.close()

def recuperar_contexto(consults_limit=10):
    conn = sqlite3.connect('artemisa_local_db')
    cursor = conn.cursor()

    #Recuperar consultas recientes
    cursor.execute("SELECT question, answer FROM recent_consults ORDER BY timestamp DESC LIMIT ?", (consults_limit,))
    recent_consults = [{'question': row[0], 'answer': row[1]} for row in cursor.fetchall()]

    #Recuperar datos importantes
    cursor.execute("SELECT key, value FROM important_data")
    important_data = {row[0]: row[1] for row in cursor.fetchall()}

    conn.close()

    #Combinar en un solo contexto
    context = {
        'recent_consult': recent_consults,
        'important_data': important_data
    }

    return context
###Crear cuenta###
def add_user(useraname, email, password):
    try:
        conn = sqlite3.connect('artemisa_local_db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO local_users (username, email, password, voice, logged, active) VALUES (?, ?, ?, ?, ?, ?)", (useraname, email, password, "Nova", True, True))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:      #Ya existe una cuenta con ese correo
        return False

def authenticate_user(email, password):
    conn = sqlite3.connect('artemisa_local_db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM local_users WHERE email = ? AND password = ? AND active = ?", (email, password, 1))
    user = cursor.fetchone()
    conn.close()
    return user is not None

###Obtener el correo, username y voice de la última sesión activa###
def get_last_active_session():
    conn = sqlite3.connect('artemisa_local_db')
    cursor  = conn.cursor()

    cursor.execute("SELECT email FROM local_users WHERE logged = TRUE")
    result_email = cursor.fetchone()
    cursor.execute("SELECT username FROM local_users WHERE logged = TRUE")
    result_username = cursor.fetchone()
    cursor.execute("SELECT voice FROM local_users WHERE logged = TRUE")
    voice = cursor.fetchone()
    conn.close()
    if result_email:
        return result_username[0], result_email[0], voice[0]     # Retorna el nombre de usuario, el correo y la voz preferida
    else:
        return None, None, 'Nova' #No hay sesión activa, devuelve None para activar modo guest, devuelve la voz "Nova" como default
    
def update_session(email=None):
    conn = sqlite3.connect('artemisa_local_db')
    cursor = conn.cursor()

    #Desactivar la sesión anterior
    cursor.execute("UPDATE local_users SET logged = FALSE WHERE logged = TRUE")

    #Insertar la última sesión activa (o modo guest si es None)
    if email:
        cursor.execute("UPDATE local_users SET logged = TRUE WHERE email = (?)", (email,))

    conn.commit()
    conn.close()

def get_user(email):
    conn = sqlite3.connect('artemisa_local_db') 
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM local_users WHERE email=(?)", (email,))
    username = cursor.fetchone()
    conn.close()
    return username[0]

#Obtener voz ya seleccionada
def get_voice(email):
    conn = sqlite3.connect('artemisa_local_db')
    cursor = conn.cursor()
    cursor.execute("SELECT voice FROM local_users WHERE email=(?)", (email,))
    voice = cursor.fetchone()
    conn.close()
    return voice[0]

#Cambiar la voz seleccionada
def change_voice(voice,email):
    conn = sqlite3.connect('artemisa_local_db')
    cursor = conn.cursor()
    cursor.execute("UPDATE local_users SET voice=(?) WHERE email=(?)", (voice, email))
    conn.commit()
    conn.close()

#Cerrar cuentas (PERMANENTEMENTE)
def close_account(email):
    conn = sqlite3.connect('artemisa_local_db')
    cursor = sqlite3.cursor()
    cursor.execute("DELETE FROM local_users WHERE email=(?)", (email,))
    conn.commit()
    conn.close()
    delete_consults(email)

#Borrar las consultas de una cuenta (PERMANENTEMENTE)
def delete_consults(email):
    conn = sqlite3.connect('artemisa_local_db')
    cursor = sqlite3.cursor()
    cursor.execute("DELETE FROM recent_consults WHERE email=(?)", (email,))
    conn.commit()
    conn.close()