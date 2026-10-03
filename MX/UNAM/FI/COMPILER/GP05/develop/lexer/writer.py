from pathlib import Path


class Writer:
    """
    Genera la salida del analizador léxico.

    Produce:
        - resumen por categorías
        - conteo total de tokens
        - detalle de cada token
        - reporte de errores léxicos

    La salida puede enviarse a consola y/o a un archivo de texto.
    """

    # Relación entre los tipos internos de token y las 7 categorías
    # conceptuales definidas para el proyecto.
    CATEGORIAS = {
        # Puntuación
        "L_PAREN": "punctuation",
        "R_PAREN": "punctuation",
        "L_BRACE": "punctuation",
        "R_BRACE": "punctuation",
        "SEMICOLON": "punctuation",
        "COMMA": "punctuation",

        # Operadores aritméticos
        "PLUS": "operator",
        "MINUS": "operator",
        "MULT": "operator",
        "DIV": "operator",

        # Asignación / comparación
        "ASSIGN": "operator",
        "EQ": "operator",
        "NEQ": "operator",
        "LT": "operator",
        "GT": "operator",
        "LEQ": "operator",
        "GEQ": "operator",

        # Operadores lógicos
        "AND": "operator",
        "OR": "operator",
        "NOT": "operator",

        # Keywords
        "START": "keyword",
        "IF": "keyword",
        "THEN": "keyword",
        "ELSE": "keyword",
        "WHILE": "keyword",
        "FOR": "keyword",
        "FROM": "keyword",
        "TO": "keyword",
        "PRINT": "keyword",
        "PRINTF": "keyword",
        "READ": "keyword",
        "INT": "keyword",
        "REAL": "keyword",
        "STRING_TYPE": "keyword",
        "BOOL_TYPE": "keyword",

        # Literales
        "INTEGER": "constant",
        "REAL_NUMBER": "constant",
        "STRING_LITERAL": "constant",
        "BOOL_LITERAL": "constant",

        # Identificador
        "ID": "identifier",
    }

    def __init__(self):
        """
        Inicializa el Writer.
        """

        pass

    def obtener_categoria(self, tipo):
        """
        Obtiene la categoría conceptual de un token.

        Args:
            tipo (str): Tipo interno del token.

        Returns:
            str: Categoría correspondiente.

        Raises:
            ValueError: Si el tipo no pertenece al catálogo.
        """

        categoria = self.CATEGORIAS.get(tipo)

        if categoria is None:
            raise ValueError(
                f"Tipo de token desconocido: {tipo}"
            )

        return categoria

    def generar_reporte(self, tokens, errores=None):
        """
        Genera el reporte completo como una cadena.

        Args:
            tokens (list[Token]): Tokens reconocidos.
            errores (list[dict] | None): Errores léxicos.

        Returns:
            str: Reporte completo.
        """

        if errores is None:
            errores = []

        lineas = []

        # Resumen por categorías
        lineas.append("- ANALIZADOR LÉXICO -")
        lineas.append("")

        categorias = [
            self.obtener_categoria(token.tipo)
            for token in tokens
        ]

        if categorias:
            lineas.append(" ".join(categorias))
        else:
            lineas.append("")

        lineas.append("")
        lineas.append(f"Total de tokens: {len(tokens)}")


        # Detalle de tokens

        lineas.append("")
        lineas.append("- DETALLE DE TOKENS -")
        lineas.append("")
        lineas.append(
            f"{'No.':>3}  "
            f"{'Tipo':<16} "
            f"{'Categoría':<12} "
            f"{'Lexema':<24} "
            f"{'Línea':<7} "
            f"{'Columna':<7}"
        )

        lineas.append("-" * 78)

        for numero, token in enumerate(tokens, start=1):
            categoria = self.obtener_categoria(token.tipo)

            lineas.append(
                f"{numero:>3}  "
                f"{token.tipo:<16} "
                f"{categoria:<12} "
                f"{token.lexema!r:<24} "
                f"{token.linea:<7} "
                f"{token.columna:<7}"
            )

        # Errores
        lineas.append("")
        lineas.append("- ERRORES LÉXICOS -")
        lineas.append("")

        if errores:
            for error in errores:
                lineas.append(
                    f"Línea {error['linea']}, "
                    f"columna {error['columna']}: "
                    f"{error['mensaje']}"
                )
        else:
            lineas.append("Sin errores léxicos.")

        return "\n".join(lineas)

    def escribir_consola(self, reporte):
        """
        Imprime el reporte en la consola.

        Args:
            reporte (str): Reporte generado.
        """

        print(reporte)

    def escribir_archivo(self, reporte, ruta):
        """
        Escribe el reporte en un archivo de texto.

        Args:
            reporte (str): Reporte generado.
            ruta (str): Ruta del archivo de salida.

        Returns:
            Path: Ruta del archivo generado.
        """

        ruta_salida = Path(ruta)

        ruta_salida.write_text(
            reporte,
            encoding="utf-8"
        )

        return ruta_salida

    def escribir(self, tokens, errores=None, ruta=None):
        """
        Genera el reporte y, opcionalmente, lo imprime
        y lo guarda en un archivo.

        Args:
            tokens (list[Token]): Tokens reconocidos.
            errores (list[dict] | None): Errores encontrados.
            ruta (str | None): Archivo de salida.

        Returns:
            str: Reporte generado.
        """

        reporte = self.generar_reporte(
            tokens,
            errores
        )

        # Salida por consola.
        self.escribir_consola(reporte)

        # Salida a archivo, si se proporciona una ruta.
        if ruta is not None:
            self.escribir_archivo(
                reporte,
                ruta
            )

        return reporte