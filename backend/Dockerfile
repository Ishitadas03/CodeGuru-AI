FROM python:3.12-slim

WORKDIR /app

# Install base postgres client and gcc build systems
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependency manager
RUN pip install poetry --no-cache-dir

# Copy configuration settings
COPY pyproject.toml poetry.lock* ./

# Turn off virtual env creating inside the container and build
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --no-directory

# Copy code
COPY . .

# Expose fastapi
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
