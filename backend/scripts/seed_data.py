"""Database Demonstration and Test Seeding Script.

Populates initial operator accounts (Admin, CSM, Viewer), demo customer accounts,
touchpoint interaction logs, and realistic AI insight analyses for local development and demos.
"""

import os
import sys
import uuid
from datetime import datetime, timedelta, timezone

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import SessionLocal, init_db
from app.models.ai_insight import AIInsight, GenerationStatus, SentimentType
from app.models.customer import Customer, CustomerStatus
from app.models.interaction import Interaction, InteractionType
from app.models.user import User, UserRole
from app.utils.security import get_password_hash


def seed_database():
    """Seed PostgreSQL database with users, customers, interactions, and AI insights.

    Creates baseline accounts:
    - Admin: admin@example.com / Password123!
    - CSM: csm@example.com / Password123!
    - Viewer: viewer@example.com / Password123!
    """
    print("Initializing database tables...")
    init_db()

    db = SessionLocal()
    try:
        # Check if already seeded
        existing_admin = db.query(User).filter(User.email == "admin@example.com").first()
        if existing_admin:
            print("Database already contains seed data. Skipping...")
            return

        print("Seeding Users...")
        # 1. Users
        password_hash = get_password_hash("Password123!")

        admin_user = User(
            name="Admin User",
            email="admin@example.com",
            hashed_password=password_hash,
            role=UserRole.ADMIN,
            is_active=True,
        )
        csm_user = User(
            name="Sarah Jenkins",
            email="csm@example.com",
            hashed_password=password_hash,
            role=UserRole.CUSTOMER_SUCCESS_MANAGER,
            is_active=True,
        )
        viewer_user = User(
            name="John Viewer",
            email="viewer@example.com",
            hashed_password=password_hash,
            role=UserRole.VIEWER,
            is_active=True,
        )

        db.add_all([admin_user, csm_user, viewer_user])
        db.commit()
        db.refresh(admin_user)
        db.refresh(csm_user)
        db.refresh(viewer_user)

        print("Seeding Customers...")
        # 2. Customers
        customers_data = [
            {
                "name": "Alex Rivera",
                "company_name": "Acme Global Tech",
                "email": "alex.rivera@acmetech.io",
                "phone": "+1 (555) 234-5678",
                "industry": "Enterprise Software / SaaS",
                "status": CustomerStatus.ACTIVE,
                "health_score": 92,
                "owner_id": csm_user.id,
                "notes": "Key enterprise account. Recently expanded to 250 seats. Happy with platform performance.",
            },
            {
                "name": "David Kim",
                "company_name": "FinPulse Analytics",
                "email": "david.kim@finpulse.com",
                "phone": "+1 (555) 876-5432",
                "industry": "Fintech & Banking",
                "status": CustomerStatus.ACTIVE,
                "health_score": 85,
                "owner_id": csm_user.id,
                "notes": "Adoption steady across finance operations team. Requested custom executive dashboard reports.",
            },
            {
                "name": "Elena Rostova",
                "company_name": "Nova Health Solutions",
                "email": "elena.r@novahealth.org",
                "phone": "+1 (555) 345-6789",
                "industry": "Healthcare & MedTech",
                "status": CustomerStatus.AT_RISK,
                "health_score": 45,
                "owner_id": csm_user.id,
                "notes": "Encountering onboarding delays. User adoption below target threshold. Urgent CSM intervention required.",
            },
            {
                "name": "Marcus Vance",
                "company_name": "CloudScale Systems",
                "email": "marcus.vance@cloudscale.io",
                "phone": "+1 (555) 901-2345",
                "industry": "Cloud Infrastructure",
                "status": CustomerStatus.AT_RISK,
                "health_score": 38,
                "owner_id": admin_user.id,
                "notes": "Renewal in 60 days. Executive sponsor departed last month. Mentioned competing RFP.",
            },
            {
                "name": "Samantha Lee",
                "company_name": "Loomis Logistics",
                "email": "slee@loomislogistics.com",
                "phone": "+1 (555) 654-3210",
                "industry": "Supply Chain & Logistics",
                "status": CustomerStatus.PROSPECT,
                "health_score": 75,
                "owner_id": csm_user.id,
                "notes": "Proof of Concept completed. Contract negotiation in legal review.",
            },
            {
                "name": "Brian Thorne",
                "company_name": "Legacy Media Corp",
                "email": "brian.t@legacymedia.net",
                "phone": "+1 (555) 112-2334",
                "industry": "Media & Publishing",
                "status": CustomerStatus.CHURNED,
                "health_score": 15,
                "owner_id": admin_user.id,
                "notes": "Churned due to budget consolidation and organizational restructuring.",
            },
        ]

        created_customers = []
        for c in customers_data:
            cust = Customer(**c)
            db.add(cust)
            created_customers.append(cust)

        db.commit()
        for cust in created_customers:
            db.refresh(cust)

        print("Seeding Interactions and AI Insights...")
        # 3. Interactions & AI Insights
        now = datetime.now(timezone.utc)

        interactions_data = [
            (
                created_customers[0],  # Acme
                csm_user.id,
                InteractionType.MEETING,
                "Quarterly Business Review - Q2 Expansion",
                now - timedelta(days=2),
                "Customer team attended QBR. Very pleased with 99.9% platform uptime and customer support responsiveness. Requested training session for their newly acquired European division. Plan to renew 3-year agreement next quarter.",
                45,
                "Quarterly Business Review concluded with strong alignment. Customer is highly satisfied with current performance and preparing 3-year renewal with European expansion.",
                SentimentType.Positive,
                [
                    "Schedule European division onboarding session for next Tuesday",
                    "Send draft 3-year renewal terms to procurement",
                    "Share updated product roadmap deck",
                ],
                [],
            ),
            (
                created_customers[1],  # FinPulse
                csm_user.id,
                InteractionType.CALL,
                "Bi-weekly Health & Adoption Check-in",
                now - timedelta(days=5),
                "Routine check-in with David Kim. Team has questions on setting up automated weekly PDF reports. Overall usage remains consistent. No blockers reported.",
                30,
                "Standard bi-weekly check-in confirmed healthy usage. Follow-up needed for automated PDF reporting workflow.",
                SentimentType.Neutral,
                [
                    "Email documentation on automated PDF exports",
                    "Confirm attendance for upcoming feature webinar",
                ],
                [],
            ),
            (
                created_customers[2],  # Nova Health (AT_RISK)
                csm_user.id,
                InteractionType.MEETING,
                "Critical Escalation Call - Integration Latency",
                now - timedelta(days=1),
                "Elena expressed severe frustration regarding API sync lag affecting doctor scheduling. Clinical staff experiencing 5-minute data delays. Threatened to pause rollout if sync speed is not resolved within 2 weeks.",
                60,
                "Escalation call regarding severe API data synchronization delays in clinical scheduling workflow. High risk of rollout suspension.",
                SentimentType.Negative,
                [
                    "Escalate API sync latency ticket to Core Engineering tier 3",
                    "Schedule technical war-room with Nova IT team within 24 hours",
                    "Provide daily executive status updates to Elena",
                ],
                [
                    "Customer may halt enterprise rollout if sync speed is not fixed within 14 days",
                    "Clinical staff frustration could impact executive renewal decision",
                ],
            ),
            (
                created_customers[3],  # CloudScale (AT_RISK)
                admin_user.id,
                InteractionType.MEETING,
                "Renewal Strategy & Stakeholder Re-alignment",
                now - timedelta(days=3),
                "Marcus informed us that their VP of Engineering left. New leadership is reviewing all tooling budgets and has received proposals from competitor vendors. Need to demonstrate quantifiable ROI before next month.",
                50,
                "Renewal at high risk following executive sponsor departure and competitor evaluation. Urgent ROI demonstration required.",
                SentimentType.Negative,
                [
                    "Prepare custom ROI and cost-savings report for incoming VP of Engineering",
                    "Request introduction meeting with new VP",
                    "Offer complimentary technical health audit",
                ],
                [
                    "Active competitor RFP in progress for upcoming renewal cycle",
                    "Lack of executive alignment after sponsor transition",
                ],
            ),
            (
                created_customers[4],  # Loomis (PROSPECT)
                csm_user.id,
                InteractionType.DEMO,
                "Security & Compliance Deep Dive Demo",
                now - timedelta(days=7),
                "Demonstrated SOC2 compliance, role-based access control, and audit log capabilities to Loomis security council. Received positive feedback from CISO. Pending standard master service agreement sign-off.",
                45,
                "Successful security compliance demonstration for Loomis stakeholders. Positive signals for imminent contract completion.",
                SentimentType.Positive,
                [
                    "Send finalized SOC2 report and security whitepaper",
                    "Follow up with legal on MSA review status",
                ],
                [],
            ),
        ]

        for cust, uid, itype, title, mdate, notes, dur, ai_summary, ai_sent, actions, risks in interactions_data:
            interaction = Interaction(
                customer_id=cust.id,
                user_id=uid,
                type=itype,
                title=title,
                meeting_date=mdate,
                notes=notes,
                duration_minutes=dur,
            )
            db.add(interaction)
            db.commit()
            db.refresh(interaction)

            ai_insight = AIInsight(
                interaction_id=interaction.id,
                summary=ai_summary,
                sentiment=ai_sent,
                action_items=actions,
                risks=risks,
                model="gpt-4o-mini",
                generation_status=GenerationStatus.SUCCESS,
            )
            db.add(ai_insight)
            db.commit()

        print("Database seeded successfully!")
        print("-" * 50)
        print("Demo Credentials:")
        print("Admin:   admin@example.com  / Password123!")
        print("CSM:     csm@example.com    / Password123!")
        print("Viewer:  viewer@example.com / Password123!")
        print("-" * 50)

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

