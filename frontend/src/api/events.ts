import type { EventDetail, PlanRevisionResponse } from '../types/event';

const API_BASE = '/api/v1';

export async function fetchEvents(): Promise<EventDetail[]> {
  const res = await fetch(`${API_BASE}/events`);
  if (!res.ok) throw new Error('Failed to load events');
  return res.json();
}

export async function fetchEvent(id: string): Promise<EventDetail> {
  const res = await fetch(`${API_BASE}/events/${id}`);
  if (!res.ok) throw new Error('Failed to load event details');
  return res.json();
}

export async function createEvent(data: {
  title: string;
  event_type: string;
  event_date: string;
  location: string;
  guest_count: number;
  total_budget: number;
  currency: string;
  preferences?: string;
}): Promise<EventDetail> {
  const res = await fetch(`${API_BASE}/events?generate_plan=true`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to create event');
  }
  return res.json();
}

export async function updateTask(eventId: string, taskId: string, updates: Partial<{ status: string; priority: string; title: string }>): Promise<EventDetail> {
  const res = await fetch(`${API_BASE}/events/${eventId}/tasks/${taskId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates),
  });
  if (!res.ok) throw new Error('Failed to update task');
  return res.json();
}

export async function addExpense(eventId: string, categoryId: string, data: { title: string; estimated_amount: number; actual_amount?: number; is_paid?: boolean }): Promise<EventDetail> {
  const res = await fetch(`${API_BASE}/events/${eventId}/categories/${categoryId}/expenses`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to add expense');
  return res.json();
}

export async function updateVendor(eventId: string, vendorId: string, updates: Partial<{ status: string; quoted_amount: number; name: string }>): Promise<EventDetail> {
  const res = await fetch(`${API_BASE}/events/${eventId}/vendors/${vendorId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates),
  });
  if (!res.ok) throw new Error('Failed to update vendor');
  return res.json();
}

export async function addVendor(eventId: string, data: { category: string; name: string; quoted_amount?: number; status: string; phone?: string; notes?: string }): Promise<EventDetail> {
  const res = await fetch(`${API_BASE}/events/${eventId}/vendors`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to add vendor');
  return res.json();
}

export async function sendChatMessage(eventId: string, prompt: string): Promise<PlanRevisionResponse> {
  const res = await fetch(`${API_BASE}/events/${eventId}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  });
  if (!res.ok) throw new Error('Failed to communicate with AI planner');
  return res.json();
}

export async function applyPlanRevision(eventId: string, messageId: string): Promise<EventDetail> {
  const res = await fetch(`${API_BASE}/events/${eventId}/apply-revision/${messageId}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to apply plan revision');
  return res.json();
}
