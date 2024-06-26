def analizar(texto):
    palabras_reservadas = set(['main', 'switch', 'case', 'integer', 'double', 'then', 'if', 'else', 'end', 'do', 'while', 'repeat', 'until', 'cin', 'cout', 'real', 'int', 'integer', 'boolean', 'true', 'false', 'float'])
    simbolos_especiales = {'(': 'LPAREN', ')': 'RPAREN', '{': 'LLAVE_IZQ', '}': 'LLAVE_DER', ';': 'PUNTO_COMA', ',': 'COMA', '<': 'MENOR_QUE', '>': 'MAYOR_QUE'}
    operadores_aritmeticos = {'+': 'SUMA', '-': 'RESTA', '*': 'MULTIPLICACION', '/': 'DIVISION', '=': 'ASIGNACION', '%':'PORCENT', '^': 'POTENCIA', }
    operadores_relacionales = {'==': 'EQEQ', '!=': 'DIFERENTE', '<>': 'DIFERENTE2', '<=': 'MENOR_IGUAL_QUE', '>=': 'MAYOR_IGUAL_QUE'}
    operadores_logicos = {'&&': 'AND', '||': 'OR', '!': 'NOT'}
    operadores_dobles = {'++': 'INCREMENTO', '--': 'DECREMENTO'}
    tokens = []
    errors = []

    resultados = []
    errores = []

    # Comenzar el análisis caracter por caracter
    linea = 1
    col = 1
    i = 0
    while i < len(texto):
        if texto[i].isspace():
            if texto[i] == "\n":
                linea += 1
                col = 1
            else:
                col += 1
            i += 1
            continue

        # Identificar comentarios de una línea
        if texto[i:i + 2] == "//":
            comentario = texto[i:].split("\n", 1)[0]
            resultados.append(("COMENTARIO", (linea, col), (linea, col+len(comentario)-1), comentario[2:]))
            i += len(comentario)
            col += len(comentario)
            continue

        # Identificar comentarios multilinea
        elif texto[i:i + 2] == "/*":
            end_comment_index = texto.find("*/", i)
            if end_comment_index == -1:
                errores.append(f"Error léxico: comentario sin cerrar en línea {linea}")
                break  # Salir del bucle si no se encuentra el cierre del comentario
            else:
                comentario = texto[i:end_comment_index+2]
                lineas_comentario = comentario.split("\n")
                inicio = (linea, col)
                fin = (linea + len(lineas_comentario) - 1, len(lineas_comentario[-1]) - lineas_comentario[-1].count('\t') + 1)
                resultados.append(("COMENTARIO_MULTILINEA", inicio, fin, comentario[2:-2]))
                linea += comentario.count("\n")
                col = len(lineas_comentario[-1]) - lineas_comentario[-1].count('\t') + 1
                i = end_comment_index + 2
                continue

        # Identificar palabras reservadas, identificadores y números
        if texto[i].isalpha():
            j = i + 1
            while j < len(texto) and (texto[j].isalnum() or texto[j] == "_"):
                j += 1
            token = texto[i:j]
            if token in palabras_reservadas:
                resultados.append(("PALABRA_RESERVADA", (linea, col), (linea, col+len(token)-1), token))
            else:
                resultados.append(("IDENTIFICADOR", (linea, col), (linea, col+len(token)-1), token))
            col += j - i
            i = j
            continue
        elif texto[i].isdigit():
            tiene_punto = False
            j = i + 1
            while j < len(texto) and (texto[j].isdigit() or (texto[j] == '.' and not tiene_punto)):
                if texto[j] == '.':
                    tiene_punto = True
                j += 1
            if tiene_punto and texto[j-1] == '.':
                errores.append(f"Error léxico: formato incorrecto para número flotante en la línea {linea}, columna {col}")
            else:
                if tiene_punto:
                    resultados.append(("NÚMERO_FLOTANTE", (linea, col), (linea, col+len(texto[i:j])-1), texto[i:j],))
                else:
                    resultados.append(("NÚMERO_ENTERO", (linea, col), (linea, col+len(texto[i:j])-1), texto[i:j]))
            col += j - i
            i = j
            continue

        # Identificar símbolos especiales
        if texto[i] in simbolos_especiales:
            resultados.append((simbolos_especiales[texto[i]], (linea, col), (linea, col), texto[i]))
            i += 1
            col += 1
            continue

        # Identificar operadores aritméticos y relacionales
        if texto[i:i + 2] in operadores_relacionales:
            resultados.append((operadores_relacionales[texto[i:i + 2]], (linea, col), (linea, col+1), texto[i:i + 2]))
            i += 2
            col += 2
            continue
        elif texto[i] in operadores_relacionales:
            resultados.append((operadores_relacionales[texto[i]], (linea, col), (linea, col), texto[i]))
            i += 1
            continue

        # Identificar operadores lógicos
        if texto[i:i + 2] in operadores_logicos:
            resultados.append((operadores_logicos[texto[i:i + 2]], (linea, col), (linea, col+1), texto[i:i + 2]))
            i += 2
            col += 2
            continue
        elif texto[i] in operadores_logicos:
            resultados.append((operadores_logicos[texto[i]], (linea, col), (linea, col), texto[i]))
            i += 1
            continue

        if texto[i:i + 2] in operadores_dobles:
            resultados.append((operadores_dobles[texto[i:i + 2]], (linea, col), (linea, col+1), texto[i:i + 2]))
            i += 2
            col += 1
            continue
        elif texto[i] in operadores_aritmeticos:
            resultados.append((operadores_aritmeticos[texto[i]], (linea, col), (linea, col), texto[i]))
            i += 1
            col += 1
            continue

        errores.append(f"Error léxico: token no reconocido '{texto[i]}' en la línea {linea}, columna {col}")
        i += 1
        col += 1
    
    with open("lexico.txt", "w") as f:
        for item in resultados:
            token = item[3]
            tipo = item[0]
            linea = item[1][0]
            
           
            line = f"{token} / {tipo}  / {linea}"
            f.write(line + "\n")
        
    return resultados, errores
