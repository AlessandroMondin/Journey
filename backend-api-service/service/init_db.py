from service.database import engine
from service import models


def init_database():
    """
    Initialize the database by creating all tables defined in models.
    """
    models.Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    init_database()
