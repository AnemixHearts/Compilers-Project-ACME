from dfa import (
    estado_leyendo_identificador,
    estado_leyendo_numero,
    estado_leyendo_literal,
    estado_leyendo_operador,
    estado_leyendo_puntuacion,
)

from models.token import Token


def probar_identificador():
    codigo = "contador123;"

    lexema, puntero = estado_leyendo_identificador(codigo, 0)

    print("- Prueba 1: Identificador -")
    print("Código:", codigo)
    print("Lexema:", lexema)
    print("Puntero:", puntero)
    print("Siguiente carácter:", codigo[puntero])

    assert lexema == "contador123"
    assert puntero == 11
    assert codigo[puntero] == ";"


def probar_entero():
    codigo = "1234;"

    lexema, puntero, tipo, valido = estado_leyendo_numero(codigo, 0)

    print("\n- Prueba 2: Entero -")
    print("Código:", codigo)
    print("Lexema:", lexema)
    print("Tipo:", tipo)
    print("Válido:", valido)
    print("Puntero:", puntero)

    assert lexema == "1234"
    assert puntero == 4
    assert tipo == "INTEGER"
    assert valido is True
    assert codigo[puntero] == ";"


def probar_real():
    codigo = "3.14;"

    lexema, puntero, tipo, valido = estado_leyendo_numero(codigo, 0)

    print("\n- Prueba 3: Real -")
    print("Código:", codigo)
    print("Lexema:", lexema)
    print("Tipo:", tipo)
    print("Válido:", valido)
    print("Puntero:", puntero)

    assert lexema == "3.14"
    assert puntero == 4
    assert tipo == "REAL_NUMBER"
    assert valido is True
    assert codigo[puntero] == ";"


def probar_real_invalido():
    codigo = "3.;"

    lexema, puntero, tipo, valido = estado_leyendo_numero(codigo, 0)

    print("\n- Prueba 4: Real inválido -")
    print("Código:", codigo)
    print("Lexema:", lexema)
    print("Tipo:", tipo)
    print("Válido:", valido)
    print("Puntero:", puntero)

    assert lexema == "3."
    assert puntero == 2
    assert tipo == "REAL_NUMBER"
    assert valido is False


def probar_literal_correcto():
    codigo = '"Hola mundo";'

    lexema, puntero, cerrado = estado_leyendo_literal(codigo, 0)

    print("\n- Prueba 5: Literal correcto -")
    print("Código:", codigo)
    print("Lexema:", lexema)
    print("Puntero:", puntero)
    print("Cerrado:", cerrado)
    print("Siguiente carácter:", codigo[puntero])

    assert lexema == '"Hola mundo"'
    assert puntero == 12
    assert cerrado is True
    assert codigo[puntero] == ";"


def probar_literal_sin_cierre():
    codigo = '"Hola mundo;'

    lexema, puntero, cerrado = estado_leyendo_literal(codigo, 0)

    print("\n- Prueba 6: Literal sin cierre -")
    print("Código:", codigo)
    print("Lexema:", lexema)
    print("Puntero:", puntero)
    print("Cerrado:", cerrado)

    assert lexema == '"Hola mundo;'
    assert puntero == 12
    assert cerrado is False


def probar_operadores():
    casos = [
        ("+", "PLUS"),
        ("-", "MINUS"),
        ("*", "MULT"),
        ("/", "DIV"),
        ("=", "ASSIGN"),
        ("==", "EQ"),
        ("!=", "NEQ"),
        ("<", "LT"),
        (">", "GT"),
        ("<=", "LEQ"),
        (">=", "GEQ"),
    ]

    print("\n- Prueba 7: Operadores -")

    for codigo, tipo_esperado in casos:
        lexema, puntero, tipo, valido = estado_leyendo_operador(
            codigo,
            0
        )

        print(
            f"{codigo:2} -> "
            f"{str(tipo):7} | "
            f"Lexema: {lexema} | "
            f"Válido: {valido}"
        )

        assert lexema == codigo
        assert puntero == len(codigo)
        assert tipo == tipo_esperado
        assert valido is True


def probar_exclamacion_invalida():
    codigo = "!"

    lexema, puntero, tipo, valido = estado_leyendo_operador(
        codigo,
        0
    )

    print("\n- Prueba 8: Operador inválido -")
    print("Código:", codigo)
    print("Lexema:", lexema)
    print("Tipo:", tipo)
    print("Válido:", valido)
    print("Puntero:", puntero)

    assert lexema == "!"
    assert puntero == 1
    assert tipo is None
    assert valido is False


def probar_puntuacion():
    casos = [
        ("(", "L_PAREN"),
        (")", "R_PAREN"),
        ("{", "L_BRACE"),
        ("}", "R_BRACE"),
        (";", "SEMICOLON"),
        (",", "COMMA"),
    ]

    print("\n- Prueba 9: Puntuación -")

    for codigo, tipo_esperado in casos:
        lexema, puntero, tipo, valido = estado_leyendo_puntuacion(
            codigo,
            0
        )

        print(
            f"{codigo} -> "
            f"{tipo:10} | "
            f"Lexema: {lexema} | "
            f"Válido: {valido}"
        )

        assert lexema == codigo
        assert puntero == 1
        assert tipo == tipo_esperado
        assert valido is True


def probar_token():
    token = Token(
        tipo="INT",
        lexema="int",
        linea=1,
        columna=1
    )

    print("\n- Prueba 10: Token -")
    print("Tipo:", token.tipo)
    print("Lexema:", token.lexema)
    print("Línea:", token.linea)
    print("Columna:", token.columna)

    assert token.tipo == "INT"
    assert token.lexema == "int"
    assert token.linea == 1
    assert token.columna == 1


def probar_token_inmutable():
    token = Token(
        tipo="ID",
        lexema="contador",
        linea=2,
        columna=5
    )

    print("\n- Prueba 11: Token inmutable -")

    try:
        token.tipo = "INT"
        assert False, "El Token debería ser inmutable."
    except AttributeError:
        print("El Token es inmutable correctamente.")


if __name__ == "__main__":
    probar_identificador()
    probar_entero()
    probar_real()
    probar_real_invalido()
    probar_literal_correcto()
    probar_literal_sin_cierre()
    probar_operadores()
    probar_exclamacion_invalida()
    probar_puntuacion()
    probar_token()
    probar_token_inmutable()

    print("\nTodas las pruebas fueron exitosas.")