alias up := docker-up
alias down := docker-down
alias db := docker-build

set dotenv-load := true

REDIS_PASSWORD := env('REDIS_PASSWORD')

run:
    uv run uvicorn app.main:app --reload --port 4200

create_db: generate_migration
    uv run alembic upgrade head

generate_migration: clear_migration
    uv run alembic revision --autogenerate -m "create users table"

clear_migration:
    -rm -rf alembic/versions/

redis:
    docker exec -it wp_labs_redis redis-cli -a {{ REDIS_PASSWORD }} MONITOR

# --- DOCKER ---

docker-up:
    docker compose up -d 

docker-down:
    docker compose down

docker-build: docker-down
    docker compose up -d --build
