from local_asr import start_asr_local                   # Módulo ASR
from local_llm import initialize_llm, generate_response  # Módulo LLM
from local_tts import initialize_tts, generate_audio     # Módulo TTS
import wake_up  #Módulo de wake words
import local_db #Módulo de la base de datos local
import GUI  #Interfaz gráfica
from GUI import internet_checker #Instancia de verificador de conexión
from cloud_llm import ask_to_openai
from cloud_tts import generate_audio_OpenAI
from cloud_asr import transcribe
import threading

#Variable global que indica si se sigue ejecutando main
running = True
conversation_active = False
tts_interrupted = False
recognized_text = None
def main():
    global context, running, conversation_active, recognized_text, tts_interrupted, app_instance
    while running:
        recognized_text = None
        if conversation_active & GUI.mic_active:
            #Seleccionar modelo online o local
            if internet_checker.internet_status:
            ### ASR en línea ###
                recognized_text = transcribe()
            else:
            ### ASR local ###
                recognized_text = start_asr_local(app_instance) 
            
            

        else:
            awaked = wake_up.recognize_wake_word()
            if awaked:
                #Seleccionar modelo online o local
                if internet_checker.internet_status:
                ### ASR en línea ###
                    recognized_text = transcribe()
                else:
                ### ASR local ###
                    recognized_text = start_asr_local(app_instance) 

            
        if  GUI.mic_active: #Si el microfono estaba activo al momento de llegar
            if recognized_text:  #Si se ha detectado texto...
                ### Pasa el texto capturado a la interfaz gráfica ###
                app_instance.transcribe_GUI(text=recognized_text, speaker='user')        
                ### Enviar a LLM ###
                llm_response = process_text(recognized_text)
                ### Pasar respuesta a interfaz gráfica ###
                app_instance.transcribe_GUI(text=llm_response, speaker='assistant')
                ### Obtener correo de usuario actual ###
                current_email = app_instance.master.current_email
                if current_email and llm_response != "Hubo un error inesperado, intentelo nuevamente" and llm_response != "Hubo un error en la respuesta, intentelo nuevamente":
                    local_db.insertar_consulta(question=recognized_text, answer=llm_response, email=current_email)
                recognized_text = None  #Reiniciar despúes de procesar el texto y almacenar en la base de datos
                #Enviar a TTS
                process_response(llm_response)
            else:
                recognized_text = None
                conversation_active = False

        else:
            print("Terminando Pipeline")
            break
            

def process_text(recognized_text):
    try:
        ###Procesamiento con LLM###
        ### Seleccionar modelo online o local
        if internet_checker.internet_status:
        ### LLM Online ###
            response = ask_to_openai(recognized_text)
        else:
        ### LLM local ###
            contexto = local_db.recuperar_contexto(app_instance.master.current_email)
            response= generate_response(recognized_text, contexto, llm_model, llm_tokenizer)

        ### Verificar que la respuesta no esté vacía ###
        if not response or response == '[CLS]':
            raise ValueError("La respuesta del LLM está vacía") 
    except ValueError as ve:
        print(f"Error en la respuesta del LLM: {ve}")
        response = "Hubo un error en la respuesta, intentelo nuevamente"
    except Exception as e: 
        print(f"Ocurrió un error inesperado: {e}")
        response = "Hubo un error inesperado, intentelo nuevamente"

    return response

def process_response(llm_response):
    global app_instance
    ### Procesamiento de la respuesta de LLM con el modelo TTS ###
    ### Seleccionar modelo online o local ###
    if internet_checker.internet_status:
    ### TTS Online###
        tts_thread = threading.Thread(target=generate_audio_OpenAI, args=(llm_response, app_instance))
        tts_thread.start()
    else:
    ### TTS Local###
        generate_audio(llm_response, tts_model)

def interrupt_tts():
    global recognized_text, tts_interrupted
    recognized_text = None
    tts_interrupted = True

def start_pipeline(starter_app_instance):
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