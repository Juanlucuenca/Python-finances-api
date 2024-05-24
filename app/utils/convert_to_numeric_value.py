def convert_to_numeric_value(valor):
    # Intenta convertir valores numéricos al formato correcto (punto decimal)
    try:
        # Primero, verifica si el valor contiene comas que puedan indicar decimales
        if "," in valor:
            # Elimina puntos que puedan ser separadores de miles
            valor_sin_puntos = valor.replace(".", "")
            # Luego, reemplaza la coma por un punto para el decimal
            return valor_sin_puntos.replace(",", ".")
        else:
            # Devuelve el valor original si no necesita conversión
            return valor
    except ValueError:
        # Devuelve el valor original si ocurre un error en la conversión
        return valor