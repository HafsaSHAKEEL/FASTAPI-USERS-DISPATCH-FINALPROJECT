from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import crud
import schemas
from auth_helper import router
from database import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")
router = APIRouter(
    prefix="/api/dispatch",
    tags=["dispatch"]
)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme)):
    # This function should verify the token and return the user
    # For example purposes, we'll assume it returns a user ID
    # Implement token validation and user retrieval here
    user_id = 1  # Replace with actual user ID extraction from token
    return user_id


@router.post("/create", response_model=schemas.Dispatch)
def create_dispatch(
        dispatch: schemas.DispatchCreate,
        db: Session = Depends(get_db),
        user_id: int = Depends(get_current_user)
):
    return crud.create_dispatch(
        db=db, dispatch=dispatch, user_id=user_id
    )


@router.get("/", response_model=List[schemas.Dispatch])
def read_dispatches(
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(get_db),
        user_id: int = Depends(get_current_user)
):
    dispatches = crud.get_dispatches(db, skip=skip, limit=limit)
    return dispatches


@router.get("/{dispatch_id}", response_model=schemas.Dispatch)
def read_dispatch(
        dispatch_id: int,
        db: Session = Depends(get_db),
        user_id: int = Depends(get_current_user)
):
    db_dispatch = crud.get_dispatch_by_id(db, dispatch_id=dispatch_id)
    if db_dispatch is None:
        raise HTTPException(status_code=404, detail="Dispatch not found")
    return db_dispatch


@router.post("/{dispatch_id}/accept", response_model=schemas.Dispatch)
def accept_dispatch(
        dispatch_id: int,
        db: Session = Depends(get_db),
        user_id: int = Depends(get_current_user)
):
    db_dispatch = crud.get_dispatch_by_id(db, dispatch_id=dispatch_id)
    if db_dispatch is None:
        raise HTTPException(status_code=404, detail="Dispatch not found")
    db_dispatch.status = schemas.DispatchStatus.ACCEPTED
    db.commit()
    db.refresh(db_dispatch)
    return db_dispatch


@router.post("/{dispatch_id}/start", response_model=schemas.Dispatch)
def start_dispatch(
        dispatch_id: int,
        db: Session = Depends(get_db),
        user_id: int = Depends(get_current_user)
):
    db_dispatch = crud.get_dispatch_by_id(db, dispatch_id=dispatch_id)
    if db_dispatch is None:
        raise HTTPException(status_code=404, detail="Dispatch not found")
    db_dispatch.status = schemas.DispatchStatus.STARTED
    db.commit()
    db.refresh(db_dispatch)
    return db_dispatch


@router.post("/{dispatch_id}/complete", response_model=schemas.Dispatch)
def complete_dispatch(
        dispatch_id: int,
        pod_data: schemas.DispatchComplete,
        db: Session = Depends(get_db),
        user_id: int = Depends(get_current_user)
):
    db_dispatch = crud.get_dispatch_by_id(db, dispatch_id=dispatch_id)
    if db_dispatch is None:
        raise HTTPException(status_code=404, detail="Dispatch not found")
    db_dispatch.status = schemas.DispatchStatus.COMPLETED
    db_dispatch.pod_image = pod_data.pod_image
    db_dispatch.notes = pod_data.notes
    db_dispatch.recipient_name = pod_data.recipient_name
    db.commit()
    db.refresh(db_dispatch)
    return db_dispatch
