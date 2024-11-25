import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from app.database import settings  # Import your database settings

# Define the database URL (use your actual DATABASE_URL from settings.py)
DATABASE_URL = settings.DATABASE_URL

# Create the database engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Create a session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def test_database_connection():
    try:
        async with async_session() as session:
            # Test a simple query to check the connection
            result = await session.execute(select(1))
            if result.scalar() == 1:
                print("Database connection successful!")
            else:
                print("Failed to verify database connection.")
    except Exception as e:
        print(f"Error connecting to the database: {e}")

# Run the connection test
if __name__ == "__main__":
    asyncio.run(test_database_connection())
