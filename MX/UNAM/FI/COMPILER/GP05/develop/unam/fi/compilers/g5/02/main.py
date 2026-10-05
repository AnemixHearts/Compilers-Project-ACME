import argparse

from .io.reader import Reader
from .lexer.scanner import Scanner
from .io.writer import Writer


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