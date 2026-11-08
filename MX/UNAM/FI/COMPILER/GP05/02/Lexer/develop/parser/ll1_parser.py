
"""
Analizador sintáctico predictivo descendente LL(1).

Utiliza:
- Una pila explícita.
- Un búfer de entrada de tokens.
- Una tabla de análisis LL(1).
- Un árbol sintáctico construido con ASTNode.

"""

from ..models.ast_node import ASTNode
from ..models.token import Token

from .grammar import (
    END_MARKER,
    START_SYMBOL,
    TERMINALS,
    PARSING_TABLE,
    map_lookahead,
)


class LL1Parser:

    def __init__(self, parsing_table=None, terminals=None):
        """
        Inicializa el Parser LL(1).

        Args:
            parsing_table: Tabla predictiva LL(1).
            terminals: Conjunto de símbolos terminales.
        """

        self.table = (
            parsing_table
            if parsing_table is not None
            else PARSING_TABLE
        )

        self.terminals = (
            terminals
            if terminals is not None
            else TERMINALS
        )

        self.trace = []
        self.error_line = None
        self.error_message = None

    def parse(self, tokens):
        """
        Realiza el análisis sintáctico de una lista de tokens.

        Args:
            tokens (list[Token]): Tokens generados por el Lexer.

        Returns:
            tuple:
                (True, parse_tree, None) si el análisis tiene éxito.
                (False, None, error_line) si encuentra un error.
        """

        # Reiniciar información de ejecuciones anteriores.
        self.trace = []
        self.error_line = None
        self.error_message = None

        tokens = list(tokens)

        for token in tokens:
            if not isinstance(token, Token):
                raise TypeError(
                    "El Parser solamente acepta objetos Token."
                )

        # 1. Preparar el búfer de entrada

        if tokens:
            last_line = tokens[-1].linea
            last_column = tokens[-1].columna + len(
                tokens[-1].lexema
            )
        else:
            last_line = 1
            last_column = 1

        # Agregar el símbolo de fin de entrada.
        eof_token = Token(
            tipo="SPECIAL_CHARACTERS",
            lexema=END_MARKER,
            linea=last_line,
            columna=last_column
        )

        input_buffer = tokens + [eof_token]

        # 2. Inicializar el árbol sintáctico

        root = ASTNode(START_SYMBOL, line=1)

        end_node = ASTNode(
            END_MARKER,
            line=last_line
        )

        # La lista representa la pila:
        # El último elemento es el tope.
        stack = [
            (END_MARKER, end_node),
            (START_SYMBOL, root)
        ]

        idx = 0
        step = 1

        # 3. Algoritmo predictivo LL(1)

        while stack:

            if idx >= len(input_buffer):
                self.error_line = last_line
                self.error_message = (
                    "El búfer de entrada terminó inesperadamente."
                )

                self._record_trace(
                    step,
                    stack,
                    input_buffer,
                    idx,
                    "Error: fin inesperado del búfer."
                )

                return False, None, self.error_line

            # Obtener el símbolo en el tope de la pila.
            top_symbol, top_node = stack[-1]

            stack_before = [
                symbol for symbol, _ in stack
            ]

            # Obtener el token actual.
            current_token = input_buffer[idx]

            # Determinar el símbolo de preanálisis.
            lookahead = map_lookahead(current_token)

            # CASO 1: Aceptación

            if (
                top_symbol == END_MARKER
                and lookahead == END_MARKER
            ):

                self._record_trace(
                    step,
                    stack,
                    input_buffer,
                    idx,
                    "Parsing Success!"
                )

                stack.pop()

                return True, root, None


            # CASO 2: El tope es un terminal

            if top_symbol in self.terminals:

                if top_symbol == lookahead:

                    action = (
                        f"Match {top_symbol} "
                        f"({current_token.lexema!r})"
                    )

                    self._record_trace(
                        step,
                        stack,
                        input_buffer,
                        idx,
                        action
                    )

                    # Asociar el token original con la hoja.
                    top_node.token = current_token
                    top_node.line = current_token.linea

                    # Quitar el terminal de la pila.
                    stack.pop()

                    # Avanzar el búfer de entrada.
                    idx += 1

                else:

                    self.error_line = current_token.linea

                    self.error_message = (
                        f"Se esperaba '{top_symbol}', "
                        f"pero se encontró "
                        f"'{current_token.lexema}'."
                    )

                    self._record_trace(
                        step,
                        stack,
                        input_buffer,
                        idx,
                        "Error: discrepancia de terminal."
                    )

                    return False, None, self.error_line

            # CASO 3: El tope es un no terminal

            else:

                production = self.table.get(
                    (top_symbol, lookahead)
                )

                # Celda vacía en la tabla LL(1).
                if production is None:

                    self.error_line = current_token.linea

                    self.error_message = (
                        f"No existe producción para "
                        f"M[{top_symbol}, {lookahead}]."
                    )

                    self._record_trace(
                        step,
                        stack,
                        input_buffer,
                        idx,
                        "Error: celda vacía en la tabla LL(1)."
                    )

                    return False, None, self.error_line

                # La producción encontrada se aplica.
                stack.pop()

                if production:

                    # Crear los hijos en orden de producción.
                    child_nodes = [
                        ASTNode(
                            symbol,
                            line=current_token.linea
                        )
                        for symbol in production
                    ]

                    # Agregar los hijos al árbol.
                    for child in child_nodes:
                        top_node.add_child(child)

                    # Apilar en orden inverso para procesar
                    # primero el símbolo más a la izquierda.
                    for child in reversed(child_nodes):
                        stack.append(
                            (child.symbol, child)
                        )

                # Registrar la acción realizada.
                if production:
                    production_text = " ".join(production)
                else:
                    production_text = "ε"

                action = (
                    f"{top_symbol} → {production_text}"
                )

            self._record_trace(
                step,
                stack_before,
                input_buffer,
                idx,
                 action,
                 use_saved_stack=True
            )   

            step += 1

        # Si la pila se vacía sin alcanzar la aceptación.
        self.error_line = last_line
        self.error_message = "El análisis terminó sin aceptar EOF."

        return False, None, self.error_line

    def _record_trace(
        self,
        step,
        stack,
        input_buffer,
        idx,
        action,
        use_saved_stack=False
    ):
        """
        Guarda la traza de una iteración.

        La pila se presenta desde la base hasta el tope.
        """

        if use_saved_stack:
            stack_symbols = stack
        else:
            stack_symbols = [
                symbol
                for symbol, _ in stack
            ]

        input_symbols = [
            token.lexema
            for token in input_buffer[idx:]
        ]

        self.trace.append({
            "step": step,
            "stack": " ".join(stack_symbols),
            "input": " ".join(input_symbols),
            "action": action
        })

    def _trace_stack_before(self, stack, top_symbol, production):
        """
        Reconstruye la pila anterior a la aplicación
        de una producción para documentar la traza.
        """

        # En este punto, el no terminal ya fue retirado
        # y los símbolos de la producción ya fueron apilados.
        result = [
            symbol
            for symbol, _ in stack
        ]

        if production:
            for _ in production:
                if result:
                    result.pop()

        result.append(top_symbol)

        return result

    def get_trace(self):
        """
        Devuelve la traza del último análisis.
        """

        return list(self.trace)
