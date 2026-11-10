
import unittest

from ..lexer.scanner import Scanner
from ..parser.ll1_parser import LL1Parser
from ..sdt.analyzer import SDTAnalyzer


class TestSDTAnalyzer(unittest.TestCase):

    def analyze(self, codigo):
        """
        Ejecuta Lexer -> Parser -> SDT.

        Para estas pruebas asumimos que la entrada
        debe ser sintácticamente válida.
        """

        scanner = Scanner(codigo)
        tokens = scanner.escanear()

        self.assertEqual(
            scanner.errores,
            [],
            "La entrada contiene errores léxicos."
        )

        parser = LL1Parser()
        parse_ok, root, syntax_line = parser.parse(tokens)

        self.assertTrue(
            parse_ok,
            f"Error sintáctico en línea {syntax_line}: "
            f"{parser.error_message}"
        )

        analyzer = SDTAnalyzer(scanner.symbol_table)
        sdt_ok, sdt_line = analyzer.verify(root)

        return scanner, analyzer, sdt_ok, sdt_line

    # 1. DECLARACIONES

    def test_declaracion_int(self):

        scanner, analyzer, ok, line = self.analyze(
            "int x = 10;"
        )

        self.assertTrue(ok, analyzer.error_message)

        symbol = scanner.symbol_table.lookup("x")

        self.assertEqual(symbol.type, "int")
        self.assertEqual(symbol.size, 4)
        self.assertEqual(symbol.dimension, 0)

    def test_declaracion_sin_inicializador(self):

        scanner, analyzer, ok, line = self.analyze(
            "int x;"
        )

        self.assertTrue(ok, analyzer.error_message)
        self.assertEqual(
            scanner.symbol_table.lookup("x").type,
            "int"
        )

    def test_declaraciones_de_los_cuatro_tipos(self):

        codigo = """
        int edad = 20;
        real promedio = 9.5;
        string nombre = "Jorge";
        bool activo = True;
        """

        scanner, analyzer, ok, line = self.analyze(codigo)

        self.assertTrue(ok, analyzer.error_message)

        expected = {
            "edad": "int",
            "promedio": "real",
            "nombre": "string",
            "activo": "bool"
        }

        for name, data_type in expected.items():
            self.assertEqual(
                scanner.symbol_table.lookup(name).type,
                data_type
            )

    def test_redeclaracion(self):

        codigo = """
        int x = 10;
        int x = 20;
        """

        scanner, analyzer, ok, line = self.analyze(codigo)

        self.assertFalse(ok)
        self.assertIn("redeclarada", analyzer.error_message)

    def test_incompatibilidad_en_declaracion(self):

        scanner, analyzer, ok, line = self.analyze(
            'int x = "diez";'
        )

        self.assertFalse(ok)
        self.assertIn(
            "Incompatibilidad de tipos",
            analyzer.error_message
        )

    # 2. ASIGNACIONES

    def test_asignacion_valida(self):

        codigo = """
        int x = 10;
        x = 20;
        """

        scanner, analyzer, ok, line = self.analyze(codigo)

        self.assertTrue(ok, analyzer.error_message)

        symbol = scanner.symbol_table.lookup("x")

        self.assertEqual(symbol.type, "int")
        self.assertEqual(symbol.declaration_line, 2)
        self.assertIn(3, symbol.line_usage)

    def test_variable_no_declarada(self):

        scanner, analyzer, ok, line = self.analyze(
            "x = 10;"
        )

        self.assertFalse(ok)
        self.assertIn(
            "no declarada",
            analyzer.error_message
        )

    def test_uso_antes_de_declaracion(self):

        codigo = """
        x = 10;
        int x = 20;
        """

        scanner, analyzer, ok, line = self.analyze(codigo)

        self.assertFalse(ok)
        self.assertIn(
            "no declarada",
            analyzer.error_message
        )

    def test_incompatibilidad_en_asignacion(self):

        codigo = """
        int x = 10;
        x = "Hola";
        """

        scanner, analyzer, ok, line = self.analyze(codigo)

        self.assertFalse(ok)
        self.assertIn(
            "Incompatibilidad en asignación",
            analyzer.error_message
        )

    # 3. EXPRESIONES Y COMPATIBILIDAD DE TIPOS

    def test_operacion_aritmetica_int(self):

        scanner, analyzer, ok, line = self.analyze(
            "int x = 10 + 5 * 2;"
        )

        self.assertTrue(ok, analyzer.error_message)

    def test_no_permitir_operacion_int_real(self):

        scanner, analyzer, ok, line = self.analyze(
            "int x = 10 + 3.14;"
        )

        self.assertFalse(ok)
        self.assertIn(
            "Operación incompatible",
            analyzer.error_message
        )

    def test_concatenacion_de_cadenas(self):

        scanner, analyzer, ok, line = self.analyze(
            'string mensaje = "Hola " + "mundo";'
        )

        self.assertTrue(ok, analyzer.error_message)

    def test_operadores_logicos(self):

        scanner, analyzer, ok, line = self.analyze(
            "bool resultado = True and not False;"
        )

        self.assertTrue(ok, analyzer.error_message)

    def test_comparacion_relacional(self):

        scanner, analyzer, ok, line = self.analyze(
            "bool resultado = 10 < 20;"
        )

        self.assertTrue(ok, analyzer.error_message)

    def test_comparacion_de_cadenas(self):

        scanner, analyzer, ok, line = self.analyze(
            'bool resultado = "a" == "b";'
        )

        self.assertTrue(ok, analyzer.error_message)

    def test_not_solamente_acepta_bool(self):

        scanner, analyzer, ok, line = self.analyze(
            "bool resultado = not 10;"
        )

        self.assertFalse(ok)
        self.assertIn(
            "not solamente acepta bool",
            analyzer.error_message
        )

    # 4. ESTRUCTURAS DE CONTROL

    def test_if_con_condicion_booleana(self):

        codigo = """
        if (True) {
            int x = 10;
        } else {
            printf("No se cumple");
        }
        """

        scanner, analyzer, ok, line = self.analyze(codigo)

        self.assertTrue(ok, analyzer.error_message)

    def test_if_con_condicion_entera(self):

        codigo = """
        if (10) {
            printf("Hola");
        }
        """

        scanner, analyzer, ok, line = self.analyze(codigo)

        self.assertFalse(ok)
        self.assertIn(
            "condición de if debe ser bool",
            analyzer.error_message
        )

    def test_while_con_condicion_booleana(self):

        codigo = """
        while (True) {
            int temporal = 1;
        }
        """

        scanner, analyzer, ok, line = self.analyze(codigo)

        self.assertTrue(ok, analyzer.error_message)

    def test_while_con_condicion_invalida(self):

        codigo = """
        while (10) {
            printf("Hola");
        }
        """

        scanner, analyzer, ok, line = self.analyze(codigo)

        self.assertFalse(ok)
        self.assertIn(
            "condición de while debe ser bool",
            analyzer.error_message
        )

    def test_for_valido(self):

        codigo = """
        for (int i = 0; i < 10; i = i + 1) {
            printf(i);
        }
        """

        scanner, analyzer, ok, line = self.analyze(codigo)

        self.assertTrue(ok, analyzer.error_message)

        # La variable i pertenece al ámbito del for.
        self.assertIsNone(scanner.symbol_table.lookup("i"))

    def test_for_exige_condicion_booleana(self):

        codigo = """
        for (int i = 0; i; i = i + 1) {
            printf(i);
        }
        """

        scanner, analyzer, ok, line = self.analyze(codigo)

        self.assertFalse(ok)
        self.assertIn(
            "condición de for debe ser bool",
            analyzer.error_message
        )

    # 5. ÁMBITOS DE BLOQUES

    def test_variable_local_no_sale_del_bloque(self):

        codigo = """
        if (True) {
            int local = 10;
        }
        local = 20;
        """

        scanner, analyzer, ok, line = self.analyze(codigo)

        self.assertFalse(ok)
        self.assertIn(
            "no declarada",
            analyzer.error_message
        )

    def test_variable_externa_accesible_en_bloque(self):

        codigo = """
        int x = 10;

        if (True) {
            x = 20;
        }

        x = 30;
        """

        scanner, analyzer, ok, line = self.analyze(codigo)

        self.assertTrue(ok, analyzer.error_message)

        self.assertEqual(
            scanner.symbol_table.lookup("x").type,
            "int"
        )

    # 6. PRINTF

    def test_printf_con_argumentos(self):

        codigo = """
        int edad = 20;
        printf("Edad:", edad, True);
        """

        scanner, analyzer, ok, line = self.analyze(codigo)

        self.assertTrue(ok, analyzer.error_message)


if __name__ == "__main__":
    unittest.main()
