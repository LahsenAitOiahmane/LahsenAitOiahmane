from app.models import Product, Promotion, FAQ
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

async def get_homepage_data(session: AsyncSession):
    """
    Fetch data for the homepage, including featured products, active promotions, and FAQs.
    """
    # Fetch featured products
    products_query = await session.execute(select(Product).where(Product.is_featured == True))
    featured_products = products_query.scalars().all()

    # Fetch active promotions
    promotions_query = await session.execute(select(Promotion))
    active_promotions = promotions_query.scalars().all()

    # Fetch FAQs
    faqs_query = await session.execute(select(FAQ))
    faqs = faqs_query.scalars().all()

    return {
        "featured_products": [product.to_dict() for product in featured_products],
        "promotions": [promo.to_dict() for promo in active_promotions],
        "faqs": [faq.to_dict() for faq in faqs],
    }
