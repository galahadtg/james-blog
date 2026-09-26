FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (caching layer)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make sure we can import from app
ENV PYTHONPATH=/app

# Pre-create upload directory
RUN mkdir -p /app/uploads && chmod 777 /app/uploads

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD sh -c "alembic upgrade head && python seed_roles.py && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 --log-level info"