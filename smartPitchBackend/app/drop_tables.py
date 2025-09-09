from app.database import Base, engine

def drop_all_tables():
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped successfully.")

if __name__ == "__main__":
    drop_all_tables()
