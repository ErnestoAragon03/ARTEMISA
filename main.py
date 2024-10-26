from local_asr import start_asr_local                   # Módulo ASR
from local_llm import initialize_llm, generate_response  # Módulo LLM
from local_tts import initialize_tts, generate_audio     # Módulo TTS
import wake_up  #Módulo de wake words
import local_db #Módulo de la base de datos local
import GUI  #Interfaz gráfica
from cloud_llm import ask_to_openai
from cloud_tts import generate_audio_OpenAI
from cloud_asr import transcribe

#Variable global que indica si se sigue ejecutando main
running = True
conversation_active = False

def main(app_instance):
    global context, running, conversation_active
    while running:
        if conversation_active & GUI.mic_active:
            #Iniciar el ASR en un hilo separado
            #recognized_text = start_asr_local(app_instance)   #QUIZÁS REQUIERA DEL USO DE HILOS EN PARALELO

            ###ASR en línea
            recognized_text = transcribe()

            print("recognized_text: ", recognized_text)
        else:
            awaked = wake_up.recognize_wake_word()
            #Iniciar el ASR en un hilo separado
            if awaked:
                #recognized_text = start_asr_local(app_instance)
                recognized_text = transcribe()

            
        if  GUI.mic_active: #Si el microfono estaba activo al momento de llegar
            if recognized_text:  #Si se ha detectado texto...
                print(f"Texto detectado: {recognized_text}")
                
                app_instance.transcribe(text=recognized_text, speaker='user')     #Pasa el texto capturado a la interfaz gráfica
                #Enviar a LLM
                llm_response = process_text(recognized_text)
                app_instance.transcribe(text=llm_response, speaker='assistant')
                current_email = app_instance.master.current_email
                print(current_email)
                if current_email:
                    local_db.insertar_consulta(question=recognized_text, answer=llm_response, email=current_email)
                recognized_text = ""  #Reiniciar despúes de procesar el texto y almacenar en la base de datos
                #Enviar a TTS
                process_response(llm_response)
            else:
                conversation_active = False

        else:
            print("Terminando Pipeline")
            break
            

def process_text(recognized_text):
    try:
        #Procesamiento con LLM
        initial_context = """El proyecto ARTEMISA es un asistente que utiliza modelos de lenguaje para responder a preguntas  
        Yo soy el proyecto ARTEMISA
        Nombres: Rebecca
        Usuario Actual: Aragón
        Información: Aragón es el usuario actual"""
        #response, context = generate_response(recognized_text, initial_context, llm_model, llm_tokenizer)
        response = ask_to_openai(recognized_text)
        #Verificar que la respuesta no esté vacía
        print("RESPUESTA QUE REGRESÓ:", response)
        if not response or response == '[CLS]':
            raise ValueError("La respuesta del LLM está vacía")    
        print(f"Respuesta del LLM: {response}")
        #print(f"Contexto: {context}")
    except ValueError as ve:
        print(f"Error en la respuesta del LLM: {ve}")
        response = "Hubo un error en la respuesta, intentelo nuevamente"
    except Exception as e: 
        print(f"Ocurrió un error inesperado: {e}")
        response = "Hubo un error inesperado, intentelo nuevamente"
    return response

def process_response(llm_response):
    #Procesamiento de la respuesta de LLM con el modelo TTS
    #generate_audio(llm_response, tts_model)
    generate_audio_OpenAI(llm_response)
    pass

def start_pipeline(app_instance):
    local_db.init_db()
    global llm_model, llm_tokenizer, tts_model
    #Inicializar el modelo LLM Flant-T5
    llm_model, llm_tokenizer = initialize_llm()
    #Inicializar el modelo TTS 
    tts_model = initialize_tts()
    main(app_instance)


if __name__ == "__main__":
    local_db.init_db()
    global llm_model, llm_tokenizer, tts_model
    #Inicializar el modelo LLM Flant-T5
    llm_model, llm_tokenizer = initialize_llm()
    #Inicializar el modelo TTS 
    tts_model = initialize_tts()
    main()