export type EventType = 'wedding' | 'birthday' | 'college' | 'community';

export interface BudgetSummary {
  total_budget: string;
  total_allocated: string;
  unallocated_amount: string;
  total_estimated: string;
  total_actual: string;
  remaining_budget: string;
  overspent_amount: string;
  is_overspent: boolean;
  contingency_allocated: string;
}

export interface Expense {
  id: string;
  category_id: string;
  title: string;
  estimated_amount: string;
  actual_amount: string | null;
  is_paid: boolean;
  paid_date: string | null;
  notes?: string | null;
}

export interface BudgetCategory {
  id: string;
  event_id: string;
  name: string;
  allocated_amount: string;
  is_contingency: boolean;
  expenses: Expense[];
}

export type TaskPriority = 'low' | 'medium' | 'high' | 'critical';
export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'blocked';

export interface Task {
  id: string;
  event_id: string;
  title: string;
  description?: string | null;
  due_date: string;
  priority: TaskPriority;
  status: TaskStatus;
  dependency_id?: string | null;
  completed_at?: string | null;
  is_overdue: boolean;
}

export type VendorStatus = 'considering' | 'contacted' | 'quoted' | 'booked' | 'rejected';

export interface Vendor {
  id: string;
  event_id: string;
  category: string;
  name: string;
  contact_name?: string | null;
  phone?: string | null;
  email?: string | null;
  quoted_amount?: string | null;
  status: VendorStatus;
  is_ai_suggested: boolean;
  notes?: string | null;
}

export interface EventDetail {
  id: string;
  user_id: string;
  title: string;
  event_type: EventType;
  event_date: string;
  timezone: string;
  location: string;
  guest_count: number;
  total_budget: string;
  currency: string;
  preferences?: string | null;
  theme?: string | null;
  concept_summary?: string | null;
  created_at: string;
  updated_at: string;
  budget_categories: BudgetCategory[];
  tasks: Task[];
  vendors: Vendor[];
  budget_summary: BudgetSummary;
}

export interface PlanRevisionResponse {
  message_id: string;
  explanation: string;
  proposed_changes?: any;
}

