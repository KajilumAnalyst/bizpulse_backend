"""
stores.py — Multi-store management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import User, Store
from app.schemas.schemas import StoreCreate, StoreOut

router = APIRouter(prefix="/stores", tags=["Stores"])

@router.post("/", response_model=StoreOut, status_code=201)
def create_store(body: StoreCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    store = Store(owner_id=user.id, **body.model_dump())
    db.add(store)
    db.commit()
    db.refresh(store)
    return store

@router.get("/", response_model=List[StoreOut])
def list_stores(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Store).filter(Store.owner_id == user.id, Store.is_active == True).all()

@router.put("/{store_id}", response_model=StoreOut)
def update_store(store_id: int, body: StoreCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    store = db.query(Store).filter(Store.id == store_id, Store.owner_id == user.id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(store, field, value)
    db.commit()
    db.refresh(store)
    return store

@router.delete("/{store_id}", status_code=204)
def delete_store(store_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    store = db.query(Store).filter(Store.id == store_id, Store.owner_id == user.id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    store.is_active = False
    db.commit()
