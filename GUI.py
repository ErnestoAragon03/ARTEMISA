import tkinter as tk
from tkinter import messagebox
from threading import Thread
import time
import main

mic_active = True

class Application(tk.Tk):
    def __init__(self):
        #Configuración de Ventana
        super().__init__()
        self.title("Artemisa")
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.geometry("%dx%d" % (width, height))
        
        self.pipeline_thread = None
        self.start_pipeline()
        
        ###Campo para mostrar Transcripciones###
        self.transcription_area = tk.Text(self, height=15, width=50, state=tk.DISABLED, wrap=tk.WORD)
        self.transcription_area.pack(pady=10)
        ###Estilos del texto##
        self.transcription_area.tag_configure("user", foreground="blue", justify='right')   #Transcripción del usuario
        self.transcription_area.tag_configure("assigstant", foreground="green", justify='left')  #Respuesta del Asistente

        ###Frame que contiene el input de texto, botón de enviar y silenciar###
        botton_frame = tk.Frame(self)
        botton_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        ###Input de texto###
        self.text_input = tk.Entry(botton_frame, width=40)
        self.text_input.pack(side=tk.LEFT, padx=5, pady=5)
        self.text_input.bind("<Return>", self.send_text)  #Vincular la tecla Enter para enviar el texto
        ###Botón para enviar input de texto###
        send_button = tk.Button(botton_frame, text="Enviar", command=self.send_text)
        send_button.pack(side=tk.LEFT, padx=5)
        ###Botón ASR###
        self.mic_button = tk.Button(botton_frame, text="Desactivar Micrófono", command= self.toggle_mic)
        self.mic_button.pack(side=tk.LEFT, padx=5)

        ###Vincular el cierre de la ventana con la función on_closing (para terminar todos los procesos)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def send_text(self, event=None):
        user_input = self.text_input.get()  #Obtener el texto ingresado
        if user_input:      #Solo en caso el texto no esté vacío            
            self.transcribe(text=user_input, speaker="user")    #Transcripción del usuario
            self.text_input.delete(0, tk.END)   #Limpiar el input de texto

            #Obtener respuesta del LLM
            response = main.process_text(user_input)
            self.transcribe(text=response, speaker="assistant") #Transcribir la respuesta del LLM

    ###Función para iniciar el pipeline###
    def start_pipeline(self):
        main.running = True
        pipeline_thread = Thread(target= lambda: main.start_pipeline(self))
        pipeline_thread.start()
    
    ###Función para terminar el pipeline###
    def stop_pipeline(self):
        main.running = False
        if self.pipeline_thread and self.pipeline_thread.is_alive():
            self.pipeline_thread.join()  #Esperar a que termine el thread

    ###Función para manejar el presionado de botón de micrófono###
    def toggle_mic(self):
        global mic_active
        if mic_active:
            mic_active = False
            self.mic_button.config(text="Activar Microfono")
            self.stop_pipeline()
            print("muting...")
        else:
            mic_active = True
            self.mic_button.config(text="Desactivar Microfono")
            self.start_pipeline()
    
    ###Función de Transcripción###
    def transcribe(self, text, speaker):
        self.transcription_area.config(state=tk.NORMAL) #Habilita la edición del text Widget
        if speaker == 'user':
            self.transcription_area.insert(tk.END, f"{text}\n", "user")    #Transcipción de lado del usuario
        elif speaker=='assistant':
            self.transcription_area.insert(tk.END, f"{text}\n", "assistant")    #Transcipción de lado del asistente
        self.transcription_area.config(state=tk.DISABLED)
    
    ###Función para manejar el cierre de ventana###
    def on_closing(self):
        self.stop_pipeline()    #Detener el pipeline si es que está activo            
        self.destroy()     #Cerrar la ventana

###Configuración inicial de la ventana###
if __name__ == "__main__":
    #root = tk.Tk()
    app = Application()
    app.mainloop()
