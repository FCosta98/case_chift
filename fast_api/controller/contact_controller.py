from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import get_db
from schemas.schemas import ContactCreate
from models.models import Contact

contact_router = APIRouter(prefix="/contacts", tags=["Contacts"])

@contact_router.post("/")
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    contact = Contact(name=contact.name, email=contact.email)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

@contact_router.get("/")
def get_contacts(db: Session = Depends(get_db)):
    return db.query(Contact).all()

@contact_router.get("/{contact_id}")
def get_contact_by_id(contact_id: int, db: Session = Depends(get_db)):
    return db.query(Contact).filter(Contact.id == contact_id).first()