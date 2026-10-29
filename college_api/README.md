# College API — вариант 4 (Стипендия)

FastAPI + SQLAlchemy + SQLite, Swagger из коробки.

## Запуск
    python -m venv venv
    venv\Scripts\activate        # Linux/macOS: source venv/bin/activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload

Swagger UI: http://127.0.0.1:8000/docs  (OpenAPI JSON: /openapi.json)

## Тесты
    pytest

## Структура (слои)
- app/routers.py — контроллеры (HTTP)
- app/services.py — бизнес-логика (правило варианта 4)
- app/repositories.py — доступ к БД
- app/models.py — модели БД; app/schemas.py — валидация
- app/errors.py — глобальные обработчики ошибок (400/404/409/500)

## Вариант 4
- Сущность: Scholarship (student_id, semester, attendance_percent, threes_count, kind, amount)
- GET /api/scholarships/high — студенты на повышенной стипендии (фильтры group_id, semester)
- Правило: повышенная, если threes_count == 0 И attendance_percent == 100; тип и сумма считаются автоматически
