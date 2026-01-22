'use client';

import {
  LayoutDashboard,
  ShieldCheck,
  AlertTriangle,
  BrainCircuit,
  FileText,
  Settings,
  LogOut,
} from 'lucide-react';

const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', active: true },
  { icon: ShieldCheck, label: 'Inspections', count: 12 },
  { icon: AlertTriangle, label: 'Risk Analysis' },
  { icon: BrainCircuit, label: 'ML Models' },
  { icon: FileText, label: 'Reports' },
];

export default function DashboardSidebar() {
  return (
    <aside className="w-64 flex-shrink-0 p-6 flex flex-col">
      {/* Header */}
      <div className="mb-10">
        <h1 className="text-2xl font-bold text-gray-800">AlUla AI</h1>
        <p className="text-sm text-gray-500">Inspection Platform</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1">
        <ul>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <li key={item.label} className="mb-2">
                <a
                  href="#"
                  className={`flex items-center gap-3 px-4 py-2.5 rounded-lg transition-colors ${
                    item.active
                      ? 'bg-blue-500/10 text-blue-600 font-semibold'
                      : 'text-gray-500 hover:bg-gray-200/50 hover:text-gray-800'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{item.label}</span>
                  {item.count && (
                    <span className="ml-auto text-xs font-bold bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center">
                      {item.count}
                    </span>
                  )}
                </a>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Footer Nav */}
      <div>
        <ul>
          <li className="mb-2">
            <a href="#" className="flex items-center gap-3 px-4 py-2.5 rounded-lg text-gray-500 hover:bg-gray-200/50 hover:text-gray-800 transition-colors">
              <Settings className="w-5 h-5" />
              <span>Settings</span>
            </a>
          </li>
          <li>
            <a href="#" className="flex items-center gap-3 px-4 py-2.5 rounded-lg text-gray-500 hover:bg-gray-200/50 hover:text-gray-800 transition-colors">
              <LogOut className="w-5 h-5" />
              <span>Log out</span>
            </a>
          </li>
        </ul>
      </div>
    </aside>
  );
}
