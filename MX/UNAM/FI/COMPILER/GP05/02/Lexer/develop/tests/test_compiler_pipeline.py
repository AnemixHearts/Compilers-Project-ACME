
import unittest
from unittest import result

from ..main import run_compiler


class TestCompilerPipeline(unittest.TestCase):

    def test_compilacion_exitosa(self):

        result = run_compiler("int x = 10;")

        self.assertEqual(result["status"], "success")

        self.assertEqual(
            result["messages"],
            ["Parsing Success!", "SDT Verified!"]
        )

        symbol = next(
            s for s in result["symbol_table"]
            if s.name == "x"
        )

        self.assertEqual(symbol.type, "int")

    def test_varias_sentencias(self):

        codigo = """
        int x = 10;
        x = x + 5;
        printf(x);
        """

        result = run_compiler(codigo)

        self.assertEqual(result["status"], "success")
        self.assertTrue(result["parse_ok"])
        self.assertTrue(result["sdt_ok"])

    def test_error_sintactico(self):

        result = run_compiler("int x = * 10;")

        self.assertEqual(result["status"], "syntax_error")
        self.assertFalse(result["parse_ok"])

        self.assertEqual(
            result["messages"][:2],
            ["Parsing error...", "error in line 1"]
        )

        self.assertNotIn("SDT error...", result["messages"])

        self.assertIsNotNone(result["syntax_error_line"])

    def test_error_semantico(self):

        result = run_compiler('int x = "diez";')

        self.assertEqual(result["status"], "semantic_error")
        self.assertTrue(result["parse_ok"])
        self.assertFalse(result["sdt_ok"])

        self.assertEqual(
            result["messages"][:2],
            ["Parsing Success!", "SDT error..."]
        )

        self.assertIsNotNone(result["sdt_error_line"])

    def test_error_lexico(self):

        result = run_compiler("int x = 3.;")

        self.assertEqual(result["status"], "lexical_error")
        self.assertGreater(len(result["lexical_errors"]), 0)

        self.assertIsNone(result["parse_ok"])
        self.assertIsNone(result["sdt_ok"])


if __name__ == "__main__":
    unittest.main()
