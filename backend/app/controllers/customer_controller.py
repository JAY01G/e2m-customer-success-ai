"""Customer HTTP Controller.

Handles HTTP requests for customer listing, filtering, creation, detail inspection,
updates, and deletions.
"""

import uuid
from sqlalchemy.orm import Session
from app.helpers import api_response
from app.schemas import (
    APIResponse,
    CustomerCreate,
    CustomerFilterParams,
    CustomerResponse,
    CustomerUpdate,
    PaginatedData,
)
from app.services.customer_service import CustomerService


class CustomerController:
    """Controller handling Customer CRUD and query filtering endpoints."""

    @staticmethod
    def get_customers(
        filters: CustomerFilterParams,
        page: int,
        page_size: int,
        db: Session,
    ) -> APIResponse[PaginatedData[CustomerResponse]]:
        """Retrieve paginated and filtered list of customers.

        Args:
            filters: Customer filter parameters.
            page: 1-based page index.
            page_size: Maximum items per page.
            db: Database session.

        Returns:
            APIResponse[PaginatedData[CustomerResponse]]: Paginated customer response envelope.
        """
        service = CustomerService(db)
        data = service.get_all_paginated(filters=filters, page=page, page_size=page_size)
        return api_response(
            data=data,
            message="Customers retrieved successfully",
        )

    @staticmethod
    def get_customer(customer_id: uuid.UUID, db: Session) -> APIResponse[CustomerResponse]:
        """Retrieve single customer details by UUID.

        Args:
            customer_id: Customer UUID.
            db: Database session.

        Returns:
            APIResponse[CustomerResponse]: Customer detail envelope.
        """
        service = CustomerService(db)
        customer = service.get_by_id(customer_id)
        return api_response(
            data=CustomerResponse.model_validate(customer),
            message="Customer retrieved successfully",
        )

    @staticmethod
    def create_customer(
        req: CustomerCreate, db: Session
    ) -> APIResponse[CustomerResponse]:
        """Create a new customer account.

        Args:
            req: Customer creation payload.
            db: Database session.

        Returns:
            APIResponse[CustomerResponse]: Created customer envelope.
        """
        service = CustomerService(db)
        customer = service.create(req)
        return api_response(
            data=CustomerResponse.model_validate(customer),
            message="Customer created successfully",
        )

    @staticmethod
    def update_customer(
        customer_id: uuid.UUID, req: CustomerUpdate, db: Session
    ) -> APIResponse[CustomerResponse]:
        """Update existing customer details.

        Args:
            customer_id: Customer UUID.
            req: Customer update fields.
            db: Database session.

        Returns:
            APIResponse[CustomerResponse]: Updated customer envelope.
        """
        service = CustomerService(db)
        customer = service.update(customer_id, req)
        return api_response(
            data=CustomerResponse.model_validate(customer),
            message="Customer updated successfully",
        )

    @staticmethod
    def delete_customer(customer_id: uuid.UUID, db: Session) -> APIResponse[None]:
        """Delete a customer account.

        Args:
            customer_id: Customer UUID.
            db: Database session.

        Returns:
            APIResponse[None]: Deletion confirmation envelope.
        """
        service = CustomerService(db)
        service.delete(customer_id)
        return api_response(
            data=None,
            message="Customer deleted successfully",
        )

