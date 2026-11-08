
"""
Analizador semántico mediante Traducción Dirigida por Sintaxis (SDT).

Recorre el árbol sintáctico construido por LL1Parser y verifica:

- Declaraciones y redeclaraciones.
- Variables no declaradas.
- Compatibilidad de tipos.
- Operaciones aritméticas, relacionales y lógicas.
- Condiciones de if, while y for.
- Uso de identificadores.
- Ámbitos de bloques.

La evaluación de expresiones se realiza de abajo hacia arriba,
utilizando atributos sintetizados.
"""

from ..models.ast_node import ASTNode


class SDTAnalyzer:

    def __init__(self, symbol_table):
        """
        Inicializa el analizador semántico.

        Args:
            symbol_table: Tabla de símbolos compartida con el Lexer.
        """

        self.symtab = symbol_table
        self.error_line = None
        self.error_message = None

    # 1. MÉTODOS GENERALES

    def verify(self, root_node):
        """
        Ejecuta el análisis semántico sobre el árbol sintáctico.

        Args:
            root_node (ASTNode): Raíz del Parse Tree.

        Returns:
            tuple:
                (True, None) si no existen errores semánticos.
                (False, error_line) si encuentra un error.
        """

        self.error_line = None
        self.error_message = None

        if not isinstance(root_node, ASTNode):
            self._fail(
                "La raíz proporcionada no es un ASTNode.",
                1
            )
            return False, self.error_line

        success = self._evaluate_node(root_node)

        return success, self.error_line

    def _fail(self, message, line):
        """
        Registra el primer error semántico encontrado.
        """

        if self.error_message is None:
            self.error_message = message
            self.error_line = line if line is not None else 1

        return False

    @staticmethod
    def _node_line(node):
        """
        Obtiene la línea asociada a un nodo.
        """

        if node is None:
            return 1

        return getattr(node, "line", 1) or 1

    def _declared_names(self):
        """
        Obtiene los identificadores que ya tienen un tipo confirmado.
        """

        return {
            symbol.name
            for symbol in self.symtab.all_symbols()
            if symbol.type != "TBD"
        }

    def _get_type_name(self, type_node):
        """
        Obtiene el nombre del tipo a partir de un nodo Type.

        Ejemplo:
            Type
             └── int
        """

        if not type_node.children:
            return None

        terminal = type_node.children[0]

        if terminal.token is None:
            return None

        return terminal.token.lexema

    # 2. RECORRIDO GENERAL DEL ÁRBOL

    def _evaluate_node(self, node):
        """
        Evalúa un nodo del árbol según su símbolo gramatical.
        """

        symbol = node.symbol

        # Programa y listas de sentencias

        if symbol in ("Program", "StmtList"):

            for child in node.children:

                if not self._evaluate_node(child):
                    return False

            return True

        if symbol == "Stmt":

            if len(node.children) != 1:
                return self._fail(
                    "Estructura inválida de una sentencia.",
                    self._node_line(node)
                )

            return self._evaluate_node(node.children[0])

        # Declaraciones y asignaciones

        if symbol == "DeclStmt":
            return self._evaluate_declaration(node)

        if symbol == "DeclRest":
            return self._evaluate_decl_rest(node)

        if symbol in ("AssignStmt", "ForUpdate"):
            return self._evaluate_assignment(node)

        if symbol == "ForInit":
            return self._evaluate_for_init(node)

        # Impresión

        if symbol == "PrintStmt":
            return self._evaluate_print(node)

        if symbol == "ArgList":
            return self._evaluate_arg_list(node)

        # Estructuras de control

        if symbol == "IfStmt":
            return self._evaluate_if(node)

        if symbol == "ElsePart":
            return self._evaluate_else(node)

        if symbol == "WhileStmt":
            return self._evaluate_while(node)

        if symbol == "ForStmt":
            return self._evaluate_for(node)

        # Expresiones

        if symbol in ("E", "R", "A", "T", "F"):
            return self._evaluate_expression(node)

        return self._fail(
            f"No existe una regla SDT para el nodo '{symbol}'.",
            self._node_line(node)
        )

    # 3. DECLARACIONES

    def _evaluate_declaration(self, node):
        """
        Evalúa:

            DeclStmt -> Type Identifier DeclRest ;
        """

        if len(node.children) != 4:
            return self._fail(
                "Estructura inválida de declaración.",
                self._node_line(node)
            )

        type_node = node.children[0]
        id_node = node.children[1]
        rest_node = node.children[2]

        declared_type = self._get_type_name(type_node)

        if declared_type not in self.symtab.VALID_TYPES:
            return self._fail(
                "Tipo de dato no válido.",
                self._node_line(type_node)
            )

        if id_node.token is None:
            return self._fail(
                "No se encontró el identificador de la declaración.",
                self._node_line(id_node)
            )

        identifier = id_node.token

        return self._declare(
            identifier,
            declared_type,
            initializer=rest_node,
        )

    def _declare(self, identifier, declared_type, initializer=None):
        """
        Comprueba y registra una declaración.

        Si existe un inicializador, también valida su tipo.
        """

        name = identifier.lexema
        line = identifier.linea

        entry = self.symtab.lookup(name)

        # No permitir redeclaraciones.
        if entry is not None and entry.type != "TBD":
            return self._fail(
                f"Variable '{name}' redeclarada.",
                line
            )

        # El Scanner normalmente ya registró el identificador.
        # Este caso también permite trabajar con identificadores
        # que fueron retirados por el cierre de un bloque.
        if entry is None:
            self.symtab.insert(name, line=line)

        # Validar el inicializador, cuando exista.
        if initializer is not None:

            if not self._evaluate_node(initializer):
                return False

            if (
                initializer.data_type != "void"
                and initializer.data_type != declared_type
            ):
                return self._fail(
                    f"Incompatibilidad de tipos: la variable "
                    f"'{name}' es {declared_type}, pero recibe "
                    f"{initializer.data_type}.",
                    line
                )

        # Confirmar la declaración y asignar memoria.
        updated = self.symtab.set(
            name,
            data_type=declared_type,
            dimension=0,
            line_decl=line
        )

        if not updated:
            return self._fail(
                f"No fue posible registrar la variable '{name}'.",
                line
            )

        return True

    def _evaluate_decl_rest(self, node):
        """
        Evalúa:

            DeclRest -> = E | epsilon

        El atributo data_type será void cuando no exista
        inicialización, o el tipo de E cuando sí exista.
        """

        if not node.children:
            node.data_type = "void"
            return True

        if len(node.children) != 2:
            return self._fail(
                "Estructura inválida de inicialización.",
                self._node_line(node)
            )

        expression = node.children[1]

        if not self._evaluate_expression(expression):
            return False

        node.data_type = expression.data_type

        return True

    # 4. ASIGNACIONES

    def _evaluate_assignment(self, node):
        """
        Evalúa:

            AssignStmt -> Identifier = E ;
            ForUpdate  -> Identifier = E
        """

        if len(node.children) < 3:
            return self._fail(
                "Estructura inválida de asignación.",
                self._node_line(node)
            )

        identifier_node = node.children[0]
        expression = node.children[2]

        if identifier_node.token is None:
            return self._fail(
                "No se encontró el identificador de asignación.",
                self._node_line(identifier_node)
            )

        identifier = identifier_node.token
        name = identifier.lexema

        entry = self.symtab.lookup(name)

        # Verificar que la variable exista y esté declarada.
        if entry is None or entry.type == "TBD":
            return self._fail(
                f"Variable '{name}' no declarada.",
                identifier.linea
            )

        if not self._evaluate_expression(expression):
            return False

        # La asignación requiere tipos idénticos.
        if entry.type != expression.data_type:
            return self._fail(
                f"Incompatibilidad en asignación: "
                f"'{name}' es {entry.type}, pero recibe "
                f"{expression.data_type}.",
                identifier.linea
            )

        self.symtab.set(
            name,
            line_usage=identifier.linea
        )

        return True

    def _evaluate_for_init(self, node):
        """
        Evalúa las dos alternativas:

            ForInit -> Type Identifier = E
            ForInit -> Identifier = E
        """

        if not node.children:
            return self._fail(
                "Inicialización de for vacía.",
                self._node_line(node)
            )

        # Declaración dentro del for.
        if node.children[0].symbol == "Type":

            if len(node.children) != 4:
                return self._fail(
                    "Inicialización de declaración inválida.",
                    self._node_line(node)
                )

            type_node = node.children[0]
            id_node = node.children[1]
            expression = node.children[3]

            declared_type = self._get_type_name(type_node)

            if declared_type not in self.symtab.VALID_TYPES:
                return self._fail(
                    "Tipo no válido en la inicialización de for.",
                    self._node_line(type_node)
                )

            if id_node.token is None:
                return self._fail(
                    "Identificador no válido en for.",
                    self._node_line(id_node)
                )

            return self._declare(
                id_node.token,
                declared_type,
                initializer=expression
            )

        # Asignación de una variable previamente declarada.
        return self._evaluate_assignment(node)

    # 5. IMPRESIÓN Y ARGUMENTOS

    def _evaluate_print(self, node):
        """
        Evalúa:

            PrintStmt -> printf ( E ArgList ) ;
        """

        if len(node.children) != 6:
            return self._fail(
                "Estructura inválida de printf.",
                self._node_line(node)
            )

        expression = node.children[2]
        arguments = node.children[3]

        if not self._evaluate_expression(expression):
            return False

        return self._evaluate_arg_list(arguments)

    def _evaluate_arg_list(self, node):
        """
        Evalúa:

            ArgList -> , E ArgList | epsilon
        """

        if not node.children:
            return True

        if len(node.children) != 3:
            return self._fail(
                "Lista de argumentos inválida.",
                self._node_line(node)
            )

        expression = node.children[1]
        next_arguments = node.children[2]

        if not self._evaluate_expression(expression):
            return False

        return self._evaluate_arg_list(next_arguments)

    # 6. MANEJO DE ÁMBITOS

    def _evaluate_scoped_block(self, stmt_list_node):
        """
        Evalúa un bloque delimitado por llaves.

        Las variables declaradas dentro del bloque se eliminan
        al terminar, conservando las que ya estaban declaradas
        en el ámbito exterior.
        """

        declared_before = self._declared_names()

        success = self._evaluate_node(stmt_list_node)

        declared_after = self._declared_names()

        local_names = declared_after - declared_before

        # Se eliminan las variables locales incluso si se
        # encuentra un error durante la evaluación.
        if local_names:
            self.symtab.reset(local_names)

        return success

    def _evaluate_if(self, node):
        """
        Evalúa:

            IfStmt -> if ( E ) { StmtList } ElsePart
        """

        if len(node.children) != 8:
            return self._fail(
                "Estructura inválida de if.",
                self._node_line(node)
            )

        condition = node.children[2]
        body = node.children[5]
        else_part = node.children[7]

        if not self._evaluate_expression(condition):
            return False

        if condition.data_type != "bool":
            return self._fail(
                "La condición de if debe ser bool.",
                self._node_line(node.children[0])
            )

        if not self._evaluate_scoped_block(body):
            return False

        return self._evaluate_else(else_part)

    def _evaluate_else(self, node):
        """
        Evalúa:

            ElsePart -> else { StmtList } | epsilon
        """

        if not node.children:
            return True

        if len(node.children) != 4:
            return self._fail(
                "Estructura inválida de else.",
                self._node_line(node)
            )

        body = node.children[2]

        return self._evaluate_scoped_block(body)

    def _evaluate_while(self, node):
        """
        Evalúa:

            WhileStmt -> while ( E ) { StmtList }
        """

        if len(node.children) != 7:
            return self._fail(
                "Estructura inválida de while.",
                self._node_line(node)
            )

        condition = node.children[2]
        body = node.children[5]

        if not self._evaluate_expression(condition):
            return False

        if condition.data_type != "bool":
            return self._fail(
                "La condición de while debe ser bool.",
                self._node_line(node.children[0])
            )

        return self._evaluate_scoped_block(body)

    def _evaluate_for(self, node):
        """
        Evalúa:

            ForStmt -> for ( ForInit ; E ; ForUpdate )
                       { StmtList }

        La variable declarada en ForInit permanece disponible
        durante el ciclo, pero se elimina al salir de él.
        """

        if len(node.children) != 11:
            return self._fail(
                "Estructura inválida de for.",
                self._node_line(node)
            )

        init_node = node.children[2]
        condition = node.children[4]
        update_node = node.children[6]
        body = node.children[9]

        declared_before = self._declared_names()

        try:

            if not self._evaluate_for_init(init_node):
                return False

            if not self._evaluate_expression(condition):
                return False

            if condition.data_type != "bool":
                return self._fail(
                    "La condición de for debe ser bool.",
                    self._node_line(node.children[0])
                )

            if not self._evaluate_assignment(update_node):
                return False

            return self._evaluate_scoped_block(body)

        finally:

            # Eliminar declaraciones propias del ciclo.
            declared_after = self._declared_names()

            loop_variables = declared_after - declared_before

            if loop_variables:
                self.symtab.reset(loop_variables)

    # 7. EVALUACIÓN DE EXPRESIONES

    def _evaluate_expression(self, node):
        """
        Evalúa expresiones y asigna el atributo sintetizado
        data_type al nodo correspondiente.
        """

        symbol = node.symbol

        # Niveles de precedencia binaria

        if symbol in ("E", "R", "A", "T"):

            if len(node.children) != 2:
                return self._fail(
                    f"Expresión inválida en {symbol}.",
                    self._node_line(node)
                )

            left_node = node.children[0]
            tail_node = node.children[1]

            if not self._evaluate_expression(left_node):
                return False

            result_type = self._evaluate_operator_tail(
                left_node.data_type,
                tail_node
            )

            if result_type is None:
                return False

            node.data_type = result_type

            return True

        # Factores

        if symbol == "F":
            return self._evaluate_factor(node)

        return self._fail(
            f"Símbolo de expresión desconocido: {symbol}.",
            self._node_line(node)
        )

    def _evaluate_factor(self, node):
        """
        Evalúa:

            F -> ( E )
            F -> not F
            F -> Identifier
            F -> Constants
            F -> Literals
        """

        if not node.children:
            return self._fail(
                "Factor vacío.",
                self._node_line(node)
            )

        first = node.children[0]

        # Constantes numéricas

        if first.symbol == "Constants":

            token = first.token

            if token is None:
                return self._fail(
                    "Constante sin token asociado.",
                    self._node_line(first)
                )

            if token.tipo == "INTEGER":
                node.data_type = "int"
                return True

            if token.tipo == "REAL_NUMBER":
                node.data_type = "real"
                return True

            return self._fail(
                f"Constante numérica desconocida: {token.lexema}.",
                token.linea
            )

        # Literales booleanos y cadenas

        if first.symbol == "Literals":

            token = first.token

            if token is None:
                return self._fail(
                    "Literal sin token asociado.",
                    self._node_line(first)
                )

            if token.tipo == "BOOL_LITERAL":
                node.data_type = "bool"
                return True

            if token.tipo == "STRING_LITERAL":
                node.data_type = "string"
                return True

            return self._fail(
                f"Literal desconocido: {token.lexema}.",
                token.linea
            )

        # Identificadores

        if first.symbol == "Identifier":

            token = first.token

            if token is None:
                return self._fail(
                    "Identificador sin token asociado.",
                    self._node_line(first)
                )

            name = token.lexema

            entry = self.symtab.lookup(name)

            if entry is None or entry.type == "TBD":
                return self._fail(
                    f"Variable '{name}' no declarada.",
                    token.linea
                )

            self.symtab.set(
                name,
                line_usage=token.linea
            )

            node.data_type = entry.type

            return True

        # Negación lógica

        if first.symbol == "not":

            if len(node.children) != 2:
                return self._fail(
                    "Operación not inválida.",
                    self._node_line(first)
                )

            operand = node.children[1]

            if not self._evaluate_expression(operand):
                return False

            if operand.data_type != "bool":
                return self._fail(
                    "El operador not solamente acepta bool.",
                    self._node_line(first)
                )

            node.data_type = "bool"

            return True

        # Expresión entre paréntesis

        if first.symbol == "(":

            if len(node.children) != 3:
                return self._fail(
                    "Expresión entre paréntesis inválida.",
                    self._node_line(node)
                )

            expression = node.children[1]

            if not self._evaluate_expression(expression):
                return False

            node.data_type = expression.data_type

            return True

        return self._fail(
            f"Factor no reconocido: {first.symbol}.",
            self._node_line(first)
        )

    # 8. EVALUACIÓN DE CADENAS DE OPERADORES

    def _evaluate_operator_tail(self, left_type, tail_node):
        """
        Evalúa las cadenas recursivas:

            E' -> and R E' | or R E' | epsilon
            R' -> op A R' | epsilon
            A' -> + T A' | - T A' | epsilon
            T' -> * F T' | / F T' | epsilon

        Mantiene el resultado acumulado de izquierda a derecha.
        """

        current_type = left_type
        current_tail = tail_node

        if not current_tail.children:
            current_tail.data_type = "void"
            return current_type

        while current_tail.children:

            if len(current_tail.children) != 3:
                self._fail(
                    "Cadena de operadores inválida.",
                    self._node_line(current_tail)
                )
                return None

            operator_node = current_tail.children[0]
            right_node = current_tail.children[1]
            next_tail = current_tail.children[2]

            if not self._evaluate_expression(right_node):
                return None

            operator = operator_node.symbol
            right_type = right_node.data_type

            result_type = self._check_binary_type(
                current_type,
                operator,
                right_type
            )

            if result_type is None:

                self._fail(
                    f"Operación incompatible: "
                    f"{current_type} {operator} {right_type}.",
                    self._node_line(operator_node)
                )

                return None

            current_type = result_type
            current_tail.data_type = current_type

            current_tail = next_tail

        current_tail.data_type = "void"

        return current_type

    # 9. MATRIZ DE COMPATIBILIDAD DE TIPOS

    @staticmethod
    def _check_binary_type(left_type, operator, right_type):
        """
        Comprueba una operación binaria de acuerdo con
        la matriz de compatibilidad semántica del proyecto.

        Devuelve:
            Tipo resultante si es válida.
            None si la operación no está permitida.
        """

        # El sistema utiliza tipado estricto.
        if left_type != right_type:
            return None

        # Operaciones aritméticas

        if operator in ("+", "-", "*", "/"):

            if left_type in ("int", "real"):
                return left_type

            if operator == "+" and left_type == "string":
                return "string"

            return None

        # Operaciones relacionales

        if operator in ("<", ">", "<=", ">="):

            if left_type in ("int", "real"):
                return "bool"

            return None

        # Operaciones de igualdad

        if operator in ("==", "!="):

            if left_type in ("int", "real", "string", "bool"):
                return "bool"

            return None

        # Operaciones lógicas

        if operator in ("and", "or"):

            if left_type == "bool":
                return "bool"

            return None

        return None
