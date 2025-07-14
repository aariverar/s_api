import tkinter as tk
import subprocess
import customtkinter as ctk
import tkinter.font as tkFont
import os
import sys
import threading
import queue
import re
from ui.frames import *
from ui.styles import *

def show_feature_content(scenario_outline_listbox, feature_files, feature_label, event=None):
    selected = scenario_outline_listbox.curselection()

    # Si no hay ningún elemento seleccionado
    if not selected:
        feature_label.config(text="❎No ha seleccionado \n ningún elemento")
    else:
        selected_index = scenario_outline_listbox.curselection()

        if selected_index:
            selected_item = scenario_outline_listbox.get(selected_index)
            parts = selected_item.split(" : ")
            scenario_outline_name = parts[1].strip() if parts else ""
            feature_content = feature_files.get(scenario_outline_name, "")

            start_index = feature_content.find(f"Scenario Outline: {scenario_outline_name}")
            end_index = feature_content.find("Examples", start_index)
            if start_index != -1 and end_index != -1:
                feature_content = feature_content[start_index:end_index]
            else:
                feature_content = "No se encontró la sección del escenario"
        
            popup = create_popup(f"Detalle del escenario: {scenario_outline_name}","600x300")

            frame_features = tk.Frame(popup)
            frame_features.pack(fill='both')

            scrollbar_y = tk.Scrollbar(frame_features)
            scrollbar_y.pack(side='right', fill='y')
            scrollbar_x = tk.Scrollbar(frame_features, orient='horizontal')
            scrollbar_x.pack(side='bottom', fill='x')

            text_widget = tk.Text(frame_features, wrap=tk.NONE, bg=font_gray_color, fg=font_light_color, bd=0)
            text_widget.pack(fill=tk.BOTH)

            text_widget.insert('end', feature_content)
            scrollbar_y.config(command=text_widget.yview)
            scrollbar_x.config(command=text_widget.xview)

            def highlight_words_in_brackets(text_widget, color='#00FFFF', font=mi_fuente_copyright):
                # Obtén todo el texto del widget
                text = text_widget.get("1.0", tk.END)

                # Encuentra todas las palabras dentro de los símbolos "<>"
                matches = re.finditer(r'<(.*?)>', text)

                # Resalta cada palabra encontrada
                for match in matches:
                    word = "<" + match.group(1) + ">"
                    start_index = "1.0"
                    while True:
                        start_index = text_widget.search(word, start_index, stopindex=tk.END)
                        if not start_index:
                            break
                        end_index = f"{start_index.split('.')[0]}.{int(start_index.split('.')[1])+len(word)}"
                        text_widget.tag_add(word, start_index, end_index)
                        start_index = end_index

                    # Configura el color de la palabra
                    text_widget.tag_config(word, foreground=color, font=font)
            
            # Cambiar color a palabras en brackets
            highlight_words_in_brackets(text_widget)

            start_index = "1.0"
            while True:
                start_index = text_widget.search('Scenario Outline', start_index, stopindex=tk.END)
                if not start_index:
                    break
                end_index = f"{start_index.split('.')[0]}.{int(start_index.split('.')[1])+len('Scenario Outline')}"
                text_widget.tag_add('Scenario Outline', start_index, end_index)
                start_index = end_index

            start_index = "1.0"
            while True:
                start_index = text_widget.search('Examples', start_index, stopindex=tk.END)
                if not start_index:
                    break
                end_index = f"{start_index.split('.')[0]}.{int(start_index.split('.')[1])+len('Examples')}"
                text_widget.tag_add('Examples', start_index, end_index)
                start_index = end_index

            # Configurar el color de las palabras "When", "Given", "And", "Then"
            for word in ['When', 'Given', 'And', 'Then']:
                start_index = "1.0"
                while True:
                    start_index = text_widget.search(word, start_index, stopindex=tk.END)
                    if not start_index:
                        break
                    end_index = f"{start_index.split('.')[0]}.{int(start_index.split('.')[1])+len(word)}"
                    text_widget.tag_add(word, start_index, end_index)
                    start_index = end_index

            bold_font = tkFont.Font(text_widget, text_widget.cget("font"))
            bold_font.configure(weight="bold")
            text_widget.tag_config('Scenario Outline', foreground='#00FFFF', font=bold_font)  # Cian fosforescente
            text_widget.tag_config('Examples', foreground='#00FFFF', font=bold_font)  # Cian fosforescente
            text_widget.tag_config('When', foreground='#FF00FF', font=bold_font)  # Magenta fosforescente
            text_widget.tag_config('Given', foreground='#FF00FF', font=bold_font)  # Magenta fosforescente
            text_widget.tag_config('And', foreground='#FF00FF', font=bold_font)  # Magenta fosforescente
            text_widget.tag_config('Then', foreground='#FF00FF', font=bold_font)  # Magenta fosforescente
            pass

def load_features(scenario_outline_listbox, feature_files):
    features_path = "./src/test/features"
    if os.path.exists(features_path):
        features = [f for f in os.listdir(features_path) if f.endswith(".feature")]
        scenario_outline_listbox.delete(0, tk.END)
        total_scenarios = 0
        feature_files.clear()  # Limpiar el diccionario para almacenar los contenidos de los archivos .feature
        for feature in features:
            feature_path = os.path.join(features_path, feature)
            with open(feature_path, "r", encoding='utf-8') as f:
                lines = f.readlines()
                scenario_outline_names = []
                tags = []
                for line_index, line in enumerate(lines):
                    if "Scenario Outline" in line:
                        scenario_outline_name = line.split("Scenario Outline:")[1].strip()
                        total_scenarios += 1
                        if line_index > 0 and "@" in lines[line_index - 1]:
                            tag_match = re.search(r'@(\w+)', lines[line_index - 1])
                            if tag_match:
                                tag = tag_match.group(1)
                                scenario_outline_names.append(scenario_outline_name)
                                tags.append(tag)
                if scenario_outline_names and tags:
                    for scenario_outline_name, tag in zip(scenario_outline_names, tags):
                        # Guardar el contenido del archivo .feature en el diccionario
                        feature_files[scenario_outline_name] = ''.join(lines)
                        item = f"@{tag} : {scenario_outline_name}" # item = f"{scenario_outline_name} - @{tag}"
                        scenario_outline_listbox.insert(tk.END, item)
        # Ajustar la altura de la lista al número total de escenarios
        scenario_outline_listbox.config(height=10)
    else:
        print("La carpeta de features no existe.")

def open_excel():
    excel_file = "src/test/resources/log/log.xlsx"
    if os.path.exists(excel_file):
        popup = create_popup("Archivo Excel Generado", "400x200")
        text_widget = tk.Text(popup, bg=font_gray_color, fg=font_light_color, bd=0, height=4)
        text_widget.pack(padx=10, pady=10)
        text_widget.insert(tk.END, "¡Se ha generado un Archivo Excel con los logs de la ejecución!")

        def open_excel_file():
            popup.withdraw()
            subprocess.run(f'start {excel_file}', shell=True)

        # Crea un botón "Aceptar" que oculta la ventana emergente cuando se presiona
        accept_button = ctk.CTkButton(popup, text="Abrir archivo", command=open_excel_file, fg_color=button_popup_color, width=button_popup_width, height=button_popup_height, font=mi_fuente_button, text_color= font_dark_color, corner_radius= corner_buttom_radius, cursor=cursor_buttom_type, hover_color= options_buttom_hover_color)
        accept_button.pack(pady=10)
        
    else:
        # Mostrar mensaje de que no se encontró archivo excel
        popup = create_popup("No se encontraron archivos excel","300x100")
        text_widget = tk.Text(popup, bg=font_gray_color, fg=font_light_color, bd=0)
        text_widget.pack(padx=10, pady=10)
        text_widget.insert(tk.END, "¡No se encontró archivo excel. Asegúrese de modificar el archivo browser.properties para generar archivo excel con logs!")

def open_report():
    current_path = os.getcwd()
    report_path = os.path.join(current_path,'src','test','reports')
    if os.path.exists(report_path):
        os.startfile(report_path)
    else:       
        #Crea una ventana emergente
        popup = create_popup("Error al generar reporte word", "360x180")
        text_widget = tk.Text(popup, bg=font_gray_color, fg=font_light_color, bd=0, height=4)
        text_widget.pack(padx=10, pady=10)
        text_widget.insert(tk.END, "¡No se encontró ninguna carpeta de reportes!")

        accept_button = ctk.CTkButton(popup, text="Aceptar", command=popup.withdraw, fg_color=button_popup_color, width=button_popup_width, height=button_popup_height, font=mi_fuente_button, text_color= font_dark_color, corner_radius= corner_buttom_radius, cursor=cursor_buttom_type, hover_color= options_buttom_hover_color)
        accept_button.pack(pady=10)


def open_excel_file():
    current_path = os.getcwd()
    excel_file = os.path.join(current_path, 'src/test/resources/data/excel')
    os.startfile(excel_file)

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def run_tests(self):
    selected_index = self.scenario_outline_listbox.curselection()
    tag = ""
    output_queue = queue.Queue()

    def run_command_and_get_output(tag):
        process = subprocess.Popen(["behave", "--tags", tag, "--no-capture", "--no-skipped"], stdout=subprocess.PIPE, text=True)
        output_lines = process.communicate()[0].splitlines()
        output = "\n".join(output_lines[-5:])
        output_queue.put(output)

    if selected_index:
        selected_item = self.scenario_outline_listbox.get(selected_index)
        print("Texto seleccionado:", selected_item)
        parts = selected_item.split(" : ")

        if len(parts) == 2:
            tag = parts[0]
            tag = tag.replace("@", "")
            threading.Thread(target=run_command_and_get_output, args=(tag,)).start()
            output = output_queue.get()  # Espera hasta que haya algo en la cola
        else:
            print("No se encontró un tag válido para el escenario seleccionado.")
            output = "No se encontró un tag válido para el escenario seleccionado."
    else:
        print("Por favor selecciona un escenario antes de ejecutar los tests.")
        output = "Por favor selecciona un escenario antes de ejecutar los tests."
    show_behave_results(output, tag)

def show_behave_results(output,tag):
    popup = create_popup(f"Resultados para el tag {tag}:", "450x200")
    text_widget = tk.Text(popup, bg=font_gray_color, fg=font_light_color, bd=0, height=6)
    text_widget.insert("end", output)
    text_widget.pack(padx=10, pady=10)

    accept_button = ctk.CTkButton(popup, text="Aceptar", command=popup.withdraw, fg_color=button_popup_color, width=button_popup_width, height=button_popup_height, font=mi_fuente_button, text_color= font_dark_color, corner_radius= corner_buttom_radius, cursor=cursor_buttom_type, hover_color= options_buttom_hover_color)
    accept_button.pack(pady=10)

def show_behave_popup(self):
    popup2 = create_popup("Ejecutando tests","400x220")
    text_widget = tk.Text(popup2, bg=font_gray_color, fg=font_light_color, bd=0, height=6)
    text_widget.insert("end", "Ejecutando tests...")
    text_widget.pack(padx=10, pady=10)
    popup2.update_idletasks()

    run_tests(self)
    
    popup2.withdraw()

def create_popup(title, size):
    popup = tk.Toplevel()
    popup.iconbitmap('src/test/app/assets/icons/robot.ico')
    popup.title(title)
    popup.geometry(size)
    popup.resizable(False, False)
    popup.configure(bg=font_gray_color)
    return popup