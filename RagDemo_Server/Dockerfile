FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# 安裝依賴（包括 fastapi/uvicorn）
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --locked --no-dev

COPY . .


EXPOSE 8888

ENV PATH="/app/.venv/bin:$PATH"
CMD ["fastapi", "dev", "--host", "0.0.0.0", "--port", "8888", "main"]
