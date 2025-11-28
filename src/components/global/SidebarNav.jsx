import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { LayoutDashboard, Activity, Search, Shield, Settings, LogOut } from 'lucide-react';
import './SidebarNav.css';

const SidebarNav = () => {
  const location = useLocation();
  const { logout } = useAuth();
  const isActive = (path) => location.pathname === path;

  const navItems = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
    { icon: Activity, label: 'Monitoring', path: '/monitoring' },
    { icon: Search, label: 'Analysis', path: '/analysis' },
    { icon: Shield, label: 'Strategy', path: '/strategy' },
    { icon: Settings, label: 'Settings', path: '/settings' },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <img src="/assets/filtr-logo.png" alt="Filtr Logo" className="logo-image" />
        <span className="logo-text">Filtr</span>
      </div>

      <nav className="nav-list">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`nav-item ${isActive(item.path) ? 'active' : ''}`}
          >
            <item.icon size={20} />
            <span>{item.label}</span>
          </Link>
        ))}

        <button onClick={logout} className="nav-item logout-btn">
          <LogOut size={20} />
          <span>Logout</span>
        </button>
      </nav>
    </aside>
  );
};

export default SidebarNav;
