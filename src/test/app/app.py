import tkinter as tk
from ui.styles import *
from ui.frames import *

class AutomationApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Automatización de Pruebas")
        self.root.configure(bg=font_dark_color)

        # Instanciar los frames
        self.frames = {}
        self.frames["Frame0"] = Frame0(root)
        self.frames["Frame1"] = Frame1(root)
        self.frames["Frame2"] = Frame2(root)
        
        # Mostrar el frame inicial
        self.show_frame("Frame0")

    def show_frame(self, frame_name):
        frame = self.frames[frame_name]
        frame.grid(row=0, column=0, sticky='nsew')  # Colocar el frame en la primera fila
        frame.tkraise()

def main():
    root = tk.Tk()

    # Cambiar el ícono de la ventana
    root.iconbitmap('src/test/app/assets/icons/robot.ico')

    root.geometry("1120x500")
    root.resizable(False, False)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    app = AutomationApp(root)

    root.mainloop()

if __name__ == "__main__":
    main()