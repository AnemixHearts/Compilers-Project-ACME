from dataclasses import dataclass
from typing import Optional


@dataclass
class Symbol:
    """
    Representa una entrada de la tabla de símbolos.

    Durante la fase léxica solamente conocemos con certeza
    el nombre y la línea donde apareció. Los demás campos
    quedan preparados para fases posteriores.
    """

    name: str
    type: Optional[str] = None
    size: Optional[int] = None
    dimension: Optional[int] = None
    declaration_line: Optional[int] = None
    usage_line: Optional[int] = None
    address: Optional[str] = None


class SymbolTable:
    """
    Tabla de símbolos del compilador.

    Contiene:
        - palabras reservadas del lenguaje
        - identificadores encontrados durante el escaneo
        - literales booleanos

    Las palabras reservadas no se insertan como identificadores.
    """

    # Palabras reservadas y operadores lógicos.
    KEYWORDS = {
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
    BOOLEAN_LITERALS = {
        "True",
        "False",
    }

    def __init__(self):
        # Diccionario:
        # nombre del identificador -> Symbol
        self.symbols = {}

    def lookup(self, name):
        """
        Busca un identificador en la tabla.

        Args:
            name (str): Nombre del identificador.

        Returns:
            Symbol | None:
                Entrada encontrada o None.
        """

        return self.symbols.get(name)

    def lookup_keyword(self, lexema):
        """
        Busca un lexema en la tabla de palabras reservadas.

        Args:
            lexema (str): Lexema leído.

        Returns:
            str | None:
                Tipo de token de la palabra reservada,
                o None si no es palabra reservada.
        """

        return self.KEYWORDS.get(lexema)

    def is_boolean_literal(self, lexema):
        """
        Determina si un lexema es un literal booleano.

        Args:
            lexema (str): Lexema leído.

        Returns:
            bool: True si es True o False.
        """

        return lexema in self.BOOLEAN_LITERALS

    def insert(self, name, line=None):
        """
        Inserta un identificador si todavía no existe.

        Args:
            name (str): Nombre del identificador.
            line (int | None): Línea donde aparece por primera vez.

        Returns:
            Symbol:
                Entrada existente o recién creada.
        """

        existing = self.lookup(name)

        if existing is not None:
            return existing

        symbol = Symbol(
            name=name,
            declaration_line=line
        )

        self.symbols[name] = symbol

        return symbol

    def contains(self, name):
        """
        Indica si un identificador ya existe.

        Args:
            name (str): Nombre del identificador.

        Returns:
            bool: True si existe, False en otro caso.
        """

        return name in self.symbols

    def all_symbols(self):
        """
        Devuelve todas las entradas de la tabla.

        Returns:
            list[Symbol]: Lista de símbolos registrados.
        """

        return list(self.symbols.values())

    def clear(self):
        """
        Vacía la tabla de símbolos.
        """

        self.symbols.clear()

    def __len__(self):
        """
        Permite usar len(symbol_table).
        """

        return len(self.symbols)