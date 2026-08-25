"""Shared Type Definitions and Aliases.

Defines reusable type variables, string literals, and generic type annotations
used throughout the service and repository layers.
"""

import uuid
from typing import Any, Dict, List, Literal, Optional, TypeVar, Union

T = TypeVar("T")

# Core Type Aliases
ID = Union[str, uuid.UUID]
JSONDict = Dict[str, Any]
StringList = List[str]

# Domain Literal Types
UserRoleType = Literal["ADMIN", "CUSTOMER_SUCCESS_MANAGER", "VIEWER"]
CustomerStatusType = Literal["ACTIVE", "AT_RISK", "CHURNED", "PROSPECT"]
InteractionTypeLiteral = Literal["MEETING", "CALL", "EMAIL", "DEMO", "OTHER"]
SentimentTypeLiteral = Literal["Positive", "Neutral", "Negative"]
GenerationStatusLiteral = Literal["SUCCESS", "FAILED", "FALLBACK"]
HealthCategoryLiteral = Literal["Healthy", "Moderate", "Critical"]
SortOrderLiteral = Literal["asc", "desc"]

# Token Payload Dictionary
TokenPayload = Dict[str, Any]

