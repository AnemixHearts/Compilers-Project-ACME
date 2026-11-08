
"""
Nodo del árbol de análisis sintáctico (Parse Tree).

Cada nodo representa:
- Un símbolo gramatical.
- Un token, cuando representa un terminal.
- Una lista de nodos hijos.
- Un atributo sintetizado para el análisis semántico.
"""

class ASTNode:

    def __init__(self, symbol, token=None, line=None):
        """
        Inicializa un nodo del árbol sintáctico.

        Args:
            symbol (str): Símbolo gramatical, por ejemplo S, E, F, int.
            token (Token | None): Token asociado si es un terminal.
            line (int | None): Línea asociada al nodo.
        """

        self.symbol = symbol
        self.token = token
        self.children = []

        # Atributo sintetizado que utilizará el SDT.
        self.data_type = "void"

        # Nuestro Token utiliza el atributo 'linea'.
        if token is not None:
            self.line = token.linea
        else:
            self.line = line if line is not None else 1

    def add_child(self, child_node):
        """
        Agrega un nodo hijo conservando el orden de derivación.
        """

        if not isinstance(child_node, ASTNode):
            raise TypeError("El hijo debe ser un objeto ASTNode.")

        self.children.append(child_node)

    def __repr__(self):
        return (
            f"ASTNode(symbol={self.symbol!r}, "
            f"children={len(self.children)}, "
            f"data_type={self.data_type!r}, "
            f"line={self.line})"
        )
