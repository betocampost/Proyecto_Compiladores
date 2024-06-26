# highlighter.py
from typing import List

def highlight_text(texto: str) -> str:
    # Lista de palabras reservadas en tu lenguaje
    palabras_reservadas = [
        'INCLUDE', 'USING', 'NAMESPACE', 'STD', 'COUT', 'CIN', 'GET', 'CADENA', 'RETURN', 'VOID',
        'INT', 'ENDL', 'SI', 'SINO', 'MIENTRAS', 'PARA', 'AND', 'OR', 'NOT', 'MENORQUE', 'MENORIGUAL',
        'MAYORQUE', 'MAYORIGUAL', 'IGUAL', 'DISTINTO', 'NUMERAL', 'PLUSPLUS', 'MINUSMINUS'
    ]

    # Separar el texto en palabras
    palabras = texto.split()

    # Resaltar las palabras reservadas
    for i in range(len(palabras)):
        if palabras[i] in palabras_reservadas:
            palabras[i] = f"\033[1;32m{palabras[i]}\033[0m"  # Resaltar en verde

    # Reconstruir el texto resaltado
    texto_resaltado = " ".join(palabras)

    return texto_resaltado
