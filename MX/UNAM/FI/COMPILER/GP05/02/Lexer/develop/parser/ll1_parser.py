
"""
Analizador sintáctico predictivo descendente LL(1).

Utiliza:
- Una pila explícita.
- Un búfer de entrada de tokens.
- Una tabla de análisis LL(1).
- Un árbol sintáctico construido con ASTNode.

Registra una sola acción por iteración, conservando
el estado de la pila y de la entrada antes de cada operación.
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

        Returns:
            tuple:
                (True, parse_tree, None) si tiene éxito.
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

        # 1. PREPARAR EL BÚFER DE ENTRADA

        if tokens:
            last_line = tokens[-1].linea
            last_column = (
                tokens[-1].columna + len(tokens[-1].lexema)
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

          # 2. INICIALIZAR EL ÁRBOL SINTÁCTICO

        root = ASTNode(START_SYMBOL, line=1)

        end_node = ASTNode(
            END_MARKER,
            line=last_line
        )

        # El último elemento es el tope de la pila.
        stack = [
            (END_MARKER, end_node),
            (START_SYMBOL, root)
        ]

        idx = 0
        step = 1

        # 3. ALGORITMO PREDICTIVO LL(1)

        while stack:

            # Guardar el estado ANTES de ejecutar la acción.
            stack_before = [
                symbol for symbol, _ in stack
            ]

            input_idx_before = idx

            if idx >= len(input_buffer):

                self.error_line = last_line

                self.error_message = (
                    "El búfer de entrada terminó inesperadamente."
                )

                self._record_trace(
                    step,
                    stack_before,
                    input_buffer,
                    input_idx_before,
                    "Error: fin inesperado del búfer."
                )

                return False, None, self.error_line

            # Obtener símbolo del tope.
            top_symbol, top_node = stack[-1]

            # Obtener token actual.
            current_token = input_buffer[idx]

            # Obtener símbolo de preanálisis.
            lookahead = map_lookahead(current_token)

               # CASO 1: ACEPTACIÓN

            if (
                top_symbol == END_MARKER
                and lookahead == END_MARKER
            ):

                self._record_trace(
                    step,
                    stack_before,
                    input_buffer,
                    input_idx_before,
                    "Parsing Success!"
                )

                stack.pop()

                return True, root, None

               # CASO 2: EL TOPE ES UN TERMINAL

            if top_symbol in self.terminals:

                if top_symbol == lookahead:

                    action = (
                        f"Match {top_symbol} "
                        f"({current_token.lexema!r})"
                    )

                    # Asociar el token original con la hoja.
                    top_node.token = current_token
                    top_node.line = current_token.linea

                    # Consumir terminal y avanzar entrada.
                    stack.pop()
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
                        stack_before,
                        input_buffer,
                        input_idx_before,
                        "Error: discrepancia de terminal."
                    )

                    return False, None, self.error_line

            # CASO 3: EL TOPE ES UN NO TERMINAL

            else:

                production = self.table.get(
                    (top_symbol, lookahead)
                )

                # No existe producción en la tabla.
                if production is None:

                    self.error_line = current_token.linea

                    self.error_message = (
                        f"No existe producción para "
                        f"M[{top_symbol}, {lookahead}]."
                    )

                    self._record_trace(
                        step,
                        stack_before,
                        input_buffer,
                        input_idx_before,
                        "Error: celda vacía en la tabla LL(1)."
                    )

                    return False, None, self.error_line

                # Aplicar la producción.
                stack.pop()

                if production:

                    # Crear nodos hijos en orden gramatical.
                    child_nodes = [
                        ASTNode(
                            symbol,
                            line=current_token.linea
                        )
                        for symbol in production
                    ]

                    # Agregar hijos al árbol.
                    for child in child_nodes:
                        top_node.add_child(child)

                    # Apilar en orden inverso.
                    for child in reversed(child_nodes):
                        stack.append(
                            (child.symbol, child)
                        )

                # Construir descripción de la producción.
                production_text = (
                    " ".join(production)
                    if production
                    else "ε"
                )

                action = (
                    f"{top_symbol} → {production_text}"
                )

            # REGISTRO ÚNICO DE LA ITERACIÓN

            # Esta llamada se realiza exactamente una vez
            # por iteración exitosa del algoritmo.
            #
            # Utiliza stack_before e input_idx_before,
            # por lo que registra el estado previo a la acción.

            self._record_trace(
                step,
                stack_before,
                input_buffer,
                input_idx_before,
                action
            )

            step += 1

        # Si la pila se vacía sin alcanzar EOF.
        self.error_line = last_line

        self.error_message = (
            "El análisis terminó sin aceptar EOF."
        )

        return False, None, self.error_line

    # 4. REGISTRO DE LA TRAZA

    def _record_trace(
        self,
        step,
        stack_symbols,
        input_buffer,
        idx,
        action
    ):
        """
        Registra una iteración del Parser.

        Cada fila representa el estado anterior
        a la acción que se va a ejecutar.
        """

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

    def get_trace(self):
        """
        Devuelve la traza del último análisis.
        """

        return list(self.trace)
