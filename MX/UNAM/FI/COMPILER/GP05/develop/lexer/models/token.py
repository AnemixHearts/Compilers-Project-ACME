from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    """
    Representa un token producido por el analizador léxico.

    Attributes:
        tipo (str): Tipo del token.
        lexema (str): Texto original reconocido.
        linea (int): Línea donde comienza el token.
        columna (int): Columna donde comienza el token.
    """

    tipo: str
    lexema: str
    linea: int
    columna: int