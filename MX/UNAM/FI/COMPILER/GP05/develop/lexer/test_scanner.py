from scanner import Scanner


def probar_ejemplo_pdf():
    codigo = 'printf("This is an example"); int a = 10;'

    scanner = Scanner(codigo)
    tokens = scanner.escanear()

    print("=== Prueba 1: Ejemplo del PDF ===")
    print("Código:")
    print(codigo)
    print("\nTokens:")

    for token in tokens:
        print(
            f"{token.tipo:16} "
            f"{token.lexema!r:24} "
            f"línea={token.linea} "
            f"columna={token.columna}"
        )

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

    assert tipos_obtenidos == tipos_esperados
    assert len(tokens) == 10
    assert scanner.errores == []


def probar_palabras_reservadas():
    codigo = (
        "Start if then else while for from to "
        "print printf read int real string bool "
        "and or not True False"
    )

    scanner = Scanner(codigo)
    tokens = scanner.escanear()

    print("\n=== Prueba 2: Palabras reservadas ===")

    for token in tokens:
        print(f"{token.lexema:10} -> {token.tipo}")

    tipos_esperados = [
        "START",
        "IF",
        "THEN",
        "ELSE",
        "WHILE",
        "FOR",
        "FROM",
        "TO",
        "PRINT",
        "PRINTF",
        "READ",
        "INT",
        "REAL",
        "STRING_TYPE",
        "BOOL_TYPE",
        "AND",
        "OR",
        "NOT",
        "BOOL_LITERAL",
        "BOOL_LITERAL",
    ]

    tipos_obtenidos = [token.tipo for token in tokens]

    assert tipos_obtenidos == tipos_esperados
    assert scanner.errores == []


def probar_identificadores():
    codigo = "contador contador1 _nombre dato_2"

    scanner = Scanner(codigo)
    tokens = scanner.escanear()

    print("\n=== Prueba 3: Identificadores ===")

    for token in tokens:
        print(f"{token.lexema:10} -> {token.tipo}")

    tipos_esperados = [
        "ID",
        "ID",
        "ID",
        "ID",
    ]

    tipos_obtenidos = [token.tipo for token in tokens]

    assert tipos_obtenidos == tipos_esperados
    assert scanner.errores == []


def probar_numeros():
    codigo = "10 256 3.14 0.5"

    scanner = Scanner(codigo)
    tokens = scanner.escanear()

    print("\n=== Prueba 4: Números ===")

    for token in tokens:
        print(f"{token.lexema:10} -> {token.tipo}")

    tipos_esperados = [
        "INTEGER",
        "INTEGER",
        "REAL_NUMBER",
        "REAL_NUMBER",
    ]

    tipos_obtenidos = [token.tipo for token in tokens]

    assert tipos_obtenidos == tipos_esperados
    assert scanner.errores == []


def probar_operadores():
    codigo = "+ - * / = == != < > <= >="

    scanner = Scanner(codigo)
    tokens = scanner.escanear()

    print("\n=== Prueba 5: Operadores ===")

    for token in tokens:
        print(f"{token.lexema:3} -> {token.tipo}")

    tipos_esperados = [
        "PLUS",
        "MINUS",
        "MULT",
        "DIV",
        "ASSIGN",
        "EQ",
        "NEQ",
        "LT",
        "GT",
        "LEQ",
        "GEQ",
    ]

    tipos_obtenidos = [token.tipo for token in tokens]

    assert tipos_obtenidos == tipos_esperados
    assert scanner.errores == []


def probar_puntuacion():
    codigo = "( ) { } ; ,"

    scanner = Scanner(codigo)
    tokens = scanner.escanear()

    print("\n=== Prueba 6: Puntuación ===")

    for token in tokens:
        print(f"{token.lexema} -> {token.tipo}")

    tipos_esperados = [
        "L_PAREN",
        "R_PAREN",
        "L_BRACE",
        "R_BRACE",
        "SEMICOLON",
        "COMMA",
    ]

    tipos_obtenidos = [token.tipo for token in tokens]

    assert tipos_obtenidos == tipos_esperados
    assert scanner.errores == []


def probar_comentarios_y_espacios():
    codigo = """
int a = 10; # este es un comentario
print(a);
"""

    scanner = Scanner(codigo)
    tokens = scanner.escanear()

    print("\n=== Prueba 7: Comentarios y espacios ===")

    for token in tokens:
        print(f"{token.lexema:10} -> {token.tipo}")

    tipos_esperados = [
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

    assert tipos_obtenidos == tipos_esperados
    assert scanner.errores == []


def probar_error_lexico():
    codigo = "int a = 10; ! @ $"

    scanner = Scanner(codigo)
    tokens = scanner.escanear()

    print("\n=== Prueba 8: Errores léxicos ===")

    for error in scanner.errores:
        print(
            f"Línea {error['linea']}, "
            f"columna {error['columna']}: "
            f"{error['mensaje']}"
        )

    tipos_esperados = [
        "INT",
        "ID",
        "ASSIGN",
        "INTEGER",
        "SEMICOLON",
    ]

    tipos_obtenidos = [token.tipo for token in tokens]

    assert tipos_obtenidos == tipos_esperados
    assert len(scanner.errores) == 3


if __name__ == "__main__":
    probar_ejemplo_pdf()
    probar_palabras_reservadas()
    probar_identificadores()
    probar_numeros()
    probar_operadores()
    probar_puntuacion()
    probar_comentarios_y_espacios()
    probar_error_lexico()

    print("\nTodas las pruebas del Scanner fueron exitosas.")