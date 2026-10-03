from symbol_table.symtab import SymbolTable


def probar_lookup_vacio():
    tabla = SymbolTable()

    resultado = tabla.lookup("contador")

    print("\n- Prueba 1: Lookup en tabla vacía -")
    print("Resultado:", resultado)

    assert resultado is None
    assert len(tabla) == 0


def probar_insertar_simbolo():
    tabla = SymbolTable()

    simbolo = tabla.insert("contador", line=2)

    print("\n- Prueba 2: Insertar símbolo -")
    print("Nombre:", simbolo.name)
    print("Línea declaración:", simbolo.declaration_line)

    assert simbolo.name == "contador"
    assert simbolo.declaration_line == 2
    assert tabla.contains("contador")
    assert len(tabla) == 1


def probar_lookup_existente():
    tabla = SymbolTable()

    tabla.insert("contador", line=2)

    resultado = tabla.lookup("contador")

    print("\n- Prueba 3: Lookup existente -")
    print("Nombre:", resultado.name)

    assert resultado is not None
    assert resultado.name == "contador"
    assert resultado.declaration_line == 2


def probar_no_duplicar_simbolos():
    tabla = SymbolTable()

    primero = tabla.insert("contador", line=2)
    segundo = tabla.insert("contador", line=5)

    print("\n- Prueba 4: No duplicar símbolos -")
    print("Primer objeto:", primero)
    print("Segundo objeto:", segundo)
    print("Cantidad de símbolos:", len(tabla))

    assert primero is segundo
    assert len(tabla) == 1
    assert segundo.declaration_line == 2


def probar_identificadores_diferentes():
    tabla = SymbolTable()

    tabla.insert("a", line=1)
    tabla.insert("contador", line=2)
    tabla.insert("_temp", line=3)

    print("\n- Prueba 5: Identificadores diferentes -")

    for simbolo in tabla.all_symbols():
        print(
            f"{simbolo.name} -> "
            f"línea {simbolo.declaration_line}"
        )

    assert len(tabla) == 3
    assert tabla.contains("a")
    assert tabla.contains("contador")
    assert tabla.contains("_temp")


def probar_limpiar_tabla():
    tabla = SymbolTable()

    tabla.insert("a", line=1)
    tabla.insert("b", line=2)

    tabla.clear()

    print("\n- Prueba 6: Limpiar tabla -")
    print("Cantidad de símbolos:", len(tabla))

    assert len(tabla) == 0
    assert tabla.lookup("a") is None
    assert tabla.lookup("b") is None

def probar_lookup_keyword():
    tabla = SymbolTable()

    tipo = tabla.lookup_keyword("printf")
    no_keyword = tabla.lookup_keyword("contador")

    print("\n- Prueba 7: Lookup de palabras reservadas -")
    print("printf ->", tipo)
    print("contador ->", no_keyword)

    assert tipo == "PRINTF"
    assert no_keyword is None

    # Las keywords no deben entrar como identificadores.
    assert len(tabla) == 0


def probar_literal_booleano():
    tabla = SymbolTable()

    print("\n- Prueba 8: Literales booleanos -")

    assert tabla.is_boolean_literal("True") is True
    assert tabla.is_boolean_literal("False") is True
    assert tabla.is_boolean_literal("true") is False
    assert tabla.is_boolean_literal("contador") is False

    print("True  -> BOOL_LITERAL")
    print("False -> BOOL_LITERAL")

if __name__ == "__main__":
    probar_lookup_vacio()
    probar_insertar_simbolo()
    probar_lookup_existente()
    probar_no_duplicar_simbolos()
    probar_identificadores_diferentes()
    probar_limpiar_tabla()
    probar_lookup_keyword()
    probar_literal_booleano()

    print("\nTodas las pruebas de la tabla de símbolos fueron exitosas.")