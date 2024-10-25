import sqlite3

def init_db():
    conn = sqlite3.connect('artemisa_local_db')    #Se contecta o crea la base de datos
    cursor = conn.cursor()

    #Crear tabla de consultas recientes
    cursor.execute('''CREATE TABLE IF NOT EXISTS recent_consults(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                timestamp DATATIME DEFAULT CURRENT_TIMESTAMP)''')
    #Crear tabla de Data importante
    cursor.execute('''CREATE TABLE IF NOT EXISTS important_data(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL,
                value TEXT NOT NULL)''')
    #Crear tabla de cuentas
    cursor.execute('''CREATE TABLE IF NOT EXISTS local_users(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   username TEXT NOT NULL,
                   email TEXT NOT NULL UNIQUE,
                   password TEXT NOT NULL)''')
         
    #Crear tabla de sesiones activas
    cursor.execute('''CREATE TABLE IF NOT EXISTS session(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_email INTEGER,
                    FOREIGN KEY(user_email) REFERENCES local_users(email)
                   )
                   ''')
    conn.commit()
    conn.close()

def insertar_consulta(question, answer):
    conn = sqlite3.connect('artemisa_local_db')
    cursor  = conn.cursor()
    cursor.execute("INSERT INTO recent_consults (question, answer) VALUES (?, ?)", (question, answer))
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
        cursor.execute("INSERT INTO local_users (username, email, password) VALUES (?, ?, ?)", (useraname, email, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:      #Ya existe una cuenta con ese correo
        return False

def authenticate_user(email, password):
    conn = sqlite3.connect('artemisa_local_db')
    cursor = conn.cursor()
    cursor.execute("SELECT FROM users WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

###Obtener el correo y username de la última sesión activa###
def get_last_active_session():
    conn = sqlite3.connect('artemisa_local_db')
    cursor  = conn.cursor()

    cursor.execute("SELECT user_email FROM session ORDER BY id DESC LIMIT 1")
    result_email = cursor.fetchone()

    if result_email:
        cursor.execute("SELECT username FROM local_users WHERE email=?", (result_email))
        result_username = cursor.fetchone()
        conn.close()
        return result_username, result_email    # Retorna el nombre de usuario y el correo
    else:
        return None, None #No hay sesión activa, devuelve None para activar modo guest
    
def update_session(email=None):
    conn = sqlite3.connect('artemisa_local_db')
    cursor = conn.cursor()

    #Eliminar la sesión anterior
    cursor.execute("DELETE FROM session")

    #Insertar la última sesión activa (o modo guest si es None)
    if email:
        cursor.execute("INSERT INTO session (user_email) VALUES (?)", (email))

    conn.commit()
    conn.close()