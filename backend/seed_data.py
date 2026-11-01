import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.core.database import AsyncSessionLocal, Base, engine
from app.core.security import get_password_hash
from app.models.models import BudgetCategory, Event, Expense, Task, User, Vendor


async def seed():
    print("[INFO] Seeding realistic sample events...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 1. Create Demo Planner User
        demo_user = User(
            email="demo@eventwise.ai",
            hashed_password=get_password_hash("demo_password_123"),
            full_name="Sarah Jenkins (Event Lead)"
        )
        session.add(demo_user)
        await session.flush()

        now = datetime.now(timezone.utc)

        # 2. Seed Realistic Event 1: Sophia & Liam's Autumn Garden Wedding
        wedding_date = now + timedelta(days=120)
        wedding = Event(
            user_id=demo_user.id,
            title="Sophia & Liam's Garden Elegance Wedding",
            event_type="wedding",
            event_date=wedding_date,
            timezone="America/New_York",
            location="Highland Botanical Conservatory, NY",
            guest_count=150,
            total_budget=Decimal("35000.00"),
            currency="USD",
            preferences="Botanical garden vibe with warm fairy lighting, seasonal vegan culinary options, and live acoustic quartet.",
            theme="Enchanted Botanical & Warm Amber Sunset",
            concept_summary="An intimate garden conservatory wedding with cascading florals, warm string lights, and an artisan farm-to-table dinner menu."
        )
        session.add(wedding)
        await session.flush()

        # Categories & Expenses for Wedding
        cat_venue = BudgetCategory(event_id=wedding.id, name="Venue & Rentals", allocated_amount=Decimal("14000.00"), is_contingency=False)
        cat_catering = BudgetCategory(event_id=wedding.id, name="Catering & Bar", allocated_amount=Decimal("10000.00"), is_contingency=False)
        cat_photo = BudgetCategory(event_id=wedding.id, name="Photography & Video", allocated_amount=Decimal("4500.00"), is_contingency=False)
        cat_music = BudgetCategory(event_id=wedding.id, name="Music & Entertainment", allocated_amount=Decimal("2000.00"), is_contingency=False)
        cat_decor = BudgetCategory(event_id=wedding.id, name="Floral & Decor", allocated_amount=Decimal("2500.00"), is_contingency=False)
        cat_contingency = BudgetCategory(event_id=wedding.id, name="Contingency Reserve", allocated_amount=Decimal("2000.00"), is_contingency=True)

        session.add_all([cat_venue, cat_catering, cat_photo, cat_music, cat_decor, cat_contingency])
        await session.flush()

        exp1 = Expense(category_id=cat_venue.id, title="Conservatory Hall Rental Deposit", estimated_amount=Decimal("7000.00"), actual_amount=Decimal("7000.00"), is_paid=True, notes="Initial 50% deposit paid")
        exp2 = Expense(category_id=cat_venue.id, title="Chiavari Chairs & Linens", estimated_amount=Decimal("3500.00"), actual_amount=Decimal("3200.00"), is_paid=False, notes="Negotiated bulk discount")
        exp3 = Expense(category_id=cat_catering.id, title="Plated Dinner & Hors d'oeuvres (150 guests)", estimated_amount=Decimal("7500.00"), actual_amount=None, is_paid=False)
        exp4 = Expense(category_id=cat_catering.id, title="Artisan Wine & Cocktail Package", estimated_amount=Decimal("2500.00"), actual_amount=Decimal("2400.00"), is_paid=True)
        exp5 = Expense(category_id=cat_photo.id, title="Full Day Photography (2 shooters)", estimated_amount=Decimal("3000.00"), actual_amount=Decimal("3000.00"), is_paid=True)
        session.add_all([exp1, exp2, exp3, exp4, exp5])

        # Tasks for Wedding
        t1 = Task(event_id=wedding.id, title="Finalize Conservatory Contract & Deposit", due_date=wedding_date - timedelta(days=90), priority="critical", status="completed", completed_at=now)
        t2 = Task(event_id=wedding.id, title="Catering Menu Tasting & Guest Dietary Finalization", due_date=wedding_date - timedelta(days=60), priority="high", status="in_progress")
        t3 = Task(event_id=wedding.id, title="Send Formal Invitations & Launch RSVP Tracker", due_date=wedding_date - timedelta(days=45), priority="high", status="pending")
        t4 = Task(event_id=wedding.id, title="Sound Check & Acoustic Quartet Repertoire Confirmation", due_date=wedding_date - timedelta(days=14), priority="medium", status="pending")
        session.add_all([t1, t2, t3, t4])

        # Vendors for Wedding
        v1 = Vendor(event_id=wedding.id, category="Venue", name="Highland Botanical Conservatory", contact_name="Elena Rostova", phone="+1-555-019-2834", email="events@highlandgardens.sample", quoted_amount=Decimal("14000.00"), status="booked", is_ai_suggested=False, notes="Verified botanical venue contract signed.")
        v2 = Vendor(event_id=wedding.id, category="Catering", name="Artisan Harvest Culinary", contact_name="Chef Marcus Vance", phone="+1-555-019-7712", email="marcus@artisanharvest.sample", quoted_amount=Decimal("9900.00"), status="quoted", is_ai_suggested=True, notes="Sample vendor quotation received for 150 guests.")
        v3 = Vendor(event_id=wedding.id, category="Photography", name="Golden Hour Luminary Studios", contact_name="Clara Oswald", phone="+1-555-019-4482", email="clara@goldenhour.sample", quoted_amount=Decimal("4500.00"), status="booked", is_ai_suggested=False, notes="Contract locked with 8 hours of continuous coverage.")
        session.add_all([v1, v2, v3])

        # 3. Seed Realistic Event 2: Annual Techfest & Hackathon
        fest_date = now + timedelta(days=45)
        fest = Event(
            user_id=demo_user.id,
            title="Nexus Campus Innovation & TechFest 2026",
            event_type="college",
            event_date=fest_date,
            timezone="America/Chicago",
            location="Student Union Auditorium & Grand Quad",
            guest_count=600,
            total_budget=Decimal("18000.00"),
            currency="USD",
            preferences="High energy, 24-hr hackathon, sponsor expo booths, esports arena, and midnight snack food trucks.",
            theme="Cybernetic Futures & Open Innovation",
            concept_summary="A multi-track campus festival combining hands-on technical hackathons, sponsor keynotes, and live cultural entertainment."
        )
        session.add(fest)
        await session.flush()

        cat_fest_av = BudgetCategory(event_id=fest.id, name="AV, Stage & Lighting", allocated_amount=Decimal("7000.00"), is_contingency=False)
        cat_fest_food = BudgetCategory(event_id=fest.id, name="Student Refreshments & Food Trucks", allocated_amount=Decimal("5000.00"), is_contingency=False)
        cat_fest_prizes = BudgetCategory(event_id=fest.id, name="Hackathon Prizes & Badges", allocated_amount=Decimal("4000.00"), is_contingency=False)
        cat_fest_contingency = BudgetCategory(event_id=fest.id, name="Contingency Reserve", allocated_amount=Decimal("2000.00"), is_contingency=True)
        session.add_all([cat_fest_av, cat_fest_food, cat_fest_prizes, cat_fest_contingency])
        await session.flush()

        exp_f1 = Expense(category_id=cat_fest_av.id, title="Mainstage Sound System & Truss Rig", estimated_amount=Decimal("4500.00"), actual_amount=Decimal("4500.00"), is_paid=True)
        exp_f2 = Expense(category_id=cat_fest_food.id, title="Midnight Pizza & Energy Drinks (600 pax)", estimated_amount=Decimal("3000.00"), actual_amount=None, is_paid=False)
        session.add_all([exp_f1, exp_f2])

        task_f1 = Task(event_id=fest.id, title="Secure Campus Administration Facility Permits", due_date=fest_date - timedelta(days=30), priority="critical", status="completed", completed_at=now)
        task_f2 = Task(event_id=fest.id, title="Finalize Sponsor Booth Trusses & Power Lines", due_date=fest_date - timedelta(days=15), priority="high", status="in_progress")
        task_f3 = Task(event_id=fest.id, title="Volunteer Crowd Control Orientation", due_date=fest_date - timedelta(days=2), priority="high", status="pending")
        session.add_all([task_f1, task_f2, task_f3])

        vend_f1 = Vendor(event_id=fest.id, category="AV Production", name="Campus Sound & Light Co.", contact_name="David Miller", phone="+1-555-012-9900", email="rentals@campussound.sample", quoted_amount=Decimal("6800.00"), status="booked", is_ai_suggested=False)
        session.add(vend_f1)

        await session.commit()
        print("[SUCCESS] Database successfully seeded with 2 rich, realistic events!")

if __name__ == "__main__":
    asyncio.run(seed())
