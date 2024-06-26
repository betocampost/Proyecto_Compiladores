import tkinter as tk

from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from tkinter import messagebox
import time

from lexico import analizar

import subprocess
import io
import sys
import threading
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.token import Token
import re
import random
import keyword

archivo_actual = None
scrolling_up = False
scrolling_down = False
hilo_verificacion = False
hilo_lex = None

PALABRAS_CLAVE = [
    "if",
    "else",
    "while",
    "for",
    "def",
    "class",
    "import",
    "from",
    "return",
    "True",
    "False",
    "None",
]
NOMBRES_VARIABLES = ["x", "y", "z", "contador", "resultado", "temporal"]

def resaltar_palabras_clave(texto):
    # Crea una expresión regular que coincida con las palabras clave completas
    patrón = r'\b(?:' + '|'.join(map(re.escape, PALABRAS_CLAVE)) + r')\b'
    # Utiliza la expresión regular para encontrar las palabras clave y resaltarlas
    texto_resaltado = re.sub(patrón, r'<strong>\g<0></strong>', texto, flags=re.IGNORECASE)
    return texto_resaltado


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
    archivo = filedialog.asksaveasfilename(
        defaultextension=".txt", filetypes=[("Archivos de texto", "*.txt")]
    )
    if archivo:
        archivo_actual = archivo
        with open(archivo, "w") as f:
            f.write(editor.get(1.0, tk.END))


def nuevo_archivo():
    global archivo_actual

    # Verificar si hay cambios no guardados
    if hay_cambios_no_guardados():
        confirmacion = tk.messagebox.askyesnocancel(
            "Guardar cambios",
            "¿Desea guardar los cambios antes de abrir un nuevo archivo?",
        )

        if (
            confirmacion is None
        ):  # Si se presiona Cancelar, salir sin abrir un nuevo archivo
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

def hilo1():
    global hilo_verificacion
    global hilo_lex
    print(hilo_verificacion)

    if hilo_verificacion:
        hilo_verificacion = False
        hilo_lex.join()
    else:
        hilo_verificacion = True
        hilo_lex = threading.Thread(target=compilar)
        hilo_lex.start()

def resaltar_sintaxis(tokens_reconocidos):
    etiquetas = {
        'PALABRA_RESERVADA': '#FF8800',  # Naranja
        'IDENTIFICADOR': '#0000FF',  # Azul
        'NÚMERO_ENTERO': '#FF0000',  # Rojo
        'NÚMERO_FLOTANTE': '#FF0000',  # Rojo
        'OPERADOR_ARITMETICO': '#00CF00',  # Verde
        'OPERADOR_RELACIONAL': '#F33394',  # Rosa
        'OPERADOR_LOGICO': '#009797',  # Turquesa
        'OPERADOR_DOBLE': '#990099',  # Morado
        'SIMBOLO': '#772700',  # Marrón
        'ASIGNACION': '#00CF00',  # Verde
        'IGUALDAD': '#FF33FF',  # Magenta
        'DIFERENTE':'#FF33FF',
        'DIFERENTE2': '#FF33FF',
        'MENOR_QUE': '#FF33FF',
        'MAYOR_QUE': '#FF33FF',
        'MENOR_IGUAL_QUE': '#FF33FF',
        'MAYOR_IGUAL_QUE': '#FF33FF',
        'COMENTARIO': '#666666',  # Gris
        'COMENTARIO_MULTILINEA': '#666666',  # Gris
        'LPAREN': '#00defb',   # Beige
        'RPAREN': '#00defb',   # Beige
        'LLAVE_IZQ':  '#00defb',   # Beige
        'LLAVE_DER':  '#00defb',   # Beige
        'PUNTO_COMA':  '#00defb',  # Beige
        'COMA':  '#00defb',   # Beige
        'SUMA': '#bf00ff',
        'RESTA': '#bf00ff',
        'MULTIPLICACION': '#bf00ff',
        'DIVISION': '#bf00ff',
        'ASIGNACION' :'#bf00ff',
        'INCREMENTO':  '#bf00ff',
        'DECREMENTO': '#bf00ff',
        'AND': '#2fff00',
        'OR': '#2fff00',
        'PUNTO' : '#00defb'

    }
    
    for etiqueta, color in etiquetas.items():
        editor.tag_remove(etiqueta, '1.0', 'end')
        
    for token_info in tokens_reconocidos:
       # print(token_info)
        tokens_split = str(token_info).split()
        tipo, lineaI, columnaI, lineaF, columnaF, valor = tokens_split[:6]
        tipo = tipo.replace('(', '')
        tipo = tipo.replace("'", '')
        tipo = tipo.replace(',', '')
        lineaI = lineaI.replace('(', '')
        lineaI = lineaI.replace(',', '')
        columnaI = columnaI.replace(')', '')
        columnaI = columnaI.replace(',', '')
        lineaF = lineaF.replace('(', '')
        lineaF = lineaF.replace(',', '')
        columnaF = columnaF.replace(')', '')
        columnaF = columnaF.replace(',', '')
        valor = valor.replace("'", '')
        valor = valor.replace(')', '')
        columnaI = int(columnaI) - 1
        configuracion_etiqueta = etiquetas.get(tipo)
        #print(f"tipo :{tipo}, filaI: {lineaI}, columnaI: {columnaI} filaF: {lineaF}, columnaF: {columnaF}")

        if configuracion_etiqueta:
            inicio = f"{lineaI}.{columnaI}"
            fin = f"{lineaF}.{columnaF}"
            editor.tag_add(tipo, inicio, fin)

    for tipo, configuracion_etiqueta in etiquetas.items():
        editor.tag_configure(tipo, foreground=configuracion_etiqueta)



def compilar():
    global resultado_lexema
    global hilo_verificacion
    codigo = editor.get("1.0", "end-1c")

    resultados, errores = analizar(codigo)

    actualizar_errores_lexicos(errores)
    actualizar_errores_sintacticos()
    resaltar_sintaxis(resultados)

    subprocess.run(['python', 'sintactico.py'])

    #errores_lexicos = []

    for index, area in enumerate(areas_editor):
        if area == "Lexico":
            frame_lexico = pestanas_editor.winfo_children()[index]
            widgets_frame = frame_lexico.winfo_children()
            widget_text_lexico = None
            for widget in widgets_frame:
                if isinstance(widget, tk.Text):
                    widget_text_lexico = widget
                    break

            if widget_text_lexico is not None:
                # Obtener la posición actual del desplazamiento vertical

                # Limpiar el contenido existente en el widget Text
                widget_text_lexico.delete(1.0, tk.END)

                # Insertar el resultado del análisis léxico en el widget Text
                for resutado in resultados:
                    widget_text_lexico.insert(tk.END, str(resutado) + "\n")
                widget_text_lexico.yview_moveto(1.0)

            else:
                print("No se encontró el widget Text dentro del área 'Lexico'")
        
        elif area == "Sintactico":
            frame_sintactico = pestanas_editor.winfo_children()[index]
            widgets_frame = frame_sintactico.winfo_children()
            widget_text_sintactico = None
            for widget in widgets_frame:
                if isinstance(widget, ttk.Treeview):
                    widget_text_sintactico = widget
                    break
            if widget_text_sintactico is None:
                widget_text_sintactico = ttk.Treeview(frame_sintactico)
                widget_text_sintactico.pack(fill="both", expand=True)

            # Se limpia xd
            widget_text_sintactico.delete(*widget_text_sintactico.get_children())
            
            with open("arbolSintactico.txt", "r") as f:
                stack = []
                last_depth = -1 
                unique_id = 1
                
                for line in f:
                    line = line.strip()
                    depth = line.count('|')
                    text = line.replace('|', '').strip() 
                    while stack and depth <= stack[-1][0]:
                        stack.pop()
                    
                    if stack:
                        parent_id = stack[-1][1]
                    else:
                        parent_id = ''
                    
                    item_id = f"{text}_{unique_id}"
                    unique_id += 1
                    
                    node_id = widget_text_sintactico.insert(parent_id, 'end', item_id, text=text)
                    stack.append((depth, node_id))
            expandir_arbol(widget_text_sintactico)
    if hilo_verificacion:
        root.after(100, compilar)

def expandir_arbol(tree):
    def expand_all_nodes(item):
        children = tree.get_children(item)
        for child in children:
            tree.item(child, open=True)
            expand_all_nodes(child)
    root_items = tree.get_children('')
    for item in root_items:
        tree.item(item, open=True)
        expand_all_nodes(item)

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
        widget_texto.insert(
            tk.END, error_info + "\n"
        )  # Inserta cada error en una línea separada
    widget_texto.config(state=tk.DISABLED)  # Deshabilita la edición del widget

def actualizar_errores_sintacticos():
    widget_texto = widgets_errores["Errores sintacticos"]
    widget_texto.config(state=tk.NORMAL)
    widget_texto.delete(1.0, tk.END)
    with open("erroresSintactico.txt", "r") as f:
        contenido = f.read()
        widget_texto.insert(tk.END, contenido)
    widget_texto.config(state=tk.DISABLED)


def hay_cambios_no_guardados():
    contenido_editor = editor.get(1.0, tk.END).strip()

    if archivo_actual:  # Verificar si hay un archivo actual
        with open(archivo_actual, "r") as f:
            contenido_archivo = f.read().strip()

        return contenido_editor != contenido_archivo
    else:
        return bool(contenido_editor)


def agregar_accion_rapida(icono, comando, row, column):
    boton = ttk.Button(frame_botones, image=icono, command=comando)
    boton.grid(row=row, column=column, padx=5, pady=5)


def scroll_numeros_lineas(event):
    if event.num == 4:  # Desplazamiento hacia arriba
        editor.yview_scroll(-1, "units")
        numeros_linea.yview_scroll(-1, "units")
    elif event.num == 5:  # Desplazamiento hacia abajo
        editor.yview_scroll(1, "units")
        numeros_linea.yview_scroll(1, "units")


def actualizar_numeracion_lineas(event=None):
    contenido = editor.get(1.0, tk.END)
    lineas = contenido.count("\n") + 1

    # Guardar la posición actual del listado de numeración de líneas
    yview_position = editor.yview()

    # Obtener la posición actual del cursor
    cursor_pos = editor.index(tk.INSERT)
    current_line, current_column = map(int, cursor_pos.split("."))

    # Actualizar la barra de estado con la línea y la columna actuales
    status_var.set(f"Línea: {current_line}   Columna: {current_column}")

    # Actualizar la numeración de líneas
    numeros_linea.config(state=tk.NORMAL)
    numeros_linea.delete(1.0, tk.END)
    numeros_linea.insert(tk.END, "\n".join(str(i) for i in range(1, lineas + 1)))
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
        bg_editor = "gray17"
        fg_editor = "white"
        bg_other = "black"
        fg_other = "red"
    elif tema == "Contrast Mode":
        bg_editor = "black"
        fg_editor = "yellow"
        bg_other = "white"
        fg_other = "black"

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

root.configure(bg="#EEEEEE")
root.resizable(0, 0)
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)

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
build_menu.add_command(label="Compilar", command="")
build_menu.add_command(label="Compilar y depurar", command=compilar_y_depurar)
menubar.add_cascade(label="Build and debug", menu=build_menu)

# Opción de temas para todas las áreas
theme_menu_all = tk.Menu(menubar, tearoff=0)
theme_menu_all.add_command(
    label="Dark Theme", command=lambda: cambiar_tema("Dark Theme")
)
theme_menu_all.add_command(
    label="Contrast Mode", command=lambda: cambiar_tema("Contrast Mode")
)
menubar.add_cascade(label="Editor Theme", menu=theme_menu_all)


editor_frame = tk.Frame(root, bg="#FFFF00", width=800, height=500)
editor_frame.grid(row=0, column=0, rowspan=2, padx=5, pady=0)

pestanas_frame = tk.Frame(root, bg="#00FFFF", width=500, height=470)
pestanas_frame.grid(row=0, column=1, columnspan=1, padx=5, pady=0)

editor_frame.pack_propagate(0)
pestanas_frame.pack_propagate(0)

numeros_linea = tk.Text(editor_frame, width=4, padx=4, pady=5, takefocus=0, border=0, background='lightgray', state=tk.DISABLED, font=('Courier', 12))
numeros_linea.pack(side=tk.LEFT, fill=tk.Y)

scroll_y = tk.Scrollbar(editor_frame, orient=tk.VERTICAL, command=numeros_linea.yview)
scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

scroll_x = tk.Scrollbar(editor_frame, orient=tk.HORIZONTAL, command=numeros_linea.xview)
scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

editor = tk.Text(
    editor_frame, wrap="none", yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set
)  # Desactivar el ajuste de línea automático
editor.config(bg='#CCCCCC')
editor.pack(expand=True, fill=tk.BOTH)
editor.config(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

frame_botones = tk.Frame(root, bg="#EEEEEE", width=100, height=10)
frame_botones.grid(row=1, column=1, padx=0, pady=0, sticky="e")


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
        widget_text_lexico.pack(
            fill="both", expand=True
        )  # Ajusta el widget de texto para llenar el área

        # Agrega el widget de texto al diccionario de widgets
        widgets_por_area[area] = widget_text_lexico
    
    if area == "Sintactico":
        widget_text_sintactico = ttk.Treeview(frame)
        widget_text_sintactico.pack(fill="both", expand=True)
        widgets_por_area[area] = widget_text_sintactico
        estilo = ttk.Style()
        estilo.configure("Treeview",
                         background="#f0f0f0",
                         foreground="black",
                         rowheight=20,
                         font=("Arial", 10))
 

# Barra de estado
status_var = tk.StringVar()
status_bar = ttk.Label(root, textvariable=status_var)
status_bar.grid(row=1, column=1, padx=5, pady=5, sticky="sw")

# Actualizar numeración de líneas cada medio segundo


# Autocompletar código
# editor.bind("<KeyRelease>", autocomplete)

# Desplazamiento suave
editor.bind("<KeyPress-Up>", start_scroll_up)
editor.bind("<KeyRelease-Up>", stop_scroll_up)
editor.bind("<KeyPress-Down>", start_scroll_down)
editor.bind("<KeyRelease-Down>", stop_scroll_down)

# Desplazamiento de las filas de números
editor.bind("<MouseWheel>", scroll_numeros_lineas)
editor.bind("<Button-4>", scroll_numeros_lineas)
editor.bind("<Button-5>", scroll_numeros_lineas)

# Carga los iconos de acción rápida
icono_abrir = ImageTk.PhotoImage(Image.open("Iconos/abrir-documento.png"))
icono_guardar = ImageTk.PhotoImage(Image.open("Iconos/guardar.png"))
icono_compilar = ImageTk.PhotoImage(Image.open("Iconos/compile.png"))
icono_salir = ImageTk.PhotoImage(Image.open("Iconos/exit.png"))
icono_compilar_y_depurar = ImageTk.PhotoImage(Image.open("Iconos/debug.png"))
lupa = ImageTk.PhotoImage(Image.open("Iconos/lupa.png"))

# Agrega botones de acción rápida al menú
agregar_accion_rapida(lupa, hilo1, 0, 0)
agregar_accion_rapida(icono_abrir, abrir_archivo, 0, 1)
agregar_accion_rapida(icono_guardar, guardar_archivo, 0, 2)
agregar_accion_rapida(icono_compilar, "", 0, 3)
agregar_accion_rapida(icono_salir, salir, 0, 4)
agregar_accion_rapida(icono_compilar_y_depurar, compilar_y_depurar, 0, 5)
actualizar_numeracion_lineas()
# Frame para las pestañas de errores y resultados
errores_frame = tk.Frame(root, bg="#FF00FF", width=1305, height=200)
errores_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

errores_frame.pack_propagate(0)
pestanas_errores = ttk.Notebook(errores_frame)
pestanas_errores.pack(fill=tk.BOTH, expand=True)

areas_errores = [
    "Errores lexicos",
    "Errores sintacticos",
    "Errores semanticos",
    "Resultados",
]

widgets_errores = (
    {}
)  # Diccionario para almacenar los widgets de texto de cada pestaña de errores

for area in areas_errores:
    frame = ttk.Frame(pestanas_errores)
    pestanas_errores.add(frame, text=area)

    # Crea un widget de texto para cada área de errores
    widget_texto_error = tk.Text(frame, wrap="word")
    widget_texto_error.pack(fill="both", expand=True)

    # Agrega el widget de texto al diccionario
    widgets_errores[area] = widget_texto_error

hilo1()



root.mainloop()
