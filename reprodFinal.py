import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
import os
import threading
import time

# Inicializar pygame
pygame.mixer.init()

# Crear la ventana
ventana = tk.Tk()
ventana.title("Reproductor de Música")
ventana.geometry("600x550")  # Un poco más alta para acomodar mejor los controles
ventana.configure(bg="#1e1e1e")  # Fondo más oscuro para un look más moderno
ventana.resizable(False, False)  # Hacer que el tamaño sea fijo
ventana.iconbitmap("")  # Asegúrate de tener un icono en el mismo directorio       


# Variables globales
playlist = []
current_index = 0
playing = False
paused = False  # Nueva variable para manejar el estado de pausa
duracion_total = 1.0
actualizando_seekbar = False
detener_hilo = False
dragging_seekbar = False
current_loaded_song = None
start_time = 0  # Tiempo de inicio para calcular posición actual
pause_time = 0  # Tiempo cuando se pausó

# Funciones Auxiliares
def format_time(seconds):
    """Formatea segundos a una cadena de tiempo MM:SS."""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

# Funciones
def cargar_canciones():
    global playlist
    archivos = filedialog.askopenfilenames(filetypes=[("Archivos de audio", "*.mp3")])
    if archivos:
        for archivo in archivos:
            if archivo not in playlist:
                playlist.append(archivo)
        
        lista_canciones.delete(0, tk.END)
        for archivo in playlist:
            lista_canciones.insert(tk.END, os.path.basename(archivo))

def reproducir():
    global playing, paused, duracion_total, actualizando_seekbar, current_index, detener_hilo, current_loaded_song, start_time, pause_time
    
    if not playlist:
        return

    detener_hilo = True
    time.sleep(0.05)
    
    pygame.mixer.music.stop()
    
    if playlist[current_index] != current_loaded_song:
        try:
            pygame.mixer.music.load(playlist[current_index])
            current_loaded_song = playlist[current_index]
        except pygame.error as e:
            messagebox.showerror("Error de Carga", f"No se pudo cargar el archivo: {os.path.basename(playlist[current_index])}\n{e}")
            if playlist:
                playlist.pop(current_index)
                if current_index >= len(playlist): 
                    current_index = 0
                if playlist:
                    reproducir()
                else:
                    detener_reproduccion_final()
            return

    pygame.mixer.music.play()
    start_time = time.time()  # Marcar el tiempo de inicio
    pause_time = 0  # Resetear tiempo de pausa
    playing = True
    paused = False
    
    try:
        duracion_total = pygame.mixer.Sound(playlist[current_index]).get_length()
    except pygame.error as e:
        messagebox.showerror("Error de Duración", f"No se pudo obtener la duración del archivo: {os.path.basename(playlist[current_index])}\n{e}")
        duracion_total = 1.0
    
    tiempo_total_label.config(text=format_time(duracion_total))
    seekbar.set(0)
    tiempo_actual_label.config(text="00:00")

    actualizando_seekbar = True
    actualizar_seekbar()
    
    lista_canciones.select_clear(0, tk.END)
    lista_canciones.select_set(current_index)
    lista_canciones.activate(current_index)

def reproducir_desde_posicion(posicion_segundos):
    """Reproduce la canción desde una posición específica en segundos."""
    global playing, paused, start_time, current_loaded_song, pause_time
    
    if not playlist:
        return
    
    pygame.mixer.music.stop()
    
    try:
        # Recargar y reproducir desde la posición específica
        pygame.mixer.music.load(playlist[current_index])
        pygame.mixer.music.play(start=posicion_segundos)
        current_loaded_song = playlist[current_index]
        start_time = time.time() - posicion_segundos  # Ajustar el tiempo de inicio
        pause_time = 0  # Resetear tiempo de pausa
        playing = True
        paused = False
        
        # Actualizar la interfaz
        porcentaje = (posicion_segundos / duracion_total * 100) if duracion_total > 0 else 0
        seekbar.set(porcentaje)
        tiempo_actual_label.config(text=format_time(posicion_segundos))
        
    except pygame.error as e:
        messagebox.showerror("Error", f"No se pudo reproducir desde la posición solicitada: {e}")

def pausar():
    global playing, paused, pause_time
    if playing and not paused:
        pygame.mixer.music.pause()
        pause_time = get_current_position()  # Guardar la posición actual
        playing = False
        paused = True

def continuar():
    global playing, paused, start_time
    if paused and not playing:
        pygame.mixer.music.unpause()
        # Ajustar el tiempo de inicio para mantener la sincronización
        start_time = time.time() - pause_time
        playing = True
        paused = False

def siguiente_cancion():
    global current_index
    if current_index < len(playlist) - 1:
        current_index += 1
        reproducir()
    else:
        detener_reproduccion_final()

def anterior_cancion():
    global current_index
    if current_index > 0:
        current_index -= 1
        reproducir()
    else:
        reproducir()

def detener_reproduccion_final():
    global playing, paused, detener_hilo, current_loaded_song, pause_time
    playing = False
    paused = False  # Resetear estado de pausa
    pause_time = 0  # Resetear tiempo de pausa
    detener_hilo = True
    pygame.mixer.music.stop()
    seekbar.set(0)
    tiempo_actual_label.config(text="00:00")
    tiempo_total_label.config(text="00:00")
    current_loaded_song = None

def get_current_position():
    """Calcula la posición actual de la canción basada en el tiempo transcurrido."""
    global start_time, pause_time, paused
    if paused:
        return pause_time  # Si está pausado, devolver la posición donde se pausó
    elif playing and start_time > 0:
        elapsed = time.time() - start_time
        return min(elapsed, duracion_total)
    return 0

def actualizar_seekbar():
    """Actualiza la barra de progreso y el tiempo actual."""
    def actualizar():
        global actualizando_seekbar, playing, paused, detener_hilo, dragging_seekbar
        
        while actualizando_seekbar and not detener_hilo:
            if not playing and not paused:
                time.sleep(0.1)
                continue
            
            # Obtener posición actual
            tiempo_actual = get_current_position()
            
            # Verificar si la canción terminó (solo si está reproduciendo, no pausada)
            if playing and not paused and tiempo_actual >= duracion_total:
                ventana.after(0, siguiente_cancion)
                break
            
            # Actualizar interfaz solo si no se está arrastrando el seekbar
            if not dragging_seekbar:
                porcentaje = (tiempo_actual / duracion_total * 100) if duracion_total > 0 else 0
                ventana.after(0, lambda p=porcentaje, t=tiempo_actual: actualizar_interfaz(p, t))
            
            time.sleep(0.1)
        
        actualizando_seekbar = False
        detener_hilo = False

    def actualizar_interfaz(porcentaje, tiempo_actual):
        """Actualiza la interfaz en el hilo principal."""
        if not dragging_seekbar:
            seekbar.set(porcentaje)
            tiempo_actual_label.config(text=format_time(tiempo_actual))

    global detener_hilo
    detener_hilo = False
    threading.Thread(target=actualizar, daemon=True).start()

def mover_seek(val):
    """Mueve la reproducción a la posición indicada por el seekbar."""
    # Esta función ahora solo se usa para clics directos, no para arrastrar
    global dragging_seekbar
    
    if not playlist or dragging_seekbar:
        return
    
    nuevo_tiempo_seek = float(val) / 100 * duracion_total
    reproducir_desde_posicion(nuevo_tiempo_seek)

# Eventos para el seekbar de arrastre
def on_seekbar_click(event):
    """Maneja los clics directos en el seekbar (no arrastre)."""
    if not playlist:
        return
    
    # Calcular posición basada en dónde se hizo clic
    widget_width = seekbar.winfo_width()
    if widget_width > 0:
        x = event.x
        porcentaje = max(0, min(100, (x / widget_width) * 100))
        nuevo_tiempo_seek = porcentaje / 100 * duracion_total
        reproducir_desde_posicion(nuevo_tiempo_seek)

def on_seekbar_drag_start(event):
    """Función que se llama cuando el usuario empieza a arrastrar el seekbar."""
    global dragging_seekbar
    dragging_seekbar = True

def on_seekbar_drag_end(event):
    """Función que se llama cuando el usuario suelta el seekbar."""
    global dragging_seekbar
    
    if not playlist:
        dragging_seekbar = False
        return
    
    # Obtener la posición donde soltó el usuario
    nuevo_tiempo_seek = float(seekbar.get()) / 100 * duracion_total
    dragging_seekbar = False
    
    # Reproducir desde la nueva posición
    reproducir_desde_posicion(nuevo_tiempo_seek)

def on_seekbar_drag(event):
    """Se ejecuta mientras se arrastra el seekbar - solo actualiza la vista previa."""
    if dragging_seekbar and duracion_total > 0:
        # Calcular tiempo basado en la posición del mouse
        widget_width = seekbar.winfo_width()
        if widget_width > 0:
            x = event.x
            porcentaje = max(0, min(100, (x / widget_width) * 100))
            seekbar.set(porcentaje)  # Actualizar visualmente la barra
            tiempo_preview = porcentaje / 100 * duracion_total
            tiempo_actual_label.config(text=format_time(tiempo_preview))

def actualizar_volumen(val):
    pygame.mixer.music.set_volume(float(val))

def reproducir_seleccionada():
    global current_index, paused
    seleccion = lista_canciones.curselection()
    if seleccion:
        new_index = seleccion[0]
        if new_index != current_index:
            current_index = new_index
            reproducir()
        elif not playing and not paused:
            reproducir()
        elif paused:  # Si está pausada, continuar
            continuar()

class HoverButton(tk.Button):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.defaultBackground = self.cget("background")
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        if self['state'] != 'disabled':
            self['background'] = '#3e3e3e'

    def on_leave(self, e):
        if self['state'] != 'disabled':
            self['background'] = self.defaultBackground

# --- Widgets UI ---
etiqueta_pistas = tk.Label(ventana, text="Pistas", bg="#23272e", fg="#f8f8f2", font=("Segoe UI", 13, "bold"))
etiqueta_pistas.pack(pady=(15, 0))

# Frame para la lista de canciones y el scrollbar
frame_lista = tk.Frame(ventana, bg="#23272e")
frame_lista.pack(pady=8)

scrollbar = tk.Scrollbar(frame_lista, orient="vertical")
scrollbar.pack(side="right", fill="y")

lista_canciones = tk.Listbox(frame_lista, bg="#181a1b", fg="#f8f8f2", width=60, height=15, 
                            selectbackground="#6272a4", selectforeground="#181a1b", 
                            font=("Segoe UI", 10), yscrollcommand=scrollbar.set, borderwidth=0, highlightthickness=0)
lista_canciones.pack(side="left", fill="both", expand=True)
scrollbar.config(command=lista_canciones.yview)
lista_canciones.bind("<Double-Button-1>", lambda e: reproducir_seleccionada())

# Frame de botones
frame_botones = tk.Frame(ventana, bg="#23272e")
frame_botones.pack(pady=10)

btn_prev = HoverButton(frame_botones, text="⏮", command=anterior_cancion, width=5, bg="#44475a", fg="#f8f8f2", font=("Segoe UI", 11, "bold"), borderwidth=0)
btn_prev.grid(row=0, column=0, padx=7)

btn_play = HoverButton(frame_botones, text="▶", command=reproducir, width=5, bg="#50fa7b", fg="#181a1b", font=("Segoe UI", 11, "bold"), borderwidth=0)
btn_play.grid(row=0, column=1, padx=7)

btn_pause = HoverButton(frame_botones, text="⏸", command=pausar, width=5, bg="#ffb86c", fg="#181a1b", font=("Segoe UI", 11, "bold"), borderwidth=0)
btn_pause.grid(row=0, column=2, padx=7)

btn_continue = HoverButton(frame_botones, text="⏯", command=continuar, width=5, bg="#8be9fd", fg="#181a1b", font=("Segoe UI", 11, "bold"), borderwidth=0)
btn_continue.grid(row=0, column=3, padx=7)

btn_next = HoverButton(frame_botones, text="⏭", command=siguiente_cancion, width=5, bg="#44475a", fg="#f8f8f2", font=("Segoe UI", 11, "bold"), borderwidth=0)
btn_next.grid(row=0, column=4, padx=7)

# Frame inferior para tiempos y volumen
frame_inferior = tk.Frame(ventana, bg="#23272e")
frame_inferior.pack(fill="x", side="bottom", pady=10)

# Frame de tiempos
frame_tiempos = tk.Frame(frame_inferior, bg="#23272e")
frame_tiempos.pack(side="left", padx=20)

tiempo_actual_label = tk.Label(frame_tiempos, text="00:00", bg="#23272e", fg="#f8f8f2", font=("Segoe UI", 10, "bold"))
tiempo_actual_label.pack(side="left", padx=10)

tiempo_total_label = tk.Label(frame_tiempos, text="00:00", bg="#23272e", fg="#f8f8f2", font=("Segoe UI", 10, "bold"))
tiempo_total_label.pack(side="right", padx=10)

# Control de volumen
frame_volumen = tk.Frame(frame_inferior, bg="#23272e")
frame_volumen.pack(side="right", padx=20)

etiqueta_volumen = tk.Label(frame_volumen, text="Volumen", bg="#23272e", fg="#f8f8f2", font=("Segoe UI", 9))
etiqueta_volumen.pack(side="left", padx=(0, 5))

volumen = tk.Scale(frame_volumen, from_=0, to=1, resolution=0.1, orient="horizontal", 
                    command=actualizar_volumen, length=100, bg="#23272e", fg="#f8f8f2", 
                    highlightbackground="#23272e", troughcolor="#44475a", sliderrelief='flat', showvalue=False)
volumen.set(0.5)
volumen.pack(side="left")

# Barra de progreso
etiqueta_progreso = tk.Label(ventana, text="Progreso", bg="#23272e", fg="#f8f8f2", font=("Segoe UI", 9))
etiqueta_progreso.pack(pady=(10, 0))

seekbar = tk.Scale(ventana, from_=0, to=100, orient="horizontal", length=420, 
                    bg="#23272e", fg="#f8f8f2", 
                    highlightbackground="#23272e", troughcolor="#44475a", showvalue=False, borderwidth=0, sliderrelief='flat')
seekbar.pack(pady=(0, 10))

# Eventos del seekbar
seekbar.bind("<Button-1>", on_seekbar_click)
seekbar.bind("<ButtonPress-1>", on_seekbar_drag_start)
seekbar.bind("<ButtonRelease-1>", on_seekbar_drag_end)
seekbar.bind("<B1-Motion>", on_seekbar_drag)

# Botón cargar canciones destacado
btn_cargar = HoverButton(ventana, text="🎵  Cargar canciones", command=cargar_canciones, bg="#bd93f9", fg="#181a1b", font=("Segoe UI", 11, "bold"), width=20, borderwidth=0)
btn_cargar.pack(pady=15)

ventana.mainloop()