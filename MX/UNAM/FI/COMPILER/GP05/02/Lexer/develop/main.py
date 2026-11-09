import argparse

from .io.reader import Reader
from .lexer.scanner import Scanner
from .io.writer import Writer
from .parser.ll1_parser import LL1Parser
from .sdt.analyzer import SDTAnalyzer


def run_compiler(source_code):
    """
    Ejecuta el proceso completo del compilador:

        Reader -> Lexer -> Parser -> SDT

    Args:
        source_code (str): Código fuente.

    Returns:
        dict: Resultados de cada etapa.
    """

    # 1. ANÁLISIS LÉXICO

    source = Reader.read_string(source_code)

    scanner = Scanner(source)
    tokens = scanner.escanear()

    result = {
        "status": None,
        "tokens": tokens,
        "lexical_errors": scanner.errores,
        "symbol_table": scanner.symbol_table.all_symbols(),
        "parse_ok": None,
        "parse_tree": None,
        "syntax_error_line": None,
        "syntax_error_message": None,
        "sdt_ok": None,
        "sdt_error_line": None,
        "sdt_error_message": None,
        "trace": [],
        "messages": []
    }

    # No continuar si existen errores léxicos.
    if scanner.errores:
        result["status"] = "lexical_error"
        result["messages"] = [
            "Lexical error..."
        ]
        return result

    # 2. ANÁLISIS SINTÁCTICO

    parser = LL1Parser()

    parse_ok, parse_tree, syntax_line = parser.parse(tokens)

    result["parse_ok"] = parse_ok
    result["parse_tree"] = parse_tree
    result["syntax_error_line"] = syntax_line
    result["syntax_error_message"] = parser.error_message
    result["trace"] = parser.get_trace()

    if not parse_ok:

        result["status"] = "syntax_error"

        result["messages"] = [
            "Parsing error...",
            f"error in line {syntax_line}"
        ]

        return result

    # 3. ANÁLISIS SEMÁNTICO (SDT)

    analyzer = SDTAnalyzer(scanner.symbol_table)

    sdt_ok, sdt_line = analyzer.verify(parse_tree)

    result["sdt_ok"] = sdt_ok
    result["sdt_error_line"] = sdt_line
    result["sdt_error_message"] = analyzer.error_message

    # Actualizar la tabla después del SDT.
    result["symbol_table"] = scanner.symbol_table.all_symbols()

    if not sdt_ok:

        result["status"] = "semantic_error"

        result["messages"] = [
            "Parsing Success!",
            "SDT error...",
            f"error in line {sdt_line}"
        ]

        return result

    # 4. COMPILACIÓN EXITOSA

    result["status"] = "success"

    result["messages"] = [
        "Parsing Success!",
        "SDT Verified!"
    ]

    return result


def run_compiler_from_file(file_path):
    """
    Ejecuta el compilador completo a partir de un archivo.
    """

    source_code = Reader.read_file(file_path)

    return run_compiler(source_code)


def ejecutar_desde_string(codigo, salida=None):
    """
    Ejecuta el analizador léxico usando una cadena como entrada.

    Args:
        codigo (str): Código fuente.
        salida (str | None): Archivo de salida opcional.

    Returns:
        Scanner: Scanner utilizado durante el análisis.
    """

    fuente = Reader.read_string(codigo)

    scanner = Scanner(fuente)
    tokens = scanner.escanear()

    writer = Writer()

    writer.escribir(
        tokens,
        scanner.errores,
        salida
    )

    return scanner


def ejecutar_desde_archivo(ruta_entrada, salida=None):
    """
    Ejecuta el analizador léxico usando un archivo como entrada.

    Args:
        ruta_entrada (str): Ruta del archivo de código fuente.
        salida (str | None): Archivo de salida opcional.

    Returns:
        Scanner: Scanner utilizado durante el análisis.
    """

    fuente = Reader.read_file(ruta_entrada)

    scanner = Scanner(fuente)
    tokens = scanner.escanear()

    writer = Writer()

    writer.escribir(
        tokens,
        scanner.errores,
        salida
    )

    return scanner


def construir_parser():
    """
    Construye el parser de argumentos de la aplicación.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Analizador léxico manual del proyecto de Compiladores."
        )
    )

    entrada = parser.add_mutually_exclusive_group()

    entrada.add_argument(
        "-s",
        "--string",
        dest="codigo",
        help="Código fuente escrito directamente como cadena."
    )

    entrada.add_argument(
        "-f",
        "--file",
        dest="archivo",
        help="Ruta del archivo de código fuente."
    )

    parser.add_argument(
        "-o",
        "--output",
        dest="salida",
        default=None,
        help="Ruta opcional para guardar el reporte."
    )

    return parser


def main():
    """
    Punto de entrada principal de la aplicación.
    """

    parser = construir_parser()
    args = parser.parse_args()

    # Si se proporciona una cadena.
    if args.codigo is not None:
        ejecutar_desde_string(
            args.codigo,
            args.salida
        )
        return

    # Si se proporciona un archivo.
    if args.archivo is not None:
        try:
            ejecutar_desde_archivo(
                args.archivo,
                args.salida
            )

        except FileNotFoundError:
            print(
                f"Error: no se encontró el archivo "
                f"'{args.archivo}'."
            )

        except OSError as error:
            print(
                f"Error al leer el archivo: {error}"
            )

        return

    # Sin argumentos: ejecutar el ejemplo del PDF.
    ejemplo = 'printf("This is an example"); int a = 10;'

    print("No se especificó una entrada.")
    print("Ejecutando el ejemplo del PDF:")
    print()

    ejecutar_desde_string(
        ejemplo,
        args.salida
    )


if __name__ == "__main__":
    main()