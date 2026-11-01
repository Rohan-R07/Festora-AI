import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Calendar, Users, DollarSign, MapPin, Clock,
  AlertTriangle, Bot, Send, Plus, Download, Sparkles, FileText, Check, ShieldAlert
} from 'lucide-react';
import {
  fetchEvent,
  updateTask,
  addExpense,
  updateVendor,
  addVendor,
  sendChatMessage,
  applyPlanRevision
} from '../api/events';
import type { EventDetail, PlanRevisionResponse } from '../types/event';

export const EventDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [event, setEvent] = useState<EventDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Tabs: 'overview', 'budget', 'timeline', 'vendors', 'chat'
  const [activeTab, setActiveTab] = useState<'overview' | 'budget' | 'timeline' | 'vendors' | 'chat'>('overview');

  // Chat Assistant State
  const [chatPrompt, setChatPrompt] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [, setPendingRevision] = useState<PlanRevisionResponse | null>(null);
  const [chatHistory, setChatHistory] = useState<Array<{ role: 'user' | 'assistant'; text: string; messageId?: string; proposed?: any }>>([
    {
      role: 'assistant',
      text: "Hello! I am your EventWise AI Copilot. Ask me to adjust your budget allocations, brainstorm alternative themes, tweak your timeline, or optimize vendor categories!"
    }
  ]);

  // Modal / Quick Entry forms
  const [newExpCatId, setNewExpCatId] = useState<string>('');
  const [expTitle, setExpTitle] = useState('');
  const [expAmount, setExpAmount] = useState('');
  const [expActual, setExpActual] = useState('');

  // Quick Vendor
  const [vendCategory, setVendCategory] = useState('');
  const [vendName, setVendName] = useState('');
  const [vendQuoted, setVendQuoted] = useState('');

  useEffect(() => {
    if (!id) return;
    fetchEvent(id)
      .then((data) => setEvent(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-600 border-t-transparent" />
        <p className="mt-3 text-sm text-slate-500">Loading celebration workspace...</p>
      </div>
    );
  }

  if (error || !event) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <ShieldAlert className="w-12 h-12 text-red-500 mx-auto mb-3" />
        <h2 className="text-xl font-bold text-slate-800">Event Not Found or Inaccessible</h2>
        <p className="text-sm text-slate-500 mt-1">{error || 'This event may have been removed or belongs to another user.'}</p>
        <Link to="/" className="mt-4 inline-block px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-semibold">
          Return to Dashboard
        </Link>
      </div>
    );
  }

  const handleTaskToggle = async (taskId: string, currentStatus: string) => {
    const nextStatus = currentStatus === 'completed' ? 'pending' : 'completed';
    try {
      const updated = await updateTask(event.id, taskId, { status: nextStatus });
      setEvent(updated);
    } catch (err: any) {
      alert(err.message || 'Error updating task');
    }
  };

  const handleAddExpense = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newExpCatId || !expTitle || !expAmount) return;
    try {
      const updated = await addExpense(event.id, newExpCatId, {
        title: expTitle,
        estimated_amount: parseFloat(expAmount),
        actual_amount: expActual ? parseFloat(expActual) : undefined,
      });
      setEvent(updated);
      setExpTitle('');
      setExpAmount('');
      setExpActual('');
    } catch (err: any) {
      alert(err.message || 'Error adding expense');
    }
  };

  const handleAddVendor = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!vendCategory || !vendName) return;
    try {
      const updated = await addVendor(event.id, {
        category: vendCategory,
        name: vendName,
        quoted_amount: vendQuoted ? parseFloat(vendQuoted) : undefined,
        status: 'considering',
      });
      setEvent(updated);
      setVendCategory('');
      setVendName('');
      setVendQuoted('');
    } catch (err: any) {
      alert(err.message || 'Error adding vendor');
    }
  };

  const handleVendorStatusChange = async (vendorId: string, newStatus: any) => {
    try {
      const updated = await updateVendor(event.id, vendorId, { status: newStatus });
      setEvent(updated);
    } catch (err: any) {
      alert(err.message || 'Error updating vendor status');
    }
  };

  const handleSendChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatPrompt.trim() || chatLoading) return;

    const userText = chatPrompt.trim();
    setChatPrompt('');
    setChatHistory((prev) => [...prev, { role: 'user', text: userText }]);
    setChatLoading(true);

    try {
      const res = await sendChatMessage(event.id, userText);
      setChatHistory((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: res.explanation,
          messageId: res.message_id,
          proposed: res.proposed_changes,
        },
      ]);
      if (res.proposed_changes) {
        setPendingRevision(res);
      }
    } catch {
      setChatHistory((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: 'Sorry, I encountered a temporary issue revising the plan. Your event data remains completely safe.',
        },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleApplyRevision = async (messageId: string) => {
    try {
      const updated = await applyPlanRevision(event.id, messageId);
      setEvent(updated);
      setPendingRevision(null);
      setChatHistory((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: '✅ Proposed plan revisions successfully applied and reconciled into your event budget and allocations!',
        },
      ]);
    } catch (err: any) {
      alert(err.message || 'Error applying revision');
    }
  };

  const formattedDate = new Date(event.event_date).toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  });

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Event Header Card */}
      <section className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm mb-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider bg-indigo-50 text-indigo-700 border border-indigo-200">
                {event.event_type}
              </span>
              <span className="text-xs text-slate-500 flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5 text-slate-400" />
                {formattedDate}
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              {event.title}
            </h1>
            {event.theme && (
              <p className="text-sm font-medium text-indigo-600 mt-1 flex items-center gap-1.5">
                <Sparkles className="w-4 h-4" /> Theme: {event.theme}
              </p>
            )}
            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-600 mt-3">
              <span className="flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-slate-400" /> {event.location}
              </span>
              <span className="flex items-center gap-1">
                <Users className="w-3.5 h-3.5 text-slate-400" /> {event.guest_count} Expected Guests
              </span>
              <span className="flex items-center gap-1 font-semibold text-slate-900">
                <DollarSign className="w-3.5 h-3.5 text-slate-400" /> {event.currency} {Number(event.total_budget).toLocaleString()} Total Budget
              </span>
            </div>
          </div>

          {/* Quick Action Export Buttons */}
          <div className="flex items-center gap-2">
            <a
              href={`/api/v1/events/${event.id}/export/csv`}
              download
              className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 transition"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export CSV</span>
            </a>
            <a
              href={`/api/v1/events/${event.id}/export/html`}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 transition"
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Printable Dossier</span>
            </a>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="mt-6 border-t border-slate-100 pt-4 flex gap-2 overflow-x-auto">
          {[
            { id: 'overview', label: 'Plan & Concept' },
            { id: 'budget', label: 'Budget & Expenses' },
            { id: 'timeline', label: 'Milestones & Tasks' },
            { id: 'vendors', label: 'Vendor Directory' },
            { id: 'chat', label: 'AI Planning Copilot' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-4 py-2 rounded-lg text-xs sm:text-sm font-semibold whitespace-nowrap transition ${
                activeTab === tab.id
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </section>

      {/* TAB 1: OVERVIEW & CONCEPT */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
              <h2 className="text-lg font-bold text-slate-900 mb-2 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-indigo-600" />
                Celebration Concept & Personalized Blueprint
              </h2>
              <p className="text-sm text-slate-600 leading-relaxed">
                {event.concept_summary || 'Custom event plan initialized with AI-assisted allocation recommendations.'}
              </p>
              {event.preferences && (
                <div className="mt-4 p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs text-slate-600">
                  <span className="font-semibold text-slate-800">Your Constraints & Preferences:</span> {event.preferences}
                </div>
              )}
            </div>

            {/* Quick Metrics */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-xs font-semibold text-slate-500 uppercase">Allocated Budget</span>
                <p className="text-xl font-bold text-slate-900 mt-1">
                  {event.currency} {Number(event.budget_summary?.total_allocated || 0).toLocaleString()}
                </p>
                <span className="text-xs text-emerald-600 font-medium">Reconciled to categories</span>
              </div>
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-xs font-semibold text-slate-500 uppercase">Remaining Funds</span>
                <p className={`text-xl font-bold mt-1 ${event.budget_summary?.is_overspent ? 'text-red-600' : 'text-slate-900'}`}>
                  {event.currency} {Number(event.budget_summary?.remaining_budget || 0).toLocaleString()}
                </p>
                <span className="text-xs text-slate-500">
                  {event.budget_summary?.is_overspent ? '⚠️ Plan exceeds target budget' : 'Comfortable liquidity'}
                </span>
              </div>
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-xs font-semibold text-slate-500 uppercase">Contingency Fund</span>
                <p className="text-xl font-bold text-indigo-600 mt-1">
                  {event.currency} {Number(event.budget_summary?.contingency_allocated || 0).toLocaleString()}
                </p>
                <span className="text-xs text-slate-500">Reserved safety buffer</span>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="bg-gradient-to-br from-indigo-50 to-white rounded-xl border border-indigo-200 p-5 shadow-sm">
              <div className="flex items-center gap-2 text-indigo-900 font-bold text-sm mb-2">
                <Bot className="w-4 h-4 text-indigo-600" />
                <span>AI Recommendation Engine</span>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed mb-4">
                Want to trim expenses or explore alternative entertainment options? Click over to the <strong>AI Planning Copilot</strong> to test scenarios.
              </p>
              <button
                onClick={() => setActiveTab('chat')}
                className="w-full py-2 bg-indigo-600 text-white rounded-lg text-xs font-semibold hover:bg-indigo-700 transition"
              >
                Launch AI Assistant
              </button>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: BUDGET & EXPENSES */}
      {activeTab === 'budget' && (
        <div className="space-y-6">
          {/* Summary Alert */}
          {event.budget_summary?.is_overspent && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-xl flex items-center gap-3 text-red-700">
              <AlertTriangle className="w-5 h-5 flex-shrink-0" />
              <div className="text-xs sm:text-sm">
                <strong className="font-semibold">Budget Warning:</strong> Actual & estimated commitments exceed total budget by {event.currency} {event.budget_summary.overspent_amount}. Consider rebalancing allocations.
              </div>
            </div>
          )}

          {/* Categories Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {event.budget_categories.map((cat) => {
              const catExpenses = cat.expenses || [];

              return (
                <div key={cat.id} className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
                  <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                    <div>
                      <h3 className="font-bold text-slate-900 text-sm">{cat.name}</h3>
                      <span className="text-xs text-slate-500">
                        {cat.is_contingency ? 'Safety Contingency' : 'Direct Service Category'}
                      </span>
                    </div>
                    <div className="text-right">
                      <span className="text-xs text-slate-400">Allocated</span>
                      <p className="font-bold text-slate-900 text-sm">
                        {event.currency} {Number(cat.allocated_amount).toLocaleString()}
                      </p>
                    </div>
                  </div>

                  {/* Expenses List */}
                  <div className="mt-3 space-y-2">
                    {catExpenses.length === 0 && (
                      <p className="text-xs text-slate-400 italic">No specific expenses recorded yet.</p>
                    )}
                    {catExpenses.map((exp) => (
                      <div key={exp.id} className="flex items-center justify-between text-xs bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                        <div>
                          <p className="font-medium text-slate-800">{exp.title}</p>
                          <span className="text-[10px] text-slate-400">
                            Est: {event.currency} {Number(exp.estimated_amount).toLocaleString()}
                          </span>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold text-slate-900">
                            {exp.actual_amount ? `${event.currency} ${Number(exp.actual_amount).toLocaleString()}` : 'Pending'}
                          </p>
                          <span className={`text-[10px] font-medium ${exp.is_paid ? 'text-emerald-600' : 'text-amber-600'}`}>
                            {exp.is_paid ? 'Paid' : 'Unpaid'}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>

                  <button
                    onClick={() => setNewExpCatId(cat.id)}
                    className="mt-3 inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-800"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Record Expense Item</span>
                  </button>
                </div>
              );
            })}
          </div>

          {/* Quick Expense Form Modal / Inline */}
          {newExpCatId && (
            <div className="bg-white rounded-xl border border-indigo-200 p-5 shadow-md">
              <h4 className="font-bold text-sm text-slate-900 mb-3">Add Expense to Selected Category</h4>
              <form onSubmit={handleAddExpense} className="grid grid-cols-1 sm:grid-cols-4 gap-3">
                <input
                  type="text"
                  required
                  placeholder="Expense description (e.g. Centerpiece flowers)"
                  value={expTitle}
                  onChange={(e) => setExpTitle(e.target.value)}
                  className="px-3 py-2 text-xs border rounded-lg border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <input
                  type="number"
                  required
                  step="0.01"
                  placeholder="Estimated Cost"
                  value={expAmount}
                  onChange={(e) => setExpAmount(e.target.value)}
                  className="px-3 py-2 text-xs border rounded-lg border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <input
                  type="number"
                  step="0.01"
                  placeholder="Actual Cost (if paid)"
                  value={expActual}
                  onChange={(e) => setExpActual(e.target.value)}
                  className="px-3 py-2 text-xs border rounded-lg border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <div className="flex gap-2">
                  <button
                    type="submit"
                    className="flex-1 bg-indigo-600 text-white rounded-lg text-xs font-semibold hover:bg-indigo-700 py-2"
                  >
                    Save
                  </button>
                  <button
                    type="button"
                    onClick={() => setNewExpCatId('')}
                    className="px-3 border border-slate-300 text-slate-600 rounded-lg text-xs hover:bg-slate-50"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: TIMELINE & TASKS */}
      {activeTab === 'timeline' && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Milestone Action Checklist</h2>
              <p className="text-xs text-slate-500">Prioritized timeline leading up to {formattedDate}.</p>
            </div>
          </div>

          <div className="space-y-3">
            {event.tasks.map((task) => {
              const taskDate = new Date(task.due_date).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
              });

              return (
                <div
                  key={task.id}
                  className={`flex items-start justify-between p-3.5 rounded-lg border transition ${
                    task.status === 'completed'
                      ? 'bg-slate-50 border-slate-200 opacity-75'
                      : task.is_overdue
                      ? 'bg-red-50 border-red-200'
                      : 'bg-white border-slate-200 hover:border-indigo-300'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <button
                      onClick={() => handleTaskToggle(task.id, task.status)}
                      className={`mt-0.5 w-5 h-5 rounded border flex items-center justify-center transition focus:outline-none ${
                        task.status === 'completed'
                          ? 'bg-emerald-600 border-emerald-600 text-white'
                          : 'border-slate-300 hover:border-indigo-500'
                      }`}
                    >
                      {task.status === 'completed' && <Check className="w-3.5 h-3.5" />}
                    </button>
                    <div>
                      <h4 className={`text-sm font-semibold ${task.status === 'completed' ? 'line-through text-slate-500' : 'text-slate-900'}`}>
                        {task.title}
                      </h4>
                      {task.description && (
                        <p className="text-xs text-slate-500 mt-0.5">{task.description}</p>
                      )}
                      <div className="flex items-center gap-2 mt-2 text-[11px]">
                        <span className="text-slate-400 flex items-center gap-1">
                          <Clock className="w-3 h-3" /> Due {taskDate}
                        </span>
                        <span className={`px-2 py-0.5 rounded-full font-semibold uppercase text-[10px] ${
                          task.priority === 'critical' ? 'bg-red-100 text-red-700' : 'bg-slate-100 text-slate-700'
                        }`}>
                          {task.priority}
                        </span>
                        {task.is_overdue && (
                          <span className="text-red-600 font-bold">⚠️ Overdue</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* TAB 4: VENDORS */}
      {activeTab === 'vendors' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
            <h2 className="text-lg font-bold text-slate-900 mb-1">Vendor Network & Booking Tracker</h2>
            <p className="text-xs text-slate-500 mb-4">Track proposals, quotes, and contract bookings safely.</p>

            {/* Quick Add Vendor */}
            <form onSubmit={handleAddVendor} className="grid grid-cols-1 sm:grid-cols-4 gap-3 mb-6 p-4 bg-slate-50 rounded-xl border border-slate-200">
              <input
                type="text"
                required
                placeholder="Category (e.g. Catering, DJ)"
                value={vendCategory}
                onChange={(e) => setVendCategory(e.target.value)}
                className="px-3 py-2 text-xs border rounded-lg border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <input
                type="text"
                required
                placeholder="Vendor Name"
                value={vendName}
                onChange={(e) => setVendName(e.target.value)}
                className="px-3 py-2 text-xs border rounded-lg border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <input
                type="number"
                step="0.01"
                placeholder="Quoted Amount (optional)"
                value={vendQuoted}
                onChange={(e) => setVendQuoted(e.target.value)}
                className="px-3 py-2 text-xs border rounded-lg border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <button
                type="submit"
                className="bg-indigo-600 text-white rounded-lg text-xs font-semibold hover:bg-indigo-700 py-2"
              >
                + Add Vendor
              </button>
            </form>

            <div className="divide-y divide-slate-100">
              {event.vendors.map((vendor) => (
                <div key={vendor.id} className="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-slate-500 uppercase tracking-wide">
                        {vendor.category}
                      </span>
                      {vendor.is_ai_suggested && (
                        <span className="text-[10px] bg-indigo-50 text-indigo-700 font-semibold px-2 py-0.5 rounded-full border border-indigo-200">
                          AI Suggested
                        </span>
                      )}
                    </div>
                    <h3 className="font-bold text-slate-900 text-sm mt-0.5">{vendor.name}</h3>
                    {vendor.notes && <p className="text-xs text-slate-500 mt-0.5">{vendor.notes}</p>}
                    <div className="flex items-center gap-3 mt-1.5 text-xs text-slate-600">
                      {vendor.phone && <span>📞 {vendor.phone}</span>}
                      {vendor.email && <span>✉️ {vendor.email}</span>}
                      {vendor.quoted_amount && (
                        <span className="font-semibold text-slate-900">
                          Quote: {event.currency} {Number(vendor.quoted_amount).toLocaleString()}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <select
                      value={vendor.status}
                      onChange={(e) => handleVendorStatusChange(vendor.id, e.target.value)}
                      className="px-3 py-1.5 rounded-lg border border-slate-300 text-xs font-semibold bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                      <option value="considering">Considering</option>
                      <option value="contacted">Contacted</option>
                      <option value="quoted">Quoted</option>
                      <option value="booked">Booked (Confirmed)</option>
                      <option value="rejected">Rejected</option>
                    </select>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 5: AI CHAT & PLAN REVISION */}
      {activeTab === 'chat' && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col h-[600px]">
          {/* Header */}
          <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bot className="w-5 h-5 text-indigo-600" />
              <div>
                <h3 className="font-bold text-slate-900 text-sm">EventWise AI Planning Copilot</h3>
                <p className="text-[11px] text-slate-500">Context-aware conversational planning & schema-validated replanning</p>
              </div>
            </div>
          </div>

          {/* Messages list */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {chatHistory.map((msg, i) => (
              <div
                key={i}
                className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.role === 'assistant' && (
                  <div className="w-7 h-7 rounded-full bg-indigo-600 text-white flex items-center justify-center flex-shrink-0 text-xs font-bold">
                    AI
                  </div>
                )}
                <div
                  className={`p-3.5 rounded-2xl max-w-lg text-xs sm:text-sm leading-relaxed ${
                    msg.role === 'user'
                      ? 'bg-indigo-600 text-white rounded-br-none'
                      : 'bg-slate-100 text-slate-800 rounded-bl-none border border-slate-200'
                  }`}
                >
                  <p>{msg.text}</p>

                  {/* Proposed Plan Review Banner */}
                  {msg.proposed && (
                    <div className="mt-3 pt-3 border-t border-slate-200 bg-white p-3 rounded-lg text-slate-900">
                      <div className="flex items-center gap-1.5 font-bold text-xs text-indigo-700 mb-1">
                        <Sparkles className="w-3.5 h-3.5" />
                        <span>Proposed Revision Ready for Review</span>
                      </div>
                      <p className="text-xs text-slate-600 mb-2">
                        Theme preview: <em>{msg.proposed.theme}</em>
                      </p>
                      <button
                        onClick={() => handleApplyRevision(msg.messageId!)}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded shadow-sm transition"
                      >
                        <Check className="w-3.5 h-3.5" />
                        <span>Commit & Apply Changes to Event</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {chatLoading && (
              <div className="flex items-center gap-2 text-xs text-slate-500 italic">
                <Bot className="w-4 h-4 animate-bounce text-indigo-600" />
                <span>EventWise AI is calculating changes...</span>
              </div>
            )}
          </div>

          {/* Input footer */}
          <form onSubmit={handleSendChat} className="p-3 bg-slate-50 border-t border-slate-200 flex gap-2">
            <input
              type="text"
              placeholder="e.g. 'Reduce catering budget by 15% and reallocate to entertainment'..."
              value={chatPrompt}
              onChange={(e) => setChatPrompt(e.target.value)}
              className="flex-1 px-3.5 py-2 text-xs sm:text-sm rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
            />
            <button
              type="submit"
              disabled={chatLoading || !chatPrompt.trim()}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-xs sm:text-sm font-semibold hover:bg-indigo-700 transition disabled:opacity-50 flex items-center gap-1.5"
            >
              <Send className="w-4 h-4" />
              <span>Send</span>
            </button>
          </form>
        </div>
      )}
    </main>
  );
};
