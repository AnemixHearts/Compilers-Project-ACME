from dfa import (
    estado_leyendo_identificador,
    estado_leyendo_numero,
    estado_leyendo_literal,
    estado_leyendo_operador,
    estado_leyendo_puntuacion,
)

from models.token import Token


class Scanner:
    """
    Analizador léxico manual basado en un DFA.

    El scanner recorre el código fuente carácter por carácter,
    utiliza las funciones definidas en dfa.py y genera una lista
    de objetos Token.

    Los espacios, saltos de línea y comentarios iniciados con '#'
    se ignoran y no generan tokens.
    """

    # Palabras reservadas y operadores lógicos.
    PALABRAS_RESERVADAS = {
        "Start": "START",
        "if": "IF",
        "then": "THEN",
        "else": "ELSE",
        "while": "WHILE",
        "for": "FOR",
        "from": "FROM",
        "to": "TO",
        "print": "PRINT",
        "printf": "PRINTF",
        "read": "READ",
        "int": "INT",
        "real": "REAL",
        "string": "STRING_TYPE",
        "bool": "BOOL_TYPE",
        "and": "AND",
        "or": "OR",
        "not": "NOT",
    }

    # Literales booleanos.
    LITERALES_BOOLEANOS = {
        "True",
        "False",
    }

    def __init__(self, fuente):
        """
        Inicializa el scanner.

        Args:
            fuente (str): Código fuente que será analizado.
        """

        self.fuente = fuente
        self.puntero = 0

        # Posición actual dentro del código fuente.
        self.linea = 1
        self.columna = 1

        # Tokens reconocidos.
        self.tokens = []

        # Errores léxicos encontrados.
        self.errores = []

    def escanear(self):
        """
        Ejecuta el análisis léxico completo.

        Returns:
            list[Token]:
                Lista de tokens reconocidos.
        """

        while self.puntero < len(self.fuente):

            char = self.fuente[self.puntero]

            # q0: espacios y saltos de línea.
            if char.isspace():
                self._avanzar_caracter(char)
                continue

            # q0 -> q11: comentario.
            if char == "#":
                self._ignorar_comentario()
                continue

            # q0 -> q1: identificador o palabra reservada.
            if char.isalpha() or char == "_":
                linea_inicial = self.linea
                columna_inicial = self.columna

                lexema, nuevo_puntero = estado_leyendo_identificador(
                    self.fuente,
                    self.puntero
                )

                self.puntero = nuevo_puntero

                tipo = self._clasificar_identificador(lexema)

                self.tokens.append(
                    Token(
                        tipo=tipo,
                        lexema=lexema,
                        linea=linea_inicial,
                        columna=columna_inicial
                    )
                )

                self._actualizar_posicion(lexema)
                continue

            # q0 -> q2: número.
            if char.isdigit():
                linea_inicial = self.linea
                columna_inicial = self.columna

                (
                    lexema,
                    nuevo_puntero,
                    tipo,
                    valido
                ) = estado_leyendo_numero(
                    self.fuente,
                    self.puntero
                )

                self.puntero = nuevo_puntero

                if valido:
                    self.tokens.append(
                        Token(
                            tipo=tipo,
                            lexema=lexema,
                            linea=linea_inicial,
                            columna=columna_inicial
                        )
                    )
                else:
                    self._registrar_error(
                        f"Número mal formado: '{lexema}'",
                        linea_inicial,
                        columna_inicial
                    )

                self._actualizar_posicion(lexema)
                continue

            # q0 -> q5: literal de cadena.
            if char == '"':
                linea_inicial = self.linea
                columna_inicial = self.columna

                (
                    lexema,
                    nuevo_puntero,
                    cerrado
                ) = estado_leyendo_literal(
                    self.fuente,
                    self.puntero
                )

                self.puntero = nuevo_puntero

                if cerrado:
                    self.tokens.append(
                        Token(
                            tipo="STRING_LITERAL",
                            lexema=lexema,
                            linea=linea_inicial,
                            columna=columna_inicial
                        )
                    )
                else:
                    self._registrar_error(
                        f"Literal de cadena sin cerrar: '{lexema}'",
                        linea_inicial,
                        columna_inicial
                    )

                self._actualizar_posicion(lexema)
                continue

            # Operadores.
            if char in "+-*/=!<>":
                linea_inicial = self.linea
                columna_inicial = self.columna

                (
                    lexema,
                    nuevo_puntero,
                    tipo,
                    valido
                ) = estado_leyendo_operador(
                    self.fuente,
                    self.puntero
                )

                self.puntero = nuevo_puntero

                if valido:
                    self.tokens.append(
                        Token(
                            tipo=tipo,
                            lexema=lexema,
                            linea=linea_inicial,
                            columna=columna_inicial
                        )
                    )
                else:
                    self._registrar_error(
                        f"Operador inválido: '{lexema}'",
                        linea_inicial,
                        columna_inicial
                    )

                self._actualizar_posicion(lexema)
                continue

            # Puntuación.
            if char in "(){};,":
                linea_inicial = self.linea
                columna_inicial = self.columna

                (
                    lexema,
                    nuevo_puntero,
                    tipo,
                    valido
                ) = estado_leyendo_puntuacion(
                    self.fuente,
                    self.puntero
                )

                self.puntero = nuevo_puntero

                if valido:
                    self.tokens.append(
                        Token(
                            tipo=tipo,
                            lexema=lexema,
                            linea=linea_inicial,
                            columna=columna_inicial
                        )
                    )
                else:
                    self._registrar_error(
                        f"Puntuación inválida: '{lexema}'",
                        linea_inicial,
                        columna_inicial
                    )

                self._actualizar_posicion(lexema)
                continue

            # Carácter no reconocido.
            linea_inicial = self.linea
            columna_inicial = self.columna

            self._registrar_error(
                f"Carácter ilegal: '{char}'",
                linea_inicial,
                columna_inicial
            )

            self._avanzar_caracter(char)

        return self.tokens

    def _clasificar_identificador(self, lexema):
        """
        Determina si un lexema corresponde a una palabra reservada,
        literal booleano o identificador.

        Args:
            lexema (str): Lexema leído.

        Returns:
            str: Tipo de token.
        """

        if lexema in self.LITERALES_BOOLEANOS:
            return "BOOL_LITERAL"

        if lexema in self.PALABRAS_RESERVADAS:
            return self.PALABRAS_RESERVADAS[lexema]

        return "ID"

    def _ignorar_comentario(self):
        """
        Implementa q11.

        Consume caracteres desde '#' hasta antes del salto de línea.
        El comentario no genera ningún token.
        """

        while self.puntero < len(self.fuente):

            char = self.fuente[self.puntero]

            if char == "\n":
                break

            self._avanzar_caracter(char)

    def _avanzar_caracter(self, char):
        """
        Avanza un carácter y actualiza línea y columna.

        Args:
            char (str): Carácter que será consumido.
        """

        self.puntero += 1

        if char == "\n":
            self.linea += 1
            self.columna = 1
        else:
            self.columna += 1

    def _actualizar_posicion(self, lexema):
        """
        Actualiza la posición después de consumir un lexema.

        Se utiliza cuando una función del DFA ya avanzó el puntero.

        Args:
            lexema (str): Lexema consumido.
        """

        for char in lexema:

            if char == "\n":
                self.linea += 1
                self.columna = 1
            else:
                self.columna += 1

    def _registrar_error(self, mensaje, linea, columna):
        """
        Registra un error léxico.

        Args:
            mensaje (str): Descripción del error.
            linea (int): Línea del error.
            columna (int): Columna del error.
        """

        error = {
            "mensaje": mensaje,
            "linea": linea,
            "columna": columna,
        }

        self.errores.append(error)

        print(
            f"Error léxico en línea {linea}, "
            f"columna {columna}: {mensaje}"
        )