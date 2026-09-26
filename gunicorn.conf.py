"""Production ASGI server configuration.

Usage:
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

Or with Gunicorn (Linux only):
    gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
"""

# Uvicorn settings
HOST = "0.0.0.0"
PORT = 8000
WORKERS = 4
LOG_LEVEL = "info"

# For production, run with:
# uvicorn app.main:app \
#     --host 0.0.0.0 \
#     --port 8000 \
#     --workers 4 \
#     --limit-concurrency 1000 \
#     --backlog 2048 \
#     --timeout-keep-alive 30 \
#     --log-level info
