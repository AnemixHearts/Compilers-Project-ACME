
from flask import Flask, render_template, request

from ..io.writer import Writer
from ..main import run_compiler


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():

    # Valores iniciales de la página.
    codigo = ""
    resultado = None

    tokens = []
    tokens_con_categoria = []
    errores = []
    symbol_table = []
    categorias = []

    # Catálogo original de tokens.
    catalogo_tokens = {}

    for tipo, categoria in Writer.CATEGORIAS.items():
        catalogo_tokens.setdefault(categoria, []).append(tipo)

    # Procesar el formulario.
    if request.method == "POST":

        codigo = request.form.get("codigo", "")

        # Ejecutar Lexer -> Parser -> SDT.
        resultado = run_compiler(codigo)

        # Obtener los resultados del compilador.
        tokens = resultado["tokens"]
        errores = resultado["lexical_errors"]
        symbol_table = resultado["symbol_table"]

        # Obtener las categorías para mostrar los tokens.
        writer = Writer()

        tokens_con_categoria = [
            (
                token,
                writer.obtener_categoria(token.tipo)
            )
            for token in tokens
        ]

        categorias = sorted({
            categoria
            for _, categoria in tokens_con_categoria
        })

    # Calcular el total de errores.
    total_errores = len(errores)

    if resultado is not None:
        if resultado["status"] in ("syntax_error", "semantic_error"):
            total_errores += 1

    return render_template(
        "index.html",

        codigo=codigo,
        resultado=resultado,

        # Lexer.
        tokens=tokens,
        tokens_con_categoria=tokens_con_categoria,
        errores=errores,

        # Tabla de símbolos.
        symbol_table=symbol_table,

        # Catálogo.
        categorias=categorias,
        catalogo_tokens=catalogo_tokens,

        # Resumen.
        total_tokens_soportados=len(Writer.CATEGORIAS),
        total_tokens=len(tokens),
        total_errores=total_errores
    )


if __name__ == "__main__":
    app.run(debug=True)
