import { Calendar, Sparkles, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Navbar: React.FC = () => {
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 text-indigo-600 hover:text-indigo-700 transition focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded">
          <div className="w-9 h-9 rounded-lg bg-indigo-600 text-white flex items-center justify-center shadow-sm">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <span className="font-bold text-lg text-slate-900 tracking-tight">EventWise</span>
            <span className="text-xs ml-1.5 px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 font-semibold border border-indigo-200">AI Planner</span>
          </div>
        </Link>

        <nav aria-label="Main Navigation" className="flex items-center gap-4">
          <Link
            to="/"
            className="text-sm font-medium text-slate-600 hover:text-slate-900 px-3 py-1.5 rounded transition"
          >
            Dashboard
          </Link>
          <Link
            to="/events/new"
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-sm font-medium rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 shadow-sm transition focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <Calendar className="w-4 h-4" />
            <span>Plan New Event</span>
          </Link>
          <div className="hidden sm:flex items-center gap-1.5 text-xs text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Active Demo Sandbox</span>
          </div>
        </nav>
      </div>
    </header>
  );
};
