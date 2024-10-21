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

if __name__ == "__main__":
    drop_session()
    drop_local_users()