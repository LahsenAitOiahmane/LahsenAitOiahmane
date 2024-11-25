from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import SSLCertificate, SSLCertificateCreate, SSLCertificateResponse

router = APIRouter()

# Route to get all SSL certificates
@router.get("/api/ssl-certificates", response_model=list[SSLCertificateResponse])
async def get_certificates(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SSLCertificate))
    certificates = result.scalars().all()
    return certificates

# Route to get a specific SSL certificate by domain name
@router.get("/api/ssl-certificate/{domain_name}", response_model=SSLCertificateResponse)
async def get_certificate(domain_name: str, db: AsyncSession = Depends(get_db)):
    certificate = await db.execute(select(SSLCertificate).filter_by(domain_name=domain_name))
    certificate = certificate.scalar_one_or_none()
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return certificate

# Route to add a new SSL certificate
@router.post("/api/ssl-certificate", response_model=SSLCertificateResponse)
async def add_certificate(cert: SSLCertificateCreate, db: AsyncSession = Depends(get_db)):
    # Create the SSLCertificate instance from the incoming data
    new_cert = SSLCertificate(**cert.dict())
    db.add(new_cert)
    await db.commit()
    await db.refresh(new_cert)  # Get the generated id and any defaults
    return new_cert
