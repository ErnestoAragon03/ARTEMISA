import sqlite3

def drop_session():
    conn = sqlite3.connect('artemisa_local_db')    #Se contecta o crea la base de datos
    cursor = conn.cursor()

    cursor.execute("DROP TABLE session")
    conn.commit()
    conn.close()

def drop_local_users():
    conn = sqlite3.connect('artemisa_local_db')    #Se contecta o crea la base de datos
    cursor = conn.cursor()

    cursor.execute("DROP TABLE local_users")
    conn.commit()
    conn.close()

def drop_recent_consults():
    conn = sqlite3.connect('artemisa_local_db')
    cursor = conn.cursor()

    cursor.execute("DROP TABLE recent_consults")
    conn.commit()
    conn.close()

def drop_important_data():
    conn = sqlite3.connect('artemisa_local_db')
    cursor = conn.cursor()

    cursor.execute("DROP TABLE important_data")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    drop_local_users()
    drop_recent_consults()