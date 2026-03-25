# User API v2.0

REST API для управления пользователями с системой аутентификации, поддержкой OAuth (Yandex) и защищенными маршрутами.

## Описание

Веб-сервис, реализующий безопасную работу с пользователями. Аутентификация построена на **JWT (JSON Web Tokens)**, передаваемых через защищенные **HttpOnly Cookies**, что обеспечивает безопасность от XSS-атак.

Технологический стек:

- **FastAPI** — веб-фреймворк
- **SQLAlchemy 2.0** — ORM для работы с БД
- **PostgreSQL** — основная база данных
- **Alembic** — миграции базы данных
- **Pydantic** — валидация данных
- **Docker** — контейнеризация

## Особенности

- 🔐 **Полная аутентификация**: Регистрация, вход, выход, обновление токенов.
- 🍪 **Безопасность**: Access и Refresh токены хранятся в HttpOnly Cookies.
- 🌐 **OAuth 2.0**: Вход через Яндекс.
- ♻️ **Soft Delete**: Пользователи не удаляются физически, а помечаются удаленными.
- 📄 **Пагинация**: Удобная навигация по списку пользователей.
- 🛡 **Access Control**: Пользователи могут редактировать и удалять только свои профили.

## Быстрый старт

### 1. Настройка окружения

Создайте файл `.env` на основе примера:

```env
# Database
DB_USER=student
DB_PASSWORD=student_secure_password
DB_HOST=db
DB_PORT=5432
DB_NAME=wp_labs

# JWT Settings
JWT_ACCESS_SECRET=super_secret_access_key_change_me
JWT_REFRESH_SECRET=super_secret_refresh_key_change_me
JWT_ACCESS_EXPIRATION=15
JWT_REFRESH_EXPIRATION=10080

# OAuth Yandex (Optional)
YANDEX_CLIENT_ID=your_yandex_client_id
YANDEX_CLIENT_SECRET=your_yandex_client_secret
YANDEX_CALLBACK_URL=http://localhost:4200/auth/oauth/yandex/callback

# App
ENVIRONMENT=development
FRONTEND_URL=http://localhost:3000
```

### 2. Запуск через Docker

```bash
docker-compose up --build
```

- API доступно по адресу: `http://localhost:4200`
- Swagger UI (документация): `http://localhost:4200/docs`

> **Важно:** При запуске в Docker миграции применяются автоматически.

## API Endpoints

### 🔐 Auth (Аутентификация)

Все токены устанавливаются автоматически в Cookies.

| Метод  | URL                  | Описание                                     |
| ------ | -------------------- | -------------------------------------------- |
| `POST` | `/auth/register`     | Регистрация (Email + Password)               |
| `POST` | `/auth/login`        | Вход (установка Cookies)                     |
| `POST` | `/auth/refresh`      | Обновление Access-токена через Refresh-токен |
| `GET`  | `/auth/whoami`       | Получить профиль текущего пользователя       |
| `POST` | `/auth/logout`       | Выход (удаление Cookies и отзыв токена)      |
| `GET`  | `/auth/oauth/yandex` | Старт входа через Яндекс                     |

### 👤 Users (Пользователи)

🔒 — Требуется авторизация.
🛡 — Можно менять только свой профиль.

| Метод    | URL           | Описание                               | Доступ |
| -------- | ------------- | -------------------------------------- | ------ |
| `GET`    | `/users/`     | Список всех пользователей (пагинация)  | 🔒     |
| `POST`   | `/users/`     | Создать пользователя (админ/служебный) | 🔒     |
| `GET`    | `/users/{id}` | Получить пользователя по ID            | 🔒     |
| `PUT`    | `/users/{id}` | Полное обновление профиля              | 🔒 🛡  |
| `PATCH`  | `/users/{id}` | Частичное обновление                   | 🔒 🛡  |
| `DELETE` | `/users/{id}` | Удаление (Soft Delete)                 | 🔒 🛡  |

## Примеры запросов (cURL)

Так как API использует **Cookies**, для тестирования через `curl` необходимо сохранять сессию (`-c cookies.txt`) и отправлять её (`-b cookies.txt`).

### 1. Регистрация

```bash
curl -X POST http://localhost:4200/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser", "email": "me@example.com", "password": "password123"}'
```

### 2. Вход (Login)

Сохраняем токены в файл `cookies.txt`:

```bash
curl -X POST http://localhost:4200/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "me@example.com", "password": "password123"}' \
  -c cookies.txt
```

### 3. Получение своего профиля

Используем сохраненные куки:

```bash
curl -b cookies.txt http://localhost:4200/auth/whoami
```

### 4. Список пользователей (с пагинацией)

```bash
curl -b cookies.txt "http://localhost:4200/users/?page=1&limit=5"
```

### 5. Обновление своего профиля (PATCH)

```bash
# Предположим, ваш ID = 1 (узнать можно через /whoami)
curl -X PATCH http://localhost:4200/users/1 \
  -H "Content-Type: application/json" \
  -d '{"os": "MacOS", "totaltime": 500}' \
  -b cookies.txt
```

## Структура проекта

```
├── alembic/              # Миграции БД
├── app/
│   ├── auth/             # Модуль аутентификации
│   │   ├── dependencies.py # Проверка токенов
│   │   ├── jwt_utils.py    # Генерация/валидация JWT
│   │   ├── service.py      # Бизнес-логика Auth
│   │   └── router.py       # Auth эндпоинты
│   ├── __init__.py
│   ├── config.py         # Конфигурация (ENV)
│   ├── database.py       # Подключение к БД
│   ├── exceptions.py     # Обработчики ошибок
│   ├── main.py           # Точка входа
│   ├── models.py         # SQLAlchemy модели (User, TokenRecord)
│   ├── repository.py     # Работа с БД (Users)
│   ├── router.py         # User эндпоинты
│   └── schemas.py        # Pydantic схемы (Users)
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Модель данных

### Таблица `users`

| Поле            | Тип      | Описание                       |
| --------------- | -------- | ------------------------------ |
| `id`            | Integer  | PK                             |
| `username`      | String   | Уникальное имя                 |
| `email`         | String   | Уникальный Email               |
| `password_hash` | Text     | Хеш пароля (bcrypt)            |
| `salt`          | String   | Соль для хеширования           |
| `yandex_id`     | String   | ID пользователя Яндекс (OAuth) |
| `deleted_at`    | DateTime | Метка времени для Soft Delete  |

### Таблица `tokens` (Revocation List)

Хранит хеши токенов для валидации и возможности отзыва сессий.

| Поле                 | Тип     | Описание             |
| -------------------- | ------- | -------------------- |
| `user_id`            | Integer | FK на пользователя   |
| `access_token_hash`  | Text    | Хеш access токена    |
| `refresh_token_hash` | Text    | Хеш refresh токена   |
| `revoked`            | Boolean | Статус отзыва токена |

## Разработка

### Локальный запуск (без Docker)

1. Поднимите базу данных (например, через docker-compose только db):
   ```bash
   docker-compose up -d db
   ```
2. Экспортируйте переменные окружения (см. `.env` раздел выше).
3. Примените миграции:
   ```bash
   alembic upgrade head
   ```
4. Запустите сервер:
   ```bash
   uvicorn app.main:app --reload --port 4200
   ```

```

```
