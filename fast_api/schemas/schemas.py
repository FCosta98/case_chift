from pydantic import BaseModel

class FactureCreate(BaseModel):
    title: str
    company: str
    amount: float

class ContactCreate(BaseModel):
    name: str
    email: str