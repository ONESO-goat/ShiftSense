import { Link, useNavigate, useRouterState } from "@tanstack/react-router";
import { LogOut, LayoutDashboard, Users, MessageSquare, Sparkles } from "lucide-react";
import type { ReactNode } from "react";
import { clearStoredStoreId, useStoreId } from "@/lib/auth";

const NAV = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/workers", label: "Workers", icon: Users },
  { to: "/chat", label: "Talk to Stora", icon: MessageSquare },
  { to: "/reviews", label: "Reviews", icon: Sparkles },
] as const;

export function AppShell({ children }: { children: ReactNode }) {
  const { storeId } = useStoreId();
  const navigate = useNavigate();
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-30 border-b border-border bg-background/85 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-3">
          <Link to="/dashboard" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand text-brand-foreground font-display text-lg">
              S
            </div>
            <div className="leading-tight">
              <div className="font-display text-lg">Stora</div>
              <div className="text-[10px] uppercase tracking-widest text-muted-foreground">
                Store Copilot
              </div>
            </div>
          </Link>

          <nav className="hidden items-center gap-1 md:flex">
            {NAV.map((n) => {
              const active = pathname === n.to || pathname.startsWith(n.to + "/");
              return (
                <Link
                  key={n.to}
                  to={n.to}
                  className={`btn btn-ghost px-3 py-1.5 text-sm ${
                    active ? "bg-secondary text-secondary-foreground" : "text-muted-foreground"
                  }`}
                >
                  <n.icon className="h-4 w-4" />
                  {n.label}
                </Link>
              );
            })}
          </nav>

          <div className="flex items-center gap-3">
            {storeId != null && (
              <span className="hidden text-xs text-muted-foreground sm:inline">
                Store #{storeId}
              </span>
            )}
            <button
              className="btn btn-outline text-sm"
              onClick={() => {
                clearStoredStoreId();
                navigate({ to: "/" });
              }}
            >
              <LogOut className="h-4 w-4" />
              Sign out
            </button>
          </div>
        </div>

        <nav className="mx-auto flex max-w-6xl items-center gap-1 overflow-x-auto px-4 pb-2 md:hidden">
          {NAV.map((n) => {
            const active = pathname === n.to || pathname.startsWith(n.to + "/");
            return (
              <Link
                key={n.to}
                to={n.to}
                className={`btn btn-ghost whitespace-nowrap px-3 py-1.5 text-sm ${
                  active ? "bg-secondary" : "text-muted-foreground"
                }`}
              >
                <n.icon className="h-4 w-4" />
                {n.label}
              </Link>
            );
          })}
        </nav>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
    </div>
  );
}

export function RequireAuth({ children }: { children: ReactNode }) {
  const { storeId, ready } = useStoreId();
  const navigate = useNavigate();
  if (!ready)
    return (
      <div className="flex min-h-screen items-center justify-center text-sm text-muted-foreground">
        Loading…
      </div>
    );
  if (storeId == null) {
    // client-side redirect
    navigate({ to: "/" });
    return null;
  }
  return <AppShell>{children}</AppShell>;
}
