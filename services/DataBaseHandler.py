from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from models.user import User

SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_admin_user():
    # Create database tables if they don't exist
    Base.metadata.create_all(bind=engine)

    # Create a database session
    db = SessionLocal()
    try:
        # Check if admin user already exists
        admin_user = db.query(User).filter(User.username == ADMIN_USERNAME).first()
        if admin_user:
            print(f"Admin user '{ADMIN_USERNAME}' already exists.")
            return

        # Create new admin user
        hashed_password = pwd_context.hash(ADMIN_PASSWORD)
        new_admin = User(
            username=ADMIN_USERNAME,
            password_hash=hashed_password,
            role="admin"
        )
        db.add(new_admin)
        db.commit()
        print(f"Admin user '{ADMIN_USERNAME}' created successfully.")
    finally:
        db.close()