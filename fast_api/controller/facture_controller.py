from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import get_db
from schemas.schemas import FactureCreate
from models.models import Facture

facture_router = APIRouter(prefix="/factures", tags=["Factures"])

@facture_router.post("/")
def create_facture(facture: FactureCreate, db: Session = Depends(get_db)):
    facture = Facture(title=facture.title, company=facture.company, amount=facture.amount)
    db.add(facture)
    db.commit()
    db.refresh(facture)
    return facture

@facture_router.get("/")
def get_factures(db: Session = Depends(get_db)):
    return db.query(Facture).all()

@facture_router.get("/{facture_id}")
def get_facture_by_id(facture_id: int, db: Session = Depends(get_db)):
    return db.query(Facture).filter(Facture.id == facture_id).first()
