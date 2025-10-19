import { ReactNode, useState } from "react";
import { NavLink } from "react-router-dom";
import { 
  LayoutDashboard, 
  Radio, 
  Brain, 
  Target, 
  Settings, 
  Menu, 
  X,
  AlertCircle
} from "lucide-react";
import { cn } from "@/lib/utils";

interface LayoutProps {
  children: ReactNode;
}

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/monitoring", icon: Radio, label: "Monitoring" },
  { to: "/analysis", icon: Brain, label: "Analysis" },
  { to: "/strategy", icon: Target, label: "Strategy" },
  { to: "/settings", icon: Settings, label: "Settings" },
];

const Layout = ({ children }: LayoutProps) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="flex min-h-screen w-full bg-background">
      {/* Sidebar */}
      <aside
        className={cn(
          "fixed left-0 top-0 z-40 h-screen bg-sidebar transition-all duration-300",
          sidebarOpen ? "w-64" : "w-20"
        )}
      >
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-sidebar-border p-4">
            {sidebarOpen && (
              <div className="flex items-center gap-2">
                <AlertCircle className="h-6 w-6 text-sidebar-foreground" />
                <span className="text-lg font-bold text-sidebar-foreground">
                  Filtr
                </span>
              </div>
            )}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="rounded-lg p-2 text-sidebar-foreground hover:bg-sidebar-accent transition-colors"
            >
              {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-2 p-4">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 rounded-lg px-3 py-3 text-sidebar-foreground transition-all duration-200",
                    isActive
                      ? "bg-sidebar-primary text-sidebar-primary-foreground shadow-glow-primary"
                      : "hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                  )
                }
              >
                <item.icon className="h-5 w-5 flex-shrink-0" />
                {sidebarOpen && (
                  <span className="font-medium">{item.label}</span>
                )}
              </NavLink>
            ))}
          </nav>

          {/* Footer */}
          {sidebarOpen && (
            <div className="border-t border-sidebar-border p-4">
              <p className="text-xs text-sidebar-foreground/60">
                Filtr Platform v1.0
              </p>
            </div>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <main
        className={cn(
          "flex-1 transition-all duration-300",
          sidebarOpen ? "ml-64" : "ml-20"
        )}
      >
        <div className="min-h-screen p-6 md:p-8">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;
