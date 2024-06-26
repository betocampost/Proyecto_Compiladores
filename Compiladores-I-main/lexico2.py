from rich import print
from rich.console import Console
from rich.syntax import Syntax
import ply.lex as lex
import random

resultado_lexema = []

tokens = (
    'ENTERO',
    'REAL',
    'PALABRA_RESERVADA',
    'OPERADOR_ARITMETICO',
    'OPERADOR_RELACIONAL',
    'OPERADOR_LOGICO',
    'SIMBOLO',
    'ASIGNACION',
    'IDENTIFICADOR',
    'CADENA_SIMPLE',
    'CADENA_DOBLE',
    'CADENA_TRIPLE',
    'COMENTARIO_UNILINEA',
)

# Expresiones regulares para los tokens
t_OPERADOR_ARITMETICO = r'[\+\-\*\/%\^]|\+\+|\-\-'
t_OPERADOR_RELACIONAL = r'[<>]=?|!=|=='
t_SIMBOLO = r'[()\{\},;.:]'
t_ASIGNACION = r'='

# Definiciones de token más complejas
def t_REAL(t):
    r'\b\d+\.\d+\b|\b\d+\.\b'
    if '.' in t.value:
        if t.value.count('.') > 1 or t.value.endswith('.'):
            estado = f"** Error léxico en la línea {t.lineno}, posición {t.lexpos}: Número real mal formado '{t.value}'."
            resultado_lexema.append(estado)
            return
    t.value = float(t.value)
    return t

def t_ENTERO(t):
    r'\b\d+\b'
    t.value = int(t.value)
    return t

def t_PALABRA_RESERVADA(t):
    r'\b(?:False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b'
    return t

# Definir operadores lógicos como tokens individuales
def t_OPERADOR_LOGICO(t):
    r'and|or|not'
    return t

def t_IDENTIFICADOR(t):
    r'\w+(_\d\w)*'
    return t

def t_CADENA_TRIPLE(t):
    r'(\'\'\'(.|\n)?\'\'\'|\"\"\"(.|\n)?\"\"\")'
    t.lexer.lineno += t.value.count('\n')
    return t

def t_CADENA_SIMPLE(t):
    r'\'([^\\\n]|(\\.))*?\''
    return t

def t_CADENA_DOBLE(t):
    r'\"([^\\\n]|(\\.))*?\"'
    return t

def t_COMENTARIO_UNILINEA(t):
    r'\/\/.*\n'
    t.lexer.lineno += 1

def t_ignore_COMENTARIO(t):
    r'\#.*\n'
    t.lexer.lineno += 1

def t_ignore_ESPACIO(t):
    r'[\s]+'
    t.lexer.lineno += t.value.count('\n')

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.lexer.lexpos = t.lexer.lexdata.find('\n', t.lexer.lexpos) + 1
    t.lexer.skip(1)

def t_error(t):
    global resultado_lexema
    estado = f"** Error léxico en la línea {t.lineno}, posición {t.lexpos}: Carácter '{t.value[0]}' no válido."
    resultado_lexema.append(estado)
    t.lexer.skip(1)

# Construyendo el analizador léxico
analizador = lex.lex()

def analizar_texto(text):
    global resultado_lexema
    analizador.input(text)
    while True:
        tok = analizador.token()
        if not tok:
            break  # No más entrada
        estilo = ""
        if tok.type == 'PALABRA_RESERVADA':
            estilo = "bold blue"
        elif tok.type in ['ENTERO', 'REAL', 'CADENA_SIMPLE', 'CADENA_DOBLE', 'CADENA_TRIPLE']:
            estilo = "bold cyan"
        elif tok.type in ['OPERADOR_ARITMETICO', 'OPERADOR_RELACIONAL', 'OPERADOR_LOGICO', 'SIMBOLO', 'ASIGNACION']:
            estilo = "bold magenta"
        elif tok.type == 'IDENTIFICADOR':
            estilo = "bold green"
        elif tok.type == 'COMENTARIO_UNILINEA':
            estilo = "bold yellow"
        print(f"[{estilo}]{tok.value}[/{estilo}] ", end="")
    
    for error in resultado_lexema:
        print(f"[bold red]{error}[/bold red]")

if __name__ == "_main_":
    codigo_fuente = input("Ingrese el código fuente: ")
    analizar_texto(codigo_fuente)