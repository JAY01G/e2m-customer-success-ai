"""Customer Interactions API Router.

Mounts endpoints for logging meeting notes, touchpoint filtering, detail viewing,
updates, and deletions with optional background AI insights pipeline.
"""

import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.controllers.interaction_controller import InteractionController
from app.database.dependencies import get_db
from app.dependencies.permissions import (
    require_admin,
    require_any_authenticated,
    require_csm_or_admin,
)
from app.models.interaction import InteractionType
from app.models.user import User
from app.schemas import (
    APIResponse,
    InteractionCreate,
    InteractionFilterParams,
    InteractionResponse,
    InteractionUpdate,
    PaginatedData,
)

router = APIRouter(prefix="/interactions", tags=["Interactions"])


@router.get(
    "",
    response_model=APIResponse[PaginatedData[InteractionResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get paginated list of interactions with filtering and search",
    response_description="Paginated interaction touchpoint logs",
)
def get_interactions(
    page: int = Query(1, ge=1, description="1-based page index"),
    page_size: int = Query(20, ge=1, le=100, description="Items returned per page (max 100)"),
    customer_id: Optional[uuid.UUID] = Query(None, description="Filter by customer UUID"),
    user_id: Optional[uuid.UUID] = Query(None, description="Filter by creator/user UUID"),
    type: Optional[InteractionType] = Query(None, description="Filter by interaction type"),
    search: Optional[str] = Query(None, description="Search across title and notes"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    sort_by: str = Query("meeting_date", description="Sort field: meeting_date, created_at, title"),
    sort_order: str = Query("desc", description="Sort order: asc, desc"),
    current_user: User = Depends(require_any_authenticated),
    db: Session = Depends(get_db),
):
    """Retrieve paginated and filtered interactions with customer and author relationships.

    Args:
        page: Page number.
        page_size: Items per page.
        customer_id: Filter by Customer UUID.
        user_id: Filter by author User UUID.
        type: Interaction channel type (CALL, EMAIL, MEETING, DEMO, NOTE).
        search: Text query for interaction title and notes.
        start_date: Lower bound meeting date.
        end_date: Upper bound meeting date.
        sort_by: Sort column.
        sort_order: Sort direction.
        current_user: Authenticated operator.
        db: Scoped database session.

    Returns:
        APIResponse[PaginatedData[InteractionResponse]]: Paginated interactions envelope.
    """
    filters = InteractionFilterParams(
        customer_id=customer_id,
        user_id=user_id,
        type=type,
        search=search,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return InteractionController.get_interactions(
        filters=filters, page=page, page_size=page_size, db=db
    )


@router.post(
    "",
    response_model=APIResponse[InteractionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create interaction and optionally trigger AI analysis (CSM and Admin)",
    response_description="Persisted interaction record with AI insight extraction",
)
async def create_interaction(
    req: InteractionCreate,
    current_user: User = Depends(require_csm_or_admin),
    db: Session = Depends(get_db),
):
    """Record customer touchpoint notes and run AI insights pipeline.

    Args:
        req: Interaction creation payload.
        current_user: Authenticated CSM or Admin user.
        db: Scoped database session.

    Returns:
        APIResponse[InteractionResponse]: Persisted interaction envelope.
    """
    return await InteractionController.create_interaction(
        current_user=current_user, req=req, db=db
    )


@router.get(
    "/{interaction_id}",
    response_model=APIResponse[InteractionResponse],
    status_code=status.HTTP_200_OK,
    summary="Get interaction details by UUID",
    response_description="Interaction details and associated AI insights",
)
def get_interaction(
    interaction_id: uuid.UUID,
    current_user: User = Depends(require_any_authenticated),
    db: Session = Depends(get_db),
):
    """Fetch complete interaction record by UUID with AI insight.

    Args:
        interaction_id: Target interaction UUID.
        current_user: Authenticated operator.
        db: Scoped database session.

    Returns:
        APIResponse[InteractionResponse]: Interaction detail envelope.
    """
    return InteractionController.get_interaction(
        interaction_id=interaction_id, db=db
    )


@router.patch(
    "/{interaction_id}",
    response_model=APIResponse[InteractionResponse],
    status_code=status.HTTP_200_OK,
    summary="Update interaction details (CSM and Admin)",
    response_description="Updated interaction record",
)
def update_interaction(
    interaction_id: uuid.UUID,
    req: InteractionUpdate,
    current_user: User = Depends(require_csm_or_admin),
    db: Session = Depends(get_db),
):
    """Update fields on an existing interaction record.

    Args:
        interaction_id: Target interaction UUID.
        req: Update attributes.
        current_user: Authenticated CSM or Admin user.
        db: Scoped database session.

    Returns:
        APIResponse[InteractionResponse]: Updated interaction envelope.
    """
    return InteractionController.update_interaction(
        interaction_id=interaction_id, req=req, db=db
    )


@router.delete(
    "/{interaction_id}",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Delete interaction (Admin only)",
    response_description="Interaction deletion confirmation",
)
def delete_interaction(
    interaction_id: uuid.UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete an interaction record and associated AI insights.

    Args:
        interaction_id: Target interaction UUID.
        current_user: Authenticated Admin user.
        db: Scoped database session.

    Returns:
        APIResponse[None]: Deletion confirmation envelope.
    """
    return InteractionController.delete_interaction(
        interaction_id=interaction_id, db=db
    )


