
"""
Tabla de símbolos del compilador.

Se comparte entre el Lexer y el analizador semántico SDT.

El Lexer registra los identificadores con información pendiente (TBD).
El SDT consulta y actualiza sus atributos cuando valida declaraciones
y referencias a variables.
"""

from dataclasses import dataclass, field
from typing import Optional

# 1. REPRESENTACIÓN DE UN SÍMBOLO

@dataclass
class Symbol:
    """
    Representa una entrada de la tabla de símbolos.
    """

    name: str

    # Atributos pendientes hasta la validación semántica.
    type: str = "TBD"
    size: int | str = "TBD"
    dimension: int | str = "TBD"

    # Línea de primera aparición; se actualiza al confirmar
    # la declaración semánticamente.
    declaration_line: Optional[int] = None

    # Lista de líneas donde se utiliza el identificador.
    line_usage: list[int] = field(default_factory=list)

    # Dirección de memoria asignada por el SDT.
    address: str = "TBD"

    @property
    def usage_line(self):
        """
        Compatibilidad con la versión anterior de Symbol.

        Devuelve la última línea de uso o None.
        """

        if not self.line_usage:
            return None

        return self.line_usage[-1]

    @usage_line.setter
    def usage_line(self, line):
        if line is None:
            self.line_usage.clear()
        elif line not in self.line_usage:
            self.line_usage.append(line)

    @property
    def line_decl(self):
        """Alias para mantener compatibilidad con el diseño SDT."""

        return self.declaration_line

    @line_decl.setter
    def line_decl(self, line):
        self.declaration_line = line


# 2. TABLA DE SÍMBOLOS

class SymbolTable:
    """
    Tabla de símbolos del compilador.

    Responsabilidades:
    - Registrar identificadores encontrados por el Lexer.
    - Consultar identificadores.
    - Identificar palabras reservadas y booleanos.
    - Actualizar atributos mediante set().
    - Limpiar entradas mediante reset().
    """

    # Tamaños en bytes definidos por el ejemplo de implementación
    # del documento de diseño.
    TYPE_SIZES = {
        "int": 4,
        "real": 8,
        "bool": 1,
        "string": 16
    }

    VALID_TYPES = frozenset(TYPE_SIZES)

    # Palabras reservadas y operadores lógicos del Lexer actual.
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
        "not": "NOT"
    }

    BOOLEAN_LITERALS = {
        "True",
        "False"
    }

    BASE_ADDRESS = 0x1000

    # 3. INICIALIZACIÓN

    def __init__(self):
        self.symbols = {}

        # Próxima dirección disponible.
        self.next_address = self.BASE_ADDRESS

    # 4. BÚSQUEDA E INSERCIÓN

    def lookup(self, name):
        """
        Busca un identificador.

        Returns:
            Symbol | None
        """

        return self.symbols.get(name)

    def lookup_keyword(self, lexema):
        """
        Busca una palabra reservada.

        Returns:
            str | None: Tipo de token o None.
        """

        return self.KEYWORDS.get(lexema)

    def is_boolean_literal(self, lexema):
        """
        Comprueba si el lexema es True o False.
        """

        return lexema in self.BOOLEAN_LITERALS

    def insert(self, name, line=None):
        """
        Registra un identificador encontrado por el Lexer.

        Los atributos semánticos comienzan como TBD.
        No se duplican identificadores existentes.

        Args:
            name (str): Nombre del identificador.
            line (int | None): Línea de primera aparición.

        Returns:
            Symbol: Entrada existente o recién creada.
        """

        if not isinstance(name, str) or not name:
            raise ValueError("El nombre del símbolo no es válido.")

        existing = self.lookup(name)

        if existing is not None:
            return existing

        symbol = Symbol(
            name=name,
            declaration_line=line
        )

        self.symbols[name] = symbol

        return symbol

    # 5. ACTUALIZACIÓN DE ATRIBUTOS

    def set(
        self,
        name,
        data_type=None,
        dimension=None,
        line_usage=None,
        line_decl=None
    ):
        """
        Actualiza los atributos de un identificador.

        Se utiliza principalmente desde el SDT.

        Args:
            name: Nombre del identificador.
            data_type: Tipo confirmado.
            dimension: Dimensión de la variable.
            line_usage: Línea donde se utiliza.
            line_decl: Línea real de declaración.

        Returns:
            bool: True si se actualizó correctamente.
        """

        entry = self.lookup(name)

        if entry is None:
            return False

        # Actualizar tipo y reservar memoria.
        if data_type is not None:

            if data_type not in self.VALID_TYPES:
                raise ValueError(
                    f"Tipo de dato no válido: {data_type}"
                )

            # No permitir declarar nuevamente un símbolo
            # que ya tiene un tipo confirmado.
            if entry.type != "TBD":
                return False

            entry.type = data_type

            entry.size = self.TYPE_SIZES[data_type]

            entry.dimension = (
                0 if dimension is None else dimension
            )

            entry.address = hex(self.next_address)

            self.next_address += entry.size

        elif dimension is not None:
            entry.dimension = dimension

        # Actualizar la línea real de declaración.
        if line_decl is not None:
            entry.declaration_line = line_decl

        # Registrar líneas de uso sin duplicarlas.
        if line_usage is not None:

            if line_usage not in entry.line_usage:
                entry.line_usage.append(line_usage)

        return True

    # 6. REINICIO DE LA TABLA

    def reset(self, scope_names=None):
        """
        Reinicia la tabla de símbolos.

        Args:
            scope_names (iterable | None):
                Si es None, elimina todos los símbolos.
                Si recibe nombres, elimina solamente esos símbolos.

        Returns:
            int: Cantidad de entradas eliminadas.
        """

        if scope_names is None:

            removed = len(self.symbols)

            self.symbols.clear()

            self.next_address = self.BASE_ADDRESS

            return removed

        if isinstance(scope_names, str):
            scope_names = [scope_names]

        removed = 0

        for name in scope_names:

            if name in self.symbols:
                del self.symbols[name]
                removed += 1

        return removed

    # 7. FUNCIONES AUXILIARES

    def contains(self, name):
        """
        Comprueba si un identificador está registrado.
        """

        return name in self.symbols

    def all_symbols(self):
        """
        Devuelve todas las entradas de la tabla.
        """

        return list(self.symbols.values())

    def clear(self):
        """
        Mantiene compatibilidad con la implementación anterior.

        Limpia toda la tabla y reinicia las direcciones.
        """

        return self.reset()

    def __len__(self):
        return len(self.symbols)
