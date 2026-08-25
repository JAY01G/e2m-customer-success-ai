# Database Architecture & Entity-Relationship Diagram

This document describes the normalized PostgreSQL relational database schema for the **AI-Powered Customer Success Platform**.

---

## 1. Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    USERS {
        uuid id PK "UUID Primary Key"
        string name "User full name"
        string email UK "Unique indexed email"
        string hashed_password "Argon2 password hash"
        enum role "ADMIN | CUSTOMER_SUCCESS_MANAGER | VIEWER"
        boolean is_active "Account status flag"
        timestamp created_at "Creation timestamp UTC"
        timestamp updated_at "Update timestamp UTC"
    }

    CUSTOMERS {
        uuid id PK "UUID Primary Key"
        string name "Primary contact name (Indexed)"
        string company_name "Company name (Indexed)"
        string email "Primary customer email"
        string phone "Contact telephone number"
        string industry "Industry vertical"
        enum status "ACTIVE | AT_RISK | CHURNED | PROSPECT (Indexed)"
        integer health_score "Health score 0-100 (Indexed)"
        uuid owner_id FK "Assigned CSM/Owner UUID (Indexed)"
        text notes "Account background and strategic notes"
        timestamp created_at "Creation timestamp UTC"
        timestamp updated_at "Update timestamp UTC"
    }

    INTERACTIONS {
        uuid id PK "UUID Primary Key"
        uuid customer_id FK "Customer UUID (Indexed)"
        uuid user_id FK "User/CSM UUID (Indexed)"
        enum type "MEETING | CALL | EMAIL | DEMO | OTHER (Indexed)"
        string title "Interaction subject or title"
        timestamp meeting_date "Meeting date (Indexed)"
        text notes "Meeting transcript / notes content"
        integer duration_minutes "Meeting duration in minutes"
        timestamp created_at "Creation timestamp UTC"
        timestamp updated_at "Update timestamp UTC"
    }

    AI_INSIGHTS {
        uuid id PK "UUID Primary Key"
        uuid interaction_id FK,UK "Unique Interaction UUID"
        text summary "Executive business summary"
        enum sentiment "Positive | Neutral | Negative"
        json action_items "Extracted action items array"
        json risks "Identified account risks array"
        string model "AI model name (e.g., gpt-4o-mini)"
        enum generation_status "SUCCESS | FAILED | FALLBACK"
        timestamp created_at "Creation timestamp UTC"
        timestamp updated_at "Update timestamp UTC"
    }

    USERS ||--o{ CUSTOMERS : "owns / manages"
    USERS ||--o{ INTERACTIONS : "records"
    CUSTOMERS ||--o{ INTERACTIONS : "has"
    INTERACTIONS ||--o| AI_INSIGHTS : "generates (1:1)"
```

---

## 2. Table Specifications & Constraints

### 2.1 Table: `users`
* **Primary Key**: `id` (UUIDv4)
* **Unique Constraints**: `email` (Case-insensitive, indexed)
* **Check Constraints**: `is_active IN (true, false)`
* **Foreign Keys**: None (Parent root entity)

### 2.2 Table: `customers`
* **Primary Key**: `id` (UUIDv4)
* **Foreign Keys**:
  * `owner_id` &rarr; `users.id` (`ON DELETE SET NULL`)
* **Check Constraints**:
  * `check_health_score_range`: `health_score >= 0 AND health_score <= 100`
* **Indexes**:
  * `ix_customers_name` on `name`
  * `ix_customers_company_name` on `company_name`
  * `ix_customers_status` on `status`
  * `ix_customers_health_score` on `health_score`
  * `ix_customers_owner_id` on `owner_id`

### 2.3 Table: `interactions`
* **Primary Key**: `id` (UUIDv4)
* **Foreign Keys**:
  * `customer_id` &rarr; `customers.id` (`ON DELETE CASCADE`)
  * `user_id` &rarr; `users.id` (`ON DELETE SET NULL`)
* **Indexes**:
  * `ix_interactions_customer_id` on `customer_id`
  * `ix_interactions_user_id` on `user_id`
  * `ix_interactions_meeting_date` on `meeting_date`
  * `ix_interactions_type` on `type`

### 2.4 Table: `ai_insights`
* **Primary Key**: `id` (UUIDv4)
* **Foreign Keys**:
  * `interaction_id` &rarr; `interactions.id` (`ON DELETE CASCADE`, Unique 1:1 relationship)
* **Indexes**:
  * `ix_ai_insights_interaction_id` on `interaction_id` (Unique)
