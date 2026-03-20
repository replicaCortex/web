alias up := docker-up
alias down := docker-down
alias db := docker-build

run:
    uv run uvicorn app.main:app --reload --port 8000

create_db: generate_migration
    uv run alembic upgrade head

generate_migration: clear_migration
    uv run alembic revision --autogenerate -m "create users table"

clear_migration:
    -rm ./app.db
    -rm -rf alembic/versions/

# --- DOCKER ---

docker-up:
    docker compose up -d 

docker-down:
    docker compose down

docker-build:
    docker compose up -d --build
