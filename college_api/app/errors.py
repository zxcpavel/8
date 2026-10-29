from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


class NotFoundError(Exception):
    def __init__(self, entity: str, id: int):
        self.message = f"{entity} с id={id} не найден"


class BusinessError(Exception):
    def __init__(self, message: str):
        self.message = message


def _resp(status: int, message: str, details=None):
    body = {"status": status, "error": message}
    if details is not None:
        body["details"] = details
    return JSONResponse(status_code=status, content=body)


def register_handlers(app: FastAPI):
    @app.exception_handler(NotFoundError)
    async def not_found(_: Request, exc: NotFoundError):
        return _resp(404, exc.message)

    @app.exception_handler(BusinessError)
    async def business(_: Request, exc: BusinessError):
        return _resp(400, exc.message)

    @app.exception_handler(RequestValidationError)
    async def validation(_: Request, exc: RequestValidationError):
        details = [
            {"field": ".".join(str(p) for p in e["loc"][1:]) or str(e["loc"][0]), "message": e["msg"]}
            for e in exc.errors()
        ]
        return _resp(400, "Некорректные входные данные", details)

    @app.exception_handler(IntegrityError)
    async def integrity(_: Request, __: IntegrityError):
        return _resp(409, "Нарушение целостности данных: дубликат или есть связанные записи")

    @app.exception_handler(Exception)
    async def unhandled(_: Request, __: Exception):
        return _resp(500, "Внутренняя ошибка сервера")
