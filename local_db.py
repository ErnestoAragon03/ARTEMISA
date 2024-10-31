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

###Función para recuperar el contexto (prioriza lo más reciente)###
def get_context(email, consults_limit=5):
    context = []
    conn = sqlite3.connect('artemisa_local_db')
    cursor = conn.cursor()

    #Recuperar consultas recientes
    cursor.execute("SELECT question, answer FROM recent_consults WHERE email = ? ORDER BY timestamp DESC LIMIT ?", (email, consults_limit))
    consults = cursor.fetchall()

    for consult in reversed(consults):
        context.append({"role": "user", "content": consult[0]})
        context.append({"role": "assistant", "content": consult[1]})
    conn.close()

    return context

###Función para recuperar toda la conversación (prioriza lo más antiguo)###
def get_conversations(email):
    conn = sqlite3.connect('artemisa_local_db')
    cursor = conn.cursor()

    #Recuperar consultas recientes
    cursor.execute("SELECT question, answer FROM recent_consults WHERE email = ? ORDER BY timestamp ASC", (email, ))
    consultas = [{'question': row[0], 'answer': row[1]} for row in cursor.fetchall()]
    
    contexto_como_texto = "\n\n".join(
            f"{consulta['question']}:  {consulta['answer']}\n"
            for consulta in consultas
    )

    conn.close()

    return contexto_como_texto
###Obtener preguntas###
def get_questions(email):
    conn = sqlite3.connect('artemisa_local_db')
    cursor = conn.cursor()
    cursor.execute("SELECT question FROM recent_consults WHERE email = ? ORDER BY timestamp ASC", (email, ))
    questions = cursor.fetchall()
    conn.close()
    return questions
###Obtener respuestas###
def get_answers(email):
    conn = sqlite3.connect('artemisa_local_db')
    cursor = conn.cursor()
    cursor.execute("SELECT answer FROM recent_consults WHERE email = ? ORDER BY timestamp ASC", (email, ))
    answers = cursor.fetchall()
    conn.close()
    return answers


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
def delete_account(email):
    conn = sqlite3.connect('artemisa_local_db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM local_users WHERE email=(?)", (email,))
    conn.commit()
    conn.close()
    delete_consults(email)

#Borrar las consultas de una cuenta (PERMANENTEMENTE)
def delete_consults(email):
    conn = sqlite3.connect('artemisa_local_db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM recent_consults WHERE email=(?)", (email,))
    conn.commit()
    conn.close()