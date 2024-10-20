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
        #Botón ASR
        self.mic_button = tk.Button(root, text="Desactivar Micrófono", command= self.toggle_mic)
        self.mic_button.grid(row=1, column = 4)
        
        #Campo para mostrar respuesta del LLM
        #self.transcription = tk.Text(ventana, height=5, width=60)
        #self.transcription.pack(pady=5)

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

        #Vincular el cierre de la ventana con la función on_closing (para terminar todos los procesos)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    ###Función para iniciar el pipeline###
    def start_pipeline(self):
        main.running = True
        pipeline_thread = Thread(target=main.start_pipeline)
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
    
    ###Función para manejar el cierre de ventana###
    def on_closing(self):
        self.stop_pipeline()    #Detener el pipeline si es que está activo            
        self.root.destroy()     #Cerrar la ventana

###Configuración inicial de la ventana###
if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    root.mainloop()
