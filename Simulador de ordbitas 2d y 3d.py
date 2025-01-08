# Bienvenidos a nuestro codigo para el funcionamiento del programa de "SIMULACION DE ORBITAS EN 2D Y EN 3D"
# El codigo tendra varios comentarios para indicar que hace cada funcion (Documentación)

# Librerias a utilizar para su correcto funcionamiento
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
import tkinter as tk
from tkinter import messagebox, filedialog
import csv
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import random
import subprocess

# Variables globales para el almacenamiento 
planetas = []
puntos = []
trayectorias = []

# Función para cargar planetas desde un archivo CSV
def cargar_planetas_desde_csv():
    global planetas
    # Abrir un cuadro de diálogo para seleccionar el archivo
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        try:
            with open(file_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                planetas.clear()    # Limpiar la lista de planetas antes de cargar nuevos datos
                for row in reader:
                    try:
                        # Extraer datos de cada fila del archivo CSV
                        nombre = row['Planeta']
                        radio = float(row['Radio'])
                        velocidad_angular = float(row['Velocidad Angular'])
                        escala = float(row['Escala'])
                        # Agregar los datos a la lista de planetas
                        planetas.append({"Planeta": nombre, "Radio": radio, "Velocidad Angular": velocidad_angular, "Escala": escala})
                    except ValueError:
                        # En caso de que ocurra un eror, mostara este mensaje
                        messagebox.showerror("Error", f"Datos inválidos en el archivo CSV: {row}")
                        continue
                messagebox.showinfo("Éxito", "Planetas cargados exitosamente desde el archivo CSV.")
                regenerar_planetas()    # Actualizar la visualización con los nuevos datos
        except Exception as e:
            # En caso de que ocurra un eror, mostara este mensaje
            messagebox.showerror("Error", f"No se pudo leer el archivo CSV: {e}")

# Función para guardar los datos de planetas en un archivo CSV
def guardar_planetas_en_csv():
    # Abre un cuadro de diálogo para seleccionar la ubicación y el nombre del archivo
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        try:
            with open(file_path, mode='w', newline='') as csvfile:
                fieldnames = ['Planeta', 'Radio', 'Velocidad Angular', 'Escala']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for planeta in planetas:
                    writer.writerow(planeta)    # Guarda los datos de cada planeta y marcara en un cuadro de exito si se guardaron los datos
                messagebox.showinfo("Éxito", "Planetas guardados exitosamente en el archivo CSV.")
        except Exception as e:
            # En caso de que ocurra un eror, mostara este mensaje
            messagebox.showerror("Error", f"No se pudo guardar el archivo CSV: {e}")

# Configurar el gráfico principal
def configurar_grafico():
    global ax, info_frame
    # Limpiar la figura actual para eliminar basura, en caso de que tenga
    fig.clear()
    fig.patch.set_facecolor("#2f2f2f")  # Establecer el color de fondo a negro
    # Configuración para modo 3D
    if modo_3d.get():
        ax = fig.add_subplot(111, projection="3d")
        ax.set_xlim([-200, 200])
        ax.set_ylim([-200, 200])
        ax.set_zlim([-200, 200])
        ax.set_title("Simulación 3D de Órbitas Planetarias", color="white")
        if 'info_frame' in globals():
            info_frame.place_forget()  # Ocultar el cuadro de información en modo 3D para no tener errores
    else:
        # Configuración para modo 2D
        ax = fig.add_subplot(111)
        ax.set_xlim([-200, 200])
        ax.set_ylim([-200, 200])
        ax.set_title("Simulación 2D de Órbitas Planetarias", color="white")

    ax.set_facecolor("#2f2f2f") # Color de fondo del gráfico a negro

    if not modo_3d.get():
        for spine in ax.spines.values():
            spine.set_color("white")    # Color de las etiquetas de los ejes
    # Mantiene la mayoria de parametros en color blanco
    ax.tick_params(colors="white")  
    ax.yaxis.label.set_color("white")
    ax.xaxis.label.set_color("white")
    if modo_3d.get():
        ax.zaxis.label.set_color("white")
    # Mantiene en color gris las orbitas
    ax.grid(color="gray", linestyle="--")
    # Genera un circulo de color amarillo llamado sol
    ax.scatter(0, 0, color="yellow", s=200, label="Sol")

    canvas.draw()

def rotacion_3d(punto, angulo, eje='z'):
    """Aplica rotación en 3D a un punto."""
    x, y, z = punto
    angulo_rad = np.radians(angulo)
    if eje == 'z':
        matriz_rotacion = np.array([
            [np.cos(angulo_rad), -np.sin(angulo_rad), 0],
            [np.sin(angulo_rad), np.cos(angulo_rad), 0],
            [0, 0, 1]
        ])
    nuevo_punto = matriz_rotacion @ np.array([x, y, z])
    return nuevo_punto

def rotacion_2d(punto, angulo):
    """Aplica rotación en 2D a un punto."""
    x, y = punto
    angulo_rad = np.radians(angulo)
    matriz_rotacion = np.array([
        [np.cos(angulo_rad), -np.sin(angulo_rad)],
        [np.sin(angulo_rad), np.cos(angulo_rad)]
    ])
    nuevo_punto = matriz_rotacion @ np.array([x, y])
    return nuevo_punto


def escalado_2d(punto, escala_x, escala_y):
    """Aplica escalado en 2D a un punto."""
    x, y = punto
    matriz_escalado = np.array([
        [escala_x, 0],
        [0, escala_y]
    ])
    nuevo_punto = matriz_escalado @ np.array([x, y])
    return nuevo_punto

def escalado_3d(punto, escala_x, escala_y, escala_z):
    """Aplica escalado en 3D a un punto."""
    x, y, z = punto
    matriz_escalado = np.array([
        [escala_x, 0, 0],
        [0, escala_y, 0],
        [0, 0, escala_z]
    ])
    nuevo_punto = matriz_escalado @ np.array([x, y, z])
    return nuevo_punto

# Actualizar la lista de planetas y sus trayectorias, en caso de que se cargue un nuevo archivo o se agregue un nuevo planeta para evitar errores
def regenerar_planetas():
    global puntos, trayectorias, planetas, ax
    ax.cla()  # Limpiar el eje actual
    configurar_grafico()  # Configurar el gráfico nuevamente
    puntos.clear()
    trayectorias.clear()

    for planeta in planetas:
        a = planeta["Radio"]  # Semieje mayor
        b = planeta["Radio"] * 0.8  # Semieje menor (ajustable)
        escala = planeta["Escala"]
        angulos = np.linspace(0, 2 * np.pi, 360)
        x_orbita = a * np.cos(angulos)
        y_orbita = b * np.sin(angulos)
        z_orbita = np.zeros_like(x_orbita)  # En 3D, órbitas están en el plano XY

        # Aplicar escalado
        if modo_3d.get():
            puntos_escalados = [escalado_3d((x, y, z), escala, escala, escala) for x, y, z in zip(x_orbita, y_orbita, z_orbita)]
            x_orbita, y_orbita, z_orbita = zip(*puntos_escalados)
            trayectorias.append(ax.plot(x_orbita, y_orbita, z_orbita, linestyle="--", color="white")[0])
            puntos.append(ax.scatter([], [], [], label=planeta["Planeta"]))
        else:
            puntos_escalados = [escalado_2d((x, y), escala, escala) for x, y in zip(x_orbita, y_orbita)]
            x_orbita, y_orbita = zip(*puntos_escalados)
            trayectorias.append(ax.plot(x_orbita, y_orbita, linestyle="--", color="white")[0])
            puntos.append(ax.plot([], [], "o", label=planeta["Planeta"])[0])

    ax.legend()  # Mostrar leyenda con nombres de los planetas
    canvas.draw()  # Redibujar el lienzo


# Actualizar posiciones de planetas en órbitas elípticas
def actualizar(frame):
    global puntos, planetas
    if actualizar_event.get():
        regenerar_planetas()
        actualizar_event.set(False)

    # Actualizar la posición de cada planeta
    for i, planeta in enumerate(planetas):
        angulo_actual = (planeta["Velocidad Angular"] * frame) % 360

        # Calcular la posición inicial en la órbita
        x = planeta["Radio"] * np.cos(np.radians(angulo_actual))
        y = planeta["Radio"] * 0.8 * np.sin(np.radians(angulo_actual))
        z = 0  # Inicialmente en el plano XY

        # Aplicar escalado
        if modo_3d.get():
            x, y, z = escalado_3d((x, y, z), planeta["Escala"], planeta["Escala"], planeta["Escala"])
        else:
            x, y = escalado_2d((x, y), planeta["Escala"], planeta["Escala"])

        # Actualizar posiciones en los gráficos
        if modo_3d.get():
            puntos[i]._offsets3d = ([x], [y], [z])
        else:
            puntos[i].set_data([x], [y])

    canvas.draw()  # Redibujar el gráfico
    return puntos

# Ajustar los límites de visualización del gráfico según el zoom
def ajustar_limites(valor=None):
    global ax, slider_zoom
    zoom = slider_zoom.get()
    ax.set_xlim([-10 * zoom, 10 * zoom])
    ax.set_ylim([-10 * zoom, 10 * zoom])
    if modo_3d.get():
        ax.set_zlim([-10 * zoom, 10 * zoom])
    fig.canvas.draw_idle()

# Agrega planetas de forma manual y aleatoria
def agregar_planetas():
    global agregar_mas_planetas, contador_planetas

    def solicitar_cantidad():
        nonlocal ventana_solicitar
        try:
            cantidad = int(entry_cantidad.get())
            aleatorios = var_aleatorios.get()  # Obtener el estado de la casilla de aleatorios
            if cantidad <= 0:
                raise ValueError
            ventana_solicitar.destroy()
            mostrar_ventana_agregar(cantidad, aleatorios)
        except ValueError:
            messagebox.showerror("Error", "Por favor, introduce un número válido.")

    # Crear ventana para solicitar la cantidad de planetas
    ventana_solicitar = tk.Toplevel(root)
    ventana_solicitar.title("Cantidad de Planetas")
    ventana_solicitar.geometry("300x200") #Resolucion de la ventana
    # Infomracion que se le solicita al usuario
    tk.Label(ventana_solicitar, text="¿Cuántos planetas deseas agregar?", font=("Unbounded ExtraBold", 9)).pack(pady=10)
    entry_cantidad = tk.Entry(ventana_solicitar, font=("Arial", 12))
    entry_cantidad.pack(pady=5)

    # Casilla para elegir si los datos serán aleatorios
    var_aleatorios = tk.BooleanVar(value=False)
    tk.Checkbutton(
        ventana_solicitar,
        text="¿Generar datos aleatorios?",
        variable=var_aleatorios,
        font=("Unbounded ExtraBold", 9)
    ).pack(pady=10)
    #Boton de aceptar
    tk.Button(ventana_solicitar, text="Aceptar", command=solicitar_cantidad, font=("Martian Mono Condensed ExtraBold", 10), bg="#4f4f4f", fg="white").pack(pady=10)

    ventana_solicitar.mainloop()

# Funcion que permite ver la ventana emergente para agregar los datos de los planetas
def mostrar_ventana_agregar(cantidad, aleatorios):
    global contador_planetas
    contador_planetas = 0
    if aleatorios:
        # Generar todos los datos aleatorios de una vez
        for _ in range(cantidad):
            nombre = f"Planeta_{contador_planetas + 1}"
            radio = round(random.uniform(10, 500), 2)
            velocidad = round(random.uniform(0.1, 30), 2)
            escala = round(random.uniform(1, 3), 2)
            planetas.append({"Planeta": nombre, "Radio": radio, "Velocidad Angular": velocidad, "Escala": escala})
            contador_planetas += 1
        regenerar_planetas()  
        messagebox.showinfo("Éxito", f"Se han agregado {cantidad} planetas con datos aleatorios exitosamente.")
        return  
    # Guarda los datos ingresados
    def guardar_datos():
        try:
            # Recuperar datos ingresados y agregarlos a la lista de planetas
            nombre = entry_nombre.get()
            radio = float(entry_radio.get())
            velocidad = float(entry_velocidad.get())
            escala = float(entry_escala.get())
            planetas.append({"Planeta": nombre, "Radio": radio, "Velocidad Angular": velocidad, "Escala": escala})
            regenerar_planetas()    # Actualizar el gráfico
        except ValueError:
            # En caso de tener un error, marca esto
            messagebox.showerror("Error", "Datos inválidos. Por favor, revisa tus entradas.")
    # Pasa al siguiente planeta en caso de que haya más de un plnaeta indicado para agregar
    def siguiente_planeta():
        nonlocal ventana_agregar
        guardar_datos()
        ventana_agregar.destroy()
        mostrar_ventana_agregar(cantidad - 1, aleatorios)

    def terminar_agregar():
        guardar_datos()  #
        ventana_agregar.destroy()
        messagebox.showinfo("Éxito", "Todos los planetas se han agregado exitosamente.") 
    # Opciones de la ventana, que indican lo de agregar planeta y sus repsectivos datos solicitados
    # Recibe datos e imprime datos
    ventana_agregar = tk.Toplevel(root)
    ventana_agregar.title(f"Agregar Planeta ({contador_planetas + 1}/{cantidad})")
    ventana_agregar.geometry("400x400")
    tk.Label(ventana_agregar, text="Nombre del Planeta:", font=("Unbounded ExtraBold", 9)).pack(pady=5)
    entry_nombre = tk.Entry(ventana_agregar, font=("Arial", 9))
    entry_nombre.pack(pady=5)

    tk.Label(ventana_agregar, text="Radio Orbital:", font=("Unbounded ExtraBold", 9)).pack(pady=5)
    entry_radio = tk.Entry(ventana_agregar, font=("Arial", 9))
    entry_radio.pack(pady=5)

    tk.Label(ventana_agregar, text="Velocidad Angular:", font=("Unbounded ExtraBold", 9)).pack(pady=5)
    entry_velocidad = tk.Entry(ventana_agregar, font=("Arial", 9))
    entry_velocidad.pack(pady=5)

    tk.Label(ventana_agregar, text="Factor de Escala:", font=("Unbounded ExtraBold", 9)).pack(pady=5)
    entry_escala = tk.Entry(ventana_agregar, font=("Arial", 9))
    entry_escala.pack(pady=5)

    if cantidad > 1:
        tk.Button(ventana_agregar, text="Siguiente", command=siguiente_planeta, font=("Martian Mono Condensed ExtraBold", 10), bg="#4f4f4f", fg="white").pack(pady=10)
        tk.Button(ventana_agregar, text="Terminar", command=terminar_agregar, font=("Martian Mono Condensed ExtraBold", 10), bg="#81d4fa", fg="white").pack(pady=10)
    else:
        tk.Button(ventana_agregar, text="Guardar", command=lambda: [guardar_datos(), terminar_agregar()], font=("Martian Mono Condensed ExtraBold", 10), bg="#4f4f4f", fg="white").pack(pady=10)
# Elimina un planeta por su nombre
def eliminar_planeta():
    global planetas, puntos, trayectorias
    # Confirma si se elimino o no
    def confirmar_eliminacion():
        nombre = entry_nombre.get()
        for planeta in planetas:
            if planeta["Planeta"].lower() == nombre.lower():
                planetas.remove(planeta)
                messagebox.showinfo("Éxito", f"Planeta '{nombre}' eliminado exitosamente.")
                regenerar_planetas()  
                canvas.draw()  # Forzar redibujado del gráfico para evitar errores de actualizacion 
                ventana_eliminar.destroy()
                return
        messagebox.showerror("Error", f"No se encontró un planeta con el nombre '{nombre}'.")
    #Ventana de informacion 
    ventana_eliminar = tk.Toplevel(root)
    ventana_eliminar.title("Eliminar Planeta")
    ventana_eliminar.geometry("300x150")

    tk.Label(ventana_eliminar, text="Nombre del Planeta a Eliminar:", font=("Unbounded ExtraBold", 10)).pack(pady=10)
    entry_nombre = tk.Entry(ventana_eliminar, font=("Arial", 12))
    entry_nombre.pack(pady=10)

    tk.Button(ventana_eliminar, text="Eliminar", command=confirmar_eliminacion, font=("Martian Mono Condensed ExtraBold", 9), bg="#4f4f4f", fg="white").pack(pady=10)

def on_hover(event):
    global panel_derecho, info_frame, info_label, planetas
    if not modo_3d.get() and event.inaxes == ax:
        x_event, y_event = event.xdata, event.ydata
        min_distance = float('inf')
        closest_planet = None

        # Verificar cercanía del cursor a las órbitas elípticas
        for planeta in planetas:
            a = planeta["Radio"]  # Semieje mayor
            b = a * 0.8  # Semieje menor (ajustable)
            escala = planeta["Escala"]

            # Escalar las coordenadas del cursor
            x_scaled = x_event / (a * escala)
            y_scaled = y_event / (b * escala)

            # Evaluar la ecuación de la elipse
            distancia_a_orbita = abs(x_scaled**2 + y_scaled**2 - 1)

            if distancia_a_orbita < 0.05:  # Umbral de cercanía a la órbita (ajustable)
                if distancia_a_orbita < min_distance:
                    min_distance = distancia_a_orbita
                    closest_planet = planeta

        if closest_planet:
            if 'info_frame' not in globals():
                info_frame = tk.Frame(panel_derecho, bg="#ffffff", relief="solid", bd=1)
                info_label = tk.Label(info_frame, text="", font=("Arial", 12), bg="#ffffff", justify="left")
                info_label.pack(padx=5, pady=5)
            info_frame.place(relx=0.75, rely=0.85, anchor="center")
            info_label.config(text=f"Nombre: {closest_planet['Planeta']}\n"
                                   f"Velocidad: {closest_planet['Velocidad Angular']}\n"
                                   f"Radio: {closest_planet['Radio']}")
        else:
            if 'info_frame' in globals():
                info_frame.place_forget()
    else:
        if 'info_frame' in globals():
            info_frame.place_forget()


# Funcion para cerrar el progrrama
def salir_con_video():
    """Muestra un video antes de salir del programa."""
    root.destroy()  # Cierra la ventana principal

# Inicio de interfaz grafica del programa
def iniciar_interfaz():
    global planetas, puntos, trayectorias, ax, fig, canvas, actualizar_event, modo_3d, slider_zoom, root, panel_derecho, info_frame, info_label

    root = tk.Tk()
    root.title("Simulación de Órbitas Planetarias") # Titulo
    root.geometry("1500x900")                       # resolucion
    root.configure(bg="#e0f7fa")                    # Color 
    

    actualizar_event = tk.BooleanVar(value=False)
    modo_3d = tk.BooleanVar(value=False)

    # Panel izquierdo con sus botones y texto
    panel_izquierdo = tk.Frame(root, bg="#81d4fa", width=200)
    panel_izquierdo.pack(side="left", fill="y")
    #Texto
    tk.Label(panel_izquierdo, text="ORBITAS PLANETARIAS", font=("Unbounded ExtraBold", 20, "bold"), bg="#81d4fa", fg="white").pack(pady=20)
    tk.Label(panel_izquierdo, text=" ", font=("Arial", 16, "bold"), bg="#81d4fa", fg="white").pack(pady=5)
    tk.Label(panel_izquierdo, text="---------OPCIONES----------", font=("Unbounded ExtraBold", 16, "bold"), bg="#81d4fa", fg="white").pack(pady=5)
    #Botones
    tk.Button(panel_izquierdo, text="      Cargar CSV      ", command=cargar_planetas_desde_csv, bg="#0288d1", fg="white", font=("EXCRATCH", 9, "bold")).pack(pady=9)
    tk.Button(panel_izquierdo, text="      Guardar CSV    ", command=guardar_planetas_en_csv, bg="#0288d1", fg="white", font=("EXCRATCH", 9)).pack(pady=9)
    tk.Button(panel_izquierdo, text=" Agregar Planetas", command=agregar_planetas, bg="#0288d1", fg="white", font=("EXCRATCH", 9)).pack(pady=9)
    tk.Button(panel_izquierdo, text=" Eliminar Planeta", command=eliminar_planeta, bg="#0288d1", fg="white", font=("EXCRATCH", 9)).pack(pady=9)
    def cambiar_modo():
        modo_3d.set(not modo_3d.get())
        configurar_grafico()
        regenerar_planetas()
        cambiar_modo_boton.config(
            text="Cambiar a 3D" if not modo_3d.get() else "Cambiar a 2D"
        )

    cambiar_modo_boton = tk.Button(panel_izquierdo, text="      Cambiar a 3D     ", command=cambiar_modo, bg="#0288d1", fg="white", font=("EXCRATCH", 9))
    cambiar_modo_boton.pack(pady=10)
    #Texto
    tk.Label(panel_izquierdo, text="-------------------------------", font=("Unbounded ExtraBold", 16, "bold"), bg="#81d4fa", fg="white").pack(pady=5)
    tk.Label(panel_izquierdo, text="Proyecto elaborado por:", font=("Martian Mono Condensed ExtraBold", 10), bg="#81d4fa", fg="white").pack(pady=5)
    tk.Label(panel_izquierdo, text="Lizeth Montserrat Cerón Samperio", font=("Martian Mono Condensed ExtraBold", 10), bg="#81d4fa", fg="white").pack(pady=5)
    tk.Label(panel_izquierdo, text="Angel Abraham Higuera Pineda", font=("Martian Mono Condensed ExtraBold", 10), bg="#81d4fa", fg="white").pack(pady=5)
    tk.Label(panel_izquierdo, text="Abad Rey Lorenzo Silva", font=("Martian Mono Condensed ExtraBold", 10), bg="#81d4fa", fg="white").pack(pady=5)
    tk.Label(panel_izquierdo, text="Mia Paulina Moya Rivera", font=("Martian Mono Condensed ExtraBold", 10), bg="#81d4fa", fg="white").pack(pady=5)
    tk.Label(panel_izquierdo, text="-------------------------------", font=("Unbounded ExtraBold", 16, "bold"), bg="#81d4fa", fg="white").pack(pady=5)
    #Boton de salir
    tk.Button(
        panel_izquierdo,
        text="Salir",
        command=salir_con_video,
        bg="#0288d1",
        fg="white",
        font=("EXCRATCH", 9)
    ).pack(pady=10)


    # Panel derecho para el zoom
    panel_derecho = tk.Frame(root, bg="#e1f5fe")
    panel_derecho.pack(side="right", fill="both", expand=True)

    fig = plt.figure(figsize=(6, 6))
    canvas = FigureCanvasTkAgg(fig, master=panel_derecho)
    canvas.get_tk_widget().pack(side="left", fill="both", expand=True)

    ax = fig.add_subplot(111)
    configurar_grafico()
    regenerar_planetas()

    # Zoom 
    zoom_frame = tk.Frame(panel_derecho, bg="#e1f5fe")
    zoom_frame.pack(side="right", fill="y", padx=10)

    tk.Label(zoom_frame, text="Acercar", font=("EXCRATCH", 9), bg="#e1f5fe").pack()

    # LargO
    slider_zoom = tk.Scale(
        zoom_frame,
        from_=1,
        to=1000.0,
        resolution=0.1,
        orient="vertical",
        command=ajustar_limites,
        bg="#e1f5fe",
        fg="black",
        highlightbackground="#0288d1",
        length=800, 
        font=("EXCRATCH", 10)  
    )
    slider_zoom.set(1.0)
    slider_zoom.pack()

    tk.Label(zoom_frame, text="Alejar", font=("EXCRATCH", 9), bg="#e1f5fe").pack()

    info_frame = tk.Frame(panel_derecho, bg="#ffffff", relief="solid", bd=1)
    info_label = tk.Label(info_frame, text="", font=("Arial", 12), bg="#ffffff", justify="left")
    info_label.pack(padx=5, pady=5)
    info_frame.place_forget()


    anim = animation.FuncAnimation(fig, actualizar, frames=360, interval=50, blit=False)

    canvas.mpl_connect("motion_notify_event", on_hover)
    root.mainloop()
# inicia la interfaz 
def main():
    iniciar_interfaz()

if __name__ == "__main__":
    main()
