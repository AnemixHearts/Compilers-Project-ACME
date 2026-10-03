from scanner import Scanner


def probar_40_tokens():
    """
    Verifica que el scanner reconozca los 40 tokens
    definidos para el proyecto.
    """

    # Entrada con exactamente un lexema representativo
    # para cada uno de los 40 tokens.
    codigo = """
(
)
{
}
;
,
+
-
*
/
=
==
!=
<
>
<=
>=
and
or
not
Start
if
then
else
while
for
from
to
print
printf
read
int
real
string
bool
10
3.14
"Hola"
True
variable
"""

    tipos_esperados = [
        # 1-6: Puntuación
        "L_PAREN",
        "R_PAREN",
        "L_BRACE",
        "R_BRACE",
        "SEMICOLON",
        "COMMA",

        # 7-10: Aritméticos
        "PLUS",
        "MINUS",
        "MULT",
        "DIV",

        # 11-17: Asignación / comparación
        "ASSIGN",
        "EQ",
        "NEQ",
        "LT",
        "GT",
        "LEQ",
        "GEQ",

        # 18-20: Lógicos
        "AND",
        "OR",
        "NOT",

        # 21-35: Palabras clave
        "START",
        "IF",
        "THEN",
        "ELSE",
        "WHILE",
        "FOR",
        "FROM",
        "TO",
        "PRINT",
        "PRINTF",
        "READ",
        "INT",
        "REAL",
        "STRING_TYPE",
        "BOOL_TYPE",

        # 36-39: Literales
        "INTEGER",
        "REAL_NUMBER",
        "STRING_LITERAL",
        "BOOL_LITERAL",

        # 40: Identificador
        "ID",
    ]

    scanner = Scanner(codigo)
    tokens = scanner.escanear()

    tipos_obtenidos = [token.tipo for token in tokens]

    print("=== Prueba: 40 tokens ===")
    print()
    print(f"Tokens encontrados: {len(tokens)}")
    print(f"Tokens esperados:   {len(tipos_esperados)}")
    print()

    # Mostrar cada token y compararlo con el esperado.
    for numero, (token, esperado) in enumerate(
        zip(tokens, tipos_esperados),
        start=1
    ):
        resultado = "OK" if token.tipo == esperado else "ERROR"

        print(
            f"{numero:2}. "
            f"{token.lexema!r:12} -> "
            f"{token.tipo:15} "
            f"[esperado: {esperado:15}] "
            f"{resultado}"
        )

    # Verificaciones principales.
    assert len(tokens) == 40
    assert tipos_obtenidos == tipos_esperados
    assert scanner.errores == []

    print()
    print("Los 40 tokens fueron reconocidos correctamente.")


def probar_categorias_principales():
    """
    Verifica un ejemplo representativo de las categorías
    principales del lexer.
    """

    codigo = """
(
+
==
and
print
10
3.14
"Hola mundo"
True
variable
"""

    tipos_esperados = [
        "L_PAREN",
        "PLUS",
        "EQ",
        "AND",
        "PRINT",
        "INTEGER",
        "REAL_NUMBER",
        "STRING_LITERAL",
        "BOOL_LITERAL",
        "ID",
    ]

    scanner = Scanner(codigo)
    tokens = scanner.escanear()

    tipos_obtenidos = [token.tipo for token in tokens]

    print("\n=== Prueba: Categorías principales ===")

    for token in tokens:
        print(
            f"{token.lexema!r:18} -> "
            f"{token.tipo}"
        )

    assert tipos_obtenidos == tipos_esperados
    assert scanner.errores == []

    print("Categorías verificadas correctamente.")


if __name__ == "__main__":
    probar_40_tokens()
    probar_categorias_principales()

    print("\nTodas las pruebas de los 40 tokens fueron exitosas.")