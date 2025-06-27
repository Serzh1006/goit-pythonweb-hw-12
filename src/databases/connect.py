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
    connection = Session()
    try:
        yield connection
    finally:
        connection.close()
