
import unittest

from ..symbol_table.symtab import SymbolTable


class TestSymbolTableSDT(unittest.TestCase):

    def setUp(self):
        self.table = SymbolTable()

    def test_simbolo_inicia_como_tbd(self):
        symbol = self.table.insert("x", line=1)

        self.assertEqual(symbol.type, "TBD")
        self.assertEqual(symbol.size, "TBD")
        self.assertEqual(symbol.dimension, "TBD")
        self.assertEqual(symbol.declaration_line, 1)
        self.assertEqual(symbol.line_usage, [])
        self.assertEqual(symbol.address, "TBD")

    def test_declaracion_y_asignacion_de_memoria(self):
        self.table.insert("x", line=1)

        result = self.table.set(
            "x",
            data_type="int",
            dimension=0,
            line_decl=1
        )

        symbol = self.table.lookup("x")

        self.assertTrue(result)
        self.assertEqual(symbol.type, "int")
        self.assertEqual(symbol.size, 4)
        self.assertEqual(symbol.dimension, 0)
        self.assertEqual(symbol.declaration_line, 1)
        self.assertEqual(symbol.address, "0x1000")

    def test_direcciones_consecutivas(self):
        self.table.insert("x", line=1)
        self.table.insert("y", line=2)

        self.table.set("x", data_type="int", line_decl=1)
        self.table.set("y", data_type="real", line_decl=2)

        self.assertEqual(
            self.table.lookup("x").address,
            "0x1000"
        )

        self.assertEqual(
            self.table.lookup("y").address,
            "0x1004"
        )

        self.assertEqual(
            self.table.lookup("y").size,
            8
        )

    def test_tamanos_de_todos_los_tipos(self):
        expected = {
            "int": 4,
            "real": 8,
            "bool": 1,
            "string": 16
        }

        for index, (data_type, size) in enumerate(
            expected.items(), start=1
        ):
            name = f"variable_{index}"

            self.table.insert(name, line=index)

            self.assertTrue(
                self.table.set(
                    name,
                    data_type=data_type,
                    line_decl=index
                )
            )

            self.assertEqual(
                self.table.lookup(name).size,
                size
            )

    def test_registro_de_lineas_de_uso(self):
        self.table.insert("contador", line=1)

        self.table.set("contador", data_type="int")

        self.table.set("contador", line_usage=2)
        self.table.set("contador", line_usage=4)
        self.table.set("contador", line_usage=4)

        symbol = self.table.lookup("contador")

        self.assertEqual(symbol.line_usage, [2, 4])

    def test_compatibilidad_usage_line(self):
        self.table.insert("x", line=1)

        symbol = self.table.lookup("x")

        symbol.usage_line = 3

        self.assertEqual(symbol.usage_line, 3)
        self.assertEqual(symbol.line_usage, [3])

    def test_evitar_redeclaracion(self):
        self.table.insert("x", line=1)

        self.assertTrue(
            self.table.set("x", data_type="int")
        )

        result = self.table.set(
            "x",
            data_type="real"
        )

        self.assertFalse(result)
        self.assertEqual(self.table.lookup("x").type, "int")

    def test_reset_de_un_simbolo(self):
        self.table.insert("x", line=1)
        self.table.insert("y", line=2)

        removed = self.table.reset(["x"])

        self.assertEqual(removed, 1)
        self.assertIsNone(self.table.lookup("x"))
        self.assertIsNotNone(self.table.lookup("y"))

    def test_reset_completo(self):
        self.table.insert("x", line=1)
        self.table.set("x", data_type="int")

        removed = self.table.reset()

        self.assertEqual(removed, 1)
        self.assertEqual(len(self.table), 0)
        self.assertEqual(
            self.table.next_address,
            SymbolTable.BASE_ADDRESS
        )

    def test_rechazar_tipo_invalido(self):
        self.table.insert("x", line=1)

        with self.assertRaises(ValueError):
            self.table.set(
                "x",
                data_type="float"
            )


if __name__ == "__main__":
    unittest.main()
