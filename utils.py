import hashlib

def SHA256_encription(input):
    print(input)
    sha256_hash = hashlib.sha256()

    # Convertir el texto en bytes y actualizar el objeto hash
    sha256_hash.update(input.encode('utf-8'))
    
    print(sha256_hash)
    # Devolver el hash en formato hexadecimal
    return sha256_hash.hexdigest()

if __name__ == "__main__":
    encripted = SHA256_encription("Prueba123@")
    print(encripted)