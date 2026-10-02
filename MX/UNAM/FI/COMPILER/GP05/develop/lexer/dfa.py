def estado_leyendo_literal(fuente, puntero):
    """
    Lee un literal de cadena delimitado por comillas dobles.

    El puntero recibido debe apuntar a la comilla inicial.

    Args:
        fuente (str): Código fuente completo.
        puntero (int): Posición de la comilla inicial.

    Returns:
        tuple:
            lexema (str): Literal completo, incluyendo las comillas.
            nuevo_puntero (int): Posición posterior a la comilla
                                 de cierre.
            cerrado (bool): True si se encontró la comilla de cierre.
    """

    inicio = puntero

    # Consumir la comilla inicial.
    puntero += 1

    while puntero < len(fuente):

        if fuente[puntero] == '"':
            # Consumir la comilla de cierre.
            puntero += 1

            lexema = fuente[inicio:puntero]

            return lexema, puntero, True

        puntero += 1

    # Se llegó al final sin encontrar la comilla de cierre.
    lexema = fuente[inicio:puntero]

    return lexema, puntero, False