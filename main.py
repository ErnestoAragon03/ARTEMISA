import asr  # Módulo ASR
from llm import initialize_llm, generate_response  # Módulo LLM

def main():
    global model, tokenizer
    #Incializar el modelo LLM BLOOM 560-M
    model, tokenizer = initialize_llm()
    #Iniciar el ASR en un hilo separado
    asr.start_asr_local()   #QUIZÁS REQUIERA DEL USO DE HILOS EN PARALELO
    

  
    if asr.recognized_text:  #Si se ha detectado texto...
        print(f"Texto detectado: {asr.recognized_text}")
        process_text(asr.recognized_text)
        asr.recognized_text = ""  #Reiniciar despúes de procesar el texto
            

def process_text(recognized_text):
    #Procesamiento con LLM
    response = generate_response(recognized_text, model, tokenizer)
    print(f"Respuesta del LLM: {response}")


if __name__ == "__main__":
    main()