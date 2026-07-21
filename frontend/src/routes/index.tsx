import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { loginStore } from "@/lib/stora-api";
import { setStoredStoreId, useStoreId } from "@/lib/auth";
import { Alert, Button, Field, Input } from "@/components/ui-bits";
import { Sparkles } from "lucide-react";

export const Route = createFileRoute("/")({
  component: LoginPage,
  head: () => ({ meta: [{ title: "Sign in — Stora" }] }),
});

function LoginPage() {
  const navigate = useNavigate();
  const { storeId, ready } = useStoreId();
  const [id, setId] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (ready && storeId != null) navigate({ to: "/dashboard" });
  }, [ready, storeId, navigate]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const parsedId = Number(id);
      if (!Number.isFinite(parsedId)) throw new Error("Store ID must be a number");
      await loginStore(parsedId, password);
      setStoredStoreId(parsedId);
      navigate({ to: "/dashboard" });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <div className="relative hidden flex-col justify-between overflow-hidden bg-primary p-12 text-primary-foreground lg:flex">
        <div className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-foreground/10 font-display text-xl backdrop-blur">
            S
          </div>
          <span className="font-display text-xl">Stora</span>
        </div>
        <div className="space-y-4">
          <Sparkles className="h-8 w-8 opacity-70" />
          <h1 className="font-display text-4xl leading-tight">
            The calm command center for your store.
          </h1>
          <p className="max-w-md text-primary-foreground/70">
            Stora watches the roster, the weather, and the flow of your floor — so you can
            focus on the people in it.
          </p>
        </div>
        <div className="text-xs uppercase tracking-widest text-primary-foreground/50">
          AI Copilot for retail managers
        </div>
      </div>

      <div className="flex items-center justify-center p-6 sm:p-12">
        <form onSubmit={submit} className="w-full max-w-sm space-y-5">
          <div className="space-y-1">
            <h2 className="font-display text-3xl">Welcome back</h2>
            <p className="text-sm text-muted-foreground">Sign in to your store.</p>
          </div>

          {error && <Alert tone="error">{error}</Alert>}

          <Field label="Store ID">
            <Input
              inputMode="numeric"
              value={id}
              onChange={(e) => setId(e.target.value)}
              placeholder="e.g. 8920501532"
              required
            />
          </Field>
          <Field label="Password">
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </Field>

          <Button type="submit" disabled={loading} className="w-full">
            {loading ? "Signing in…" : "Sign in"}
          </Button>

          <div className="flex justify-between text-sm text-muted-foreground">
            <Link to="/forgot" className="hover:text-foreground">
              Forgot ID or password?
            </Link>
            <Link to="/signup" className="font-medium text-brand hover:opacity-80">
              Create store
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
