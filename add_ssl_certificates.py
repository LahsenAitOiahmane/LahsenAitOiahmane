from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import async_session, engine
from app.models import SSLCertificate
import asyncio
import datetime

async def add_ssl_certificates():
    async with async_session() as session:
        # Check if the table already has data
        result = await session.execute(select(SSLCertificate))
        existing_certificates = result.scalars().all()

        if existing_certificates:
            print("Certificates already exist in the database.")
            return
        expiration_date = datetime.datetime.strptime("2025-11-25", '%Y-%m-%d').date()
        
        # Define the SSL certificates to add
        certificates = [
            SSLCertificate(
                domain_name="basic.example.com",
                cert_type="Basic SSL",
                price=49.99,
                expiration_date=expiration_date,
            ),
            SSLCertificate(
                domain_name="wildcard.example.com",
                cert_type="Wildcard SSL",
                price=199.99,
                expiration_date=expiration_date,
            ),
            SSLCertificate(
                domain_name="ev.example.com",
                cert_type="Extended Validation (EV) SSL",
                price=299.99,
                expiration_date=expiration_date,
            ),
        ]

        # Add certificates to the database
        session.add_all(certificates)
        await session.commit()
        print("SSL certificates added successfully.")


if __name__ == "__main__":
    asyncio.run(add_ssl_certificates())
