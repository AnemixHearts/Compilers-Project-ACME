def estado_leyendo_identificador(fuente, puntero):
    """
    Estado q1 del DFA.

    Lee un identificador completo.

    Los identificadores pueden contener:
        - letras
        - dígitos
        - guion bajo

    Ejemplos:
        a
        contador
        variable1
        _nombre
        dato_2

    Args:
        fuente (str): Código fuente completo.
        puntero (int): Posición inicial del identificador.

    Returns:
        tuple:
            lexema (str): Identificador completo.
            nuevo_puntero (int): Primera posición que ya no
                                 pertenece al identificador.
    """

    inicio = puntero

    while puntero < len(fuente):
        char = fuente[puntero]

        if char.isalnum() or char == "_":
            puntero += 1
        else:
            break

    lexema = fuente[inicio:puntero]

    return lexema, puntero


def estado_leyendo_numero(fuente, puntero):
    """
    Estados q2, q3 y q4 del DFA.

    Reconoce:

        INTEGER
        REAL_NUMBER

    Ejemplos:

        10      -> INTEGER
        256     -> INTEGER
        3.14    -> REAL_NUMBER
        0.5     -> REAL_NUMBER

    No se aceptan:

        3.
        3.a

    El signo '-' se reconoce por separado como MINUS.

    Args:
        fuente (str): Código fuente completo.
        puntero (int): Posición inicial del número.

    Returns:
        tuple:
            lexema (str): Número reconocido.
            nuevo_puntero (int): Posición posterior al número.
            tipo (str): INTEGER o REAL_NUMBER.
            valido (bool): Indica si el número es válido.
    """

    inicio = puntero

    # q2: consumir parte entera.
    while puntero < len(fuente) and fuente[puntero].isdigit():
        puntero += 1

    # Si no hay punto decimal, es entero.
    if puntero >= len(fuente) or fuente[puntero] != ".":
        lexema = fuente[inicio:puntero]

        return lexema, puntero, "INTEGER", True

    # q3: consumir el punto decimal.
    puntero += 1

    # El punto debe ir seguido de al menos un dígito.
    if puntero >= len(fuente) or not fuente[puntero].isdigit():
        lexema = fuente[inicio:puntero]

        return lexema, puntero, "REAL_NUMBER", False

    # q4: consumir parte fraccionaria.
    while puntero < len(fuente) and fuente[puntero].isdigit():
        puntero += 1

    lexema = fuente[inicio:puntero]

    return lexema, puntero, "REAL_NUMBER", True


def estado_leyendo_literal(fuente, puntero):
    """
    Estados q5 y q6 del DFA.

    Lee un literal de cadena delimitado por comillas dobles.

    Ejemplos:

        "Hola mundo"          -> válido
        "This is an example"  -> válido
        "Hola mundo           -> inválido

    Args:
        fuente (str): Código fuente completo.
        puntero (int): Posición de la comilla inicial.

    Returns:
        tuple:
            lexema (str): Literal completo.
            nuevo_puntero (int): Posición posterior a la comilla
                                 de cierre o EOF.
            cerrado (bool): True si se encontró la comilla final.
    """

    inicio = puntero

    # q5: consumir comilla inicial.
    puntero += 1

    while puntero < len(fuente):

        if fuente[puntero] == '"':
            # q6: consumir comilla de cierre.
            puntero += 1

            lexema = fuente[inicio:puntero]

            return lexema, puntero, True

        puntero += 1

    # EOF sin comilla de cierre.
    lexema = fuente[inicio:puntero]

    return lexema, puntero, False


def estado_leyendo_operador(fuente, puntero):
    """
    Reconoce operadores aritméticos, de asignación
    y de comparación.

    Operadores reconocidos:

        +   -> PLUS
        -   -> MINUS
        *   -> MULT
        /   -> DIV

        =   -> ASSIGN
        ==  -> EQ
        !=  -> NEQ
        <   -> LT
        >   -> GT
        <=  -> LEQ
        >=  -> GEQ
    """

    char = fuente[puntero]

    # Operadores aritméticos.
    if char == "+":
        return "+", puntero + 1, "PLUS", True

    if char == "-":
        return "-", puntero + 1, "MINUS", True

    if char == "*":
        return "*", puntero + 1, "MULT", True

    if char == "/":
        return "/", puntero + 1, "DIV", True

    # q7: '=' o '=='.
    if char == "=":
        if (
            puntero + 1 < len(fuente)
            and fuente[puntero + 1] == "="
        ):
            return "==", puntero + 2, "EQ", True

        return "=", puntero + 1, "ASSIGN", True

    # q8: '!='.
    if char == "!":
        if (
            puntero + 1 < len(fuente)
            and fuente[puntero + 1] == "="
        ):
            return "!=", puntero + 2, "NEQ", True

        # '!' por sí solo no pertenece al lenguaje.
        return "!", puntero + 1, None, False

    # q9: '<' o '<='.
    if char == "<":
        if (
            puntero + 1 < len(fuente)
            and fuente[puntero + 1] == "="
        ):
            return "<=", puntero + 2, "LEQ", True

        return "<", puntero + 1, "LT", True

    # q10: '>' o '>='.
    if char == ">":
        if (
            puntero + 1 < len(fuente)
            and fuente[puntero + 1] == "="
        ):
            return ">=", puntero + 2, "GEQ", True

        return ">", puntero + 1, "GT", True

    # Carácter no reconocido.
    return char, puntero + 1, None, False


def estado_leyendo_puntuacion(fuente, puntero):
    """
    Reconoce los signos de puntuación.

        (  -> L_PAREN
        )  -> R_PAREN
        {  -> L_BRACE
        }  -> R_BRACE
        ;  -> SEMICOLON
        ,  -> COMMA
    """

    char = fuente[puntero]

    if char == "(":
        return "(", puntero + 1, "L_PAREN", True

    if char == ")":
        return ")", puntero + 1, "R_PAREN", True

    if char == "{":
        return "{", puntero + 1, "L_BRACE", True

    if char == "}":
        return "}", puntero + 1, "R_BRACE", True

    if char == ";":
        return ";", puntero + 1, "SEMICOLON", True

    if char == ",":
        return ",", puntero + 1, "COMMA", True

    return char, puntero + 1, None, False