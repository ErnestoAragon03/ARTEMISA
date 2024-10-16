import asr  # Módulo ASR
from llm import initialize_llm, generate_response  # Módulo LLM
from tts import initialize_tts, generate_audio     # Módulo TTS
import wake_up  #Módulo de wake words
import local_db #Módulo de la base de datos local

def main():
    global llm_model, llm_tokenizer, tts_model, context
    #Inicializar el modelo LLM Flant-T5
    llm_model, llm_tokenizer = initialize_llm()
    #Inicializar el modelo TTS 
    tts_model = initialize_tts()
    if asr.conversation_active:
         #Iniciar el ASR en un hilo separado
        asr.start_asr_local()   #QUIZÁS REQUIERA DEL USO DE HILOS EN PARALELO
    else:
        #Esperar wake word
        wake_up.recognize_wake_word()
        #Iniciar el ASR en un hilo separado
        asr.start_asr_local()
        
    if asr.recognized_text:  #Si se ha detectado texto...
        print(f"Texto detectado: {asr.recognized_text}")
        #Enciar a LLM
        llm_response = process_text(asr.recognized_text)
        #Enviar a TTS
        process_response(llm_response)
        asr.recognized_text = ""  #Reiniciar despúes de procesar el texto
    else:
        asr.conversation_active = False
    main()
            

def process_text(recognized_text):
    #Procesamiento con LLM
    initial_context = """El proyecto ARTEMISA es un asistente que utiliza modelos de lenguaje para responder a preguntas  
    Yo soy el proyecto ARTEMISA
    Nombres: Rebecca
    Usuario Actual: Aragón
    Información: Aragón es el usuario actual"""
    response, context = generate_response(recognized_text, initial_context, llm_model, llm_tokenizer)
    print(f"Respuesta del LLM: {response}")
    print(f"Contexto: {context}")
    return response

def process_response(llm_response):
    #Procesamiento de la respuesta de LLM con el modelo TTS
    generate_audio(llm_response, tts_model)
    pass



if __name__ == "__main__":
    local_db.init_db()
    main()