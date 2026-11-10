
"""
Gramática libre de contexto (CFG) y tabla de análisis LL(1).

Esta gramática corresponde al diseño de 24 reglas del proyecto Parser & SDT,
adaptada a los tokens que genera nuestro Lexer.
"""

# 1. CONSTANTES GENERALES

EPSILON = "ε"
END_MARKER = "$"
START_SYMBOL = "Program"

# 2. CLASIFICACIÓN DE LOS 40 TIPOS DE TOKENS

TOKEN_CATEGORIES = {
    "Keyword": frozenset({
        "START", "IF", "THEN", "ELSE", "WHILE", "FOR",
        "FROM", "TO", "PRINT", "PRINTF", "READ",
        "INT", "REAL", "STRING_TYPE", "BOOL_TYPE"
    }),

    "Identifier": frozenset({
        "ID"
    }),

    "Operator": frozenset({
        "PLUS", "MINUS", "MULT", "DIV", "ASSIGN",
        "EQ", "NEQ", "LT", "GT", "LEQ", "GEQ",
        "AND", "OR", "NOT"
    }),

    "Constants": frozenset({
        "INTEGER", "REAL_NUMBER"
    }),

    "Literals": frozenset({
        "STRING_LITERAL", "BOOL_LITERAL"
    }),

    "Punctuators": frozenset({
        "L_PAREN", "R_PAREN", "L_BRACE",
        "R_BRACE", "SEMICOLON", "COMMA"
    }),

    # Token sintético que agrega el Parser al final de la entrada.
    # No es uno de los 40 tokens generados por el Lexer.
    "Special_Characters": frozenset({
        "SPECIAL_CHARACTERS"
    })
}


# Crear un diccionario inverso:
# tipo de token -> categoría general.

TOKEN_CATEGORY_BY_TYPE = {}

for category, token_types in TOKEN_CATEGORIES.items():
    for token_type in token_types:
        if token_type in TOKEN_CATEGORY_BY_TYPE:
            raise ValueError(
                f"El token {token_type} está en más de una categoría."
            )

        TOKEN_CATEGORY_BY_TYPE[token_type] = category


# Comprobar que el catálogo original del Lexer contiene 40 tipos.
LEXER_TOKEN_TYPES = (
    set(TOKEN_CATEGORY_BY_TYPE)
    - {"SPECIAL_CHARACTERS"}
)

if len(LEXER_TOKEN_TYPES) != 40:
    raise ValueError(
        f"Se esperaban 40 tipos de tokens, "
        f"pero se encontraron {len(LEXER_TOKEN_TYPES)}."
    )

# 3. TERMINALES Y NO TERMINALES

TERMINALS = frozenset({

    # Tipos de datos
    "int", "real", "string", "bool",

    # Palabras reservadas utilizadas en la gramática
    "printf", "if", "else", "while", "for",

    # Categorías generales del Lexer
    "Identifier", "Constants", "Literals",

    # Operadores de asignación, aritméticos,
    # relacionales y lógicos.
    "=",
    "+", "-", "*", "/",
    "and", "or", "not",
    "<", ">", "<=", ">=", "==", "!=",

    # Puntuación
    "(", ")", "{", "}", ";", ",",

    # Fin de entrada
    END_MARKER
})

# 4. GRAMÁTICA (CFG)

# Cada producción se representa mediante una tupla.
# Una tupla vacía () representa epsilon.

PRODUCTIONS = {

    # A. Estructura del programa y sentencias

    # 1. Program -> StmtList
    "Program": [
        ("StmtList",)
    ],

    # 2. StmtList -> Stmt StmtList | epsilon
    "StmtList": [
        ("Stmt", "StmtList"),
        ()
    ],

    # 3. Stmt -> DeclStmt | AssignStmt | PrintStmt
    #           | IfStmt | WhileStmt | ForStmt
    "Stmt": [
        ("DeclStmt",),
        ("AssignStmt",),
        ("PrintStmt",),
        ("IfStmt",),
        ("WhileStmt",),
        ("ForStmt",)
    ],

    # 4. DeclStmt -> Type Identifier DeclRest ;
    "DeclStmt": [
        ("Type", "Identifier", "DeclRest", ";")
    ],

    # 5. DeclRest -> = E | epsilon
    "DeclRest": [
        ("=", "E"),
        ()
    ],

    # 6. AssignStmt -> Identifier = E ;
    "AssignStmt": [
        ("Identifier", "=", "E", ";")
    ],

    # 7. PrintStmt -> printf ( E ArgList ) ;
    "PrintStmt": [
        ("printf", "(", "E", "ArgList", ")", ";")
    ],

    # 8. ArgList -> , E ArgList | epsilon
    "ArgList": [
        (",", "E", "ArgList"),
        ()
    ],

    # 9. IfStmt -> if ( E ) { StmtList } ElsePart
    "IfStmt": [
        ("if", "(", "E", ")", "{", "StmtList", "}", "ElsePart")
    ],

    # 10. ElsePart -> else { StmtList } | epsilon
    "ElsePart": [
        ("else", "{", "StmtList", "}"),
        ()
    ],

    # 11. WhileStmt -> while ( E ) { StmtList }
    "WhileStmt": [
        ("while", "(", "E", ")", "{", "StmtList", "}")
    ],

    # 12. ForStmt -> for ( ForInit ; E ; ForUpdate )
    #                { StmtList }
    "ForStmt": [
        (
            "for", "(", "ForInit", ";",
            "E", ";", "ForUpdate", ")",
            "{", "StmtList", "}"
        )
    ],

    # 13. ForInit -> Type Identifier = E | Identifier = E
    "ForInit": [
        ("Type", "Identifier", "=", "E"),
        ("Identifier", "=", "E")
    ],

    # 14. ForUpdate -> Identifier = E
    "ForUpdate": [
        ("Identifier", "=", "E")
    ],

    # 15. Type -> int | real | string | bool
    "Type": [
        ("int",),
        ("real",),
        ("string",),
        ("bool",)
    ],

    # B. Jerarquía de expresiones

    # 16. E -> R E'
    "E": [
        ("R", "E'")
    ],

    # 17. E' -> and R E' | or R E' | epsilon
    # Adaptación: se utilizan and y or, no && y ||.
    "E'": [
        ("and", "R", "E'"),
        ("or", "R", "E'"),
        ()
    ],

    # 18. R -> A R'
    "R": [
        ("A", "R'")
    ],

    # 19. R' -> operadores relacionales/equidad | epsilon
    "R'": [
        ("<", "A", "R'"),
        (">", "A", "R'"),
        ("<=", "A", "R'"),
        (">=", "A", "R'"),
        ("==", "A", "R'"),
        ("!=", "A", "R'"),
        ()
    ],

    # 20. A -> T A'
    "A": [
        ("T", "A'")
    ],

    # 21. A' -> + T A' | - T A' | epsilon
    "A'": [
        ("+", "T", "A'"),
        ("-", "T", "A'"),
        ()
    ],

    # 22. T -> F T'
    "T": [
        ("F", "T'")
    ],

    # 23. T' -> * F T' | / F T' | epsilon
    "T'": [
        ("*", "F", "T'"),
        ("/", "F", "T'"),
        ()
    ],

    # 24. F -> ( E ) | not F | Identifier | Constants | Literals
    "F": [
        ("(", "E", ")"),
        ("not", "F"),
        ("Identifier",),
        ("Constants",),
        ("Literals",)
    ]
}


NON_TERMINALS = frozenset(PRODUCTIONS)


def validar_simbolos_gramatica():
    """
    Comprueba que todos los símbolos terminales utilizados
    en las producciones estén definidos en TERMINALS.
    """

    simbolos_utilizados = set()

    for alternatives in PRODUCTIONS.values():
        for production in alternatives:
            for symbol in production:
                if symbol not in NON_TERMINALS:
                    simbolos_utilizados.add(symbol)

    simbolos_desconocidos = simbolos_utilizados - TERMINALS

    if simbolos_desconocidos:
        raise ValueError(
            "Hay símbolos sin definir en TERMINALS: "
            f"{sorted(simbolos_desconocidos)}"
        )


def first_of_sequence(sequence, first_sets):
    """
    Calcula FIRST de una secuencia de símbolos.

    sequence:
        Tupla con símbolos gramaticales.

    first_sets:
        Diccionario con los conjuntos FIRST.

    Returns:
        Conjunto FIRST de la secuencia.
    """

    if not sequence:
        return {EPSILON}

    result = set()
    all_nullable = True

    for symbol in sequence:

        if symbol in NON_TERMINALS:
            symbol_first = first_sets[symbol]
        else:
            symbol_first = {symbol}

        result.update(symbol_first - {EPSILON})

        if EPSILON not in symbol_first:
            all_nullable = False
            break

    if all_nullable:
        result.add(EPSILON)

    return result


def compute_first_sets():
    """
    Calcula los conjuntos FIRST de todos los no terminales
    mediante iteraciones hasta que no existan cambios.
    """

    first_sets = {
        non_terminal: set()
        for non_terminal in NON_TERMINALS
    }

    changed = True

    while changed:
        changed = False

        for non_terminal, alternatives in PRODUCTIONS.items():

            for production in alternatives:

                production_first = first_of_sequence(
                    production,
                    first_sets
                )

                previous_size = len(first_sets[non_terminal])

                first_sets[non_terminal].update(
                    production_first
                )

                if len(first_sets[non_terminal]) > previous_size:
                    changed = True

    return {
        non_terminal: frozenset(values)
        for non_terminal, values in first_sets.items()
    }



def compute_follow_sets(first_sets=None):
    """
    Calcula los conjuntos FOLLOW de todos los no terminales.

    El símbolo de fin de entrada se agrega al FOLLOW
    del símbolo inicial.
    """

    if first_sets is None:
        first_sets = compute_first_sets()

    follow_sets = {
        non_terminal: set()
        for non_terminal in NON_TERMINALS
    }

    follow_sets[START_SYMBOL].add(END_MARKER)

    changed = True

    while changed:
        changed = False

        for lhs, alternatives in PRODUCTIONS.items():

            for production in alternatives:

                for index, symbol in enumerate(production):

                    if symbol not in NON_TERMINALS:
                        continue

                    suffix = production[index + 1:]

                    suffix_first = first_of_sequence(
                        suffix,
                        first_sets
                    )

                    previous_size = len(follow_sets[symbol])

                    # Agregar FIRST del sufijo sin epsilon.
                    follow_sets[symbol].update(
                        suffix_first - {EPSILON}
                    )

                    # Si el sufijo deriva en epsilon,
                    # agregar FOLLOW del lado izquierdo.
                    if EPSILON in suffix_first:
                        follow_sets[symbol].update(
                            follow_sets[lhs]
                        )

                    if len(follow_sets[symbol]) > previous_size:
                        changed = True

    return {
        non_terminal: frozenset(values)
        for non_terminal, values in follow_sets.items()
    }


def build_ll1_table(first_sets=None, follow_sets=None):
    """
    Construye la tabla predictiva LL(1).

    Cada entrada tiene la forma:

        (NoTerminal, Lookahead) -> Producción

    Si encuentra una colisión, genera un error porque
    la gramática no sería LL(1).
    """

    if first_sets is None:
        first_sets = compute_first_sets()

    if follow_sets is None:
        follow_sets = compute_follow_sets(first_sets)

    table = {}

    for non_terminal, alternatives in PRODUCTIONS.items():

        for production in alternatives:

            production_first = first_of_sequence(
                production,
                first_sets
            )

            lookaheads = set(
                production_first - {EPSILON}
            )

            # Las producciones epsilon se colocan
            # en las columnas de FOLLOW.
            if EPSILON in production_first:
                lookaheads.update(
                    follow_sets[non_terminal]
                )

            for lookahead in lookaheads:

                key = (non_terminal, lookahead)

                if key in table and table[key] != production:
                    raise ValueError(
                        "Conflicto LL(1) detectado en "
                        f"M[{non_terminal}, {lookahead}]."
                    )

                table[key] = production

    return table


def map_lookahead(token):
    """
    Convierte un Token del Lexer en el símbolo terminal
    que utilizará el Parser.

    No modifica el objeto Token original.
    """

    category = TOKEN_CATEGORY_BY_TYPE.get(token.tipo)

    if category == "Identifier":
        return "Identifier"

    if category == "Constants":
        return "Constants"

    if category == "Literals":
        return "Literals"

    # Las palabras reservadas, operadores y signos de
    # puntuación se identifican mediante su lexema.
    if category in {
        "Keyword",
        "Operator",
        "Punctuators",
        "Special_Characters"
    }:
        return token.lexema

    # Un token desconocido llegará al Parser como un
    # lookahead sin producción válida.
    return token.lexema


STATEMENT_STARTERS = frozenset({
    "int",
    "real",
    "string",
    "bool",
    "Identifier",
    "printf",
    "if",
    "while",
    "for"
})

EXPRESSION_STARTERS = frozenset({
    "(",
    "not",
    "Identifier",
    "Constants",
    "Literals"
})


validar_simbolos_gramatica()

FIRST = compute_first_sets()

FOLLOW = compute_follow_sets(FIRST)

PARSING_TABLE = build_ll1_table(FIRST, FOLLOW)
