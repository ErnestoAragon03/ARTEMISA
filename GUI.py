import tkinter as tk
from tkinter import messagebox
from threading import Thread
import main
import local_db

mic_active = True

class HomeScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        #Configuración de Widgets de la pantalla principal
        label = tk.Label(self, text="Home", font=("Arial", 18))
        label.pack(pady=10)
        
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
        botton_frame.pack(fill=tk.X, pady=10)

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

        ###Barra de navegación###
        ##Botón para Pantalla de cuenta##
        account_button = tk.Button(self, text="Cuenta", command=lambda: controller.show_frame(AccountScreen))
        account_button.pack(side=tk.BOTTOM, pady=10)

        ##Botón para Pantalla Principal
        self.home_button = tk.Button(self, text="Home", state="disabled", ) #Deshabilitado porque ya estamos en esta pantalla
        self.home_button.pack(side=tk.BOTTOM, pady=10)
        

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

class AccountScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app 
        
        #Subpantallas de AccountScreen
        self.login_screen = self.init_login_screen()
        self.register_screen = self.init_register_screen()
        self.profile_screen = self.init_profile_screen()

        #Por el momento se muestra Login por default
        username, email = local_db.get_last_active_session()
        if username:
            self.show_profile(username=username, email=email)
        else:
            self.show_login()
        
    #Pantalla de login
    def init_login_screen(self):
        frame = tk.Frame(self)
        title_label = tk.Label(frame, text="Iniciar Sesión")
        title_label.pack(pady=10)
        
        #Campos de entradas
        email_label = tk.Label(frame, text = "Email Asociado")
        email_label.pack(pady=5)
        self.email_entry = tk.Entry(frame)
        self.email_entry.pack(pady=5)

        password_label = tk.Label(frame, text="Contraseña")
        password_label.pack(pady=5)
        self.password_entry = tk.Entry(frame, show="*")
        self.password_entry.pack(pady=5)

        # Botón para mostrar/ocultar contraseña
        show_password_btn = tk.Button(frame, text="Mostrar", command=self.toggle_password)
        show_password_btn.pack()

        # Botones de acciones
        login_btn = tk.Button(frame, text="Iniciar sesión", command=self.login)
        login_btn.pack(pady=10)

        switch_register_btn = tk.Button(frame, text="Crear cuenta", command=self.show_register)
        switch_register_btn.pack()

        ###Barra de navegación###   
        ##Botón para Pantalla Principal##
        home_button = tk.Button(frame, text="Home", command=lambda: self.app.show_frame(HomeScreen))
        home_button.pack(side=tk.BOTTOM, pady=10)

        return frame

    #Pantalla sign in
    def init_register_screen(self):
        frame = tk.Frame(self)
        title_label = tk.Label(frame, text="Crear Cuenta")
        title_label.pack(pady=10)

        # Campos de entrada
        email_label = tk.Label(frame, text="Email")
        email_label.pack(pady=5)
        self.register_email_entry = tk.Entry(frame)
        self.register_email_entry.pack(pady=5)

        username_label = tk.Label(frame, text="Nombre de usuario (Este será el nombre por el que el asistente lo llamará)")
        username_label.pack(pady=5)
        self.register_username_entry = tk.Entry(frame)
        self.register_username_entry.pack(pady=5)

        password_label = tk.Label(frame, text="Contraseña")
        password_label.pack(pady=5)
        self.register_password_entry = tk.Entry(frame, show="*")
        self.register_password_entry.pack(pady=5)

        confirm_password_label = tk.Label(frame, text="Confirmar contraseña")
        confirm_password_label.pack(pady=5)
        self.confirm_password_entry = tk.Entry(frame, show="*")
        self.confirm_password_entry.pack(pady=5)

        # Botón para mostrar/ocultar contraseña
        show_password_btn = tk.Button(frame, text="Mostrar", command=self.toggle_password)
        show_password_btn.pack()

        # Botones de acciones
        register_btn = tk.Button(frame, text="Crear cuenta", command=self.register)
        register_btn.pack(pady=10)

        switch_login_btn = tk.Button(frame, text="Iniciar sesión", command=self.show_login)
        switch_login_btn.pack()

        ###Barra de navegación###   
        ##Botón para Pantalla Principal##
        home_button = tk.Button(frame, text="Home", command=lambda: self.app.show_frame(HomeScreen))
        home_button.pack(side=tk.BOTTOM, pady=10)

        return frame
    
    ###Función de Profile (sesión ya inicidada)
    def init_profile_screen(self):
        frame = tk.Frame(self)
        title_label = tk.Label(frame, text="Perfil")
        title_label.pack(pady=10)

        #Mostrar nombre de usuario
        self.user_label = tk.Label(frame, text="Usuario:")
        self.user_label.pack(pady=5)

        #Botón de cierre de sesión
        logout_btn = tk.Button(frame, text="Cerrar Sesión", command=self.logout)
        logout_btn.pack(pady=10)

        ###Barra de navegación###   
        ##Botón para Pantalla Principal##
        home_button = tk.Button(frame, text="Home", command=lambda: self.app.show_frame(HomeScreen))
        home_button.pack(side=tk.BOTTOM, pady=10)
        return frame
    
    def show_login(self):
        self.clear_frame()
        self.login_screen.pack()

    def show_register(self):
        self.clear_frame()
        self.register_screen.pack()
    
    def show_profile(self, username, email):
        self.clear_frame()
        self.user_label.config(text=f"Usuario: {username}")
        self.profile_screen.pack()

    #Función para limpiar la pantalla de subpantallas
    def clear_frame(self):
        self.login_screen.pack_forget()
        self.register_screen.pack_forget()
        self.profile_screen.pack_forget()

    #Función de mostrar/ocultar contraseña
    def toggle_password(self):
        show = "" if self.password_entry.cget("show") == "*" else "*"
        self.password_entry.config(show=show)
        self.register_password_entry.config(show=show)
        self.confirm_password_entry.config(show=show)
    
    #Función para iniciar sesión (login)
    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        if local_db.authenticate_user(email, password):
            messagebox.showinfo("Éxito", "¡Sesión iniciada exitosamente!")
            username = local_db.get_user(email=email)
            self.app.current_user = username
            self.app.current_email = email
            self.show_profile(username=username, email=email)
            local_db.update_session(email)
        else:
            messagebox.showerror("Error", "Email o contraseña incorrectos")

    ###Función para registrar usuarios (sign in)
    def register(self):
        username = self.register_username_entry.get()
        email = self.register_email_entry.get()
        password = self.register_password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if password != confirm_password:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
        elif local_db.add_user(username, email, password):
            messagebox.showinfo("Éxito", "¡Cuenta creada exitosamente!")
            self.app.current_user = username
            self.app.current_email = email
            self.show_profile(username=username, email=email)
        else:
            messagebox.showerror("Error", "Ya hay una cuenta asociada con ese email")

    ###Función para limpiar campos de login y register###
    def reset_fields(self):
        self.email_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.register_username_entry.delete(0, tk.END)
        self.register_email_entry.delete(0, tk.END)
        self.register_password_entry.delete(0, tk.END)
        self.confirm_password_entry.delete(0, tk.END)
        if self.password_entry.cget("show") == "":
            self.toggle_password()
        
    ###Función para Cerrar Sesión
    def logout(self):
        self.app.logout()
        self.reset_fields()
        self.show_login()


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.current_email = None
        ###Configuración de Ventana###
        self.title("Artemisa")
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.geometry("%dx%d" % (width, height))

        ###Diccionario para almacenar pantallas (Frames)###
        self.frames = {}
        ###Crear Frames para cada pantalla ###
        for Screen in (HomeScreen, AccountScreen):
            frame = Screen(self, self)
            self.frames[Screen] = frame
            #Los frames se apilan
            frame.grid(row=0, column=0, sticky="nsew")  

        self.show_frame(HomeScreen)   #Se inicia en la pantalla principal

        ###Vincular el cierre de la ventana con la función on_closing (para terminar todos los procesos)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    ###Función para mostrar pantallas
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise() #Trae el Frame al frente

    ###Función para cerrar sesión
    def logout(self):
        self.current_user = None
        self.current_email = None
        messagebox.showerror("Sesión cerrada", "Se ha cerrado la sesión, vuelve pronto.  Pasando al modo guest.")
        local_db.update_session(email=None)
        self.show_frame(HomeScreen)

    ###Función para terminar todos los procesos al cerrar la aplicación###
    def on_closing(self):
        home_screen = self.frames[HomeScreen] #Acceder a HomeScreen desde el diccionario de Frames
        if hasattr(home_screen, 'stop_pipeline'):
            print("Deteniendo Pipeline actual")
            home_screen.stop_pipeline()
        self.destroy()     #Cerrar la ventana
    

###Configuración inicial de la ventana###
if __name__ == "__main__":
    ###Confirmar creación de DB al iniciar la aplicación###
    local_db.init_db()
    ###Obtener el nombre de usuario y correo de la última cuenta activa, si es que hay una###
    username, email = local_db.get_last_active_session()
    if username:
        print(f"Sesión ini  ciada en la cuenta {username}")
    else:
        print("Modo guest")

    app = Application()
    app.mainloop()
