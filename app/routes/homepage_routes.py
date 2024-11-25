from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.homepage_service import get_homepage_data
from app.database import get_db
from fastapi import Depends

router = APIRouter()

@router.get("/api/homepage", tags=["Homepage"])
async def homepage(session: AsyncSession = Depends(get_db)):
    """
    Fetch data for the homepage, including featured products, promotions, and FAQs.
    """
    try:
        data = await get_homepage_data(session)  # Call service to get homepage data
        return {"homepage_data": data}
    except Exception as e:
        # Log the error (you can also log to a file or monitoring system)
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
