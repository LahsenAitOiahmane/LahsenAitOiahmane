import asyncio
import datetime
from app.database import async_session
from app.models import Product, Promotion, FAQ

async def populate_data():
    async with async_session() as session:
        # Add test products
        session.add_all([
            Product(name="SSL Basic", description="Basic SSL certificate", price=10, is_featured=True),
            Product(name="SSL Pro", description="Advanced SSL certificate", price=30, is_featured=True),
        ])

        # Add test promotions
        valid_until = datetime.datetime.strptime('2024-12-01', '%Y-%m-%d').date()
        session.add(Promotion(title="Black Friday Sale", description="50% off!", valid_until=valid_until))

        # Add test FAQs
        session.add_all([
            FAQ(question="What is an SSL?", answer="It secures your site."),
            FAQ(question="How to install SSL?", answer="Follow our guide."),
        ])

        await session.commit()

if __name__ == "__main__":
    asyncio.run(populate_data())
