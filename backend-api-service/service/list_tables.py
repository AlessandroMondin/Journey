from sqlalchemy import inspect, text
from .database import engine


def list_tables_sqlalchemy():
    """List all tables using SQLAlchemy's inspect functionality"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Tables in database (via SQLAlchemy):")
    for table in tables:
        print(f"- {table}")
    return tables


def list_tables_sql():
    """List all tables using direct SQL query"""
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT name FROM sqlite_master WHERE type='table';")
        )
        tables = [row[0] for row in result]
        print("\nTables in database (via SQL):")
        for table in tables:
            print(f"- {table}")
        return tables


if __name__ == "__main__":
    list_tables_sqlalchemy()
    list_tables_sql()
