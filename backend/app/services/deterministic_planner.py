from decimal import Decimal
from typing import Any, Dict

from app.schemas.ai_plan import (
    GeneratedBudgetItem,
    GeneratedPlanSchema,
    GeneratedScheduleItem,
    GeneratedTaskItem,
    GeneratedVendorItem,
)


class DeterministicFallbackPlanner:
    """
    Deterministic planner providing robust, production-quality baseline plans
    when AI services are unreachable, timed out, or rate-limited.
    """

    TEMPLATES: Dict[str, Dict[str, Any]] = {
        "wedding": {
            "theme": "Timeless Elegance & Modern Romance",
            "concept_summary": "A cohesive, sophisticated celebration focusing on meaningful guest experiences, elegant floral aesthetics, and seamless logistical flow.",
            "personalized_ideas": [
                "Personalized welcome mocktail or cocktail station reflecting your journey",
                "Acoustic prelude during guest arrival followed by live evening entertainment",
                "Audio guestbook or vintage rotary phone recording station for heartfelt voice notes",
                "Late-night dessert bar or savory artisan snack station"
            ],
            "budget_allocations": [
                {"category": "Venue & Rentals", "allocated_percentage": Decimal("40.0"), "is_contingency": False, "suggested_expenses": ["Venue rental deposit", "Tables and seating", "Lighting"]},
                {"category": "Catering & Bar", "allocated_percentage": Decimal("25.0"), "is_contingency": False, "suggested_expenses": ["Dinner per guest", "Cocktail hour appetizers", "Bar package"]},
                {"category": "Photography & Video", "allocated_percentage": Decimal("12.0"), "is_contingency": False, "suggested_expenses": ["Lead photographer", "Highlight reel videographer"]},
                {"category": "Floral & Decor", "allocated_percentage": Decimal("10.0"), "is_contingency": False, "suggested_expenses": ["Centerpieces", "Ceremony arch", "Bouquets"]},
                {"category": "Music & Entertainment", "allocated_percentage": Decimal("5.0"), "is_contingency": False, "suggested_expenses": ["DJ & Sound equipment", "Emcee"]},
                {"category": "Contingency Fund", "allocated_percentage": Decimal("8.0"), "is_contingency": True, "suggested_expenses": ["Last-minute weather adjustments", "Tips & overtime"]}
            ],
            "tasks": [
                {"title": "Book Venue & Set Date", "description": "Confirm ceremony and reception spaces with signed contract.", "days_before_event": 180, "priority": "critical"},
                {"title": "Engage Catering & Finalize Menu Tasting", "description": "Review dietary options and guest count milestones.", "days_before_event": 120, "priority": "high"},
                {"title": "Hire Photographer & Videographer", "description": "Secure portfolios and agree on shot list.", "days_before_event": 90, "priority": "high"},
                {"title": "Send Formal Invitations & Track RSVPs", "description": "Distribute digital/paper invites with RSVP deadline.", "days_before_event": 60, "priority": "high"},
                {"title": "Finalize Floor Plan & Seating Chart", "description": "Coordinate vendor placement and guest table allocations.", "days_before_event": 21, "priority": "medium"},
                {"title": "Conduct Rehearsal & Final Vendor Sync", "description": "Confirm arrival times, load-in paths, and contact list.", "days_before_event": 3, "priority": "critical"}
            ],
            "vendor_categories": [
                {"category": "Venue", "suggested_role_description": "Hosts ceremony and reception setup", "estimated_budget_share": Decimal("40.0")},
                {"category": "Catering", "suggested_role_description": "Full dining, staff, and beverage service", "estimated_budget_share": Decimal("25.0")},
                {"category": "Photography", "suggested_role_description": "Captures pre-event, ceremony, and reception memories", "estimated_budget_share": Decimal("12.0")},
                {"category": "DJ / Band", "suggested_role_description": "Audio systems, ceremony mics, and dance music", "estimated_budget_share": Decimal("5.0")},
                {"category": "Florist", "suggested_role_description": "Floral displays, bridal party flowers, and centerpieces", "estimated_budget_share": Decimal("10.0")}
            ],
            "event_day_schedule": [
                {"time_offset_or_hour": "09:00 AM", "activity": "Vendor Load-in & Prep", "description": "Venue opens for setup, florist and sound checks begin."},
                {"time_offset_or_hour": "02:00 PM", "activity": "Pre-Ceremony Photography", "description": "Portraits and wedding party photography."},
                {"time_offset_or_hour": "04:00 PM", "activity": "Ceremony Begins", "description": "Processional, exchange of vows, and recessional."},
                {"time_offset_or_hour": "05:00 PM", "activity": "Cocktail Hour", "description": "Appetizers and signature drinks while hall transitions."},
                {"time_offset_or_hour": "06:30 PM", "activity": "Dinner & Speeches", "description": "Grand entrance, toast sequence, and dinner service."},
                {"time_offset_or_hour": "08:30 PM", "activity": "Dance Floor & Celebration", "description": "First dance, cake cutting, and open dance floor."},
                {"time_offset_or_hour": "11:00 PM", "activity": "Grand Exit & Teardown", "description": "Sparkler/bubble sendoff and scheduled pack-out."}
            ],
            "risks_and_mitigations": [
                "Weather disruption: Secure indoor contingency backup with the venue 30 days prior.",
                "Dietary surprises: Require explicit allergy submissions on RSVP forms.",
                "Overtime fees: Designate an on-site timeline coordinator to keep speeches on schedule."
            ]
        },
        "birthday": {
            "theme": "Vibrant Celebration & Milestone Social",
            "concept_summary": "A dynamic, high-energy party featuring interactive entertainment, curated food stations, and personalized photo moments.",
            "personalized_ideas": [
                "Curated retro throwback playlist or live acoustic DJ duo",
                "Signature dessert tower with personalized celebratory sparklers",
                "Interactive DIY photo booth with custom neon signage and instant prints",
                "Trivia or highlight game celebrating the guest of honor"
            ],
            "budget_allocations": [
                {"category": "Venue & Private Space", "allocated_percentage": Decimal("35.0"), "is_contingency": False, "suggested_expenses": ["Room rental", "Setup fee"]},
                {"category": "Food & Beverages", "allocated_percentage": Decimal("35.0"), "is_contingency": False, "suggested_expenses": ["Appetizer platters", "Beverage packages", "Cake/Desserts"]},
                {"category": "Decor & Lighting", "allocated_percentage": Decimal("12.0"), "is_contingency": False, "suggested_expenses": ["Balloon installation", "Lighting rental", "Table accents"]},
                {"category": "Entertainment & Music", "allocated_percentage": Decimal("10.0"), "is_contingency": False, "suggested_expenses": ["DJ or Playlist sound gear", "Games"]},
                {"category": "Contingency Fund", "allocated_percentage": Decimal("8.0"), "is_contingency": True, "suggested_expenses": ["Extra guests / extra bar tabs"]}
            ],
            "tasks": [
                {"title": "Reserve Venue / Social Space", "description": "Lock in space capacity and initial deposit.", "days_before_event": 45, "priority": "critical"},
                {"title": "Send Digital Invitations", "description": "Collect headcount via RSVP tracker.", "days_before_event": 30, "priority": "high"},
                {"title": "Order Custom Cake & Party Favors", "description": "Confirm baker delivery timeline.", "days_before_event": 14, "priority": "medium"},
                {"title": "Finalize Music Playlist & Activities", "description": "Coordinate speaker setup or DJ cue sheet.", "days_before_event": 7, "priority": "medium"},
                {"title": "Final Confirmation Call with Venue", "description": "Confirm access time for balloon artists and cake delivery.", "days_before_event": 2, "priority": "high"}
            ],
            "vendor_categories": [
                {"category": "Venue / Lounge", "suggested_role_description": "Event hall or party room", "estimated_budget_share": Decimal("35.0")},
                {"category": "Catering / Bakery", "suggested_role_description": "Hors d'oeuvres and celebratory cake", "estimated_budget_share": Decimal("35.0")},
                {"category": "Decor / Balloons", "suggested_role_description": "Backdrops, balloon garlands, and neon signs", "estimated_budget_share": Decimal("12.0")},
                {"category": "Photographer / Booth", "suggested_role_description": "Candid photos or self-serve photo kiosk", "estimated_budget_share": Decimal("10.0")}
            ],
            "event_day_schedule": [
                {"time_offset_or_hour": "05:00 PM", "activity": "Decor Setup & Cake Delivery", "description": "Balloon artist and cake placement."},
                {"time_offset_or_hour": "06:30 PM", "activity": "Guest Arrival & Welcome Drinks", "description": "Ambient background music, appetizers circulating."},
                {"time_offset_or_hour": "07:30 PM", "activity": "Welcome Toast & Mingling", "description": "Host welcome remarks and group photos."},
                {"time_offset_or_hour": "08:30 PM", "activity": "Cake Cutting & Dessert Celebration", "description": "Singing, sparklers, and sweet treats."},
                {"time_offset_or_hour": "09:15 PM", "activity": "Dancing & Party Games", "description": "Upbeat playlist and open mingling."}
            ],
            "risks_and_mitigations": [
                "Unregistered plus-ones: Budget 10% buffer for extra appetizers.",
                "Noise ordinances: Clarify venue curfews and decibel regulations early."
            ]
        },
        "college": {
            "theme": "Campus Innovation & Cultural Showcase",
            "concept_summary": "An engaging, student-centered campus fest balancing technical exhibitions, lively cultural performances, and networking hubs.",
            "personalized_ideas": [
                "Interactive sponsor tech showcase and student project exhibition",
                "Battle of the bands or acoustic stage showcasing campus talent",
                "Digital campus scavenger hunt with leaderboards and branded merchandise",
                "Food truck alley featuring diverse local vendors"
            ],
            "budget_allocations": [
                {"category": "Stage, AV & Production", "allocated_percentage": Decimal("35.0"), "is_contingency": False, "suggested_expenses": ["Mainstage trusses", "PA system", "LED screen rental"]},
                {"category": "Food & Beverage Stalls", "allocated_percentage": Decimal("25.0"), "is_contingency": False, "suggested_expenses": ["Student meal vouchers", "Refreshment kiosks"]},
                {"category": "Artist / Guest Honorariums", "allocated_percentage": Decimal("20.0"), "is_contingency": False, "suggested_expenses": ["Keynote speaker honorarium", "Performer fees"]},
                {"category": "Safety, Security & Permits", "allocated_percentage": Decimal("10.0"), "is_contingency": False, "suggested_expenses": ["Campus security overtime", "First aid station", "Barricades"]},
                {"category": "Contingency Fund", "allocated_percentage": Decimal("10.0"), "is_contingency": True, "suggested_expenses": ["Generator fuel", "Emergency equipment backup"]}
            ],
            "tasks": [
                {"title": "Submit Campus Facility & Security Permits", "description": "Obtain administrative approvals and security clearance.", "days_before_event": 60, "priority": "critical"},
                {"title": "Confirm Sound & Stage Production Vendor", "description": "Sign contracts for power backup, lighting, and audio rig.", "days_before_event": 45, "priority": "critical"},
                {"title": "Launch Student Registrations & Volunteer Drive", "description": "Form logistics, registration, and hospitality sub-committees.", "days_before_event": 30, "priority": "high"},
                {"title": "Finalize Schedule & Artist Rider Requirements", "description": "Verify stage equipment list and acoustic checks.", "days_before_event": 14, "priority": "high"},
                {"title": "Full Technical Rehearsal & Safety Briefing", "description": "Walkthrough emergency exits, crowd control, and cue sheets.", "days_before_event": 2, "priority": "critical"}
            ],
            "vendor_categories": [
                {"category": "Stage & Audio-Visual", "suggested_role_description": "Sound engineering, staging, mics, and lighting", "estimated_budget_share": Decimal("35.0")},
                {"category": "Food Trucks / Concessions", "suggested_role_description": "Multiple food options for students and staff", "estimated_budget_share": Decimal("25.0")},
                {"category": "Merchandise & Printing", "suggested_role_description": "Banners, ID badges, and festival t-shirts", "estimated_budget_share": Decimal("10.0")},
                {"category": "Emergency & Medical Support", "suggested_role_description": "On-site EMT and hydration stations", "estimated_budget_share": Decimal("5.0")}
            ],
            "event_day_schedule": [
                {"time_offset_or_hour": "08:00 AM", "activity": "Campus Gates Open & Registration", "description": "Student check-in, wristband issue, stall setups."},
                {"time_offset_or_hour": "10:00 AM", "activity": "Opening Ceremony & Keynote", "description": "Dean's welcome speech and fest kickoff."},
                {"time_offset_or_hour": "12:00 PM", "activity": "Exhibition & Competitive Tracks", "description": "Hackathons, debates, and tech demos."},
                {"time_offset_or_hour": "04:00 PM", "activity": "Cultural Performances & Battle of Bands", "description": "Main stage live performances."},
                {"time_offset_or_hour": "07:30 PM", "activity": "Award Ceremony & Closing DJ Session", "description": "Trophy distributions and concluding concert."}
            ],
            "risks_and_mitigations": [
                "Overcrowding: Implement zoned capacity controls and wristband checkpoints.",
                "Power tripping: Mandate secondary silent diesel generator backups."
            ]
        },
        "community": {
            "theme": "Community Harmony & Neighborhood Festival",
            "concept_summary": "An inclusive, family-friendly gathering emphasizing local culture, volunteer collaboration, and engaging shared activities.",
            "personalized_ideas": [
                "Local artisan craft marketplace and neighborhood talent booth",
                "Community potluck or sponsored community picnic BBQ",
                "Kids activity zone with face painting and lawn games",
                "Community mural canvas where every attendee contributes a brushstroke"
            ],
            "budget_allocations": [
                {"category": "Permits, Park & Sanitation", "allocated_percentage": Decimal("30.0"), "is_contingency": False, "suggested_expenses": ["Park reservation", "Portable restrooms", "Waste cleanup"]},
                {"category": "Refreshments & Community Food", "allocated_percentage": Decimal("30.0"), "is_contingency": False, "suggested_expenses": ["BBQ supplies", "Water stations", "Snacks"]},
                {"category": "Activities & Family Games", "allocated_percentage": Decimal("20.0"), "is_contingency": False, "suggested_expenses": ["Inflatables", "Lawn games", "Craft materials"]},
                {"category": "Signage & Safety", "allocated_percentage": Decimal("10.0"), "is_contingency": False, "suggested_expenses": ["Community notice signs", "First aid kits"]},
                {"category": "Contingency Fund", "allocated_percentage": Decimal("10.0"), "is_contingency": True, "suggested_expenses": ["Inclement weather shelters", "Extra supplies"]}
            ],
            "tasks": [
                {"title": "File Municipal Park & Sound Permit", "description": "Ensure public space reservation meets town ordinances.", "days_before_event": 60, "priority": "critical"},
                {"title": "Recruit Community Volunteer Leads", "description": "Assign setup, activity supervision, and teardown leads.", "days_before_event": 30, "priority": "high"},
                {"title": "Order Portable Sanitation & Waste Bins", "description": "Confirm delivery and servicing schedule with local vendor.", "days_before_event": 20, "priority": "high"},
                {"title": "Distribute Neighborhood Flyers & Social Posts", "description": "Encourage attendance and potluck signups.", "days_before_event": 14, "priority": "medium"},
                {"title": "Safety & Clean-up Committee Walkthrough", "description": "Inspect perimeter, trash stations, and shade tents.", "days_before_event": 1, "priority": "high"}
            ],
            "vendor_categories": [
                {"category": "Equipment Rental & Sanitation", "suggested_role_description": "Tents, folding chairs, and portable washrooms", "estimated_budget_share": Decimal("30.0")},
                {"category": "Food & Beverage Suppliers", "suggested_role_description": "Bulk community refreshments and grills", "estimated_budget_share": Decimal("30.0")},
                {"category": "Family Entertainment", "suggested_role_description": "Face painters, lawn games, or local musicians", "estimated_budget_share": Decimal("20.0")}
            ],
            "event_day_schedule": [
                {"time_offset_or_hour": "08:30 AM", "activity": "Volunteer Assembly & Site Setup", "description": "Erecting shade canopies, placing picnic tables and trash bins."},
                {"time_offset_or_hour": "10:30 AM", "activity": "Welcome & Activity Zones Open", "description": "Craft tables, lawn games, and background acoustic music open."},
                {"time_offset_or_hour": "12:30 PM", "activity": "Community Lunch & Picnic", "description": "BBQ service, shared potluck items, and community announcement."},
                {"time_offset_or_hour": "02:30 PM", "activity": "Family Contests & Group Photo", "description": "Sack races, trivia, and community mural completion."},
                {"time_offset_or_hour": "04:30 PM", "activity": "Volunteer Pack-down & Leave No Trace Cleanup", "description": "Site restoration, trash collection, and equipment load-out."}
            ],
            "risks_and_mitigations": [
                "Trash overflow: Double waste disposal bins and schedule mid-day sweep.",
                "Heat exhaustion: Set up dedicated shade canopies and free hydration stations."
            ]
        }
    }

    @classmethod
    def generate_plan(cls, event_type: str, guest_count: int, total_budget: Decimal, location: str, preferences: str = None) -> GeneratedPlanSchema:
        key = event_type.strip().lower()
        template = cls.TEMPLATES.get(key, cls.TEMPLATES["community"])

        # Deep copy structure into schema
        budget_items = [
            GeneratedBudgetItem(
                category=b["category"],
                allocated_percentage=b["allocated_percentage"],
                is_contingency=b.get("is_contingency", False),
                suggested_expenses=list(b.get("suggested_expenses", []))
            )
            for b in template["budget_allocations"]
        ]

        task_items = [
            GeneratedTaskItem(
                title=t["title"],
                description=t.get("description"),
                days_before_event=t["days_before_event"],
                priority=t.get("priority", "medium")
            )
            for t in template["tasks"]
        ]

        vendor_items = [
            GeneratedVendorItem(
                category=v["category"],
                suggested_role_description=v["suggested_role_description"],
                estimated_budget_share=v.get("estimated_budget_share")
            )
            for v in template["vendor_categories"]
        ]

        schedule_items = [
            GeneratedScheduleItem(
                time_offset_or_hour=s["time_offset_or_hour"],
                activity=s["activity"],
                description=s.get("description")
            )
            for s in template["event_day_schedule"]
        ]

        theme = template["theme"]
        if preferences and len(preferences.strip()) > 0:
            theme = f"{theme} (Adapted for {preferences[:40]}...)"

        return GeneratedPlanSchema(
            theme=theme,
            concept_summary=f"{template['concept_summary']} Crafted for {guest_count} guests in {location}.",
            personalized_ideas=list(template["personalized_ideas"]),
            budget_allocations=budget_items,
            tasks=task_items,
            vendor_categories=vendor_items,
            event_day_schedule=schedule_items,
            risks_and_mitigations=list(template["risks_and_mitigations"])
        )

