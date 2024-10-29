import tkinter as tk
from tkinter import messagebox
from threading import Thread
import main
import local_db
import re
from check_internet_connection import InternetChecker

mic_active = True

class HomeScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        #Configuración de Widgets de la pantalla principal
        label = tk.Label(self, text="Home", font=("Arial", 18))
        label.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")
        
        self.pipeline_thread = None
        self.start_pipeline()

        ###Frame para contener toda el área de transcripciones###
        self.transcription_frame = tk.Frame(self)
        self.transcription_frame.grid(row = 1, column=0, pady=10, padx=20, sticky="nsew")

        ###Campo para mostrar Transcripciones###
        self.transcription_area = tk.Text(self.transcription_frame, height=30, width=150, state=tk.DISABLED, wrap="word")
        self.transcription_area.grid(row=0, column=0, sticky="nsew")

        ###Scrollbar para el área de transcripciones###
        self.scrollbar = tk.Scrollbar(self.transcription_frame, command=self.transcription_area.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.transcription_area.config(yscrollcommand=self.scrollbar.set)

        self.transcription_area.see("end") 

        ###Estilos del texto##
        self.transcription_area.tag_configure("user", foreground="blue", justify='right')   #Transcripción del usuario
        self.transcription_area.tag_configure("assigstant", foreground="green", justify='left')  #Respuesta del Asistente

        ###Frame que contiene el input de texto, botón de enviar y silenciar###
        botton_frame = tk.Frame(self)
        botton_frame.grid(row=2, column=0, pady=10, padx=20, sticky="ew")

        ###Input de texto###
        self.text_input = tk.Entry(botton_frame, width=40)
        self.text_input.grid(row=0, column=0, padx=5, pady=5)
        self.text_input.bind("<Return>", self.send_text)  #Vincular la tecla Enter para enviar el texto
        ###Botón para enviar input de texto###
        send_button = tk.Button(botton_frame, text="Enviar", command=self.send_text)
        send_button.grid(row=0, column=1, padx=5)
        ###Botón para terminar TTS ###
        end_tts_button = tk.Button(botton_frame, text="Silenciar TTS", command=self.interrupt_tts)
        end_tts_button.grid(row=0, column=2, padx=5)
        ###Botón ASR###
        self.mic_button = tk.Button(botton_frame, text="Desactivar Micrófono", command= self.toggle_mic)
        self.mic_button.grid(row=0, column=3, padx=5)

        ###Barra de navegación###
        ##Botón para Pantalla de cuenta##
        account_button = tk.Button(self, text="Cuenta", command=lambda: controller.show_frame(AccountScreen))
        account_button.grid(row=3, column=0, pady=40)

        # Configurar el peso de las filas y columnas para el diseño responsivo
        self.grid_rowconfigure(1, weight=1)  # Hacer que la fila 1 (transcripción) se expanda
        self.grid_columnconfigure(0, weight=1)  # Hacer que la columna 0 se expanda
        self.grid_rowconfigure(3, weight=1) #Hacer que la fila 3 (botón de navegación) se expanda
        

    def send_text(self, event=None):
        user_input = self.text_input.get()  #Obtener el texto ingresado
        if user_input:      #Solo en caso el texto no esté vacío            
            self.transcribe_GUI(text=user_input, speaker="user")    #Transcripción del usuario
            self.text_input.delete(0, tk.END)   #Limpiar el input de texto

            #Obtener respuesta del LLM
            response = main.process_text(user_input)
            self.transcribe_GUI(text=response, speaker="assistant") #Transcribir la respuesta del LLM
            #Guardar la consulta únicamente si la respuesta no fue un error
            if response != "Hubo un error inesperado, intentelo nuevamente" and response != "Hubo un error en la respuesta, intentelo nuevamente":
                local_db.insertar_consulta(question=user_input, answer=response, email=app.current_email)

    #Función para interrumpir al TTS
    def interrupt_tts(self):
        main.interrupt_tts()

    ###Función para iniciar el pipeline###
    def start_pipeline(self):
        main.running = True
        pipeline_thread = Thread(target= lambda: main.start_pipeline(self))
        pipeline_thread.start()
    
    ###Función para terminar el pipeline###
    def stop_pipeline(self):
        main.running = False
        main.interrupt_tts()
        if self.pipeline_thread and self.pipeline_thread.is_alive():
            self.pipeline_thread.join()  #Esperar a que termine el thread

    ###Función para manejar el presionado de botón de micrófono###
    def toggle_mic(self):
        global mic_active
        if mic_active:
            mic_active = False
            self.mic_button.config(text="Activar Microfono")
            self.stop_pipeline()
            main.recognized_text = ""
        else:
            mic_active = True
            self.mic_button.config(text="Desactivar Microfono")
            self.start_pipeline()
    
    ###Función de Transcripción###
    def transcribe_GUI(self, text, speaker):
        self.transcription_area.config(state=tk.NORMAL) #Habilita la edición del text Widget
        if speaker == 'user':
            self.transcription_area.insert(tk.END, f"{text}\n", "user")    #Transcipción de lado del usuario
        elif speaker=='assistant':
            self.transcription_area.insert(tk.END, f"{text}\n", "assistant")    #Transcipción de lado del asistente
        self.transcription_area.config(state=tk.DISABLED)
        self.transcription_area.see("end") 

    ###Función para limpiar el área de transcripciones
    def reset_transcriptions(self):
        self.transcription_area.config(state=tk.NORMAL) #Habilitar la edición del widget
        self.transcription_area.delete("1.0", tk.END)
        self.transcription_area.config(state=tk.DISABLED)
        self.text_input.delete(0, tk.END)

class AccountScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app 
        
        #Subpantallas de AccountScreen
        self.login_screen = self.init_login_screen()
        self.register_screen = self.init_register_screen()
        self.profile_screen = self.init_profile_screen()

        username, email, voice = local_db.get_last_active_session()
        #Mostrar profile si hay sesión activa, si no login
        if username:
            self.show_profile(username=username, email=email)
        else:
            self.show_login()
        
    #Pantalla de login
    def init_login_screen(self):
        frame = tk.Frame(self)
        frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)  # Asegúrate de agregar el frame a la cuadrícula

        title_label = tk.Label(frame, text="Iniciar Sesión", font=("Arial", 18))
        title_label.grid(row=0, column=0, pady=10)

        # Campos de entradas
        email_label = tk.Label(frame, text="Email Asociado")
        email_label.grid(row=1, column=0, pady=5)
        self.email_entry = tk.Entry(frame)
        self.email_entry.grid(row=2, column=0, pady=5)
        self.email_entry.bind("<Return>", self.login)  # Vincular la tecla Enter para enviar datos al login

        password_label = tk.Label(frame, text="Contraseña")
        password_label.grid(row=3, column=0, pady=5)
        self.password_entry = tk.Entry(frame, show="*")
        self.password_entry.grid(row=4, column=0, pady=5)
        self.password_entry.bind("<Return>", self.login)  # Vincular la tecla Enter para enviar datos al login
        
        # Botón para mostrar/ocultar contraseña
        show_password_btn = tk.Button(frame, text="Mostrar", command=self.toggle_password)
        show_password_btn.grid(row=5, column=0, pady=5)

        # Botones de acciones
        login_btn = tk.Button(frame, text="Iniciar sesión", command=self.login)
        login_btn.grid(row=6, column=0, pady=10)

        switch_register_btn = tk.Button(frame, text="Crear cuenta", command=self.show_register)
        switch_register_btn.grid(row=7, column=0, pady=5)

        ### Barra de navegación ###
        ## Botón para Pantalla Principal ##
        home_button = tk.Button(frame, text="Home", command=lambda: self.app.show_frame(HomeScreen))
        home_button.grid(row=8, column=0, pady=10)

        # Configurar el peso de las filas y columnas para el diseño responsivo
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.update_idletasks()  # Fuerza el redibujado

        return frame

    #Pantalla sign in
    def init_register_screen(self):
        frame = tk.Frame(self)
        frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)  # Asegúrate de agregar el frame a la cuadrícula

        title_label = tk.Label(frame, text="Crear Cuenta", font=("Arial", 18))
        title_label.grid(row=0, column=0, pady=10)

        # Campos de entrada
        email_label = tk.Label(frame, text="Email")
        email_label.grid(row=1, column=0, pady=5)
        self.register_email_entry = tk.Entry(frame)
        self.register_email_entry.grid(row=2, column=0, pady=5)
        self.register_email_entry.bind("<Return>", self.register)  # Vincular la tecla Enter para enviar datos al Register

        username_label = tk.Label(frame, text="Nombre de usuario (Este será el nombre por el que el asistente lo llamará)")
        username_label.grid(row=3, column=0, pady=5)
        self.register_username_entry = tk.Entry(frame)
        self.register_username_entry.grid(row=4, column=0, pady=5)
        self.register_username_entry.bind("<Return>", self.register)  # Vincular la tecla Enter para enviar datos al Register

        password_label = tk.Label(frame, text="Contraseña")
        password_label.grid(row=5, column=0, pady=5)
        self.register_password_entry = tk.Entry(frame, show="*")
        self.register_password_entry.grid(row=6, column=0, pady=5)
        self.register_password_entry.bind("<Return>", self.register)  # Vincular la tecla Enter para enviar datos al Register

        confirm_password_label = tk.Label(frame, text="Confirmar contraseña")
        confirm_password_label.grid(row=7, column=0, pady=5)
        self.confirm_password_entry = tk.Entry(frame, show="*")
        self.confirm_password_entry.grid(row=8, column=0, pady=5)
        self.confirm_password_entry.bind("<Return>", self.register)  # Vincular la tecla Enter para enviar datos al Register

        # Botón para mostrar/ocultar contraseña
        show_password_btn = tk.Button(frame, text="Mostrar", command=self.toggle_password)
        show_password_btn.grid(row=9, column=0, pady=5)

        # Botones de acciones
        register_btn = tk.Button(frame, text="Crear cuenta", command=self.register)
        register_btn.grid(row=10, column=0, pady=10)

        switch_login_btn = tk.Button(frame, text="Iniciar sesión", command=self.show_login)
        switch_login_btn.grid(row=11, column=0, pady=5)

        ### Barra de navegación ###
        ## Botón para Pantalla Principal ##
        home_button = tk.Button(frame, text="Home", command=lambda: self.app.show_frame(HomeScreen))
        home_button.grid(row=12, column=0, pady=10)

        # Configurar el peso de las filas y columnas para el diseño responsivo
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.update_idletasks()  # Fuerza el redibujado

        return frame
    
    ###Función de Profile (sesión ya inicidada)
    def init_profile_screen(self):
        frame = tk.Frame(self)
        frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)  # Asegúrate de agregar el frame a la cuadrícula

        title_label = tk.Label(frame, text="Perfil", font=("Arial", 18))
        title_label.grid(row=0, column=0, pady=10)

        # Mostrar nombre de usuario
        self.user_label = tk.Label(frame, text="Usuario: ")
        self.user_label.grid(row=1, column=0, pady=5)

        # Mostrar email
        self.email_label = tk.Label(frame, text="Email: ")
        self.email_label.grid(row=2, column=0, pady=5)

        # Opción Menu para mostrar voces
        self.selected_voice = tk.StringVar(self)
        self.selected_voice.set(self.app.current_voice)  # Opción default

        voices = ["Nova", "Alloy", "Echo", "Fable", "Onyx", "Shimmer"]
        self.dropdown = tk.OptionMenu(frame, self.selected_voice, *voices, command=self.app.change_voice)
        self.dropdown.grid(row=3, column=0, pady=10)

        # Botón de cierre de sesión
        logout_btn = tk.Button(frame, text="Cerrar Sesión", command=self.logout)
        logout_btn.grid(row=4, column=0, pady=10)

        # Botón de eliminación de cuenta
        delete_btn = tk.Button(frame, text="Eliminar Cuenta", command=self.confirm_deletion)
        delete_btn.grid(row=5, column=0, pady=10)

        ### Barra de navegación ###
        ## Botón para Pantalla Principal ##
        home_button = tk.Button(frame, text="Home", command=lambda: self.app.show_frame(HomeScreen))
        home_button.grid(row=6, column=0, pady=10)

        # Configurar el peso de las filas y columnas para el diseño responsivo
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.update_idletasks()  # Fuerza el redibujado

        return frame
    
    def show_login(self):
        self.clear_frame()
        self.login_screen.grid()

    def show_register(self):
        self.clear_frame()
        self.register_screen.grid()
    
    def show_profile(self, username, email):
        self.clear_frame()
        self.user_label.config(text=f"Usuario: {username}")
        self.email_label.config(text=f"Email: {email}")
        self.profile_screen.grid()

    #Función para limpiar la pantalla de subpantallas
    def clear_frame(self):
        self.login_screen.grid_forget()
        self.register_screen.grid_forget()
        self.profile_screen.grid_forget()

    #Función de mostrar/ocultar contraseña
    def toggle_password(self):
        show = "" if self.password_entry.cget("show") == "*" else "*"
        self.password_entry.config(show=show)
        self.register_password_entry.config(show=show)
        self.confirm_password_entry.config(show=show)
    
    #Función para iniciar sesión (login)
    def login(self, event=None):
        email = self.email_entry.get()
        password = self.password_entry.get()
        if email == '' or password == '':
            messagebox.showerror("Campos incompletos", "Complete todos los campos porfavor")
        elif local_db.authenticate_user(email, password):
            messagebox.showinfo("Éxito", "¡Sesión iniciada exitosamente!")
            username = local_db.get_user(email=email)
            voice = local_db.get_voice(email=email)
            self.app.current_user = username
            self.app.current_email = email
            self.app.current_voice = voice
            self.update_idletasks()  # Fuerza el redibujado
            self.show_profile(username=username, email=email)
            local_db.update_session(email)
            self.app.clearHome()
             ###Reconsturir la conversación anterior###
            self.app.reconstruct_conversation()
        else:
            messagebox.showerror("Error", "Email o contraseña incorrectos")

    ###Función para registrar usuarios (sign in)
    def register(self, event=None):
        username = self.register_username_entry.get()
        email = self.register_email_entry.get()
        password = self.register_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        if username == '' or email == '' or password == '':
            messagebox.showerror("Campos incompletos", "Complete todos los campos porfavor")
        elif self.validate_email(email):
            messagebox.showerror("Correo inválido", "Ingrese una dirección de correo válida")
        elif self.validate_password(password):
            messagebox.showerror("Contraseña inválida", 
                                 "La contraseña no es válida.\n\nDebe cumplir con los siguientes requisitos:\n"
                                 "- Al menos 8 caracteres de longitud\n"
                                 "- Al menos una mayúscula \n"
                                 "- Al menos una minúsucla \n"
                                 "- Al menos un número\n"
                                 "- Al menos un caracter especial (@, $, !, %, *, ?, &)")
        elif password != confirm_password:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
        elif local_db.add_user(username, email, password):
            messagebox.showinfo("Éxito", "¡Cuenta creada exitosamente!")
            self.app.current_user = username
            self.app.current_email = email
            self.app.current_voice = 'nova'
            self.show_profile(username=username, email=email)
        else:
            messagebox.showerror("Error", "Ya hay una cuenta asociada con ese email")

    ###Funciones de validación de campos ###
    def validate_email(self, email):
        patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"    #Expresión regular
        return re.match(patron, email) is None
    def validate_password(self, password):
        patron = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$" #Expresión regular
        return re.match(patron, password) is None
    ###Función para limpiar campos de login, register y Home###
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

    ###Función para confirmar la eliminación de cuenta###
    def confirm_deletion(self):
        # Crear ventana emergente
        popup = tk.Toplevel()
        popup.title("Eliminar cuenta")
        popup.geometry("450x350")

        #Titulo
        title_label1 = tk.Label(popup, text="Confirmar eliminación de cuenta")
        title_label1.grid(row=0, column=0, pady=10)
        title_label2 = tk.Label(popup, text="Esta acción es permanente")
        title_label2.grid(row=1, column=0, pady=5)

        #Pedir info de cuenta
        title_label3 = tk.Label(popup, text="Para confirmar que está seguro llene los siguientes campos:")
        title_label3.grid(row=2, column=0, pady=5)
        #Etiqueta y entrada para el correo
        tk.Label(popup, text="Email: ").grid(row=3, column=0, pady=5)
        email_entry = tk.Entry(popup)
        email_entry.grid(row=3, column=1, pady=5)
        
        #Etiqueta y entrada para la contraseña
        tk.Label(popup, text="Contraseña: ").grid(row=4, column=0, pady=5)
        password_entry = tk.Entry(popup, show="*")
        password_entry.grid(row=4, column=1, pady=5)

        def mini_toggle_password():
            show = "" if password_entry.cget("show") == "*" else "*"
            password_entry.config(show=show)

        # Botón para mostrar/ocultar contraseña
        show_password_btn = tk.Button(popup, text="Mostrar", command=mini_toggle_password)
        show_password_btn.grid(row=5, column=0, columnspan=2, pady=10)
        
        def submit_form():
            email = email_entry.get()
            password = password_entry.get()

            if email and password:
                if email != self.app.current_email:
                    messagebox.showerror("Email incorrecto", "El email no corresponde con la cuenta actual ¿Está seguro que esta es la cuenta que desea eliminar?")
                elif local_db.authenticate_user(email, password):
                    self.delete_account()
                    messagebox.showinfo("Cuenta Eliminada", "Cuenta eliminada exitosamente")
                    popup.destroy() #Cerrar popup
                else:
                    messagebox.showerror("Datos incorrectos", "Correo o contraseña incorrectos")
            else:
                messagebox.showerror("Campos incompletos", "Complete todos los campos porfavor")
        #Botón de confirmación
        tk.Button(popup, text="Confirmar eliminación de cuenta", command=submit_form).grid(row=6, column=0, columnspan=2, pady=10)

        # Botón de cancelación
        cancel_btn = tk.Button(popup, text="Cancelar", command=popup.destroy)
        cancel_btn.grid(row=7, column=0, columnspan=2, pady=10)

        popup.transient(app)    # Asegura que la ventana principal esté detrás del popup
        popup.grab_set          # Bloquea la ventana principal hasta que el popup se cierre
        app.wait_window(popup) # Espera a que el popup se cierre antes de seguir ejecutando

    def delete_account(self):
        local_db.delete_account(self.app.current_email)
        self.app.logout(Deleted=True)
        self.reset_fields()
        self.show_login()


class Application(tk.Tk):
    global username, email, voice, internet_checker
    ###Verificador de conexión###
    internet_checker = InternetChecker()
    def __init__(self):
        super().__init__()
        self.current_user = username
        self.current_email = email
        self.current_voice = voice
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
        
        # Configurar el peso de las filas y columnas para el diseño responsivo
        self.grid_rowconfigure(0, weight=1)  # Hacer que la fila 0 (donde se colocan los frames) se expanda
        self.grid_columnconfigure(0, weight=1)  # Hacer que la columna 0 se expanda

        self.show_frame(HomeScreen)   #Se inicia en la pantalla principal
        ###Reconsturir la conversación anterior###
        self.reconstruct_conversation() 

        ###Vincular el cierre de la ventana con la función on_closing (para terminar todos los procesos)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    ###Función para mostrar pantallas
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise() #Trae el Frame al frente

    ###Función para cerrar sesión
    def logout(self, Deleted=False):
        self.current_user = None
        self.current_email = None
        self.current_voice = 'nova'
        if not Deleted:
            messagebox.showwarning("Sesión cerrada", "Se ha cerrado la sesión, vuelve pronto.  Pasando al modo guest.")
        local_db.update_session(email=None)
        self.clearHome()
        self.show_frame(HomeScreen)

    ###Función para limpiar Home###
    def clearHome(self):
        home_screen = self.frames[HomeScreen]
        home_screen.reset_transcriptions()

    ###Función para terminar todos los procesos al cerrar la aplicación###
    def on_closing(self):
        global internet_checker
        ### Acceder a HomeScreen desde el diccionario de Frames ###
        home_screen = self.frames[HomeScreen] 
        if hasattr(home_screen, 'stop_pipeline'):
            home_screen.stop_pipeline()

        ### Detener el verificador de conexión ###
        internet_checker.stop_checking()

        ### Cerrar la ventana ###
        self.destroy()

    ###Función para cambiar la voz seleccionada###
    def change_voice(self, new_voice):
        local_db.change_voice(new_voice, self.current_email)
        self.current_voice = new_voice

    ###Función para reconstruir la conversación del usuaro###
    def reconstruct_conversation(self):
        home_screen = self.frames[HomeScreen]
        questions = local_db.get_questions(self.current_email)
        answers = local_db.get_answers(self.current_email)

        #Intercalar y transcribir conversaciones
        for question, answer in zip(questions, answers):
            home_screen.transcribe_GUI(question[0], "user")
            home_screen.transcribe_GUI(answer[0], "assistant")
        
        home_screen.transcription_area.see("end") 
###Configuración inicial de la ventana###
if __name__ == "__main__":
    ###Confirmar creación de DB al iniciar la aplicación###
    local_db.init_db()
    global username, email
    ###Obtener el nombre de usuario y correo de la última cuenta activa, si es que hay una###
    username, email, voice = local_db.get_last_active_session()

    app = Application()
    internet_checker.stop_checking()
    app.mainloop()
