alias up := docker-up
alias down := docker-down
alias db := docker-build

run:
    uv run main.py

docker-up:
    docker compose up -d 

docker-down:
    docker compose down

docker-build:
    docker compose up -d --build
