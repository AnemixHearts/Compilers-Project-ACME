from pathlib import Path

from ..io.reader import Reader
from ..lexer.scanner import Scanner
from ..io.writer import Writer


def probar_pipeline_string():
    """
    Prueba el flujo completo usando una cadena.
    """

    codigo = 'printf("This is an example"); int a = 10;'

    # 1. Reader
    fuente = Reader.read_string(codigo)

    # 2. Scanner
    scanner = Scanner(fuente)
    tokens = scanner.escanear()

    # 3. Writer
    writer = Writer()
    reporte = writer.generar_reporte(
        tokens,
        scanner.errores
    )

    print("\n- Prueba 1: Pipeline completo desde string -")
    print(reporte)

    assert len(tokens) == 10
    assert scanner.errores == []

    assert "Total de tokens: 10" in reporte
    assert "PRINTF" in reporte
    assert "STRING_LITERAL" in reporte
    assert "INT" in reporte
    assert "ID" in reporte
    assert "Sin errores léxicos." in reporte


def probar_pipeline_archivo():
    """
    Prueba el flujo completo usando un archivo.
    """

    ruta_entrada = Path("pipeline_input.src")
    ruta_salida = Path("pipeline_output.txt")

    codigo = (
        'printf("Hola mundo");\n'
        'int contador = 10;\n'
        'print(contador);\n'
    )

    ruta_entrada.write_text(
        codigo,
        encoding="utf-8"
    )

    try:
        # 1. Reader
        fuente = Reader.read_file(ruta_entrada)

        # 2. Scanner
        scanner = Scanner(fuente)
        tokens = scanner.escanear()

        # 3. Writer
        writer = Writer()

        reporte = writer.escribir(
            tokens,
            scanner.errores,
            ruta_salida
        )

        print("\n- Prueba 2: Pipeline completo desde archivo -")
        print("Archivo de entrada:", ruta_entrada)
        print("Archivo de salida:", ruta_salida)

        assert len(tokens) == 15
        assert scanner.errores == []

        assert ruta_salida.exists()

        contenido = ruta_salida.read_text(
            encoding="utf-8"
        )

        assert contenido == reporte
        assert "Total de tokens: 15" in contenido

        # Verificar tabla de símbolos.
        assert scanner.symbol_table.lookup("contador") is not None
        assert scanner.symbol_table.lookup("int") is None
        assert scanner.symbol_table.lookup("print") is None

        print("Pipeline completo desde archivo correcto.")

    finally:
        if ruta_entrada.exists():
            ruta_entrada.unlink()

        if ruta_salida.exists():
            ruta_salida.unlink()


def probar_pipeline_con_errores():
    """
    Verifica que los errores pasen correctamente desde Scanner
    hacia Writer.
    """

    codigo = "int a = 10; @ $"

    fuente = Reader.read_string(codigo)

    scanner = Scanner(fuente)
    tokens = scanner.escanear()

    writer = Writer()

    reporte = writer.generar_reporte(
        tokens,
        scanner.errores
    )

    print("\n- Prueba 3: Pipeline con errores -")
    print(reporte)

    assert len(tokens) == 5
    assert len(scanner.errores) == 2

    assert "@"
    assert "$"

    assert "Carácter ilegal: '@'" in reporte
    assert "Carácter ilegal: '$'" in reporte


if __name__ == "__main__":
    probar_pipeline_string()
    probar_pipeline_archivo()
    probar_pipeline_con_errores()

    print("\nTodas las pruebas del pipeline fueron exitosas.")