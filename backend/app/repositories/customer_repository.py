"""Customer Data Access Repository.

Implements database queries, multi-attribute filtering, sorting, pagination,
and statistical aggregations (health distribution, churn analysis) for Customer entities.
"""

import uuid
from typing import Dict, List, Optional, Tuple
from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session, joinedload
from app.models.customer import Customer, CustomerStatus
from app.schemas.customer import CustomerFilterParams


class CustomerRepository:
    """Repository managing Customer data access, queries, and aggregations."""

    def __init__(self, db: Session):
        """Initialize repository with an active SQLAlchemy database session.

        Args:
            db: Scoped database session.
        """
        self.db = db

    def get_by_id(self, customer_id: uuid.UUID) -> Optional[Customer]:
        """Fetch a customer by UUID with eager loaded owner.

        Args:
            customer_id: Unique UUID of the customer.

        Returns:
            Optional[Customer]: Customer ORM entity if found, else None.
        """
        stmt = (
            select(Customer)
            .options(joinedload(Customer.owner))
            .where(Customer.id == customer_id)
        )
        return self.db.scalars(stmt).first()

    def get_all_paginated(
        self,
        filters: CustomerFilterParams,
        offset: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Customer], int]:
        """Retrieve filtered, searched, sorted, and paginated customer records.

        Args:
            filters: Filter and sort parameters schema.
            offset: Offset index for pagination.
            limit: Page size limit.

        Returns:
            Tuple[List[Customer], int]: List of matching customer records and total matching count.
        """
        query = select(Customer).options(joinedload(Customer.owner))
        count_query = select(func.count(Customer.id))

        # Apply search across name, company_name, email
        if filters.search:
            search_term = f"%{filters.search.strip()}%"
            search_clause = or_(
                Customer.name.ilike(search_term),
                Customer.company_name.ilike(search_term),
                Customer.email.ilike(search_term),
            )
            query = query.where(search_clause)
            count_query = count_query.where(search_clause)

        # Apply status filter
        if filters.status:
            query = query.where(Customer.status == filters.status)
            count_query = count_query.where(Customer.status == filters.status)

        # Apply owner filter
        if filters.owner_id:
            query = query.where(Customer.owner_id == filters.owner_id)
            count_query = count_query.where(Customer.owner_id == filters.owner_id)

        # Apply health score range filters
        if filters.min_health_score is not None:
            query = query.where(Customer.health_score >= filters.min_health_score)
            count_query = count_query.where(Customer.health_score >= filters.min_health_score)
        if filters.max_health_score is not None:
            query = query.where(Customer.health_score <= filters.max_health_score)
            count_query = count_query.where(Customer.health_score <= filters.max_health_score)

        # Total count
        total = self.db.scalar(count_query) or 0

        # Sorting
        sort_column = getattr(Customer, filters.sort_by, Customer.created_at)
        if filters.sort_order.lower() == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # Pagination
        query = query.offset(offset).limit(limit)
        items = list(self.db.scalars(query).all())

        return items, total

    def create(self, customer: Customer) -> Customer:
        """Persist a new customer record to the database.

        Args:
            customer: Unpersisted Customer model.

        Returns:
            Customer: Committed and refreshed Customer model.
        """
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def update(self, customer: Customer) -> Customer:
        """Commit updates to an existing customer record.

        Args:
            customer: Modified Customer model.

        Returns:
            Customer: Refreshed Customer model.
        """
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def delete(self, customer: Customer) -> None:
        """Delete a customer record from the database.

        Args:
            customer: Customer model to delete.
        """
        self.db.delete(customer)
        self.db.commit()

    def get_status_counts(self) -> Dict[str, int]:
        """Aggregate total customer counts grouped by lifecycle status.

        Returns:
            Dict[str, int]: Mapping of status string to count.
        """
        stmt = select(Customer.status, func.count(Customer.id)).group_by(Customer.status)
        results = self.db.execute(stmt).all()
        counts = {status.value: 0 for status in CustomerStatus}
        for status, count in results:
            if hasattr(status, "value"):
                counts[status.value] = count
            else:
                counts[str(status)] = count
        return counts

    def get_average_health(self) -> float:
        """Calculate the average health score across all customer accounts.

        Returns:
            float: Rounded average health score (0-100).
        """
        stmt = select(func.avg(Customer.health_score))
        avg = self.db.scalar(stmt)
        return round(float(avg), 1) if avg is not None else 0.0

    def get_health_distribution(self) -> Dict[str, int]:
        """Group and count customers across health score tiers (healthy, moderate, critical).

        Returns:
            Dict[str, int]: Dictionary with 'healthy', 'moderate', and 'critical' counts.
        """
        stmt = select(
            func.count(case((Customer.health_score >= 80, 1))).label("healthy"),
            func.count(case(((Customer.health_score >= 50) & (Customer.health_score < 80), 1))).label("moderate"),
            func.count(case((Customer.health_score < 50, 1))).label("critical"),
        )
        result = self.db.execute(stmt).first()
        if result:
            return {"healthy": result.healthy or 0, "moderate": result.moderate or 0, "critical": result.critical or 0}
        return {"healthy": 0, "moderate": 0, "critical": 0}

    def get_at_risk_customers(self, limit: int = 5) -> List[Customer]:
        """Retrieve highest-risk customer accounts ordered by health score ascending.

        Args:
            limit: Maximum number of at-risk accounts to retrieve.

        Returns:
            List[Customer]: List of at-risk customer ORM records.
        """
        stmt = (
            select(Customer)
            .options(joinedload(Customer.owner))
            .where(or_(Customer.status == CustomerStatus.AT_RISK, Customer.health_score < 60))
            .order_by(Customer.health_score.asc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

