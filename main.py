import asr  # módulo ASR

def main():
    #Iniciar el ASR en un hilo separado
    asr.start_asr_local()   #QUIZÁS REQUIERA DEL USO DE HILOS EN PARALELO
    

    while True:
        if asr.recognized_text:  #Si se ha detectado texto...
            print(f"Texto detectado: {asr.recognized_text}")
            process_text(asr.recognized_text)
            asr.recognized_text = ""  #Reiniciar despúes de procesar el texto
            

def process_text(recognized_text):
    #Procesamiento con LLM (por el momento solo se imprime lo recibido)
    print(f"Procesando texto: {recognized_text}")

if __name__ == "__main__":
    main()