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
                   password TEXT NOT NULL
                   session_active INTEGER DEFAULT 0
                   )
                    ''')
         
    #Crear tabla de sesiones activas
    cursor.execute('''CREATE TABLE IF NOT EXISTS session(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER
                    FOREIGN KEY(user_id) REFERENCES local_users(id)
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