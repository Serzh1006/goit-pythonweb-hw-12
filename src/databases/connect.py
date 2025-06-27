from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


engine = create_engine(url=DATABASE_URL)
Session = sessionmaker(bind=engine)

Base = declarative_base()


def get_db():
    """
    Створює та надає сесію до бази даних для одного запиту.

    Yields:
        Session: Об'єкт сесії SQLAlchemy для виконання запитів до бази даних.

    Ensures:
        Сесія буде автоматично закрита після завершення використання.
    """
    connection = Session()
    try:
        yield connection
    finally:
        connection.close()
