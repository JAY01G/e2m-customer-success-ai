"""Customer Account Business Logic Service.

Orchestrates customer account operations, health score validation, assigned owner verification,
Redis caching layer integration, and cache invalidation workflows.
"""

import hashlib
import json
import uuid
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.config.logging import logger
from app.exceptions.custom_exceptions import NotFoundException, ValidationException
from app.models.customer import Customer
from app.models.user import User
from app.repositories.customer_repository import CustomerRepository
from app.repositories.user_repository import UserRepository
from app.schemas.customer import CustomerCreate, CustomerFilterParams, CustomerResponse, CustomerUpdate
from app.services.cache_service import cache_service
from app.utils.pagination import PaginatedData, create_paginated_response
from app.utils.validators import validate_health_score


class CustomerService:
    """Service providing business logic, validation, and caching for Customer accounts."""

    def __init__(self, db: Session):
        """Initialize CustomerService with database session, repositories, and cache.

        Args:
            db: Scoped SQLAlchemy database session.
        """
        self.db = db
        self.customer_repo = CustomerRepository(db)
        self.user_repo = UserRepository(db)

    def _generate_cache_key(self, filters: CustomerFilterParams, page: int, page_size: int) -> str:
        """Generate a deterministic MD5 hash cache key for customer query filters and pagination.

        Args:
            filters: Active filter parameters.
            page: Current page number.
            page_size: Maximum items per page.

        Returns:
            str: Cache key string with `customers:list:` prefix.
        """
        filter_dict = {
            "search": filters.search,
            "status": filters.status.value if filters.status else None,
            "owner_id": str(filters.owner_id) if filters.owner_id else None,
            "min_health_score": filters.min_health_score,
            "max_health_score": filters.max_health_score,
            "sort_by": filters.sort_by,
            "sort_order": filters.sort_order,
            "page": page,
            "page_size": page_size,
        }
        filters_str = json.dumps(filter_dict, sort_keys=True)
        filters_hash = hashlib.md5(filters_str.encode()).hexdigest()
        return f"customers:list:{filters_hash}"

    def get_by_id(self, customer_id: uuid.UUID) -> Customer:
        """Fetch a customer by UUID with detail caching.

        Args:
            customer_id: Unique UUID of the customer.

        Returns:
            Customer: Customer ORM entity.

        Raises:
            NotFoundException: If no customer exists with the given UUID.
        """
        # Check cache
        cache_key = f"customers:detail:{customer_id}"
        cached = cache_service.get(cache_key)
        if cached:
            pass

        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise NotFoundException(f"Customer with ID '{customer_id}' not found")

        # Populate cache
        try:
            resp = CustomerResponse.model_validate(customer).model_dump(mode="json")
            cache_service.set(cache_key, resp, ttl=60)
        except Exception as e:
            logger.warning(f"Failed to cache customer detail: {e}")

        return customer

    def get_all_paginated(
        self,
        filters: CustomerFilterParams,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedData[CustomerResponse]:
        """Fetch paginated customer records with Redis cache-aside strategy.

        Args:
            filters: Filter and sort parameter schema.
            page: 1-based page index.
            page_size: Items per page limit.

        Returns:
            PaginatedData[CustomerResponse]: Paginated response envelope containing customer DTOs.
        """
        # Cache lookup
        cache_key = self._generate_cache_key(filters, page, page_size)
        cached_data = cache_service.get(cache_key)
        if cached_data:
            logger.debug(f"[CACHE HIT] Returning cached customer list for key: {cache_key}")
            return PaginatedData[CustomerResponse](**cached_data)

        # DB Query on Cache Miss
        offset = (page - 1) * page_size
        items, total = self.customer_repo.get_all_paginated(filters, offset=offset, limit=page_size)

        response_items = [CustomerResponse.model_validate(item) for item in items]
        paginated_result = create_paginated_response(response_items, total, page, page_size)

        # Cache Population
        try:
            cache_service.set(cache_key, paginated_result.model_dump(mode="json"), ttl=60)
        except Exception as e:
            logger.warning(f"Failed to cache customer list: {e}")

        return paginated_result

    def create(self, data: CustomerCreate) -> Customer:
        """Validate, persist, and invalidate caches for a new customer account.

        Args:
            data: Customer creation payload.

        Returns:
            Customer: Created Customer ORM model.

        Raises:
            ValidationException: If health score is invalid or assigned owner does not exist.
        """
        validate_health_score(data.health_score)

        if data.owner_id:
            owner = self.user_repo.get_by_id(data.owner_id)
            if not owner:
                raise ValidationException(f"Assigned owner user ID '{data.owner_id}' does not exist")

        new_customer = Customer(
            name=data.name.strip(),
            company_name=data.company_name.strip(),
            email=data.email.lower().strip(),
            phone=data.phone.strip() if data.phone else None,
            industry=data.industry.strip() if data.industry else None,
            status=data.status,
            health_score=data.health_score,
            owner_id=data.owner_id,
            notes=data.notes,
        )

        customer = self.customer_repo.create(new_customer)
        logger.info(f"Created customer '{customer.name}' ({customer.company_name}) [ID: {customer.id}]")

        # Cache Invalidation
        cache_service.invalidate_customer_cache(str(customer.id))
        return customer

    def update(self, customer_id: uuid.UUID, data: CustomerUpdate) -> Customer:
        """Validate and apply updates to a customer record and flush associated caches.

        Args:
            customer_id: Unique UUID of the customer to update.
            data: Customer update fields.

        Returns:
            Customer: Updated Customer ORM model.

        Raises:
            ValidationException: If updated health score or assigned owner ID is invalid.
        """
        customer = self.get_by_id(customer_id)

        if data.health_score is not None:
            validate_health_score(data.health_score)
            customer.health_score = data.health_score

        if data.owner_id is not None:
            owner = self.user_repo.get_by_id(data.owner_id)
            if not owner:
                raise ValidationException(f"Assigned owner user ID '{data.owner_id}' does not exist")
            customer.owner_id = data.owner_id

        if data.name is not None:
            customer.name = data.name.strip()
        if data.company_name is not None:
            customer.company_name = data.company_name.strip()
        if data.email is not None:
            customer.email = data.email.lower().strip()
        if data.phone is not None:
            customer.phone = data.phone.strip() if data.phone else None
        if data.industry is not None:
            customer.industry = data.industry.strip() if data.industry else None
        if data.status is not None:
            customer.status = data.status
        if data.notes is not None:
            customer.notes = data.notes

        updated = self.customer_repo.update(customer)
        logger.info(f"Updated customer '{updated.name}' [ID: {updated.id}]")

        # Invalidate Cache
        cache_service.invalidate_customer_cache(str(customer_id))
        return updated

    def delete(self, customer_id: uuid.UUID) -> None:
        """Delete a customer record and flush related caches.

        Args:
            customer_id: Unique UUID of the customer to delete.
        """
        customer = self.get_by_id(customer_id)
        self.customer_repo.delete(customer)
        logger.info(f"Deleted customer [ID: {customer_id}]")

        # Invalidate Cache
        cache_service.invalidate_customer_cache(str(customer_id))

