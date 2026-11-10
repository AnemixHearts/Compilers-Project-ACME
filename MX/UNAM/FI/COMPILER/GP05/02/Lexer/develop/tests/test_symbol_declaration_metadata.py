import unittest

from symbol_table.symtab import SymbolTable


class SymbolDeclarationMetadataTests(unittest.TestCase):
    def setUp(self):
        self.table = SymbolTable()

    def test_lexer_insert_sets_first_appearance_only(self):
        symbol = self.table.insert("x", line=3)

        self.assertEqual(symbol.first_appearance_line, 3)
        self.assertIsNone(symbol.declaration_line)
        self.assertEqual(symbol.type, "TBD")

    def test_semantic_confirmation_sets_declaration_line(self):
        symbol = self.table.insert("x", line=3)

        updated = self.table.set(
            "x",
            data_type="int",
            dimension=0,
            line_decl=3,
        )

        self.assertTrue(updated)
        self.assertEqual(symbol.first_appearance_line, 3)
        self.assertEqual(symbol.declaration_line, 3)
        self.assertEqual(symbol.type, "int")
        self.assertEqual(symbol.size, 4)

    def test_failed_declaration_can_remain_without_declaration_line(self):
        # Simula el registro léxico de un identificador cuya declaración
        # no llegó a confirmarse por el análisis semántico.
        symbol = self.table.insert("x", line=1)

        self.assertEqual(symbol.first_appearance_line, 1)
        self.assertIsNone(symbol.declaration_line)
        self.assertEqual(symbol.type, "TBD")
        self.assertEqual(symbol.size, "TBD")


if __name__ == "__main__":
    unittest.main()
