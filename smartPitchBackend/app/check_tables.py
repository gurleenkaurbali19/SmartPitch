from sqlalchemy import inspect
from app.database import engine

inspector = inspect(engine)

tables = inspector.get_table_names()

print("Tables in database:", tables)
