import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { DollarSign, Users, MapPin, Sparkles, Loader2, AlertCircle } from 'lucide-react';
import { createEvent } from '../api/events';

export const NewEventPage: React.FC = () => {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState({
    title: '',
    event_type: 'wedding',
    event_date: '',
    location: '',
    guest_count: 100,
    total_budget: 15000,
    currency: 'USD',
    preferences: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!form.title.trim()) {
      setError('Please provide an event title.');
      return;
    }
    if (!form.event_date) {
      setError('Please select a valid event date.');
      return;
    }
    if (new Date(form.event_date) < new Date()) {
      setError('Event date must be in the future.');
      return;
    }
    if (form.guest_count <= 0) {
      setError('Guest count must be greater than zero.');
      return;
    }
    if (form.total_budget <= 0) {
      setError('Budget must be greater than zero.');
      return;
    }

    setSubmitting(true);
    try {
      const created = await createEvent({
        ...form,
        event_date: new Date(form.event_date).toISOString(),
        guest_count: Number(form.guest_count),
        total_budget: Number(form.total_budget),
      });
      navigate(`/events/${created.id}`);
    } catch (err: any) {
      setError(err.message || 'Error creating event and generating plan.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="max-w-3xl mx-auto px-4 py-8">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8">
        <div className="border-b border-slate-100 pb-5 mb-6">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50 text-indigo-700 text-xs font-semibold mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            <span>GenAI Autonomous Planner</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Create & Architect a Celebration
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Specify your celebration parameters. EventWise will synthesize personalized ideas, balanced budget categories, dated milestone timelines, and vendor needs.
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-center gap-3 text-red-700">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <p className="text-sm">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="title" className="block text-sm font-semibold text-slate-700 mb-1">
              Event Title <span className="text-red-500">*</span>
            </label>
            <input
              id="title"
              type="text"
              required
              placeholder="e.g. Maya & Alex's Modern Rooftop Wedding"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label htmlFor="event_type" className="block text-sm font-semibold text-slate-700 mb-1">
                Event Type <span className="text-red-500">*</span>
              </label>
              <select
                id="event_type"
                value={form.event_type}
                onChange={(e) => setForm({ ...form, event_type: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
              >
                <option value="wedding">Wedding Celebration</option>
                <option value="birthday">Birthday Party</option>
                <option value="college">College Fest / Hackathon</option>
                <option value="community">Community Celebration</option>
              </select>
            </div>

            <div>
              <label htmlFor="event_date" className="block text-sm font-semibold text-slate-700 mb-1">
                Event Date <span className="text-red-500">*</span>
              </label>
              <input
                id="event_date"
                type="date"
                required
                value={form.event_date}
                onChange={(e) => setForm({ ...form, event_date: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label htmlFor="location" className="block text-sm font-semibold text-slate-700 mb-1">
                Location / Venue <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <MapPin className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  id="location"
                  type="text"
                  required
                  placeholder="e.g. San Francisco, CA"
                  value={form.location}
                  onChange={(e) => setForm({ ...form, location: e.target.value })}
                  className="w-full pl-9 pr-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>

            <div>
              <label htmlFor="guest_count" className="block text-sm font-semibold text-slate-700 mb-1">
                Expected Guests <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Users className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  id="guest_count"
                  type="number"
                  min="1"
                  required
                  value={form.guest_count}
                  onChange={(e) => setForm({ ...form, guest_count: parseInt(e.target.value) || 0 })}
                  className="w-full pl-9 pr-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>

            <div>
              <label htmlFor="total_budget" className="block text-sm font-semibold text-slate-700 mb-1">
                Budget ({form.currency}) <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <DollarSign className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  id="total_budget"
                  type="number"
                  min="100"
                  step="100"
                  required
                  value={form.total_budget}
                  onChange={(e) => setForm({ ...form, total_budget: parseFloat(e.target.value) || 0 })}
                  className="w-full pl-9 pr-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>
          </div>

          <div>
            <label htmlFor="preferences" className="block text-sm font-semibold text-slate-700 mb-1">
              Preferences, Themes & Constraints <span className="text-xs text-slate-400 font-normal">(Optional)</span>
            </label>
            <textarea
              id="preferences"
              rows={3}
              placeholder="e.g. Vegan culinary preferences, rustic wooden tables, acoustic indie background music, eco-friendly non-plastic materials..."
              value={form.preferences}
              onChange={(e) => setForm({ ...form, preferences: e.target.value })}
              className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div className="pt-4 border-t border-slate-100 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={() => navigate('/')}
              className="px-4 py-2.5 rounded-lg border border-slate-300 text-slate-700 font-medium text-sm hover:bg-slate-50 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-lg bg-indigo-600 text-white font-semibold text-sm hover:bg-indigo-700 shadow-md transition disabled:opacity-50"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Synthesizing Plan with AI...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Generate Personalized Plan</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </main>
  );
};
