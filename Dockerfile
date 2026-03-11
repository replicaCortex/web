FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY . .

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 4200

CMD ["./entrypoint.sh"]
