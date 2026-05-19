alias up := docker-up
alias down := docker-down
alias db := docker-build

set dotenv-load := true

REDIS_PASSWORD := env('REDIS_PASSWORD')

run:
    just docker-up

redism:
    docker exec -it wp_labs_redis redis-cli -a {{ REDIS_PASSWORD }} MONITOR

redis:
    docker exec -it wp_labs_redis redis-cli -a {{ REDIS_PASSWORD }} 

# --- DOCKER ---

docker-up:
    docker compose up -d 

docker-down:
    docker compose down

docker-build: docker-down
    docker compose up -d --build
    just docker-logs-app

docker-logs-app:
    docker logs -f wp_labs_app
