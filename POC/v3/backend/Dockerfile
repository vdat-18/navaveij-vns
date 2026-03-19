# Use official Python image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv (modern python package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files from root
COPY pyproject.toml uv.lock ./
COPY .env ./

# Copy all necessary backend and shared code
COPY backend/ ./backend/
COPY shared/ ./shared/
COPY baml_src/ ./baml_src/
COPY baml_client/ ./baml_client/
COPY assets/ ./assets/

# Symlink src to the backend/src so python -m src works
RUN ln -s /app/backend/src /app/src

# Sync dependencies
RUN uv sync --frozen

# Generate BAML client
RUN uv run baml-cli generate

# Expose backend port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app:/app/backend
ENV PYTHONUNBUFFERED=1

# Run the API server
CMD ["uv", "run", "python", "-m", "src.api.main"]
