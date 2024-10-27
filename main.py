from local_asr import start_asr_local                   # Módulo ASR
from local_llm import initialize_llm, generate_response  # Módulo LLM
from local_tts import initialize_tts, generate_audio     # Módulo TTS
import wake_up  #Módulo de wake words
import local_db #Módulo de la base de datos local
import GUI  #Interfaz gráfica
from cloud_llm import ask_to_openai
from cloud_tts import generate_audio_OpenAI
from cloud_asr import transcribe
from check_internet_connection import check_internet_connection
import threading

#Variable global que indica si se sigue ejecutando main
running = True
conversation_active = False
tts_interrupted = False
recognized_text = None
alredy_alerted_Disconnection = False
alredy_alerted_Connection = True
def main():
    global context, running, conversation_active, recognized_text, tts_interrupted, app_instance, alredy_alerted_Connection, alredy_alerted_Disconnection
    while running:
        recognized_text = None
        if conversation_active & GUI.mic_active:
            #Seleccionar modelo online o local
            if check_internet_connection():
            ### Levantar un anuncio indicando que se recuperó la conexión (Solo si aplica)###
                alert_Connection()
            ### ASR en línea ###
                recognized_text = transcribe()
            else:
            ### Levantar un anuncio indicando que se perdió la conexión###
                alert_No_Connection()
            ### ASR local ###
                recognized_text = start_asr_local(app_instance) 
            
            

        else:
            awaked = wake_up.recognize_wake_word()
            if awaked:
                #Seleccionar modelo online o local
                if check_internet_connection():
                ### Levantar un anuncio indicando que se recuperó la conexión (Solo si aplica)###
                    alert_Connection()
                ### ASR en línea ###
                    recognized_text = transcribe()
                else:
                ### Levantar un anuncio indicando que se perdió la conexión###
                    app_instance.master.alert_disconnection()
                ### ASR local ###
                    recognized_text = start_asr_local(app_instance) 

            
        if  GUI.mic_active: #Si el microfono estaba activo al momento de llegar
            if recognized_text:  #Si se ha detectado texto...
                ### Pasa el texto capturado a la interfaz gráfica ###
                app_instance.transcribe_GUI(text=recognized_text, speaker='user')        
                ### Enviar a LLM ###
                llm_response = process_text(recognized_text, app_instance)
                ### Pasar respuesta a interfaz gráfica ###
                app_instance.transcribe_GUI(text=llm_response, speaker='assistant')
                ### Obtener correo de usuario actual ###
                current_email = app_instance.master.current_email
                if current_email:
                    local_db.insertar_consulta(question=recognized_text, answer=llm_response, email=current_email)
                recognized_text = None  #Reiniciar despúes de procesar el texto y almacenar en la base de datos
                #Enviar a TTS
                process_response(llm_response, app_instance)
            else:
                recognized_text = None
                conversation_active = False

        else:
            print("Terminando Pipeline")
            break
            

def process_text(recognized_text, app_instance):
    try:
        ###Procesamiento con LLM###
        ### Seleccionar modelo online o local
        if check_internet_connection():
        ### Levantar un anuncio indicando que se recuperó la conexión (Solo si aplica)###
            alert_Connection()
        ### LLM Online ###
            response = ask_to_openai(recognized_text)
        else:
        ### Levantar un anuncio indicando que se perdió la conexión###
            alert_No_Connection()
        ### LLM local ###
            initial_context = """El proyecto ARTEMISA es un asistente que utiliza modelos de lenguaje para responder a preguntas  
            Yo soy el proyecto ARTEMISA
            Nombres: Rebecca
            Usuario Actual: Aragón
            Información: Aragón es el usuario actual"""
            response, context = generate_response(recognized_text, initial_context, llm_model, llm_tokenizer)

        ### Verificar que la respuesta no esté vacía ###
        if not response or response == '[CLS]':
            raise ValueError("La respuesta del LLM está vacía")    
        print(f"Respuesta del LLM: {response}")
    except ValueError as ve:
        print(f"Error en la respuesta del LLM: {ve}")
        response = "Hubo un error en la respuesta, intentelo nuevamente"
    except Exception as e: 
        print(f"Ocurrió un error inesperado: {e}")
        response = "Hubo un error inesperado, intentelo nuevamente"

    return response

def process_response(llm_response, app_instance):
    ### Procesamiento de la respuesta de LLM con el modelo TTS ###
    ### Seleccionar modelo online o local ###
    if check_internet_connection():
    ### Levantar un anuncio indicando que se recuperó la conexión (Solo si aplica)###
        alert_Connection()
    ### TTS Online###
        tts_thread = threading.Thread(target=generate_audio_OpenAI, args=(llm_response,))
        tts_thread.start()
    else:
    ### Levantar un anuncio indicando que se perdió la conexión###
        alert_No_Connection()
    ### TTS Local###
        generate_audio(llm_response, tts_model)

def interrupt_tts():
    global recognized_text, tts_interrupted
    recognized_text = None
    tts_interrupted = True

def alert_No_Connection():
    global app_instance, alredy_alerted_Disconnection, alredy_alerted_Connection
    if not alredy_alerted_Disconnection:
        app_instance.master.alert_disconnection()
        alredy_alerted_Disconnection = True
        alredy_alerted_Connection = False

def alert_Connection():
    global app_instance, alredy_alerted_Connection, alredy_alerted_Disconnection
    if not alredy_alerted_Connection:
        app_instance.master.alert_connection()
        alredy_alerted_Connection = True
        alredy_alerted_Disconnection = False

def start_pipeline(starter_app_instance):
    local_db.init_db()
    global llm_model, llm_tokenizer, tts_model, app_instance
    app_instance = starter_app_instance
    #Inicializar el modelo LLM Flant-T5
    llm_model, llm_tokenizer = initialize_llm()
    #Inicializar el modelo TTS 
    tts_model = initialize_tts()
    main()


if __name__ == "__main__":
    local_db.init_db()
    global llm_model, llm_tokenizer, tts_model
    #Inicializar el modelo LLM Flant-T5
    llm_model, llm_tokenizer = initialize_llm()
    #Inicializar el modelo TTS 
    tts_model = initialize_tts()
    main()