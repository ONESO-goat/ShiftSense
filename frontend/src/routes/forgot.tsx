import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { forgotId, resetPassword } from "@/lib/stora-api";
import { Alert, Button, Card, Field, Input } from "@/components/ui-bits";

export const Route = createFileRoute("/forgot")({
  component: ForgotPage,
  head: () => ({ meta: [{ title: "Account recovery — Stora" }] }),
});

function ForgotPage() {
  const [email, setEmail] = useState("");
  const [idResult, setIdResult] = useState<string | null>(null);
  const [idError, setIdError] = useState<string | null>(null);
  const [idLoading, setIdLoading] = useState(false);

  const [resetId, setResetId] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [resetMsg, setResetMsg] = useState<string | null>(null);
  const [resetError, setResetError] = useState<string | null>(null);
  const [resetLoading, setResetLoading] = useState(false);

  async function lookupId(e: React.FormEvent) {
    e.preventDefault();
    setIdError(null);
    setIdResult(null);
    setIdLoading(true);
    try {
      const res = await forgotId(email);
      const found = res.id ?? res.store_id ?? res.message;
      setIdResult(found != null ? String(found) : JSON.stringify(res));
    } catch (err) {
      setIdError(err instanceof Error ? err.message : "Lookup failed");
    } finally {
      setIdLoading(false);
    }
  }

  async function doReset(e: React.FormEvent) {
    e.preventDefault();
    setResetError(null);
    setResetMsg(null);
    setResetLoading(true);
    try {
      await resetPassword(Number(resetId), newPassword);
      setResetMsg("Password updated. You can sign in now.");
    } catch (err) {
      setResetError(err instanceof Error ? err.message : "Reset failed");
    } finally {
      setResetLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-12">
      <Link to="/" className="text-sm text-muted-foreground hover:text-foreground">
        ← Back to sign in
      </Link>
      <h1 className="mt-4 font-display text-3xl">Account recovery</h1>

      <div className="mt-8 grid gap-6">
        <Card>
          <h2 className="font-display text-xl">Forgot your Store ID?</h2>
          <p className="mt-1 text-sm text-muted-foreground">Look it up with your email.</p>
          <form onSubmit={lookupId} className="mt-4 space-y-3">
            {idError && <Alert tone="error">{idError}</Alert>}
            {idResult && <Alert tone="success">Store ID: {idResult}</Alert>}
            <Field label="Email">
              <Input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </Field>
            <Button type="submit" disabled={idLoading}>
              {idLoading ? "Looking up…" : "Find my ID"}
            </Button>
          </form>
        </Card>

        <Card>
          <h2 className="font-display text-xl">Reset password</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Set a new password for your store.
          </p>
          <form onSubmit={doReset} className="mt-4 space-y-3">
            {resetError && <Alert tone="error">{resetError}</Alert>}
            {resetMsg && <Alert tone="success">{resetMsg}</Alert>}
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label="Store ID">
                <Input
                  inputMode="numeric"
                  required
                  value={resetId}
                  onChange={(e) => setResetId(e.target.value)}
                />
              </Field>
              <Field label="New password">
                <Input
                  type="password"
                  required
                  minLength={8}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                />
              </Field>
            </div>
            <Button type="submit" disabled={resetLoading}>
              {resetLoading ? "Updating…" : "Update password"}
            </Button>
          </form>
        </Card>
      </div>
    </div>
  );
}
