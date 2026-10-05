import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from ..main import (
    construir_parser,
    ejecutar_desde_archivo,
    ejecutar_desde_string,
    main,
)


class TestMain(unittest.TestCase):

    def test_ejecutar_desde_string(self):
        codigo = 'print(a + 10);'

        salida = StringIO()
        with redirect_stdout(salida):
            scanner = ejecutar_desde_string(codigo)

        self.assertEqual(len(scanner.tokens), 7)
        self.assertEqual(
            [token.tipo for token in scanner.tokens],
            [
                "PRINT",
                "L_PAREN",
                "ID",
                "PLUS",
                "INTEGER",
                "R_PAREN",
                "SEMICOLON",
            ],
        )
        self.assertEqual(scanner.errores, [])
        self.assertIn("Total de tokens: 7", salida.getvalue())

    def test_ejecutar_desde_archivo(self):
        codigo = "int a = 10;\nreal b = 3.14;"

        with TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "entrada.txt"
            ruta.write_text(codigo, encoding="utf-8")

            salida = StringIO()
            with redirect_stdout(salida):
                scanner = ejecutar_desde_archivo(str(ruta))

        self.assertEqual(len(scanner.tokens), 10)
        self.assertEqual(scanner.tokens[0].tipo, "INT")
        self.assertEqual(scanner.tokens[1].tipo, "ID")
        self.assertEqual(scanner.tokens[4].tipo, "SEMICOLON")
        self.assertEqual(scanner.tokens[5].tipo, "REAL")
        self.assertEqual(scanner.tokens[8].tipo, "REAL_NUMBER")
        self.assertEqual(scanner.errores, [])
        self.assertIn("Total de tokens: 10", salida.getvalue())

    def test_generar_salida_a_archivo(self):
        codigo = "print(a);"

        with TemporaryDirectory() as directorio:
            ruta_salida = Path(directorio) / "resultado.txt"

            salida = StringIO()
            with redirect_stdout(salida):
                ejecutar_desde_string(codigo, str(ruta_salida))

            self.assertTrue(ruta_salida.exists())

            contenido = ruta_salida.read_text(encoding="utf-8")

        self.assertIn("ANALIZADOR LÉXICO", contenido)
        self.assertIn("Total de tokens: 5", contenido)
        self.assertIn("PRINT", contenido)
        self.assertIn("SEMICOLON", contenido)

    def test_parser_string(self):
        parser = construir_parser()

        args = parser.parse_args(
            ["--string", "print(a);"]
        )

        self.assertEqual(args.codigo, "print(a);")
        self.assertIsNone(args.archivo)
        self.assertIsNone(args.salida)

    def test_parser_file_and_output(self):
        parser = construir_parser()

        args = parser.parse_args(
            [
                "--file",
                "ejemplo.txt",
                "--output",
                "resultado.txt",
            ]
        )

        self.assertEqual(args.archivo, "ejemplo.txt")
        self.assertEqual(args.salida, "resultado.txt")
        self.assertIsNone(args.codigo)

    def test_archivo_inexistente(self):
        ruta_inexistente = "archivo_que_no_existe_lexer.txt"

        with self.assertRaises(FileNotFoundError):
            ejecutar_desde_archivo(ruta_inexistente)

    def test_main_sin_argumentos(self):
        salida = StringIO()

        with patch.object(sys, "argv", ["main.py"]):
            with redirect_stdout(salida):
                main()

        contenido = salida.getvalue()

        self.assertIn("No se especificó una entrada.", contenido)
        self.assertIn("Ejecutando el ejemplo del PDF:", contenido)
        self.assertIn("Total de tokens: 10", contenido)
        self.assertIn("Sin errores léxicos.", contenido)

    def test_main_archivo_inexistente(self):
        salida = StringIO()

        with patch.object(
            sys,
            "argv",
            [
                "main.py",
                "--file",
                "archivo_que_no_existe_lexer.txt",
            ],
        ):
            with redirect_stdout(salida):
                main()

        self.assertIn(
            "Error: no se encontró el archivo",
            salida.getvalue(),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)