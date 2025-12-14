import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Upload, FileText, Search, Wand2, History, Bug } from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Import', href: '/import', icon: Upload },
  { name: 'Master Resume', href: '/master-resume', icon: FileText },
  { name: 'Research', href: '/research', icon: Search },
  { name: 'Generate', href: '/generate', icon: Wand2 },
  { name: 'History', href: '/history', icon: History },
  { name: 'Debug', href: '/debug', icon: Bug },
];

export default function Sidebar() {
  return (
    <aside className="flex w-64 flex-col border-r border-gray-200 bg-white">
      <div className="flex h-16 items-center justify-center border-b border-gray-200">
        <h1 className="text-xl font-bold text-primary-600">GroundedCV</h1>
      </div>
      <nav className="flex-1 space-y-1 p-4">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                isActive ? 'bg-primary-50 text-primary-600' : 'text-gray-700 hover:bg-gray-100'
              }`
            }
          >
            <item.icon className="h-5 w-5" />
            {item.name}
          </NavLink>
        ))}
      </nav>
      <div className="border-t border-gray-200 p-4">
        <p className="text-xs text-gray-500 text-center">Your story. Truthfully tailored.</p>
      </div>
    </aside>
  );
}
