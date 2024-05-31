import sqlite3

# Ruta a tu base de datos
db_path = 'app/finance.db'

# Conectar a la base de datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Leer el archivo de inserciones
with open('app/indicebigmac_inserts.sql', 'r') as file:
    sql_inserts = file.read()

# Ejecutar las consultas de inserción
cursor.executescript(sql_inserts)

# Confirmar los cambios y cerrar la conexión
conn.commit()
conn.close()
