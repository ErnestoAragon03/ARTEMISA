import tkinter as tk
from tkinter import messagebox

class Application:
    def __init__(self, ventana):
        #Configuración de Ventana
        self.ventana = ventana
        self.ventana.title("Artemisa")
        width = ventana.winfo_screenwidth()
        height = ventana.winfo_screenheight()
        self.ventana.geometry("%dx%d" % (width, height))
        
        #Botón ASR
        
        #Campo para mostrar respuesta del LLM
        #self.transcription = tk.Text(ventana, height=5, width=60)
        #self.transcription.pack(pady=5)

        #Botón para enviar al LLM
        #self.boton_enviar_llm = tk.Button(ventana, text="Enviar", command=self.enviar_llm)
        #self.pack(pady=10)



        #Etiqueta
        self.etiqueta = tk.Label(ventana, text="Ingrese su nombre: ")
        self.etiqueta.grid(row=0,column=0)

        #Input
        self.input_nombre = tk.Entry(ventana)
        self.input_nombre.grid(row=0,column=1)

        #Botón
        self.boton_saludo = tk.Button(ventana, text="Saludar", command = self.saludar)
        self.boton_saludo.grid(row=0,column=3)

    def saludar(self):
        nombre = self.input_nombre.get()
        if nombre:
            messagebox.showinfo("Saludo", f"¡Hola {nombre}! Bienvenido")
        else:
            messagebox.showwarning("Advertencia", f"Por favor ingrese su nombre")
        print("Hola")

if __name__ == "__main__":
    ventana = tk.Tk()
    app = Application(ventana)
    ventana.mainloop()
