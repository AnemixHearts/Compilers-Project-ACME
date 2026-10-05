from ..io.reader import Reader
from ..lexer.scanner import Scanner


def probar_string_a_scanner():
    codigo = 'printf("Hola mundo"); int a = 10;'

    fuente = Reader.read_string(codigo)
    scanner = Scanner(fuente)
    tokens = scanner.escanear()

    tipos_esperados = [
        "PRINTF",
        "L_PAREN",
        "STRING_LITERAL",
        "R_PAREN",
        "SEMICOLON",
        "INT",
        "ID",
        "ASSIGN",
        "INTEGER",
        "SEMICOLON",
    ]

    tipos_obtenidos = [token.tipo for token in tokens]

    print("\n- Prueba 1: Reader string -> Scanner -")

    for token in tokens:
        print(
            f"{token.tipo:16} "
            f"{token.lexema!r:24} "
            f"línea={token.linea} "
            f"columna={token.columna}"
        )

    assert tipos_obtenidos == tipos_esperados
    assert len(tokens) == 10
    assert scanner.errores == []

    print("Integración desde string correcta.")


def probar_archivo_a_scanner():
    ruta = "example_lexer.src"

    codigo = (
        'printf("This is an example");\n'
        'int contador = 10;\n'
        'print(contador);\n'
    )

    # Crear archivo temporal.
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write(codigo)

    try:
        fuente = Reader.read_file(ruta)

        scanner = Scanner(fuente)
        tokens = scanner.escanear()

        tipos_esperados = [
            "PRINTF",
            "L_PAREN",
            "STRING_LITERAL",
            "R_PAREN",
            "SEMICOLON",
            "INT",
            "ID",
            "ASSIGN",
            "INTEGER",
            "SEMICOLON",
            "PRINT",
            "L_PAREN",
            "ID",
            "R_PAREN",
            "SEMICOLON",
        ]

        tipos_obtenidos = [token.tipo for token in tokens]

        print("\n- Prueba 2: Reader archivo -> Scanner -")

        for token in tokens:
            print(
                f"{token.tipo:16} "
                f"{token.lexema!r:24} "
                f"línea={token.linea} "
                f"columna={token.columna}"
            )

        assert tipos_obtenidos == tipos_esperados
        assert len(tokens) == 15
        assert scanner.errores == []

        # Verificar que los identificadores se registraron.
        assert scanner.symbol_table.lookup("contador") is not None

        # Las keywords no deben estar en la tabla.
        assert scanner.symbol_table.lookup("int") is None
        assert scanner.symbol_table.lookup("print") is None

        print("Integración desde archivo correcta.")

    finally:
        import os

        if os.path.exists(ruta):
            os.remove(ruta)


if __name__ == "__main__":
    probar_string_a_scanner()
    probar_archivo_a_scanner()

    print("\nTodas las pruebas de integración fueron exitosas.")