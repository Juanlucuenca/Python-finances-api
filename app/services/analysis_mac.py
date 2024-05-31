from services.scrapping_dolarhoy import scrapping_dolarhoy
from services.get_uva import uva_parsing


# Constantes
CONSTANTE_OFICIAL = 3.5 * 742.0 / 386.91
CONSTANTE_OTROS = 2.25 * 1155.0 / 386.91
CONSTANTE_MAYORISTA = 3.345 * 777.0 / 386.91

def calc_mac():
    mac_list = []

    # Obtener datos
    uva = uva_parsing()
    dolares = scrapping_dolarhoy()

    # Lista para almacenar los resultados
    mac_list = []

    for dolar in dolares:
        dollar_id = dolar.id
        name = dolar.name
        sell_price = dolar.sell_price

        # Calcular índice MAC según el tipo de dólar
        if dollar_id == 'dolar_oficial':
            indice_mac = (CONSTANTE_OFICIAL * uva['valor']) / sell_price
        elif dollar_id in ['dolar_blue', 'dolar_bolsa', 'contado_con_liqui']:
            indice_mac = (CONSTANTE_OTROS * uva['valor']) / sell_price
        elif dollar_id == 'dolar_mayorista':
            indice_mac = (CONSTANTE_MAYORISTA * uva['valor']) / sell_price
            # Modificar el nombre y el id
            dollar_id += '_sincepo'
            name += '(SINCEPO)'
        else:
            continue

        # Agregar los resultados a la lista
        mac_list.append({
            'id': dollar_id,
            'nombre': name,
            'indice_mac': indice_mac
        })

    return mac_list