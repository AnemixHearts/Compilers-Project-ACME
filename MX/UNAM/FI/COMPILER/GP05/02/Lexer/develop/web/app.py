from flask import Flask, render_template, request

from ..io.writer import Writer
from ..lexer.scanner import Scanner


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    codigo = ""
    tokens = []
    tokens_con_categoria = []
    errores = []
    symbol_table = []
    categorias = []

    # Catálogo de los 40 tokens definido por Writer.
    catalogo_tokens = {}

    for tipo, categoria in Writer.CATEGORIAS.items():
        catalogo_tokens.setdefault(categoria, []).append(tipo)

    if request.method == "POST":
        codigo = request.form.get("codigo", "")

        scanner = Scanner(codigo)
        tokens = scanner.escanear()

        errores = scanner.errores
        symbol_table = scanner.symbol_table.all_symbols()

        writer = Writer()

        tokens_con_categoria = [
            (
                token,
                writer.obtener_categoria(token.tipo)
            )
            for token in tokens
        ]

        categorias = sorted(
            {
                categoria
                for _, categoria in tokens_con_categoria
            }
        )

    return render_template(
        "index.html",
        codigo=codigo,
        tokens=tokens,
        tokens_con_categoria=tokens_con_categoria,
        errores=errores,
        symbol_table=symbol_table,
        categorias=categorias,
        catalogo_tokens=catalogo_tokens,
        total_tokens_soportados=len(Writer.CATEGORIAS),
        total_tokens=len(tokens),
        total_errores=len(errores),
    )


if __name__ == "__main__":
    app.run(debug=True)