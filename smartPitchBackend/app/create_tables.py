from app.database import engine, Base
from app.models import User

# This command creates all tables defined by the Base metadata 
Base.metadata.create_all(bind=engine)

print("Tables created successfully!")
