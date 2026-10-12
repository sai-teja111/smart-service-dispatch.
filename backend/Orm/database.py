
from contextlib import contextmanager

from sqlmodel import SQLModel, Session, create_engine

from config import get_settings


settings = get_settings()
DATABASE_URL = settings.database_url

# Configure the PostgreSQL driver.
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg2://",
        1,
    )

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)


# For FastAPI dependency injection: Depends(get_session)
def get_session():
    with Session(engine) as session:
        yield session


# For service functions that use: with get_session_context() as session
@contextmanager
def get_session_context():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
