import csv
import html
import io
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import BudgetCategory, ChatMessage, Event, Expense, Task, User, Vendor
from app.schemas.ai_plan import GeneratedPlanSchema, PlanRevisionRequest, PlanRevisionResponse
from app.schemas.budget import BudgetCategoryCreate, BudgetCategoryUpdate, ExpenseCreate, ExpenseUpdate
from app.schemas.event import EventCreate, EventDetailResponse, EventUpdate, TaskResponse
from app.schemas.task import TaskCreate, TaskUpdate
from app.schemas.vendor import VendorCreate, VendorUpdate
from app.services.ai_planner import ai_planner
from app.services.financial_engine import FinancialEngine

router = APIRouter(prefix="/events", tags=["Events"])

async def get_user_event(event_id: str, current_user: User, db: AsyncSession) -> Event:
    stmt = (
        select(Event)
        .where(Event.id == event_id)
        .options(
            selectinload(Event.budget_categories).selectinload(BudgetCategory.expenses),
            selectinload(Event.tasks),
            selectinload(Event.vendors),
            selectinload(Event.chat_messages)
        )
    )
    result = await db.execute(stmt)
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if event.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this event")
    return event

def build_event_detail(event: Event) -> EventDetailResponse:
    now = datetime.now(timezone.utc)
    tasks_resp = []
    for t in event.tasks:
        due = t.due_date
        if due.tzinfo is None:
            due = due.replace(tzinfo=timezone.utc)
        is_overdue = t.status != "completed" and due < now
        t_data = TaskResponse.model_validate(t)
        t_data.is_overdue = is_overdue
        tasks_resp.append(t_data)

    budget_summary = FinancialEngine.calculate_budget_summary(event.total_budget, event.budget_categories)

    resp = EventDetailResponse.model_validate(event)
    resp.tasks = tasks_resp
    resp.budget_summary = budget_summary
    return resp

# ----------------- EVENT CRUD ----------------- #

@router.post("", response_model=EventDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_in: EventCreate,
    generate_plan: bool = Query(True, description="Automatically generate initial plan via GenAI/Fallback"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Reject dates in past for planning
    now = datetime.now(timezone.utc)
    event_date = event_in.event_date
    if event_date.tzinfo is None:
        event_date = event_date.replace(tzinfo=timezone.utc)
    if event_date < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event date cannot be in the past."
        )

    event = Event(
        user_id=current_user.id,
        title=event_in.title,
        event_type=event_in.event_type,
        event_date=event_in.event_date,
        timezone=event_in.timezone,
        location=event_in.location,
        guest_count=event_in.guest_count,
        total_budget=event_in.total_budget,
        currency=event_in.currency,
        preferences=event_in.preferences
    )
    db.add(event)
    await db.flush()

    if generate_plan:
        plan = await ai_planner.generate_initial_plan(
            event_type=event.event_type,
            guest_count=event.guest_count,
            total_budget=event.total_budget,
            currency=event.currency,
            location=event.location,
            preferences=event.preferences
        )

        event.theme = plan.theme
        event.concept_summary = plan.concept_summary

        # Deterministic Budget Allocation
        percentages = [b.allocated_percentage for b in plan.budget_allocations]
        reconciled_amounts = FinancialEngine.reconcile_allocations(event.total_budget, percentages)

        for b_item, amount in zip(plan.budget_allocations, reconciled_amounts):
            category = BudgetCategory(
                event_id=event.id,
                name=b_item.category,
                allocated_amount=amount,
                is_contingency=b_item.is_contingency
            )
            db.add(category)
            await db.flush()

            # Seed suggested expenses
            for exp_title in b_item.suggested_expenses:
                est_share = (amount / Decimal(max(1, len(b_item.suggested_expenses)))).quantize(Decimal("0.01"))
                exp = Expense(
                    category_id=category.id,
                    title=exp_title,
                    estimated_amount=est_share
                )
                db.add(exp)

        # Generate Tasks
        for t_item in plan.tasks:
            # Handle edge case where event is very soon
            due = event_date - timedelta(days=t_item.days_before_event)
            if due < now:
                due = now + timedelta(days=1)

            task = Task(
                event_id=event.id,
                title=t_item.title,
                description=t_item.description,
                due_date=due,
                priority=t_item.priority,
                status="pending"
            )
            db.add(task)

        # Generate Vendors
        for v_item in plan.vendor_categories:
            vendor = Vendor(
                event_id=event.id,
                category=v_item.category,
                name=f"Recommended {v_item.category} Partner",
                notes=v_item.suggested_role_description,
                is_ai_suggested=True,
                status="considering"
            )
            db.add(vendor)

    await db.commit()
    return await get_event(event.id, current_user, db)

@router.get("", response_model=List[EventDetailResponse])
async def list_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Event)
        .where(Event.user_id == current_user.id)
        .order_by(Event.event_date.asc())
        .offset(skip)
        .limit(limit)
        .options(
            selectinload(Event.budget_categories).selectinload(BudgetCategory.expenses),
            selectinload(Event.tasks),
            selectinload(Event.vendors),
            selectinload(Event.chat_messages)
        )
    )
    result = await db.execute(stmt)
    events = result.scalars().all()
    return [build_event_detail(e) for e in events]

@router.get("/{event_id}", response_model=EventDetailResponse)
async def get_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    event = await get_user_event(event_id, current_user, db)
    return build_event_detail(event)

@router.put("/{event_id}", response_model=EventDetailResponse)
async def update_event(
    event_id: str,
    event_in: EventUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    event = await get_user_event(event_id, current_user, db)
    for field, val in event_in.model_dump(exclude_unset=True).items():
        setattr(event, field, val)

    await db.commit()
    return await get_event(event_id, current_user, db)

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    event = await get_user_event(event_id, current_user, db)
    await db.delete(event)
    await db.commit()
    return None

# ----------------- BUDGET & EXPENSES ----------------- #

@router.post("/{event_id}/categories")
async def add_budget_category(
    event_id: str,
    category_in: BudgetCategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    event = await get_user_event(event_id, current_user, db)
    category = BudgetCategory(
        event_id=event.id,
        name=category_in.name,
        allocated_amount=category_in.allocated_amount,
        is_contingency=category_in.is_contingency
    )
    db.add(category)
    await db.commit()
    return await get_event(event_id, current_user, db)

@router.put("/{event_id}/categories/{category_id}")
async def update_budget_category(
    event_id: str,
    category_id: str,
    cat_in: BudgetCategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    event = await get_user_event(event_id, current_user, db)
    category = next((c for c in event.budget_categories if c.id == category_id), None)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    for field, val in cat_in.model_dump(exclude_unset=True).items():
        setattr(category, field, val)

    await db.commit()
    return await get_event(event_id, current_user, db)

@router.delete("/{event_id}/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget_category(
    event_id: str,
    category_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    event = await get_user_event(event_id, current_user, db)
    category = next((c for c in event.budget_categories if c.id == category_id), None)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.delete(category)
    await db.commit()
    return None

@router.post("/{event_id}/categories/{category_id}/expenses")
async def add_expense(
    event_id: str,
    category_id: str,
    exp_in: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    event = await get_user_event(event_id, current_user, db)
    category = next((c for c in event.budget_categories if c.id == category_id), None)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    expense = Expense(
        category_id=category.id,
        title=exp_in.title,
        estimated_amount=exp_in.estimated_amount,
        actual_amount=exp_in.actual_amount,
        is_paid=exp_in.is_paid,
        paid_date=exp_in.paid_date,
        notes=exp_in.notes
    )
    db.add(expense)
    category.expenses.append(expense)
    await db.commit()
    return await get_event(event_id, current_user, db)

@router.put("/{event_id}/expenses/{expense_id}")
async def update_expense(
    event_id: str,
    expense_id: str,
    exp_in: ExpenseUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    event = await get_user_event(event_id, current_user, db)
    target_exp = None
    for cat in event.budget_categories:
        for exp in cat.expenses:
            if exp.id == expense_id:
                target_exp = exp
                break

    if not target_exp:
        raise HTTPException(status_code=404, detail="Expense not found")

    for field, val in exp_in.model_dump(exclude_unset=True).items():
        setattr(target_exp, field, val)

    await db.commit()
    return await get_event(event_id, current_user, db)

@router.delete("/{event_id}/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    event_id: str,
    expense_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    event = await get_user_event(event_id, current_user, db)
    target_exp = None
    for cat in event.budget_categories:
        for exp in cat.expenses:
            if exp.id == expense_id:
                target_exp = exp
                break

    if not target_exp:
        raise HTTPException(status_code=404, detail="Expense not found")

    await db.delete(target_exp)
    await db.commit()
    return None

# ----------------- TASKS ----------------- #

@router.post("/{event_id}/tasks")
async def add_task(
    event_id: str,
    task_in: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    event = await get_user_event(event_id, current_user, db)
    task = Task(
        event_id=event.id,
        title=task_in.title,
        description=task_in.description,
        due_date=task_in.due_date,
        priority=task_in.priority,
        status=task_in.status,
        dependency_id=task_in.dependency_id
    )
    db.add(task)
    await db.commit()
    return await get_event(event_id, current_user, db)

@router.put("/{event_id}/tasks/{task_id}")
async def update_task(
    event_id: str,
    task_id: str,
    task_in: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    event = await get_user_event(event_id, current_user, db)
    task = next((t for t in event.tasks if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    data = task_in.model_dump(exclude_unset=True)
    if "status" in data:
        if data["status"] == "completed" and task.status != "completed":
            task.completed_at = datetime.now(timezone.utc)
        elif data["status"] != "completed":
            task.completed_at = None

    for field, val in data.items():
        setattr(task, field, val)

    await db.commit()
    return await get_event(event_id, current_user, db)

@router.delete("/{event_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    event_id: str,
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    event = await get_user_event(event_id, current_user, db)
    task = next((t for t in event.tasks if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.delete(task)
    await db.commit()
    return None

# ----------------- VENDORS ----------------- #

@router.post("/{event_id}/vendors")
async def add_vendor(
    event_id: str,
    vendor_in: VendorCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    event = await get_user_event(event_id, current_user, db)
    vendor = Vendor(
        event_id=event.id,
        category=vendor_in.category,
        name=vendor_in.name,
        contact_name=vendor_in.contact_name,
        phone=vendor_in.phone,
        email=vendor_in.email,
        quoted_amount=vendor_in.quoted_amount,
        status=vendor_in.status,
        is_ai_suggested=vendor_in.is_ai_suggested,
        notes=vendor_in.notes
    )
    db.add(vendor)
    await db.commit()
    return await get_event(event_id, current_user, db)

@router.put("/{event_id}/vendors/{vendor_id}")
async def update_vendor(
    event_id: str,
    vendor_id: str,
    vendor_in: VendorUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    event = await get_user_event(event_id, current_user, db)
    vendor = next((v for v in event.vendors if v.id == vendor_id), None)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    for field, val in vendor_in.model_dump(exclude_unset=True).items():
        setattr(vendor, field, val)

    await db.commit()
    return await get_event(event_id, current_user, db)

@router.delete("/{event_id}/vendors/{vendor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vendor(
    event_id: str,
    vendor_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    event = await get_user_event(event_id, current_user, db)
    vendor = next((v for v in event.vendors if v.id == vendor_id), None)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    await db.delete(vendor)
    await db.commit()
    return None

# ----------------- AI CHAT & PLAN REVISION ----------------- #

@router.post("/{event_id}/chat", response_model=PlanRevisionResponse)
async def chat_and_revise_plan(
    event_id: str,
    req: PlanRevisionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    event = await get_user_event(event_id, current_user, db)

    # Convert existing event state to a plan baseline
    current_plan = await ai_planner.generate_initial_plan(
        event_type=event.event_type,
        guest_count=event.guest_count,
        total_budget=event.total_budget,
        currency=event.currency,
        location=event.location,
        preferences=event.preferences
    )
    if event.theme:
        current_plan.theme = event.theme

    explanation, proposed = await ai_planner.revise_plan(
        current_plan=current_plan,
        user_request=req.prompt,
        total_budget=event.total_budget,
        currency=event.currency
    )

    # Save user message and AI response
    user_msg = ChatMessage(event_id=event.id, role="user", content=req.prompt)
    ai_msg = ChatMessage(
        event_id=event.id,
        role="assistant",
        content=explanation,
        proposed_plan_json=proposed.model_dump_json() if proposed else None
    )
    db.add(user_msg)
    db.add(ai_msg)
    await db.commit()
    await db.refresh(ai_msg)

    return PlanRevisionResponse(
        message_id=ai_msg.id,
        explanation=explanation,
        proposed_changes=proposed
    )

@router.post("/{event_id}/apply-revision/{message_id}", response_model=EventDetailResponse)
async def apply_revision(
    event_id: str,
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Applies proposed revision upon user confirmation, ensuring non-destructive review flow.
    """
    event = await get_user_event(event_id, current_user, db)
    result = await db.execute(select(ChatMessage).where(ChatMessage.id == message_id, ChatMessage.event_id == event.id))
    msg = result.scalar_one_or_none()
    if not msg or not msg.proposed_plan_json or msg.applied:
        raise HTTPException(status_code=400, detail="Invalid or already applied revision message")

    plan = GeneratedPlanSchema.model_validate_json(msg.proposed_plan_json)
    if plan.theme:
        event.theme = plan.theme
    if plan.concept_summary:
        event.concept_summary = plan.concept_summary

    # Update category allocations reconcilably
    if plan.budget_allocations:
        percentages = [b.allocated_percentage for b in plan.budget_allocations]
        reconciled = FinancialEngine.reconcile_allocations(event.total_budget, percentages)

        # Match existing or add
        for b_item, amt in zip(plan.budget_allocations, reconciled):
            match = next((c for c in event.budget_categories if c.name.lower() == b_item.category.lower()), None)
            if match:
                match.allocated_amount = amt
            else:
                new_cat = BudgetCategory(event_id=event.id, name=b_item.category, allocated_amount=amt, is_contingency=b_item.is_contingency)
                db.add(new_cat)

    msg.applied = True
    await db.commit()
    return await get_event(event.id, current_user, db)

# ----------------- EXPORTING ----------------- #

def sanitize_csv_cell(val: any) -> str:
    """
    Prevents CSV Formula Injection attacks (=, +, -, @, \t, \r).
    If a string starts with formula triggers, prepend a single quote so spreadsheets treat it strictly as text.
    """
    if val is None:
        return ""
    s = str(val)
    if s and s[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + s
    return s

@router.get("/{event_id}/export/csv")
async def export_event_csv(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    event = await get_user_event(event_id, current_user, db)

    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    writer.writerow(["Title", sanitize_csv_cell(event.title)])
    writer.writerow(["Type", sanitize_csv_cell(event.event_type.capitalize())])
    writer.writerow(["Date", event.event_date.strftime('%Y-%m-%d')])
    writer.writerow(["Location", sanitize_csv_cell(event.location)])
    writer.writerow(["Guests", str(event.guest_count)])
    writer.writerow(["Total Budget", f"{event.currency} {event.total_budget}"])
    writer.writerow([])
    writer.writerow(["--- BUDGET BREAKDOWN ---"])
    writer.writerow(["Category", "Allocated", "Expense Title", "Estimated", "Actual", "Paid"])

    for cat in event.budget_categories:
        if not cat.expenses:
            writer.writerow([sanitize_csv_cell(cat.name), str(cat.allocated_amount), "N/A", "0.00", "0.00", "N/A"])
        for exp in cat.expenses:
            actual = str(exp.actual_amount) if exp.actual_amount is not None else "0.00"
            writer.writerow([
                sanitize_csv_cell(cat.name),
                str(cat.allocated_amount),
                sanitize_csv_cell(exp.title),
                str(exp.estimated_amount),
                actual,
                "Yes" if exp.is_paid else "No"
            ])

    writer.writerow([])
    writer.writerow(["--- TASKS ---"])
    writer.writerow(["Title", "Priority", "Status", "Due Date"])
    for t in event.tasks:
        writer.writerow([
            sanitize_csv_cell(t.title),
            t.priority,
            t.status,
            t.due_date.strftime("%Y-%m-%d")
        ])

    writer.writerow([])
    writer.writerow(["--- VENDORS ---"])
    writer.writerow(["Category", "Name", "Status", "Quoted Amount", "Phone"])
    for v in event.vendors:
        writer.writerow([
            sanitize_csv_cell(v.category),
            sanitize_csv_cell(v.name),
            v.status,
            str(v.quoted_amount or "0.00"),
            sanitize_csv_cell(v.phone or "")
        ])

    content = output.getvalue()
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="eventwise_{event.id[:8]}.csv"'}
    )

@router.get("/{event_id}/export/html", response_class=HTMLResponse)
async def export_event_html(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    event = await get_user_event(event_id, current_user, db)
    summary = FinancialEngine.calculate_budget_summary(event.total_budget, event.budget_categories)

    def esc(text: any) -> str:
        return html.escape(str(text or ""))

    categories_html = "".join([
        f"""<tr>
            <td style="padding: 8px; border: 1px solid #e2e8f0;">{esc(c.name)}</td>
            <td style="padding: 8px; border: 1px solid #e2e8f0;">{esc(event.currency)} {c.allocated_amount}</td>
            <td style="padding: 8px; border: 1px solid #e2e8f0;">{'Contingency' if c.is_contingency else 'Standard'}</td>
        </tr>""" for c in event.budget_categories
    ])

    tasks_html = "".join([
        f"""<tr>
            <td style="padding: 8px; border: 1px solid #e2e8f0;">{esc(t.title)}</td>
            <td style="padding: 8px; border: 1px solid #e2e8f0;">{esc(t.priority.upper())}</td>
            <td style="padding: 8px; border: 1px solid #e2e8f0;">{esc(t.status.replace('_', ' ').capitalize())}</td>
            <td style="padding: 8px; border: 1px solid #e2e8f0;">{t.due_date.strftime('%b %d, %Y')}</td>
        </tr>""" for t in event.tasks
    ])

    vendors_html = "".join([
        f"""<tr>
            <td style="padding: 8px; border: 1px solid #e2e8f0;">{esc(v.category)}</td>
            <td style="padding: 8px; border: 1px solid #e2e8f0;">{esc(v.name)}</td>
            <td style="padding: 8px; border: 1px solid #e2e8f0;">{esc(v.status.capitalize())}</td>
            <td style="padding: 8px; border: 1px solid #e2e8f0;">{esc(event.currency)} {v.quoted_amount or '0.00'}</td>
        </tr>""" for v in event.vendors
    ])

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Event Summary - {esc(event.title)}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #1e293b; padding: 40px; }}
        h1 {{ color: #0f172a; border-bottom: 2px solid #3b82f6; padding-bottom: 8px; }}
        h2 {{ color: #1e293b; margin-top: 24px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
        th {{ background: #f1f5f9; padding: 10px; border: 1px solid #cbd5e1; text-align: left; }}
        .badge {{ display: inline-block; padding: 4px 10px; border-radius: 9999px; background: #e0f2fe; color: #0369a1; font-weight: 600; font-size: 12px; }}
        .metric-card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 20px; }}
        @media print {{ body {{ padding: 0; }} }}
    </style>
</head>
<body>
    <h1>{esc(event.title)}</h1>
    <span class="badge">{esc(event.event_type.upper())}</span>
    <p><strong>Date:</strong> {event.event_date.strftime('%B %d, %Y')} | <strong>Location:</strong> {esc(event.location)} | <strong>Guests:</strong> {event.guest_count}</p>
    <p><strong>Theme:</strong> {esc(event.theme or 'Custom Theme')}</p>
    <p><em>{esc(event.concept_summary or '')}</em></p>

    <div class="metric-card">
        <h3>Financial Reconciliation</h3>
        <p><strong>Total Budget:</strong> {esc(event.currency)} {summary.total_budget} | <strong>Allocated:</strong> {esc(event.currency)} {summary.total_allocated} | <strong>Remaining:</strong> {esc(event.currency)} {summary.remaining_budget}</p>
    </div>

    <h2>Budget Allocations</h2>
    <table>
        <thead>
            <tr><th>Category</th><th>Allocated</th><th>Type</th></tr>
        </thead>
        <tbody>{categories_html}</tbody>
    </table>

    <h2>Timeline & Tasks</h2>
    <table>
        <thead>
            <tr><th>Task</th><th>Priority</th><th>Status</th><th>Due Date</th></tr>
        </thead>
        <tbody>{tasks_html}</tbody>
    </table>

    <h2>Vendors & Booking Status</h2>
    <table>
        <thead>
            <tr><th>Category</th><th>Vendor Name</th><th>Status</th><th>Quoted</th></tr>
        </thead>
        <tbody>{vendors_html}</tbody>
    </table>
</body>
</html>"""
    return HTMLResponse(content=html_content)
