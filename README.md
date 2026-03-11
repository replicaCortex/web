Клиент (curl / браузер / фронтенд)
  │
  │  POST /users  {"username": "john", "os": "linux", ...}
  ▼
┌──────────────────────────────────┐
│  Uvicorn (ASGI-сервер)           │
│  Принимает HTTP, передаёт в app  │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│  FastAPI Router                  │
│  1. Парсит JSON                  │
│  2. Валидирует через UserCreate  │  ← Pydantic
│  3. Вызывает Depends(get_repo)   │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│  Depends(get_session)            │
│  Создаёт AsyncSession            │  ← SQLAlchemy
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│  Depends(get_repo)               │
│  Создаёт UserRepository(session) │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│  UserRepository.create(data)     │
│  1. User(\*\*data.model_dump())    │
│  2. session.add(user)            │
│  3. session.commit()             │  → INSERT INTO users ...
│  4. session.refresh(user)        │  → SELECT (получить id)
│  5. return user                  │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│  FastAPI                         │
│  1. user → UserRead (Pydantic)   │
│  2. UserRead → JSON              │
│  3. HTTP 201 + JSON body         │
└──────────────┬───────────────────┘
               │
               ▼
Клиент получает:
HTTP/1.1 201 Created
{"id": 1, "username": "john", "os": "linux", "totaltime": 0, ...}
