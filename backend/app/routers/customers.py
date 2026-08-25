"""Customer Accounts API Router.

Mounts endpoints for paginated filtering and searching, account creation,
detail retrieval, updates, and deletions with RBAC protection.
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.controllers.customer_controller import CustomerController
from app.database.dependencies import get_db
from app.dependencies.permissions import (
    require_admin,
    require_any_authenticated,
    require_csm_or_admin,
)
from app.models.customer import CustomerStatus
from app.models.user import User
from app.schemas import (
    APIResponse,
    CustomerCreate,
    CustomerFilterParams,
    CustomerResponse,
    CustomerUpdate,
    PaginatedData,
)

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get(
    "",
    response_model=APIResponse[PaginatedData[CustomerResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get paginated list of customers with filtering, search, and sorting",
    response_description="Paginated customer collection matching active query parameters",
)
def get_customers(
    page: int = Query(1, ge=1, description="1-based page index"),
    page_size: int = Query(20, ge=1, le=100, description="Items returned per page (max 100)"),
    search: Optional[str] = Query(None, description="Search across name, company, email"),
    status: Optional[CustomerStatus] = Query(None, description="Filter by customer status"),
    owner_id: Optional[uuid.UUID] = Query(None, description="Filter by assigned CSM/Owner UUID"),
    min_health_score: Optional[int] = Query(None, ge=0, le=100, description="Minimum health score filter (0-100)"),
    max_health_score: Optional[int] = Query(None, ge=0, le=100, description="Maximum health score filter (0-100)"),
    sort_by: str = Query("created_at", description="Sort field: created_at, health_score, name, company_name"),
    sort_order: str = Query("desc", description="Sort order: asc, desc"),
    current_user: User = Depends(require_any_authenticated),
    db: Session = Depends(get_db),
):
    """Retrieve paginated and filtered list of customer records with Redis caching.

    Args:
        page: 1-based page number.
        page_size: Number of items per page.
        search: Free-text search term matching customer name, company, or email.
        status: Lifecycle status filter (ACTIVE, AT_RISK, CHURNED, PROSPECT).
        owner_id: UUID of assigned Account Owner / CSM.
        min_health_score: Lower bound health score filter (0-100).
        max_health_score: Upper bound health score filter (0-100).
        sort_by: Target sort column.
        sort_order: Sort direction ('asc' or 'desc').
        current_user: Authenticated operator user.
        db: Scoped database session.

    Returns:
        APIResponse[PaginatedData[CustomerResponse]]: Paginated customer response envelope.
    """
    filters = CustomerFilterParams(
        search=search,
        status=status,
        owner_id=owner_id,
        min_health_score=min_health_score,
        max_health_score=max_health_score,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return CustomerController.get_customers(
        filters=filters, page=page, page_size=page_size, db=db
    )


@router.post(
    "",
    response_model=APIResponse[CustomerResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new customer account (CSM and Admin)",
    response_description="Persisted customer account details",
)
def create_customer(
    req: CustomerCreate,
    current_user: User = Depends(require_csm_or_admin),
    db: Session = Depends(get_db),
):
    """Create and persist a new customer account.

    Args:
        req: Customer creation payload.
        current_user: Authenticated CSM or Admin user.
        db: Scoped database session.

    Returns:
        APIResponse[CustomerResponse]: Created customer record envelope.
    """
    return CustomerController.create_customer(req=req, db=db)


@router.get(
    "/{customer_id}",
    response_model=APIResponse[CustomerResponse],
    status_code=status.HTTP_200_OK,
    summary="Get customer details by UUID",
    response_description="Customer account details and CSM owner info",
)
def get_customer(
    customer_id: uuid.UUID,
    current_user: User = Depends(require_any_authenticated),
    db: Session = Depends(get_db),
):
    """Fetch complete customer record including assigned owner details.

    Args:
        customer_id: Target customer UUID.
        current_user: Authenticated user.
        db: Scoped database session.

    Returns:
        APIResponse[CustomerResponse]: Customer detail envelope.
    """
    return CustomerController.get_customer(customer_id=customer_id, db=db)


@router.patch(
    "/{customer_id}",
    response_model=APIResponse[CustomerResponse],
    status_code=status.HTTP_200_OK,
    summary="Update customer details (CSM and Admin)",
    response_description="Updated customer profile record",
)
def update_customer(
    customer_id: uuid.UUID,
    req: CustomerUpdate,
    current_user: User = Depends(require_csm_or_admin),
    db: Session = Depends(get_db),
):
    """Update fields on an existing customer account.

    Args:
        customer_id: Target customer UUID.
        req: Updated customer attributes.
        current_user: Authenticated CSM or Admin user.
        db: Scoped database session.

    Returns:
        APIResponse[CustomerResponse]: Updated customer record envelope.
    """
    return CustomerController.update_customer(
        customer_id=customer_id, req=req, db=db
    )


@router.delete(
    "/{customer_id}",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Delete customer (Admin only)",
    response_description="Customer deletion confirmation",
)
def delete_customer(
    customer_id: uuid.UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a customer account from the database.

    Args:
        customer_id: Target customer UUID to delete.
        current_user: Authenticated Admin user.
        db: Scoped database session.

    Returns:
        APIResponse[None]: Deletion confirmation envelope.
    """
    return CustomerController.delete_customer(customer_id=customer_id, db=db)


