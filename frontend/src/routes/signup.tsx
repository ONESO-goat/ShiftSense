import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { createStore } from "@/lib/stora-api";
import { setStoredStoreId } from "@/lib/auth";
import { Alert, Button, Field, Input } from "@/components/ui-bits";

export const Route = createFileRoute("/signup")({
  component: SignupPage,
  head: () => ({ meta: [{ title: "Create store — Stora" }] }),
});

function SignupPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: "",
    email: "",
    city: "",
    address: "",
    zip: "",
    password: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [created, setCreated] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  const set = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await createStore({
        name: form.name,
        email: form.email,
        city: form.city,
        address: form.address,
        zip: Number(form.zip),
        password: form.password,
      });
      const newId = Number(res.id ?? res.store_id ?? 0);
      if (Number.isFinite(newId) && newId > 0) {
        setCreated(newId);
        setStoredStoreId(newId);
        setTimeout(() => navigate({ to: "/dashboard" }), 1500);
      } else {
        setError("Store created, but no ID returned. Please sign in.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign up failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-xl px-6 py-12">
      <Link to="/" className="text-sm text-muted-foreground hover:text-foreground">
        ← Back to sign in
      </Link>
      <h1 className="mt-4 font-display text-3xl">Create your store</h1>
      <p className="mt-1 text-sm text-muted-foreground">
        Stora will start tracking workers, weather, and daily flow for this location.
      </p>

      <form onSubmit={submit} className="card-surface mt-8 space-y-4 p-6">
        {error && <Alert tone="error">{error}</Alert>}
        {created && (
          <Alert tone="success">
            Store created! Your Store ID is <b>{created}</b>. Save it somewhere safe.
          </Alert>
        )}

        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Store name">
            <Input required value={form.name} onChange={set("name")} />
          </Field>
          <Field label="Email">
            <Input type="email" required value={form.email} onChange={set("email")} />
          </Field>
          <Field label="City">
            <Input required value={form.city} onChange={set("city")} />
          </Field>
          <Field label="ZIP">
            <Input inputMode="numeric" required value={form.zip} onChange={set("zip")} />
          </Field>
          <Field label="Address" hint="Street address" >
            <Input required value={form.address} onChange={set("address")} />
          </Field>
          <Field label="Password">
            <Input type="password" required minLength={8} value={form.password} onChange={set("password")} />
          </Field>
        </div>

        <Button type="submit" disabled={loading} className="w-full">
          {loading ? "Creating…" : "Create store"}
        </Button>
      </form>
    </div>
  );
}
