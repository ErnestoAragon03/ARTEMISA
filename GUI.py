import tkinter as tk
from tkinter import messagebox
from threading import Thread
import time
import main

mic_active = True

class Application:
    def __init__(self, root):
        #Configuración de Ventana
        self.root = root
        self.root.title("Artemisa")
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        self.root.geometry("%dx%d" % (width, height))
        
        self.pipeline_thread = None
        self.start_pipeline()
        
        ###Campo para mostrar Transcripciones###
        self.transcription_area = tk.Text(root, height=15, width=50, state=tk.DISABLED, wrap=tk.WORD)
        self.transcription_area.grid(row=1, column=10)
        ##Estilos del texto##
        self.transcription_area.tag_configure("user", foreground="blue", justify='right')   #Transcripción del usuario
        self.transcription_area.tag_configure("assistant", foreground="green", justify='left')  #Respuesta del Asistente

        ###Botón ASR###
        self.mic_button = tk.Button(root, text="Desactivar Micrófono", command= self.toggle_mic)
        self.mic_button.grid(row=6, column = 10)

        #Botón para enviar al LLM
        #self.boton_enviar_llm = tk.Button(ventana, text="Enviar", command=self.enviar_llm)
        #self.pack(pady=10)



        #Etiqueta
        #self.etiqueta = tk.Label(root, text="Ingrese su nombre: ")
        #self.etiqueta.grid(row=0,column=0)

        #Input
        #self.input_nombre = tk.Entry(root)
        #self.input_nombre.grid(row=0,column=1)

        #Botón
        #self.boton_saludo = tk.Button(root, text="Saludar", command = self.saludar)
        #self.boton_saludo.grid(row=0,column=3)

        ###Vincular el cierre de la ventana con la función on_closing (para terminar todos los procesos)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

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
        self.root.destroy()     #Cerrar la ventana

###Configuración inicial de la ventana###
if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    root.mainloop()
