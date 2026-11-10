
import unittest

from ..web.app import app


class TestWebPipeline(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_pagina_principal(self):

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Compilador", response.data)

    def test_compilacion_exitosa(self):

        response = self.client.post(
            "/",
            data={"codigo": "int x = 10;"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Parsing Success!", response.data)
        self.assertIn(b"SDT Verified!", response.data)

    def test_error_sintactico(self):

        response = self.client.post(
            "/",
            data={"codigo": "int x = * 10;"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Parsing error...", response.data)

    def test_error_semantico(self):

        response = self.client.post(
            "/",
            data={"codigo": 'int x = "diez";'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Parsing Success!", response.data)
        self.assertIn(b"SDT error...", response.data)

    def test_error_lexico(self):

        response = self.client.post(
            "/",
            data={"codigo": "int x = 3.;"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Lexical error...", response.data)

    def test_visualizacion_de_traza(self):

        response = self.client.post(
            "/",
            data={"codigo": "int x = 10;"}
        )

        self.assertIn(b"Traza del Parser LL(1)", response.data)
        self.assertIn(b"Stack", response.data)
        self.assertIn(b"Action", response.data)


if __name__ == "__main__":
    unittest.main()
