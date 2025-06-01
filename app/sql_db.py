# import pymysql


# connection = pymysql.connect(
#         host="13.202.126.99",
#         user="pushpender",
#         password="StrongPassword",
#         database="influenceflow",
#         port=5432  # Change this to the correct MySQL port (default is 3306)
#     )


# cursor = connection.cursor()


# query = f"""
#     select * from usersr limit 1
# """
# cursor.execute(query)

# data = cursor.fetchone()

# print(data)

from app.config import settings
from sqlalchemy import text
from sqlalchemy import create_engine
import asyncio
engine = create_engine(settings.DATABASE_URL)
from sqlalchemy.sql import text

from app.config import settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import asyncio

# Create an async engine
engine = create_async_engine(settings.DATABASE_URL, echo=True)

async def fetch_data():
    """Fetch data asynchronously from the database."""
    async with engine.connect() as con:
        query = """
            SELECT * FROM users LIMIT 1
        """
        result = await con.execute(text(query))
        rows = await result.fetchall()  # Use `await` for async result fetching
        print(rows)

# Run the async function
asyncio.run(fetch_data())