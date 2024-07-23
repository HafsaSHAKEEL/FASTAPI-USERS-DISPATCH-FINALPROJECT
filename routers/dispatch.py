# routers/dispatch.py
import dispatch

import schemas
import crud
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from auth_helper import get_db
from routers.auth_bearer import JWTBearer

router = APIRouter()


@router.post("/create", response_model=schemas.DispatchBase)
async def create_dispatch(
    dispatch: schemas.DispatchCreate,
    db: Session = Depends(get_db),
    token: str = Depends(JWTBearer())
):
    user = crud.get_current_user(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Create and return the new dispatch directly
    return crud.create_dispatch(
        db,
        area=dispatch.area,
        created_at=datetime.utcnow(),
        user_id=user.id
    )


@router.get("/dispatches", response_model=schemas.DispatchList)
async def get_dispatches(
        page: int = Query(1, ge=1),
        limit: int = Query(10, le=100),
        db: Session = Depends(get_db),
        token: str = Depends(JWTBearer())
):
    user = crud.get_current_user(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    skip = (page - 1) * limit
    dispatches = crud.get_dispatches(db, skip=skip, limit=limit)
    total = db.query(crud.models.Dispatch).count()

    # Log the dispatches fetched from the database
    for dispatch in dispatches:
        print(dispatch.__dict__)  # Print the SQLAlchemy model fields

    # Convert SQLAlchemy models to Pydantic models
    dispatch_list = []
    for dispatch in dispatches:
        try:
            dispatch_list.append(schemas.DispatchBase.from_orm(dispatch))
        except Exception as e:
            print(f"Error converting dispatch: {e}")

    return schemas.DispatchList(total=total, dispatches=dispatch_list)
