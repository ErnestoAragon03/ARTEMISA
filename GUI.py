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
        self.etiqueta = tk.Label(root, text="Ingrese su nombre: ")
        self.etiqueta.grid(row=0,column=0)

        #Input
        self.input_nombre = tk.Entry(root)
        self.input_nombre.grid(row=0,column=1)

        #Botón
        self.boton_saludo = tk.Button(root, text="Saludar", command = self.saludar)
        self.boton_saludo.grid(row=0,column=3)

    def saludar(self):
        nombre = self.input_nombre.get()
        if nombre:
            messagebox.showinfo("Saludo", f"¡Hola {nombre}! Bienvenido")
        else:
            messagebox.showwarning("Advertencia", f"Por favor ingrese su nombre")
        print("Hola")
        

    def toggle_mic(self):
        global mic_active
        if mic_active:
            mic_active = False
            main.running = False
            self.mic_button.config(text="Activar Microfono")
            #Detener el thread
            if pipeline_thread and pipeline_thread.is_alive():
                ###AQUÍ ESTÁ EL ERROR
                pipeline_thread.join()  #Esperar a que termine el thread
                print("muting...")
        else:
            mic_active = True
            main.running = True
            self.mic_button.config(text="Desactivar Microfono")
            pipeline_thread = Thread(target=main.start_pipeline)
            pipeline_thread.start()
            #Thread(target=start_asr).start()
            

if __name__ == "__main__":
    root = tk.Tk()
    main.running = True
    pipeline_thread = Thread(target=main.start_pipeline)
    pipeline_thread.start()
    app = Application(root)
    root.mainloop()
