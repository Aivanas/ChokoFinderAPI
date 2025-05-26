import time

from prometheus_client import Counter, Gauge, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

RESPONSE_TIME = Histogram(
    'http_response_time_seconds',
    'HTTP response time in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0)
)

HTTP_ERRORS = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'status_code']
)

UPDATE_BASE_COUNT = Counter(
    'update_base_total',
    'Total number of vector base updates'
)

UPLOADED_FILES_COUNT = Counter(
    'uploaded_files_total',
    'Total number of uploaded files'
)

FILE_SIZE_HISTOGRAM = Histogram(
    'uploaded_file_size_bytes',
    'Size of uploaded files in bytes',
    buckets=(1024, 10240, 102400, 1048576, 10485760)  # 1KB, 10KB, 100KB, 1MB, 10MB
)

DELETED_FILES_COUNT = Counter(
    'deleted_files_total',
    'Total number of deleted files'
)

DOCUMENTS_COUNT = Gauge(
    'documents_total',
    'Total number of documents'
)

LOGIN_ATTEMPTS = Counter(
    'login_attempts_total',
    'Total login attempts',
    ['success']
)

REGISTRATIONS_COUNT = Counter(
    'registrations_total',
    'Total number of user registrations'
)

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        method = request.method
        endpoint = request.url.path
        status_code = response.status_code

        REQUEST_COUNT.labels(method, endpoint, status_code).inc()
        RESPONSE_TIME.labels(method, endpoint).observe(process_time)
        if status_code >= 400:
            HTTP_ERRORS.labels(method, endpoint, status_code).inc()

        return response

# Добавление middleware в приложение
