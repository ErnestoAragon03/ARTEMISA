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
    initial_context = """El proyecto ARTEMISA es un asistente que utiliza modelos de lenguaje para responder a preguntas  
    Yo soy el proyecto ARTEMISA
    Mi nombre es Rebecca
    Usuario Actual: Aragón
    Información: Aragón es el creador del proyecto ARTEMISA"""
    response = generate_response(recognized_text, initial_context, model, tokenizer)
    print(f"Respuesta del LLM: {response}")


if __name__ == "__main__":
    main()