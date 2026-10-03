from pathlib import Path

from ..io.reader import Reader
from ..lexer.scanner import Scanner
from ..io.writer import Writer


def probar_reporte_en_memoria():
    codigo = 'printf("Hola"); int a = 10;'

    fuente = Reader.read_string(codigo)

    scanner = Scanner(fuente)
    tokens = scanner.escanear()

    writer = Writer()

    reporte = writer.generar_reporte(
        tokens,
        scanner.errores
    )

    print("\n- Prueba 1: Reporte en memoria -")
    print(reporte)

    assert "Total de tokens: 10" in reporte
    assert "PRINTF" in reporte
    assert "STRING_LITERAL" in reporte
    assert "INT" in reporte
    assert "ID" in reporte
    assert "Sin errores léxicos." in reporte


def probar_categorias():
    codigo = 'print(a + 10);'

    scanner = Scanner(codigo)
    tokens = scanner.escanear()

    writer = Writer()

    print("\n- Prueba 2: Categorías -")

    categorias = [
        writer.obtener_categoria(token.tipo)
        for token in tokens
    ]

    for token, categoria in zip(tokens, categorias):
        print(
            f"{token.lexema!r:12} -> "
            f"{token.tipo:15} -> "
            f"{categoria}"
        )

    categorias_esperadas = [
        "keyword",
        "punctuation",
        "identifier",
        "operator",
        "constant",
        "punctuation",
        "punctuation",
    ]

    assert categorias == categorias_esperadas


def probar_archivo():
    codigo = 'printf("Hola"); int a = 10;'

    scanner = Scanner(codigo)
    tokens = scanner.escanear()

    writer = Writer()

    ruta = "lexer_output.txt"

    try:
        reporte = writer.generar_reporte(
            tokens,
            scanner.errores
        )

        ruta_generada = writer.escribir_archivo(
            reporte,
            ruta
        )

        print("\n- Prueba 3: Escritura a archivo -")
        print("Archivo:", ruta_generada)

        assert ruta_generada.exists()

        contenido = ruta_generada.read_text(
            encoding="utf-8"
        )

        assert contenido == reporte
        assert "Total de tokens: 10" in contenido

        print("Archivo generado correctamente.")

    finally:
        if Path(ruta).exists():
            Path(ruta).unlink()


def probar_errores():
    codigo = "int a = 10; @ $"

    scanner = Scanner(codigo)
    tokens = scanner.escanear()

    writer = Writer()

    reporte = writer.generar_reporte(
        tokens,
        scanner.errores
    )

    print("\n- Prueba 4: Reporte de errores -")
    print(reporte)

    assert len(scanner.errores) == 2
    assert "@" in reporte
    assert "$" in reporte
    assert "ERRORES LÉXICOS" in reporte


def probar_tipo_desconocido():
    writer = Writer()

    print("\n- Prueba 5: Tipo desconocido -")

    try:
        writer.obtener_categoria("TOKEN_INEXISTENTE")

        assert False, "Se esperaba ValueError."

    except ValueError:
        print("ValueError detectado correctamente.")


if __name__ == "__main__":
    probar_reporte_en_memoria()
    probar_categorias()
    probar_archivo()
    probar_errores()
    probar_tipo_desconocido()

    print("\nTodas las pruebas del Writer fueron exitosas.")