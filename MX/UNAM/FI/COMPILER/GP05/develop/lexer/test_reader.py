from reader import Reader


def probar_lectura_string():
    codigo = 'printf("Hola"); int a = 10;'

    resultado = Reader.read_string(codigo)

    print("\n- Prueba 1: Lectura desde string -")
    print("Entrada:", codigo)
    print("Resultado:", resultado)

    assert resultado == codigo


def probar_lectura_archivo():
    ruta = "test_input.src"

    contenido = 'int contador = 25;\nprint(contador);'

    # Crear archivo de prueba.
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write(contenido)

    try:
        resultado = Reader.read_file(ruta)

        print("\n- Prueba 2: Lectura desde archivo -")
        print("Ruta:", ruta)
        print("Contenido:")
        print(resultado)

        assert resultado == contenido

    finally:
        # Eliminar el archivo temporal de prueba.
        import os
        os.remove(ruta)


def probar_archivo_inexistente():
    ruta = "archivo_que_no_existe.src"

    print("\n- Prueba 3: Archivo inexistente -")

    try:
        Reader.read_file(ruta)

        # Si llegamos aquí, no se produjo el error esperado.
        assert False, "Se esperaba FileNotFoundError."

    except FileNotFoundError:
        print("FileNotFoundError detectado correctamente.")


def probar_tipo_invalido():
    print("\n- Prueba 4: Tipo de entrada inválido -")

    try:
        Reader.read_string(123)

        assert False, "Se esperaba TypeError."

    except TypeError:
        print("TypeError detectado correctamente.")


if __name__ == "__main__":
    probar_lectura_string()
    probar_lectura_archivo()
    probar_archivo_inexistente()
    probar_tipo_invalido()

    print("\nTodas las pruebas del Reader fueron exitosas.")