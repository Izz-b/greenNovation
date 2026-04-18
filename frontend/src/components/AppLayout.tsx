import { Link, useRouterState } from "@tanstack/react-router";
import { useState, type ReactNode } from "react";
import {
  LayoutDashboard,
  FolderKanban,
  GraduationCap,
  HeartPulse,
  Trees,
  BookOpen,
  Sparkles,
  Bell,
  Search,
  Menu,
  X,
  Zap,
} from "lucide-react";
import { Panda } from "@/components/PandaCompanion";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/projects", label: "Projects", icon: FolderKanban },
  { to: "/learning", label: "Learning", icon: GraduationCap },
  { to: "/workspace", label: "Workspace", icon: BookOpen },
  { to: "/wellbeing", label: "Well-being", icon: HeartPulse },
  { to: "/forest", label: "Eco Forest", icon: Trees },
] as const;

export function AppLayout({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const { location } = useRouterState();
  const path = location.pathname;

  return (
    <div className="min-h-screen flex w-full">
      {/* Mobile overlay */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-foreground/20 backdrop-blur-sm lg:hidden"
          onClick={() => setOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:sticky top-0 left-0 z-50 h-screen w-72 shrink-0 transform transition-transform duration-300 ease-out lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex h-full flex-col gap-2 bg-sidebar border-r border-sidebar-border p-4">
          <div className="flex items-center justify-between px-2 py-3">
            <Link to="/" className="flex items-center gap-2.5" onClick={() => setOpen(false)}>
              <div className="relative h-10 w-10 rounded-2xl gradient-primary grid place-items-center shadow-glow">
                <Sparkles className="h-5 w-5 text-primary-foreground" strokeWidth={2.5} />
              </div>
              <div className="leading-tight">
                <div className="font-display text-lg font-bold tracking-tight">EcoLearn</div>
                <div className="text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
                  AI · OS
                </div>
              </div>
            </Link>
            <button
              className="lg:hidden rounded-lg p-2 hover:bg-sidebar-accent"
              onClick={() => setOpen(false)}
              aria-label="Close menu"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <nav className="flex flex-col gap-1 mt-2">
            {navItems.map((item) => {
              const active = path === item.to;
              const Icon = item.icon;
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  onClick={() => setOpen(false)}
                  className={`group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all ${
                    active
                      ? "bg-sidebar-primary text-sidebar-primary-foreground shadow-soft"
                      : "text-sidebar-foreground hover:bg-sidebar-accent hover:translate-x-0.5"
                  }`}
                >
                  <Icon
                    className={`h-[18px] w-[18px] transition-transform ${active ? "" : "group-hover:scale-110"}`}
                    strokeWidth={active ? 2.4 : 2}
                  />
                  <span>{item.label}</span>
                  {active && (
                    <span className="ml-auto h-1.5 w-1.5 rounded-full bg-primary-foreground/80" />
                  )}
                </Link>
              );
            })}
          </nav>

          {/* Avatar card at bottom */}
          <div className="mt-auto rounded-2xl gradient-forest p-4 relative overflow-hidden">
            <div className="absolute -right-4 -bottom-4 h-24 w-24 rounded-full bg-primary/10 blur-2xl" />
            <div className="flex items-start gap-3 relative">
              <div className="h-12 w-12 rounded-xl bg-card/60 p-1 grid place-items-center shrink-0">
                <Panda mood="waving" size={40} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-xs font-semibold text-foreground">Bamboo says</div>
                <p className="text-xs text-muted-foreground mt-0.5 leading-snug">
                  You're on a 4-day streak! Keep it growing 🌱
                </p>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="sticky top-0 z-30 glass border-b border-border/60">
          <div className="flex items-center gap-3 px-4 lg:px-8 h-16">
            <button
              className="lg:hidden rounded-lg p-2 hover:bg-muted"
              onClick={() => setOpen(true)}
              aria-label="Open menu"
            >
              <Menu className="h-5 w-5" />
            </button>

            <div className="hidden md:flex items-center gap-2 flex-1 max-w-md">
              <div className="relative w-full">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                  type="search"
                  placeholder="Search courses, notes, projects..."
                  className="w-full h-10 pl-10 pr-4 rounded-xl bg-muted/60 border border-transparent focus:bg-card focus:border-ring focus:outline-none text-sm transition-colors"
                />
              </div>
            </div>

            <div className="flex items-center gap-2 ml-auto">
              <div className="hidden sm:flex items-center gap-2 rounded-full bg-success/10 text-success px-3 py-1.5 text-xs font-semibold">
                <Zap className="h-3.5 w-3.5" />
                Eco mode
              </div>
              <button className="relative rounded-xl p-2.5 hover:bg-muted transition-colors">
                <Bell className="h-5 w-5" />
                <span className="absolute top-2 right-2 h-2 w-2 rounded-full bg-destructive ring-2 ring-background" />
              </button>
              <div className="h-9 w-9 rounded-xl gradient-primary grid place-items-center text-primary-foreground text-sm font-bold shadow-soft">
                S
              </div>
            </div>
          </div>
        </header>

        <main className="flex-1 px-4 lg:px-8 py-6 lg:py-8">{children}</main>
      </div>
    </div>
  );
}
