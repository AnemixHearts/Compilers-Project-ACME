
import unittest

from ..lexer.scanner import Scanner
from ..parser.ll1_parser import LL1Parser


class TestLL1Parser(unittest.TestCase):

    def analizar(self, codigo):

        scanner = Scanner(codigo)
        tokens = scanner.escanear()

        self.assertEqual(
            scanner.errores,
            [],
            "La entrada contiene errores léxicos."
        )

        parser = LL1Parser()
        resultado = parser.parse(tokens)

        return parser, resultado

    def test_declaracion_simple(self):

        parser, (ok, root, error_line) = self.analizar(
            "int x = 10;"
        )

        self.assertTrue(ok)
        self.assertIsNotNone(root)
        self.assertIsNone(error_line)
        self.assertEqual(root.symbol, "Program")

    def test_declaracion_sin_inicializar(self):

        parser, (ok, root, error_line) = self.analizar(
            "int contador;"
        )

        self.assertTrue(ok)
        self.assertIsNotNone(root)

    def test_asignacion(self):

        parser, (ok, root, error_line) = self.analizar(
            "x = x + 5;"
        )

        self.assertTrue(ok)
        self.assertIsNotNone(root)

    def test_printf(self):

        parser, (ok, root, error_line) = self.analizar(
            'printf("Hola", 10);'
        )

        self.assertTrue(ok)
        self.assertIsNotNone(root)

    def test_if_else(self):

        codigo = """
        if (True) {
            int x = 10;
        } else {
            printf("No se cumple");
        }
        """

        parser, (ok, root, error_line) = self.analizar(codigo)

        self.assertTrue(ok)
        self.assertIsNotNone(root)

    def test_while(self):

        codigo = """
        while (True) {
            x = x + 1;
        }
        """

        parser, (ok, root, error_line) = self.analizar(codigo)

        self.assertTrue(ok)
        self.assertIsNotNone(root)

    def test_for(self):

        codigo = """
        for (int i = 0; i < 10; i = i + 1) {
            printf(i);
        }
        """

        parser, (ok, root, error_line) = self.analizar(codigo)

        self.assertTrue(ok)
        self.assertIsNotNone(root)

    def test_operadores_logicos(self):

        codigo = """
        if (True and not False or False) {
            printf("Correcto");
        }
        """

        parser, (ok, root, error_line) = self.analizar(codigo)

        self.assertTrue(ok)
        self.assertIsNotNone(root)

    def test_falta_punto_y_coma(self):

        parser, (ok, root, error_line) = self.analizar(
            "int x = 10"
        )

        self.assertFalse(ok)
        self.assertIsNone(root)
        self.assertIsNotNone(error_line)
        self.assertIsNotNone(parser.error_message)

    def test_operador_mal_ubicado(self):

        parser, (ok, root, error_line) = self.analizar(
            "int x = * 10;"
        )

        self.assertFalse(ok)
        self.assertIsNone(root)
        self.assertIsNotNone(error_line)

    def test_traza(self):

        parser, (ok, root, error_line) = self.analizar(
            "int x = 10;"
        )

        self.assertTrue(ok)
        self.assertGreater(len(parser.trace), 0)

        ultima_accion = parser.trace[-1]["action"]

        self.assertEqual(
            ultima_accion,
            "Parsing Success!"
        )

        for row in parser.trace:
            self.assertIn("step", row)
            self.assertIn("stack", row)
            self.assertIn("input", row)
            self.assertIn("action", row)


if __name__ == "__main__":
    unittest.main()
