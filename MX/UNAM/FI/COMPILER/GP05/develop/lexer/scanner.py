from dfa import (
    estado_leyendo_identificador,
    estado_leyendo_numero,
    estado_leyendo_literal,
    estado_leyendo_operador,
    estado_leyendo_puntuacion,
)

from models.token import Token
from symbol_table.symtab import SymbolTable


class Scanner:
    """
    Analizador léxico manual basado en un DFA.

    El scanner recorre el código fuente carácter por carácter,
    utiliza las funciones definidas en dfa.py y genera una lista
    de objetos Token.

    Los espacios, saltos de línea y comentarios iniciados con '#'
    se ignoran y no generan tokens.
    """

    def __init__(self, fuente):
        """
        Inicializa el scanner.

        Args:
            fuente (str): Código fuente que será analizado.
        """

        self.fuente = fuente

        # Puntero de lectura.
        self.puntero = 0

        # Posición actual dentro del código fuente.
        self.linea = 1
        self.columna = 1

        # Lista de tokens reconocidos.
        self.tokens = []

        # Tabla de símbolos.
        self.symbol_table = SymbolTable()

        # Lista de errores léxicos.
        self.errores = []

    def escanear(self):
        """
        Ejecuta el análisis léxico completo.

        Returns:
            list[Token]:
                Lista de tokens reconocidos.
        """

        # q0: estado inicial.
        while self.puntero < len(self.fuente):

            char = self.fuente[self.puntero]

            # q0 -> espacio, tab o salto de línea
            if char.isspace():
                self._avanzar_caracter(char)
                continue

            # q0 -> q11
            # Inicio de comentario.
            if char == "#":
                self._ignorar_comentario()
                continue

            # q0 -> q1
            # Identificador / palabra reservada / booleano.
            if char.isalpha() or char == "_":

                linea_inicial = self.linea
                columna_inicial = self.columna

                (
                    lexema,
                    nuevo_puntero
                ) = estado_leyendo_identificador(
                    self.fuente,
                    self.puntero
                )

                # El DFA ya avanzó el puntero.
                self.puntero = nuevo_puntero

                # Determinar el tipo mediante la tabla de símbolos.
                tipo = self._clasificar_identificador(
                    lexema,
                    linea_inicial
                )

                self.tokens.append(
                    Token(
                        tipo=tipo,
                        lexema=lexema,
                        linea=linea_inicial,
                        columna=columna_inicial
                    )
                )

                # Actualizar línea y columna.
                self._actualizar_posicion(lexema)

                continue

            # q0 -> q2
            # Número entero o real.
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

            # q0 -> q5
            # Literal de cadena.
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

            # q0 -> q7/q8/q9/q10
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

            # q0 -> q12
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

            # Carácter ilegal.
            # Panic Mode Recovery.
            linea_inicial = self.linea
            columna_inicial = self.columna

            self._registrar_error(
                f"Carácter ilegal: '{char}'",
                linea_inicial,
                columna_inicial
            )

            # Descartar carácter inválido y continuar.
            self._avanzar_caracter(char)

        return self.tokens

    def _clasificar_identificador(self, lexema, linea):
        """
        Clasifica un lexema alfanumérico mediante la tabla de símbolos.

        Orden de clasificación:

            1. Literal booleano.
            2. Palabra reservada.
            3. Identificador.

        Los identificadores se insertan en la tabla de símbolos.
        """

        # 1. Literal booleano.
        if self.symbol_table.is_boolean_literal(lexema):
            return "BOOL_LITERAL"

        # 2. Palabra reservada.
        tipo_keyword = self.symbol_table.lookup_keyword(lexema)

        if tipo_keyword is not None:
            return tipo_keyword

        # 3. Identificador.
        self.symbol_table.insert(
            lexema,
            line=linea
        )

        return "ID"

    def _ignorar_comentario(self):
        """
        Implementa el estado q11.

        Consume el contenido del comentario desde '#'
        hasta antes del salto de línea.

        El comentario no genera ningún token.
        """

        while self.puntero < len(self.fuente):

            char = self.fuente[self.puntero]

            # Dejamos el salto de línea para que q0
            # lo procese y actualice correctamente la línea.
            if char == "\n":
                break

            self._avanzar_caracter(char)

    def _avanzar_caracter(self, char):
        """
        Consume un carácter y actualiza línea y columna.

        Args:
            char (str): Carácter consumido.
        """

        self.puntero += 1

        if char == "\n":
            self.linea += 1
            self.columna = 1
        else:
            self.columna += 1

    def _actualizar_posicion(self, lexema):
        """
        Actualiza línea y columna después de consumir un lexema.

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

        El Scanner solamente almacena el error.
        La presentación del error corresponde a Writer.

        Args:
        mensaje (str): Descripción del error.
        linea (int): Línea donde ocurrió.
        columna (int): Columna donde ocurrió.
        """

        error = {
        "mensaje": mensaje,
        "linea": linea,
        "columna": columna,
        }

        self.errores.append(error)