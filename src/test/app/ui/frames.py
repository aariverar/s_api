import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
from ui.styles import *
from logic.utilities import *
from logic.variables import *

class Frame0(tk.Frame):
    def __init__(self, root):
        super().__init__(root, bg=font_gray_color)
        self.grid(row=0, column=0, padx=0, pady=0, sticky='nsew')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Cargar logo de mibanco
        image_mibanco = Image.open("./src/test/app/assets/images/logo_mibanco.png")

        #Cambiar el tamaño de la imagen
        new_size_mibanco = (120, 60)  # Nuevo tamaño en píxeles
        image_mibanco = image_mibanco.resize(new_size_mibanco, Image.LANCZOS)

        # Convertir la imagen de PIL a una imagen de Tkinter
        tk_image_mibanco = ImageTk.PhotoImage(image_mibanco)

        # Crear un Label con la imagen de mibanco
        image_label_mibanco = tk.Label(self, image=tk_image_mibanco, bd=0, fg = font_gray_color, bg=font_gray_color)
        image_label_mibanco.image_mibanco = tk_image_mibanco
        image_label_mibanco.grid(row=0, column=0, padx=10, pady=0, sticky="we")
        
        self.principal_title = tk.Label(self, text="Framework de Automatización 💻", font=mi_fuente_tittle, bg=font_gray_color,fg=font_light_color , anchor="center")
        self.principal_title.grid(row=0, column=1, padx=(10,0), pady=0,sticky="w")

class Frame2(tk.Frame):
    def __init__(self, root):
        super().__init__(root, bg=font_gray_color)
        self.grid(row=2, column=0, padx=0, pady=0, sticky='nsew')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.copyright_text = tk.Label(self, text="© 2024 Mi Banco - Automatización y Performance", font=mi_fuente_copyright, bg=font_gray_color,fg=font_light_color , anchor="center")
        self.copyright_text.grid(row=0, column=0, padx=10, pady=20,sticky='ew')


class Frame1(tk.Frame):
    def __init__(self, root):
        super().__init__(root, bg=font_dark_color)
        self.grid(row=1, column=0, padx=0, pady=0, sticky='nsew')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        #dentro de frame1
        self.frame2 = tk.Frame(self, bg=font_dark_color)
        self.frame2.grid(row=0, column=0, padx=(0,0), pady=0, sticky='nswe')
        self.frame2.columnconfigure(0, weight=1)
        
        self.frame3 = tk.Frame(self, bg=font_gray_color)
        self.frame3.grid(row=0, column=1, padx=(0,10), pady=10, sticky='nswe')
        self.frame3.columnconfigure(0, weight=1)
        self.frame3.columnconfigure(1, weight=1)
        self.frame3.rowconfigure(0, weight=1)

        self.frame4 = tk.Frame(self.frame3, bg=font_gray_color)
        self.frame4.grid(row=0, column=0, padx=(10, 0), pady=10, sticky='nswe')
        self.frame4.columnconfigure(0, weight=1)
        
        self.frame5 = tk.Frame(self.frame3, bg=font_dark_color)
        self.frame5.grid(row=0, column=1, padx=(10,10), pady=10, sticky='wens')
        self.frame5.columnconfigure(0, weight=1)

        self.frame6 = tk.Frame(self.frame4, bg=font_gray_color)
        self.frame6.grid(row=0, column=0, padx=0, pady=0, sticky='nswe')

        # Cargar la imagen
        image = Image.open("src/test/app/assets/images/logo_app.jpg")
        
        #Cambiar el tamaño de la imagen
        new_size = (150, 150)  # Nuevo tamaño en píxeles
        image = image.resize(new_size, Image.LANCZOS)

        # Convertir la imagen de PIL a una imagen de Tkinter
        tk_image = ImageTk.PhotoImage(image)

        # Crear un Label con la imagen
        image_label = tk.Label(self.frame2, image=tk_image, fg = font_gray_color, bd=0, bg=font_dark_color)
        image_label.image = tk_image
        image_label.grid(row=2, column=0, padx=10, pady=(30,10), sticky='nswe')

        # Botón para cargar la lista de features
        self.load_features_button_frame = tk.Frame(self.frame2, bg= font_dark_color)
        self.load_features_button_frame.grid(row=0, column=0, padx=20, pady=(20,10), sticky='nsew')

        self.load_features_button_label = tk.Label(self.load_features_button_frame, text="Cargar Escenarios: ", bg=font_dark_color, fg=font_light_color, font=mi_fuente_bold)
        self.load_features_button_label.pack(side=tk.LEFT)

        self.load_features_button = ctk.CTkButton(self.load_features_button_frame, text="▶️Iniciar", command=lambda: load_features(self.scenario_outline_listbox, self.feature_files), fg_color=options_buttom_color, width=ctk_buttom_width, height=ctk_buttom_height, font=mi_fuente_button, text_color= font_dark_color, corner_radius= corner_buttom_radius, cursor=cursor_buttom_type, hover_color= options_buttom_hover_color)
        self.load_features_button.pack(side=tk.RIGHT)

        # Botón para abrir excel y modificar data
        self.open_excel_button = ctk.CTkButton(self.frame2, text="🖋️Modificar data", command=open_excel_file,border_color=border_color, fg_color=font_dark_color, border_width=ctk_border_width, width=ctk_buttom_width, height=ctk_buttom_height, font=mi_fuente_button, text_color= font_light_color, corner_radius= corner_buttom_radius, border_spacing=border_buttom_spacing, hover_color = font_gray_color, cursor=cursor_buttom_type )
        self.open_excel_button.grid(row=1, column=0, padx=20, pady=10, sticky='nsew')

        # Lista de Scenario Outlines
        self.frame_listbox = tk.Frame(self.frame4, bd=10, bg=font_dark_color)
        self.frame_listbox.grid(row=1, column=0, padx=0, pady=10)

        # Crear las Scrollbars
        self.y_scrollbar = tk.Scrollbar(self.frame_listbox, orient='vertical')
        self.y_scrollbar.pack(side='right', fill='y')

        self.x_scrollbar = tk.Scrollbar(self.frame_listbox, orient='horizontal')
        self.x_scrollbar.pack(side='bottom', fill='x')

        # Crear el Listbox con las Scrollbars
        self.scenario_outline_listbox = tk.Listbox(self.frame_listbox, width=35, height=2, selectbackground=options_buttom_color, bg=font_dark_color, fg=font_light_color, borderwidth=0, font=mi_fuente_little, cursor=cursor_buttom_type, highlightbackground=highlightbackground, highlightthickness=0, selectforeground=font_light_color, selectborderwidth=0, relief=tk.FLAT, activestyle='none', yscrollcommand=self.y_scrollbar.set, xscrollcommand=self.x_scrollbar.set)
        self.scenario_outline_listbox.pack(padx=0, pady=10, side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configurar las Scrollbars para que se desplacen con el Listbox
        self.y_scrollbar.config(command=self.scenario_outline_listbox.yview)
        self.x_scrollbar.config(command=self.scenario_outline_listbox.xview)

        # Label para mostrar el contenido del archivo .feature
        self.feature_label = tk.Label(self.frame6, text="👇 Selecciona un caso \n para ver el detalle", fg = font_green_color, bg= font_gray_color, font=mi_fuente_bold)
        self.feature_label.grid(row=0, column=0, padx=10, pady=10)

        self.show_feature_content_buttom = ctk.CTkButton(self.frame6, text="🔍 Ver Detalle", command=lambda: show_feature_content(self.scenario_outline_listbox, self.feature_files, self.feature_label), fg_color=font_dark_color, width=ctk_buttom_width, height=ctk_buttom_height, font=mi_fuente_button, text_color= font_light_color, corner_radius= corner_buttom_radius, hover_color = options_buttom_hover_color, cursor=cursor_buttom_type)
        self.show_feature_content_buttom.grid(row=0, column=1, padx=20, pady=10, sticky='ew')
        
        # Botón para ejecutar los tests
        self.run_tests_button = ctk.CTkButton(self.frame5, text="🚀 Ejecutar Tests", command=lambda: show_behave_popup(self), border_color=border_color, fg_color=font_dark_color, border_width=ctk_border_width, width=ctk_buttom_width, height=ctk_buttom_height, font=mi_fuente_button, text_color= font_light_color, corner_radius= corner_buttom_radius, border_spacing=border_buttom_spacing, hover_color = font_gray_color, cursor=cursor_buttom_type)
        self.run_tests_button.grid(row=0, column=0, padx=20, pady=(30,20), sticky='nsew')
        
        # Botón para generar reporte web
        self.open_report_button = ctk.CTkButton(self.frame5, text="📊 Reporte", command=open_report,border_color=border_color, fg_color=font_dark_color, border_width=ctk_border_width, width=ctk_buttom_width, height=ctk_buttom_height, font=mi_fuente_button, text_color= font_light_color, corner_radius= corner_buttom_radius, border_spacing=border_buttom_spacing, hover_color = font_gray_color, cursor=cursor_buttom_type)
        self.open_report_button.grid(row=2, column=0, padx=20, pady=20, sticky='nsew')


        #Botón para abrir archivo excel con logs
        self.open_excel_buttom = ctk.CTkButton(self.frame5, text="📈 Abrir Logs", command=open_excel, border_color=border_color, fg_color=font_dark_color, border_width=ctk_border_width, width=ctk_buttom_width, height=ctk_buttom_height, font=mi_fuente_button, text_color= font_light_color, corner_radius= corner_buttom_radius, border_spacing=border_buttom_spacing, hover_color = font_gray_color, cursor=cursor_buttom_type)
        self.open_excel_buttom.grid(row=4, column=0, padx=20, pady=(20,30), sticky='nsew')

        self.feature_files = {}
  