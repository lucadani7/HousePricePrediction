from collections.abc import Generator
from datetime import datetime, timezone

from sqlmodel import JSON, Column, Field, Session, SQLModel, create_engine

from housepriceprediction.config import DATABASE_PATH


class PredictionRecord(SQLModel, table=True):
    """Database model storing user inputs as JSON, predicted price, and timestamp."""

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    features: dict = Field(sa_column=Column(JSON))
    predicted_price: float


# FastAPI runs sync routes in a thread pool, so SQLite must accept connections
# used from a thread other than the one that created them.
engine = create_engine(
    f"sqlite:///{DATABASE_PATH}", connect_args={"check_same_thread": False}
)


def create_db_and_tables() -> None:
    """Creates the SQLite file (and its folder) and the tables, if they do not exist yet."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency yielding a database session for one request."""
    with Session(engine) as session:
        yield session
