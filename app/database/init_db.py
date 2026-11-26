from app.database.base import Base
from app.database.session import engine

# Import all models so SQLAlchemy registers their tables
from app.models import User, Invoice, Batch, LineItem, QAReview


# Create all tables in PostgreSQL
def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("All database tables created successfully!")