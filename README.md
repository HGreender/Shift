# Shift

Перед началом работы удостоверьтесь, что у вас установлен Docker и Docker-Compose.
Docker-Compose должен быть совместим с версией v2.18.1.

**Важное примечание!** Вся работа с файлами должна производиться в директории `weather_service/`

Например, если вы хотите загрузить JSON-файл для обработки, 
можете поместить его так: `weather_service/inputs/json_test.json`

Все итоговые данные будут сохранены в директории `weather_service/loader_data/`

Перед запуском соберите контейнеры, выполнив команду 
(необходимо находиться в корневой директории проекта): `docker-compose build`

Тесты запускаются автоматически перед сборкой образа

### Аргументы командной строки
- -s, --source (Обязательно):
- - api: Для извлечения данных из Open-Meteo API.
- - json: Для извлечения данных из локального JSON-файла.
- -f, --file-path (Обязательно для --source json): Путь к входному JSON-файлу.
- -start, --start-date (Обязательно для --source api): Начальная дата для извлечения из API в формате ГГГГ-ММ-ДД.
- -end, --end-date (Обязательно для --source api): Конечная дата для извлечения из API в формате ГГГГ-ММ-ДД.
- -t, --target (Обязательно):
- - csv: Для загрузки преобразованных данных в CSV-файл.
- - db: Для загрузки преобразованных данных в базу данных SQLite.
- -o, --output-file (Обязательно для --target csv): Путь для выходного CSV-файла (например, output/weather.csv).

### Примеры команд
### 1. API -> База данных
`docker compose run --rm weather-etl --source api --target db --start-date 2025-07-20 --end-date 2025-07-22`

### 2. API -> CSV
`docker compose run --rm weather-etl --source api --target csv --start-date 2025-07-20 --end-date 2025-07-22`

### 3. JSON -> База данных
`docker compose run --rm weather-etl --source json --target db `

### 4. JSON -> CSV
`docker compose run --rm weather-etl --source json --target csv `
