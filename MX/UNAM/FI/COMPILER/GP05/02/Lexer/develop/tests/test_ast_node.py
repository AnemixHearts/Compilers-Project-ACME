
import unittest

from ..models.ast_node import ASTNode
from ..models.token import Token


class TestASTNode(unittest.TestCase):

    def test_crear_nodo(self):
        node = ASTNode("Program")

        self.assertEqual(node.symbol, "Program")
        self.assertEqual(node.children, [])
        self.assertEqual(node.data_type, "void")
        self.assertEqual(node.line, 1)

    def test_crear_nodo_con_token(self):
        token = Token("INT", "int", 3, 5)
        node = ASTNode("int", token=token)

        self.assertEqual(node.symbol, "int")
        self.assertIs(node.token, token)
        self.assertEqual(node.line, 3)

    def test_agregar_hijos(self):
        parent = ASTNode("DeclStmt")
        child1 = ASTNode("Type")
        child2 = ASTNode("Identifier")

        parent.add_child(child1)
        parent.add_child(child2)

        self.assertEqual(len(parent.children), 2)
        self.assertIs(parent.children[0], child1)
        self.assertIs(parent.children[1], child2)

    def test_linea_de_nodo(self):
        node = ASTNode("Expression", line=7)

        self.assertEqual(node.line, 7)

    def test_rechazar_hijo_invalido(self):
        node = ASTNode("Program")

        with self.assertRaises(TypeError):
            node.add_child("DeclStmt")


if __name__ == "__main__":
    unittest.main()
