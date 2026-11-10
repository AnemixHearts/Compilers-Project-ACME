
import unittest

from ..lexer.scanner import Scanner
from ..parser.grammar import (
    TOKEN_CATEGORIES,
    LEXER_TOKEN_TYPES,
    PRODUCTIONS,
    FIRST,
    FOLLOW,
    PARSING_TABLE,
    map_lookahead,
)


class TestGrammar(unittest.TestCase):

    def test_categorias_y_catalogo(self):
        self.assertEqual(len(TOKEN_CATEGORIES), 7)
        self.assertEqual(len(LEXER_TOKEN_TYPES), 40)
        self.assertEqual(len(PRODUCTIONS), 24)

    def test_first_y_follow(self):
        self.assertIn("int", FIRST["Program"])
        self.assertIn("Identifier", FIRST["Program"])
        self.assertIn("printf", FIRST["Program"])
        self.assertIn("ε", FIRST["Program"])

        self.assertEqual(FOLLOW["Program"], {"$"})

    def test_tabla_ll1(self):
        self.assertGreater(len(PARSING_TABLE), 0)

        self.assertEqual(
            PARSING_TABLE[("Program", "int")],
            ("StmtList",)
        )

        self.assertEqual(
            PARSING_TABLE[("Stmt", "printf")],
            ("PrintStmt",)
        )

        self.assertIn(
            ("E'", "and"),
            PARSING_TABLE
        )

        self.assertIn(
            ("E'", "or"),
            PARSING_TABLE
        )

    def test_adaptacion_de_tokens(self):
        codigo = 'int x = 10 + 3.14 * (True) and not False;'

        scanner = Scanner(codigo)
        tokens = scanner.escanear()

        self.assertEqual(scanner.errores, [])

        lookaheads = [
            map_lookahead(token)
            for token in tokens
        ]

        esperados = [
            "int",
            "Identifier",
            "=",
            "Constants",
            "+",
            "Constants",
            "*",
            "(",
            "Literals",
            ")",
            "and",
            "not",
            "Literals",
            ";"
        ]

        self.assertEqual(lookaheads, esperados)


if __name__ == "__main__":
    unittest.main()
