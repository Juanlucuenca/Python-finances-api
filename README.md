# Dollar Api Scrapper

(Todavia esta todo el BETA para probar que seae viable y funcional)

### (Funcionalidades / End-Points)

- Scrapper de la pagina [dolarhoy](https://dolarhoy.com/) para obtener las princiaples **cotizaciones de los diferentes dolares**.
- Toma el precio del **UVA al dia de la fecha**.
- Calcula el **indice BIG MAC** de cada uno de los dolares, el mismo se puede guardar en una base de datos SQLite.
- Se toman los indices de la base de datos y se **calcula el desvio estandar y el promedio, para el analisis**.
- Realiza un POST todos los dias, a los horarios de apertura y cierre del mercado para minar datos y obtener un desvio estandar promedio perfecto.

### Dependencias

- `fastapi`
- `sqlmodel`
- `BeautifulSoup`
- `pydantic`
- `unidecode`
- `schedule`
