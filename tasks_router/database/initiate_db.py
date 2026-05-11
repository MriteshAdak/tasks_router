# import os
# from dotenv import load_dotenv
# load_dotenv()

# Database connection setup using psycopg2 and SQLAlchemy with AWS RDS IAM authentication

# import psycopg2
# # import boto3

# password = "default-vpc-015066fb0e6e860da"

# conn = None
# try:
#     conn = psycopg2.connect(
#         host='database-1-psql.crskgicaqb2p.eu-north-1.rds.amazonaws.com',
#         port=5432,
#         database='db_name_psql',
#         user='postgres',
#         password=password,
#         sslmode='verify-full',
#     sslrootcert='./global-bundle.pem'
#     )
#     cur = conn.cursor()
#     cur.execute('SELECT version();')
#     print(cur.fetchone()[0]) #type: ignore
#     cur.close()
# except Exception as e:
#     print(f"Database error: {e}")
#     raise
# finally:
#     if conn:
#         conn.close()

# # SQLAlchemy setup for ORM and connection pooling

# from sqlalchemy import create_engine
# from sqlalchemy.engine.url import URL

# engine = create_engine(URL.create(
#     drivername='postgresql+psycopg2',
#     username='postgres',
#     password=password, # type: ignore
#     host='database-1-psql.crskgicaqb2p.eu-north-1.rds.amazonaws.com',
#     port=5432,
#     database='postgres',
# ))


from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from tasks_router.models.task_model import Base

# 1. Define the connection URI (replace 'your_password' with actual password)
DATABASE_URI = "postgresql+psycopg2://main:postgresql@localhost:5432/main"

# 2. Create the engine
engine = create_engine(DATABASE_URI, echo=True)  # echo=True logs SQL; remove in production

# 3. Test the connection
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        print("Connected to:", result.fetchone()[0])
except Exception as e:
    print("Connection failed:", e)

# 4. Create a session factory (for ORM usage)
SessionLocal = sessionmaker(bind=engine)

# Example quick query using session
with SessionLocal() as session:
    result = session.execute(text("SELECT current_database(), current_user"))
    db, user = result.fetchone()
    print(f"Connected to database '{db}' as user '{user}'")

Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """Dependency to get DB session for FastAPI routes"""
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()