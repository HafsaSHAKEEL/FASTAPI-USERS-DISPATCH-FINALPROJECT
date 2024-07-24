import logging
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

import crud
import schemas

from auth_helper import get_db
from routers.auth_bearer import JWTBearer

router = APIRouter()

logging.basicConfig(level=logging.DEBUG)  # Set up logging configuration
logger = logging.getLogger(__name__)


@router.get("/dispatches/accepted", response_model=List[schemas.DispatchBase])
async def get_accepted_dispatches(
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
    token: str = Depends(JWTBearer()),
):
    """
    Retrieving a paginated list of accepted dispatches for the current user.
    - Validates the token to identify the current user.
    - Retrieves accepted dispatches for the user from the database.
    - Ensures that all fields of the dispatches are populated, providing defaults if necessary.
    - Returns the list of validated dispatches.
    """
    logger.debug(
        f"Received request for accepted dispatches: page={page}, limit={limit}, token={token}"
    )

    user = crud.get_current_user(db, token)
    logger.debug(f"Current user: {user}")

    if not user:
        logger.error("Invalid token, no user found.")
        raise HTTPException(status_code=401, detail="Invalid token")

    skip = (page - 1) * limit
    logger.debug(f"Calculated skip: {skip}")

    dispatches = crud.get_accepted_dispatches(
        db, user_id=user.id, skip=skip, limit=limit
    )
    logger.debug(f"Retrieved dispatches: {dispatches}")

    # Ensure all fields are populated correctly
    validated_dispatches: List[schemas.DispatchBase] = []
    for dispatch in dispatches:
        if dispatch.description is None:
            dispatch.description = "No description"
        if dispatch.date is None:
            dispatch.date = datetime.utcnow()
        if dispatch.created_at is None:
            dispatch.created_at = datetime.utcnow()
        validated_dispatches.append(dispatch)

    return validated_dispatches


@router.post("/create", response_model=schemas.DispatchBase)
async def create_dispatch(
    dispatch: schemas.DispatchCreate,
    db: Session = Depends(get_db),
    token: str = Depends(JWTBearer()),
):
    """
    Creating a new dispatch.
    - Validates the token to identify the current user.
    - Creates a new dispatch entry in the database with the specified area.
    - Returns the newly created dispatch.
    """
    user = crud.get_current_user(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return crud.create_dispatch(
        db, area=dispatch.area, created_at=datetime.utcnow(), user_id=user.id
    )


@router.get("/dispatches", response_model=List[schemas.DispatchBase])
async def get_dispatches(
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
    token: str = Depends(JWTBearer()),
):
    """
    Retrieve a list(paginated) of all dispatches for the current user.
    - Validates the token to identify the current user.
    - Retrieves all dispatches from the database.
    - Returns the list of dispatches.
    """
    user = crud.get_current_user(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    skip = (page - 1) * limit
    dispatches = crud.get_dispatches(db, skip=skip, limit=limit)

    return dispatches


@router.get("/dispatches/filter", response_model=List[schemas.DispatchBase])
async def filter_dispatches(
    status: Optional[str] = Query(None),
    date: Optional[datetime] = Query(None),
    area: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db),
    token: str = Depends(JWTBearer()),
):
    """
    Retrieve a paginated list of dispatches filtered by optional criteria.
    - Validates the token to identify the current user.
    - Applies filters (status, date, area) to the dispatches query.
    - Retrieves filtered dispatches from the database.
    - Returns the list of filtered dispatches.
    """
    user = crud.get_current_user(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    skip = (page - 1) * limit
    dispatches = crud.get_filtered_dispatches(db, status, date, area, skip, limit)

    return dispatches


@router.get("/dispatches/{dispatch_id}", response_model=schemas.DispatchBase)
async def get_dispatch_by_id(
    dispatch_id: int = Path(..., title="The ID of the dispatch to get"),
    db: Session = Depends(get_db),
    token: str = Depends(JWTBearer()),
):
    """
    Retrieving a dispatch by its ID.
    - Validates the token to identify the current user.
    - Retrieves the dispatch with the specified ID from the database.
    - Returns the dispatch or raises a 404 error if not found.
    """
    user = crud.get_current_user(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    dispatch = crud.get_dispatch_by_id(db, dispatch_id)
    if not dispatch:
        raise HTTPException(status_code=404, detail="Dispatch not found")

    return dispatch


@router.post("/dispatches/{dispatch_id}/accept")
async def accept_dispatch(
    dispatch_id: int = Path(..., title="The ID of the dispatch to accept"),
    db: Session = Depends(get_db),
    token: str = Depends(JWTBearer()),
):
    """
    Take a dispatch at face value.
    - Verifies the token's identity to determine the current user.
    - Assigns the current user to the dispatch after accepting it with the given ID.
    - if the accepted dispatch cannot be located, throws a 404 error and returns it.
    """
    print(f"Received dispatch_id: {dispatch_id}")  # Debugging line

    user = crud.get_current_user(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    accepted_dispatch = crud.accept_dispatch(db, dispatch_id, user.id)
    if not accepted_dispatch:
        raise HTTPException(status_code=404, detail="Dispatch not found")

    return accepted_dispatch


@router.post("/dispatches/{dispatch_id}/start")
async def start_dispatch(
    dispatch_id: int = Path(..., title="The ID of the dispatch to start"),
    db: Session = Depends(get_db),
    token: str = Depends(JWTBearer()),
):
    """
   Launch a dispatch using its ID.
    - it then confirms the current user by validating the token.
    - links the dispatch to the active user and launches it with the given ID.
    - If the dispatch is not found or permitted, returns the begun dispatch or issues a 404 error.
    """
    user = crud.get_current_user(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    started_dispatch = crud.start_dispatch(db, dispatch_id, user.id)
    if not started_dispatch:
        raise HTTPException(
            status_code=404, detail="Dispatch not found or not authorized"
        )

    return started_dispatch


@router.post("/dispatches/{dispatch_id}/complete")
async def complete_dispatch(
    dispatch_id: int = Path(..., title="The ID of the dispatch to complete"),
    pod_image: Optional[str] = Query(None, alias="podImage"),
    notes: Optional[str] = Query(None),
    recipient_name: Optional[str] = Query(None, alias="recipientName"),
    db: Session = Depends(get_db),
    token: str = Depends(JWTBearer()),
):
    """
    Complete a dispatch by its ID.
    - Ensures at least one of 'podImage', 'notes', or 'recipientName' is provided.
    - Validates the token to identify the current user.
    - Completes the dispatch with the specified ID and updates it with provided details.
    - Returns the completed dispatch or raises a 404 error if not found or authorized.
    """
    if not any([pod_image, notes, recipient_name]):    # Ensure at least one field is provided
        raise HTTPException(
            status_code=400,
            detail="At least one of 'podImage', 'notes', or 'recipientName' must be provided",
        )

    user = crud.get_current_user(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    completed_dispatch = crud.complete_dispatch(
        db,
        dispatch_id,
        user.id,
        pod_image if pod_image else "",
        notes if notes else "",
        recipient_name if recipient_name else "",
    )

    if not completed_dispatch:
        raise HTTPException(
            status_code=404, detail="Dispatch not found or not authorized"
        )

    return completed_dispatch
