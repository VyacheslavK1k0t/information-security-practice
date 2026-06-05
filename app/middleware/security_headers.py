# app/middleware/security_headers.py

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Content Security Policy (CSP): дозволяємо роботу Swagger UI (CDN та інлайн-стилі)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://fastapi.tiangolo.com; "
            "frame-ancestors 'none'"
        )
        # Захист від Clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        # Заборона MIME-type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Контроль витоку URL через Referer
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Захист від XSS для застарілих браузерів
        response.headers["X-XSS-Protection"] = "1; mode=block"

        return response