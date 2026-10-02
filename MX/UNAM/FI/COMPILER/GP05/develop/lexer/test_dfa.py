from dfa import estado_leyendo_literal


def probar_literal_correcto():
    codigo = '"Hola mundo";'

    lexema, puntero, cerrado = estado_leyendo_literal(codigo, 0)

    print("- Prueba 1: Literal correcto -")
    print("Código:", codigo)
    print("Lexema:", lexema)
    print("Puntero:", puntero)
    print("Cerrado:", cerrado)
    print("Siguiente carácter:", codigo[puntero])

    assert lexema == '"Hola mundo"'
    assert cerrado is True
    assert codigo[puntero] == ';'


def probar_literal_sin_cierre():
    codigo = '"Hola mundo;'

    lexema, puntero, cerrado = estado_leyendo_literal(codigo, 0)

    print("\n- Prueba 2: Literal sin cierre -")
    print("Código:", codigo)
    print("Lexema:", lexema)
    print("Puntero:", puntero)
    print("Cerrado:", cerrado)

    assert lexema == '"Hola mundo;'
    assert cerrado is False


if __name__ == "__main__":
    probar_literal_correcto()
    probar_literal_sin_cierre()

    print("\nTodas las pruebas fueron exitosas.")