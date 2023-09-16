import asyncpg
import asyncio
from decouple import config
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import Session

from database.models import Base,FetchPhaseInfo


POSTGRES_USER = config("POSTGRES_USER")
POSTGRES_HOST = config("POSTGRES_HOST")
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD")
DATABASE_NAME = config("DATABASE_NAME")


# Configure the PostgreSQL database connection URL
DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{DATABASE_NAME}"

# Create the database engine
async_engine = create_async_engine(DATABASE_URL,echo=True)

async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def initialize_database(session: Session):
    # Check if we have already created record in the table
    existing_records = session.query(FetchPhaseInfo).count()

    # If no records exist, create a new row
    if existing_records == 0:
        new_record = FetchPhaseInfo(
            phase_1_complete=False,
            phase_2_complete=False,
            phase_3_complete=False,
            phase_4_complete=False,
            phase_5_complete=False,
        )
        session.add(new_record)
        session.commit()

# Create a function to create tables asynchronously
async def connect_create_if_not_exists(user, database):
    try:
        conn = await asyncpg.connect(user=user, database=database)
    except asyncpg.InvalidCatalogNameError:
        # Database does not exist, create it.
        sys_conn = await asyncpg.connect(
            database='template1',
            user='postgres'
        )
        await sys_conn.execute(
            f'CREATE DATABASE "{database}" OWNER "{user}"'
        )
        await sys_conn.close()

        # Connect to the newly created database.
        conn = await asyncpg.connect(user=user, database=database)

    return conn



