import tkinter as tk

from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from tkinter import messagebox

from lexico import resultado_lexema, analizar_texto

import subprocess
import io
import sys
import threading
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.token import Token
import re
from pygments.lexers import PythonLexer
from pygments import token as Token
from pygments import lex



archivo_actual = None
scrolling_up = False
scrolling_down = False

PALABRAS_CLAVE = ["if", "else", "while", "for", "def", "class", "import", "from", "return", "True", "False", "None"]
NOMBRES_VARIABLES = ["x", "y", "z", "contador", "resultado", "temporal"]

def abrir_archivo():
    global archivo_actual
    archivo = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt")])
    if archivo:
        archivo_actual = archivo
        with open(archivo, "r") as f:
            editor.delete(1.0, tk.END)
            editor.insert(tk.END, f.read())
        actualizar_numeracion_lineas()

def guardar_archivo():
    global archivo_actual
    if archivo_actual:
        with open(archivo_actual, "w") as f:
            f.write(editor.get(1.0, tk.END))
    else:
        guardar_como()

def guardar_como():
    global archivo_actual
    archivo = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivos de texto", "*.txt")])
    if archivo:
        archivo_actual = archivo
        with open(archivo, "w") as f:
            f.write(editor.get(1.0, tk.END))

def nuevo_archivo():
    global archivo_actual

    # Verificar si hay cambios no guardados
    if hay_cambios_no_guardados():
        confirmacion = tk.messagebox.askyesnocancel("Guardar cambios", "¿Desea guardar los cambios antes de abrir un nuevo archivo?")
        
        if confirmacion is None:  # Si se presiona Cancelar, salir sin abrir un nuevo archivo
            return
        elif confirmacion:  # Si se elige Guardar, llamar a la función de guardar
            guardar_archivo()
    
    # Abrir un nuevo archivo en blanco
    archivo_actual = None
    editor.delete(1.0, tk.END)
    actualizar_numeracion_lineas()

def tu_analizador_lexico(codigo):
    lexer = PythonLexer()
    return list(lex(codigo, lexer))

import lexico  # Importar tu propio analizador léxico

def resaltar_sintaxis(event=None):
    codigo = editor.get("1.0", "end-1c")  # Obtener todo el código del editor
    editor.tag_remove("resaltado", "1.0", "end")  # Eliminar cualquier resaltado previo

    # Analizar el código con tu propio analizador léxico
    tokens, errores_lexicos = lexico.analizar_texto(codigo)

    # Definir los colores para cada tipo de token
    colores = {
        'ENTERO': 'orange',
        'REAL': 'orange',
        'PALABRA_RESERVADA': 'blue',
        'OPERADOR_ARITMETICO': 'red',
        'OPERADOR_RELACIONAL': 'red',
        'OPERADOR_LOGICO': 'purple',
        'SIMBOLO': 'pink',
        'ASIGNACION': 'green',
        'IDENTIFICADOR': 'black',
        'COMENTARIO_UNILINEA': 'red',
    }

    for token_info in tokens:
        # Obtener el tipo de token, la línea y la columna
        token_info = token_info.split()
        tipo_token = token_info[-3]  # El antepenúltimo elemento es el tipo de token
        linea = int(token_info[1])  # La segunda palabra es la línea
        columna = int(token_info[3][:-1])  # La cuarta palabra es la columna, eliminar el último carácter ':'
        valor = token_info[-1]  # El último elemento es el valor del token

        # Verificar si el contenido del token está presente en el código fuente
        if valor in codigo:
            inicio = f"{linea}.{columna}"  # Inicio del token
            fin = f"{linea}.{columna + len(valor)}"  # Fin del token
            # Resaltar el token con el color correspondiente
            editor.tag_add(str(tipo_token), inicio, fin)
            editor.tag_configure(str(tipo_token), foreground=colores.get(tipo_token, 'black'))  # Obtener el color o usar negro

    # Manejar errores léxicos (si es necesario)
 
   


def compilar():
    global resultado_lexema

    # Limpiar las pestañas de lexema y errores léxicos
    limpiar_pestana_lexico()
    limpiar_pestana_errores_lexicos()

    codigo = editor.get("1.0", "end-1c")  # Obtener todo el código del editor
    resultado_lexico, errores_lexicos = analizar_texto(codigo)  # Obtener los resultados del análisis léxico

    # Actualizar el contenido del widget de texto en la pestaña "Errores léxicos"
    actualizar_errores_lexicos(errores_lexicos)
    
    # Iterar sobre las pestañas del notebook para encontrar el área "Lexico"
    for index, area in enumerate(areas_editor):
        if area == "Lexico":
            # Obtener el frame correspondiente al área "Lexico"
            frame_lexico = pestanas_editor.winfo_children()[index]
            # Obtener todos los widgets dentro del frame
            widgets_frame = frame_lexico.winfo_children()
            # Buscar el widget Text dentro de los widgets del frame
            widget_text_lexico = None
            for widget in widgets_frame:
                if isinstance(widget, tk.Text):
                    widget_text_lexico = widget
                    break
            # Verificar si se encontró el widget Text
            if widget_text_lexico is not None:
                # Limpiar el contenido existente en el widget Text
                widget_text_lexico.delete(1.0, tk.END)
                # Insertar el resultado del análisis léxico en el widget Text
                for token_info in resultado_lexico:
                    widget_text_lexico.insert(tk.END, token_info + "\n")  # Insertar cada token en una línea separada
            else:
                print("No se encontró el widget Text dentro del área 'Lexico'")
            break  # Salir del bucle una vez que se encuentra el área "Lexico"

def limpiar_pestana_lexico():
    for area in areas_editor:
        if area == "Lexico":
            frame_lexico = pestanas_editor.winfo_children()[areas_editor.index(area)]
            widget_text_lexico = None
            for widget in frame_lexico.winfo_children():
                if isinstance(widget, tk.Text):
                    widget_text_lexico = widget
                    break
            if widget_text_lexico is not None:
                widget_text_lexico.delete(1.0, tk.END)
            else:
                print("No se encontró el widget Text dentro del área 'Lexico'")

def limpiar_pestana_errores_lexicos():
    widget_texto = widgets_errores["Errores lexicos"]
    widget_texto.config(state=tk.NORMAL)  # Habilita la edición del widget
    widget_texto.delete(1.0, tk.END)  # Borra el contenido existente
    widget_texto.config(state=tk.DISABLED)  # Deshabilita la edición del widget

def salir():
    root.quit()

def compilar_y_depurar():
    # Agrega aquí el código para compilar y depurar
    pass
def actualizar_errores_lexicos(errores_lexicos):
    widget_texto = widgets_errores["Errores lexicos"]
    widget_texto.config(state=tk.NORMAL)  # Habilita la edición del widget
    widget_texto.delete(1.0, tk.END)  # Borra el contenido existente
    for error_info in errores_lexicos:
        widget_texto.insert(tk.END, error_info + "\n")  # Inserta cada error en una línea separada
    widget_texto.config(state=tk.DISABLED)  # Deshabilita la edición del widget


def hay_cambios_no_guardados():
    contenido_editor = editor.get(1.0, tk.END).strip()

    if archivo_actual:  # Verificar si hay un archivo actual
        with open(archivo_actual, "r") as f:
            contenido_archivo = f.read().strip()

        return contenido_editor != contenido_archivo
    else:
        return bool(contenido_editor)

def agregar_accion_rapida(icono, comando):
    boton = ttk.Button(root, image=icono, command=comando)
    boton.pack(side=tk.LEFT, padx=5)

def scroll_numeros_lineas(event):
    if event.num == 4:  # Desplazamiento hacia arriba
        editor.yview_scroll(-1, "units")
        numeros_linea.yview_scroll(-1, "units")
    elif event.num == 5:  # Desplazamiento hacia abajo
        editor.yview_scroll(1, "units")
        numeros_linea.yview_scroll(1, "units")

def actualizar_numeracion_lineas(event=None):
    contenido = editor.get(1.0, tk.END)
    lineas = contenido.count('\n') + 1
    
    # Guardar la posición actual del listado de numeración de líneas
    yview_position = editor.yview()
    
    # Obtener la posición actual del cursor
    cursor_pos = editor.index(tk.INSERT)
    current_line, current_column = map(int, cursor_pos.split('.'))
    
    # Actualizar la barra de estado con la línea y la columna actuales
    status_var.set(f"Línea: {current_line}   Columna: {current_column}")
    
    # Actualizar la numeración de líneas
    numeros_linea.config(state=tk.NORMAL)
    numeros_linea.delete(1.0, tk.END)
    numeros_linea.insert(tk.END, '\n'.join(str(i) for i in range(1, lineas + 1)))
    numeros_linea.config(state=tk.DISABLED) 
    
    # Restaurar la posición del listado de numeración de líneas
    numeros_linea.yview_moveto(yview_position[0])
    
    # Programar la próxima actualización
    root.after(500, actualizar_numeracion_lineas)



def start_scroll_up(event):
    global scrolling_up
    scrolling_up = True
    scroll_up()

def stop_scroll_up(event):
    global scrolling_up
    scrolling_up = False

def scroll_up():
    if scrolling_up:
        editor.yview_scroll(-1, "units")
        numeros_linea.yview_scroll(-1, "units")
        root.after(50, scroll_up)

def start_scroll_down(event):
    global scrolling_down
    scrolling_down = True
    scroll_down()

def stop_scroll_down(event):
    global scrolling_down
    scrolling_down = False

def scroll_down():
    if scrolling_down:
        editor.yview_scroll(1, "units")
        numeros_linea.yview_scroll(1, "units")
        root.after(50, scroll_down)

def cambiar_tema(tema):
    if tema == "Dark Theme":
        bg_editor = 'gray17'
        fg_editor = 'white'
        bg_other = 'black'
        fg_other = 'red'
    elif tema == "Contrast Mode":
        bg_editor = 'black'
        fg_editor = 'yellow'
        bg_other = 'white'
        fg_other = 'black'

    editor.config(bg=bg_editor, fg=fg_editor)
    for i in range(pestanas_errores.index("end")):
        frame = pestanas_errores.winfo_children()[i]
        for widget in frame.winfo_children():
            if isinstance(widget, tk.Text):
                widget.config(bg=bg_other, fg=fg_other)

    for i in range(pestanas_editor.index("end")):
        frame = pestanas_editor.winfo_children()[i]
        for widget in frame.winfo_children():
            if isinstance(widget, tk.Text):
                widget.config(bg=bg_other, fg=fg_other)

root = tk.Tk()
root.title("IDE Python")

# Menú
menubar = tk.Menu(root)
root.config(menu=menubar)

# Opción de archivo
archivo_menu = tk.Menu(menubar, tearoff=0)
archivo_menu.add_command(label="Abrir", command=abrir_archivo)
archivo_menu.add_command(label="Guardar", command=guardar_archivo)
archivo_menu.add_command(label="Guardar como", command=guardar_como)
archivo_menu.add_command(label="Nuevo", command=nuevo_archivo)

archivo_menu.add_separator()
archivo_menu.add_command(label="Salir", command=salir)
menubar.add_cascade(label="File", menu=archivo_menu)

# Opción de edición
edit_menu = tk.Menu(menubar, tearoff=0)
edit_menu.add_command(label="Copiar")
edit_menu.add_command(label="Cortar")
edit_menu.add_command(label="Pegar")
menubar.add_cascade(label="Edit", menu=edit_menu)

# Opción de compilación y depuración
build_menu = tk.Menu(menubar, tearoff=0)
build_menu.add_command(label="Compilar", command=compilar)
build_menu.add_command(label="Compilar y depurar", command=compilar_y_depurar)
menubar.add_cascade(label="Build and debug", menu=build_menu)

# Opción de temas para todas las áreas
theme_menu_all = tk.Menu(menubar, tearoff=0)
theme_menu_all.add_command(label="Dark Theme", command=lambda: cambiar_tema("Dark Theme"))
theme_menu_all.add_command(label="Contrast Mode", command=lambda: cambiar_tema("Contrast Mode"))
menubar.add_cascade(label="Editor Theme", menu=theme_menu_all)


# Frame principal para el diseño
main_panedwindow = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
main_panedwindow.pack(fill=tk.BOTH, expand=True)

# Frame para el editor de texto y las pestañas
editor_frame = ttk.Frame(main_panedwindow)
editor_frame.pack(fill=tk.BOTH, expand=True)

numeros_linea = tk.Text(editor_frame, width=4, padx=4, takefocus=0, border=0, background='lightgray', state=tk.DISABLED, font=('Courier', 10))
numeros_linea.pack(side=tk.LEFT, fill=tk.Y)

editor = tk.Text(editor_frame, wrap="none")  # Desactivar el ajuste de línea automático

editor.pack(expand=True, fill=tk.BOTH)

# Barra lateral para desplazamiento vertical
scroll_y = tk.Scrollbar(editor_frame, orient=tk.VERTICAL, command=editor.yview)
scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

# Barra inferior para desplazamiento horizontal
scroll_x = tk.Scrollbar(editor_frame, orient=tk.HORIZONTAL, command=editor.xview)
scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

# Configuración adicional para la barra de desplazamiento vertical y horizontal
editor.config(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)  # Configuración adicional







pestanas_frame = ttk.Frame(main_panedwindow)
pestanas_frame.pack(fill=tk.Y, expand=True)

pestanas_editor = ttk.Notebook(pestanas_frame)
pestanas_editor.pack(fill=tk.BOTH, expand=True)

areas_editor = ["Lexico", "Sintactico", "Semantico", "Hash Table", "Codigo Intermedio"]

widgets_por_area = {}

for area in areas_editor:
    frame = ttk.Frame(pestanas_editor)
    pestanas_editor.add(frame, text=area)
    
    # Verifica si el área actual es "Lexico"
    if area == "Lexico":
        # Crea un widget de texto para el área "Lexico"
        widget_text_lexico = tk.Text(frame, wrap="word")
        widget_text_lexico.pack(fill="both", expand=True)  # Ajusta el widget de texto para llenar el área
        
        # Agrega el widget de texto al diccionario de widgets
        widgets_por_area[area] = widget_text_lexico

main_panedwindow.add(editor_frame)
main_panedwindow.add(pestanas_frame)

# Barra de estado
status_var = tk.StringVar()
status_bar = ttk.Label(root, textvariable=status_var, anchor=tk.W)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# Actualizar numeración de líneas cada medio segundo


# Autocompletar código
#editor.bind("<KeyRelease>", autocomplete)

# Desplazamiento suave
editor.bind("<KeyPress-Up>", start_scroll_up)
editor.bind("<KeyRelease-Up>", stop_scroll_up)
editor.bind("<KeyPress-Down>", start_scroll_down)
editor.bind("<KeyRelease-Down>", stop_scroll_down)
editor.bind("<KeyRelease>", resaltar_sintaxis)

# Desplazamiento de las filas de números
editor.bind("<MouseWheel>", scroll_numeros_lineas)
editor.bind("<Button-4>", scroll_numeros_lineas)
editor.bind("<Button-5>", scroll_numeros_lineas)

# Carga los iconos de acción rápida
icono_abrir = ImageTk.PhotoImage(Image.open("./Iconos/abrir-documento.png"))
icono_guardar = ImageTk.PhotoImage(Image.open("./Iconos/guardar.png"))
icono_compilar = ImageTk.PhotoImage(Image.open("./Iconos/compile.png"))
icono_salir = ImageTk.PhotoImage(Image.open("./Iconos/exit.png"))
icono_compilar_y_depurar = ImageTk.PhotoImage(Image.open("./Iconos/debug.png"))

# Agrega botones de acción rápida al menú
agregar_accion_rapida(icono_abrir, abrir_archivo)
agregar_accion_rapida(icono_guardar, guardar_archivo)
agregar_accion_rapida(icono_compilar, compilar)
agregar_accion_rapida(icono_salir, salir)
agregar_accion_rapida(icono_compilar_y_depurar, compilar_y_depurar)
actualizar_numeracion_lineas()
# Frame para las pestañas de errores y resultados
errores_frame = ttk.Frame(root)
errores_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

pestanas_errores = ttk.Notebook(errores_frame)
pestanas_errores.pack(fill=tk.BOTH, expand=True)

areas_errores = ["Errores lexicos", "Errores sintacticos", "Errores semanticos", "Resultados"]

widgets_errores = {}  # Diccionario para almacenar los widgets de texto de cada pestaña de errores

for area in areas_errores:
    frame = ttk.Frame(pestanas_errores)
    pestanas_errores.add(frame, text=area)
    
    # Crea un widget de texto para cada área de errores
    widget_texto_error = tk.Text(frame, wrap="word")
    widget_texto_error.pack(fill="both", expand=True)
    
    # Agrega el widget de texto al diccionario
    widgets_errores[area] = widget_texto_error




root.mainloop()
