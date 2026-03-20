# User API

REST API для управления пользователями с поддержкой soft delete и пагинации.

## Описание

Веб-сервис, реализующий CRUD-операции для сущности "Пользователь" с использованием:

- **FastAPI** — веб-фреймворк
- **SQLAlchemy** — ORM для работы с БД
- **PostgreSQL** — реляционная СУБД
- **Alembic** — миграции базы данных
- **Docker** — контейнеризация

## Быстрый старт

### 1. Клонировать репозиторий

```bash
docker-compose up --build
```

Приложение будет доступно по адресу: http://localhost:4200

Swagger-документация: http://localhost:4200/docs

## Переменные окружения

Пример файла `.env.example`:

```env
DB_USER=student
DB_PASSWORD=student_secure_password
DB_NAME=wp_labs
```

## API Endpoints

| Метод    | URL           | Описание                            | Статус успеха    |
| -------- | ------------- | ----------------------------------- | ---------------- |
| `GET`    | `/`           | Проверка работоспособности          | `200 OK`         |
| `GET`    | `/users/`     | Список пользователей (с пагинацией) | `200 OK`         |
| `GET`    | `/users/{id}` | Получить пользователя по ID         | `200 OK`         |
| `POST`   | `/users/`     | Создать пользователя                | `201 Created`    |
| `PUT`    | `/users/{id}` | Полное обновление пользователя      | `200 OK`         |
| `PATCH`  | `/users/{id}` | Частичное обновление пользователя   | `200 OK`         |
| `DELETE` | `/users/{id}` | Мягкое удаление пользователя        | `204 No Content` |

## Пагинация

Параметры передаются через Query String:

```
GET /users/?page=1&limit=10
```

| Параметр | Тип | По умолчанию | Описание                    |
| -------- | --- | ------------ | --------------------------- |
| `page`   | int | 1            | Номер страницы (≥ 1)        |
| `limit`  | int | 10           | Записей на странице (1-100) |

### Пример ответа с пагинацией

```json
{
  "data": [
    {
      "id": 1,
      "username": "john",
      "email": "john@example.com",
      "os": "linux",
      "totaltime": 100,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "meta": {
    "total": 25,
    "page": 1,
    "limit": 10,
    "total_pages": 3
  }
}
```

## Примеры запросов (cURL)

### Создание пользователя

```bash
curl -X POST http://localhost:4200/users/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com", "os": "linux", "totaltime": 100}'
```

### Получение списка с пагинацией

```bash
curl "http://localhost:4200/users/?page=1&limit=5"
```

### Получение по ID

```bash
curl http://localhost:4200/users/1
```

### Полное обновление (PUT)

```bash
curl -X PUT http://localhost:4200/users/1 \
  -H "Content-Type: application/json" \
  -d '{"username": "john_updated", "email": "john_new@example.com", "os": "ubuntu", "totaltime": 500}'
```

### Частичное обновление (PATCH)

```bash
curl -X PATCH http://localhost:4200/users/1 \
  -H "Content-Type: application/json" \
  -d '{"totaltime": 999}'
```

### Удаление (Soft Delete)

```bash
curl -X DELETE http://localhost:4200/users/1
```

## Миграции

Миграции запускаются **автоматически** при старте контейнера.

### Ручной запуск миграций

```bash
# Внутри контейнера
docker exec -it wp_labs_app alembic upgrade head

# Или локально (при наличии подключения к БД)
alembic upgrade head
```

### Создание новой миграции

```bash
# Автогенерация на основе изменений в моделях
alembic revision --autogenerate -m "описание изменений"

# Применить миграцию
alembic upgrade head

# Откатить последнюю миграцию
alembic downgrade -1
```

## Структура проекта

```
├── app/
│   ├── __init__.py
│   ├── main.py           # Точка входа FastAPI
│   ├── config.py         # Настройки приложения
│   ├── database.py       # Подключение к БД
│   ├── models.py         # SQLAlchemy модели
│   ├── schemas.py        # Pydantic схемы (DTO)
│   ├── repository.py     # Слой работы с данными
│   └── router.py         # HTTP эндпоинты
├── alembic/
│   ├── env.py            # Конфигурация Alembic
│   ├── script.py.mako    # Шаблон миграций
│   └── versions/         # Файлы миграций
├── alembic.ini           # Настройки Alembic
├── docker-compose.yml    # Оркестрация контейнеров
├── Dockerfile            # Сборка образа приложения
├── entrypoint.sh         # Скрипт запуска
├── requirements.txt      # Python зависимости
├── .env.example          # Пример переменных окружения
└── README.md
```

## Модель данных

### User

| Поле         | Тип        | Описание                      |
| ------------ | ---------- | ----------------------------- |
| `id`         | Integer    | Первичный ключ                |
| `username`   | String(50) | Имя пользователя (уникальное) |
| `email`      | String(50) | Email (уникальный)            |
| `os`         | String(50) | Операционная система          |
| `totaltime`  | Integer    | Общее время                   |
| `created_at` | DateTime   | Дата создания                 |
| `updated_at` | DateTime   | Дата обновления               |
| `deleted_at` | DateTime   | Дата удаления (soft delete)   |

## Коды ошибок

| Код                         | Описание                                  |
| --------------------------- | ----------------------------------------- |
| `400 Bad Request`           | Неверный формат данных                    |
| `404 Not Found`             | Ресурс не найден                          |
| `409 Conflict`              | Конфликт данных (дубликат username/email) |
| `500 Internal Server Error` | Внутренняя ошибка сервера                 |

## Разработка

### Локальный запуск (без Docker)

```bash
# Настроить переменные окружения
export DB_HOST=localhost
export DB_USER=student
export DB_PASSWORD=student_secure_password
export DB_NAME=wp_labs

# Применить миграции
alembic upgrade head

# Запустить сервер
uvicorn app.main:app --reload --port 4200
```

### Полезные команды Docker

```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Пересборка
docker-compose up --build

# Логи приложения
docker logs wp_labs_app

# Логи базы данных
docker logs wp_labs_db

# Подключение к БД
docker exec -it wp_labs_db psql -U student -d wp_labs
```

## Технологии

- Python 3.11+
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL 16
- Alembic
- Docker & Docker Compose
- Pydantic
