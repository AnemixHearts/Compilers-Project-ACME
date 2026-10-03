class Reader:
    """
    Módulo encargado de leer la entrada del analizador léxico.

    Permite obtener el código fuente:
        - desde una cadena
        - desde un archivo de texto
    """

    @staticmethod
    def read_string(source):
        """
        Recibe directamente una cadena de código fuente.

        Args:
            source (str): Código fuente.

        Returns:
            str: Código fuente recibido.
        """

        if not isinstance(source, str):
            raise TypeError("La entrada debe ser una cadena de texto.")

        return source

    @staticmethod
    def read_file(path):
        """
        Lee un archivo de código fuente completo.

        Args:
            path (str): Ruta del archivo.

        Returns:
            str: Contenido completo del archivo.

        Raises:
            FileNotFoundError:
                Si el archivo no existe.
            OSError:
                Si ocurre un error al abrir o leer el archivo.
        """

        with open(path, "r", encoding="utf-8") as archivo:
            return archivo.read()