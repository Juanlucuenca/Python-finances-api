def convert_to_float(value):
    try:
        if "," in value:
            formatted_value = value.replace(".", "").replace(",", ".")
            return float(formatted_value)
        else:
            return value
    except ValueError:
        return value