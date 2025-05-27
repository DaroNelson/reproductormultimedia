from tkinter import *
from tkinter import filedialog
import pygame
import os

# Inicializar pygame
pygame.mixer.init()

# Colores
co1 = "#ffffff"  # blanco
co2 = "#3C1DC6"  # violeta
co3 = "#333333"  # negro

# Funciones
def cargar_cancion():
    file = filedialog.askopenfilename(filetypes=[("Archivos MP3", "*.mp3")])
    if file:
        pygame.mixer.music.load(file)
        label_nombre.config(text=os.path.basename(file))

def reproducir():
    pygame.mixer.music.play()

def pausar():
    pygame.mixer.music.pause()

def continuar():
    pygame.mixer.music.unpause()

def detener():
    pygame.mixer.music.stop()
    label_nombre.config(text="Ninguna canción cargada")

# Ventana principal
window = Tk()
window.title("Reproductor Multimedia")
window.geometry('554x256')
window.configure(background=co1)
window.resizable(width=FALSE, height=FALSE)

# Si querés evitar el error del icono, comentá esta línea si sigue fallando
try:
    window.iconbitmap("C:\\Users\\Usuario\\Pictures\\iconos\\icono.ico")
except Exception as e:
    print("No se pudo cargar el ícono de la ventana:", e)

# Frame principal
frame = Frame(window, bg=co1)
frame.pack(pady=20)

label_nombre = Label(frame, text="Ninguna canción cargada", bg=co1, fg=co3, font=("Arial", 12))
label_nombre.pack(pady=10)

# Frame de controles
frame_controles = Frame(window, bg=co1)
frame_controles.pack()

# === Carga de íconos ===
try:
    img_play = PhotoImage(file=r"C:/Users/Usuario/Pictures/iconos/play.png")
    img_pause = PhotoImage(file=r"C:/Users/Usuario/Pictures/iconos/pause.png")
    img_continue = PhotoImage(file=r"C:/Users/Usuario/Pictures/iconos/continue.png")
    img_stop = PhotoImage(file=r"C:/Users/Usuario/Pictures/iconos/stop.png")
except Exception as e:
    print("Error cargando íconos:", e)
    exit()

# Botones con íconos
btn_play = Button(frame_controles, image=img_play, bd=0, command=reproducir)
btn_play.grid(row=0, column=0, padx=10)

btn_pause = Button(frame_controles, image=img_pause, bd=0, command=pausar)
btn_pause.grid(row=0, column=1, padx=10)

btn_unpause = Button(frame_controles, image=img_continue, bd=0, command=continuar)
btn_unpause.grid(row=0, column=2, padx=10)

btn_stop = Button(frame_controles, image=img_stop, bd=0, command=detener)
btn_stop.grid(row=0, column=3, padx=10)

# Botón cargar
btn_cargar = Button(window, text="Cargar Canción", bg=co2, fg=co1, font=("Arial", 10), command=cargar_cancion)
btn_cargar.pack(pady=10)

# Ejecutar ventana
window.mainloop()


