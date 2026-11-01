import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Calendar, Users, DollarSign, MapPin, ArrowRight, PlusCircle, AlertCircle } from 'lucide-react';
import { fetchEvents } from '../api/events';
import type { EventDetail } from '../types/event';

export const DashboardPage: React.FC = () => {
  const [events, setEvents] = useState<EventDetail[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchEvents()
      .then((data) => setEvents(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const getBadgeClass = (type: string) => {
    switch (type) {
      case 'wedding':
        return 'bg-pink-50 text-pink-700 border-pink-200';
      case 'birthday':
        return 'bg-purple-50 text-purple-700 border-purple-200';
      case 'college':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'community':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      default:
        return 'bg-slate-50 text-slate-700 border-slate-200';
    }
  };

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Hero Welcome banner */}
      <section className="bg-gradient-to-r from-indigo-700 via-indigo-600 to-indigo-800 rounded-2xl p-6 sm:p-8 text-white shadow-lg mb-8">
        <div className="max-w-3xl">
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Intelligent Celebration & Event Operations
          </h1>
          <p className="mt-2 text-indigo-100 text-sm sm:text-base leading-relaxed">
            Personalized event conceptualization, precision budget reconciliation, milestone task tracking, and conversational AI replanning in a unified workspace.
          </p>
          <div className="mt-5 flex flex-wrap gap-3">
            <Link
              to="/events/new"
              className="inline-flex items-center gap-2 bg-white text-indigo-700 px-4 py-2 rounded-lg font-semibold text-sm hover:bg-indigo-50 shadow-sm transition focus:outline-none focus:ring-2 focus:ring-white"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Create New Event</span>
            </Link>
          </div>
        </div>
      </section>

      {/* Events Section */}
      <section aria-labelledby="events-heading">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 id="events-heading" className="text-xl font-bold text-slate-900">
              Your Managed Celebrations
            </h2>
            <p className="text-xs sm:text-sm text-slate-500">
              Access real-time timelines, expenses, and AI planning assistant.
            </p>
          </div>
        </div>

        {loading && (
          <div className="text-center py-16 bg-white rounded-xl border border-slate-200">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-600 border-t-transparent" />
            <p className="mt-2 text-sm text-slate-500">Retrieving event dossiers...</p>
          </div>
        )}

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-xl flex items-center gap-3 text-red-700">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <p className="text-sm">{error}</p>
          </div>
        )}

        {!loading && !error && events.length === 0 && (
          <div className="text-center py-16 bg-white rounded-xl border border-dashed border-slate-300 p-8">
            <Calendar className="w-12 h-12 text-slate-400 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-slate-800">No events planned yet</h3>
            <p className="text-sm text-slate-500 mt-1 max-w-sm mx-auto">
              Get started by creating your first wedding, birthday bash, college fest, or community gathering.
            </p>
            <Link
              to="/events/new"
              className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700"
            >
              Plan Your First Event
            </Link>
          </div>
        )}

        {!loading && !error && events.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {events.map((event) => {
              const formattedDate = new Date(event.event_date).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
              });

              const completedTasks = event.tasks.filter((t) => t.status === 'completed').length;
              const taskProgress = event.tasks.length > 0 ? Math.round((completedTasks / event.tasks.length) * 100) : 0;

              return (
                <div
                  key={event.id}
                  className="bg-white rounded-xl border border-slate-200 hover:border-indigo-300 hover:shadow-md transition flex flex-col justify-between overflow-hidden"
                >
                  <div className="p-5">
                    <div className="flex items-center justify-between gap-2 mb-3">
                      <span className={`text-xs px-2.5 py-0.5 rounded-full font-semibold border ${getBadgeClass(event.event_type)} capitalize`}>
                        {event.event_type}
                      </span>
                      <span className="text-xs text-slate-500 flex items-center gap-1">
                        <Calendar className="w-3.5 h-3.5 text-slate-400" />
                        {formattedDate}
                      </span>
                    </div>

                    <h3 className="font-bold text-lg text-slate-900 line-clamp-1 mb-1">
                      {event.title}
                    </h3>

                    {event.theme && (
                      <p className="text-xs text-indigo-700 font-medium mb-3 line-clamp-1">
                        Theme: {event.theme}
                      </p>
                    )}

                    <div className="space-y-1.5 text-xs text-slate-600 mt-4 border-t border-slate-100 pt-3">
                      <div className="flex items-center justify-between">
                        <span className="flex items-center gap-1.5 text-slate-500">
                          <MapPin className="w-3.5 h-3.5" /> Location:
                        </span>
                        <span className="font-medium text-slate-800 truncate max-w-[150px]">{event.location}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="flex items-center gap-1.5 text-slate-500">
                          <Users className="w-3.5 h-3.5" /> Guests:
                        </span>
                        <span className="font-medium text-slate-800">{event.guest_count} attendees</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="flex items-center gap-1.5 text-slate-500">
                          <DollarSign className="w-3.5 h-3.5" /> Budget:
                        </span>
                        <span className="font-bold text-slate-900">
                          {event.currency} {Number(event.total_budget).toLocaleString()}
                        </span>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="mt-4 pt-3 border-t border-slate-100">
                      <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                        <span>Milestones</span>
                        <span>{completedTasks}/{event.tasks.length} Completed ({taskProgress}%)</span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                        <div
                          className="bg-indigo-600 h-1.5 rounded-full"
                          style={{ width: `${taskProgress}%` }}
                        />
                      </div>
                    </div>
                  </div>

                  <div className="bg-slate-50 px-5 py-3 border-t border-slate-100 flex items-center justify-between">
                    <span className="text-xs text-slate-500">
                      {event.vendors.length} Vendors tracked
                    </span>
                    <Link
                      to={`/events/${event.id}`}
                      className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-800 transition"
                    >
                      <span>Manage Event</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>
    </main>
  );
};
