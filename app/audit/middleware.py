# app/audit/middleware.py

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.database import SessionLocal
from app.audit.logger import log_event

class AuditMiddleware(BaseHTTPMiddleware):
    """Автоматично логує кожен HTTP-запит."""
    
    # Шляхи, які ми ігноруємо, щоб не перевантажувати логи
    SKIP_PATHS = {"/docs", "/openapi.json", "/redoc", "/favicon.ico"}

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        start_time = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)

        ip = request.client.host if request.client else "unknown"

        # Визначення статусу безпеки на основі HTTP-коду відповіді
        if response.status_code >= 500:
            status = "error"
        elif response.status_code in (401, 403):
            status = "failure"
        else:
            status = "success"

        # Логуємо лише модифікуючі запити (POST, PUT, DELETE) або будь-які помилки (>= 400)
        if request.method != "GET" or response.status_code >= 400:
            db = SessionLocal()
            try:
                log_event(
                    db=db,
                    action=f"http_{request.method.lower()}",
                    status=status, 
                    ip_address=ip,
                    http_method=request.method,
                    endpoint=str(request.url.path),
                    status_code=response.status_code,
                    details={"duration_ms": duration_ms},
                )
            finally:
                db.close()

        return response