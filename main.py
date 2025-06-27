from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from starlette.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from src.databases.connect import get_db
from src.routes import contacts, auth, users

app = FastAPI()

origins = [
    "http://localhost:8000",
    "http://localhost:8000/me"
    "http://127.0.0.1:5432",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", name="API root")
def get_index():
    """
    Базовий маршрут API.

    Returns:
        dict: Повідомлення-привітання для користувача.
    """
    return {"message": "Welcome to Contacts API."}


@app.get("/health", name="Service availability")
def get_health_status(db=Depends(get_db)):
    """
    Перевіряє доступність бази даних.

    Виконує простий SQL-запит `SELECT 1+1` для перевірки з'єднання з БД.
    Якщо запит не виконується або не повертає результат — викидається помилка 503.

    Args:
        db: Залежність FastAPI для отримання сесії бази даних.

    Returns:
        dict: Повідомлення про стан бази даних.

    Raises:
        HTTPException: Якщо база даних не відповідає або не налаштована.
    """
    try:
        result = db.execute(text("Select 1+1")).fetchone()
        print(result)
        if result is None:
            raise Exception
        return {"message": "DataBase is ready for use!"}
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="DataBase is not configure correctly ",
        )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Обробляє помилки перевищення ліміту запитів.

    Повертає статус 429 Too Many Requests з повідомленням українською мовою.

    Args:
        request (Request): Вхідний HTTP-запит.
        exc (RateLimitExceeded): Виняток, що виник при перевищенні ліміту.

    Returns:
        JSONResponse: JSON-відповідь з кодом 429 та повідомленням.
    """
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": "Перевищено ліміт запитів. Спробуйте пізніше."},
    )

app.include_router(contacts.router)
app.include_router(auth.router)
app.include_router(users.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)