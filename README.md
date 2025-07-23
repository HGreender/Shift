# Shift

### Аргументы командной строки
- -s, --source (Обязательно):
- - api: Для извлечения данных из Open-Meteo API.
- - json: Для извлечения данных из локального JSON-файла.
- --target (Обязательно):
- - csv: Для загрузки преобразованных данных в CSV-файл.
- - db: Для загрузки преобразованных данных в базу данных SQLite.
- --file-path (Обязательно для --source json): Путь к входному JSON-файлу.
- -start, --start-date (Обязательно для --source api): Начальная дата для извлечения из API в формате ГГГГ-ММ-ДД.
- -end, --end-date (Обязательно для --source api): Конечная дата для извлечения из API в формате ГГГГ-ММ-ДД.
- -o, --output-file (Обязательно для --target csv): Путь для выходного CSV-файла (например, output/weather.csv).


`docker compose run --rm weather-etl --source api --target db --start-date 2025-07-20 --end-date 2025-07-22`
