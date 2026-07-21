import { createFileRoute, Link } from "@tanstack/react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { RequireAuth } from "@/components/AppShell";
import { useStoreId } from "@/lib/auth";
import { addWorker, listStoreWorkers, removeWorker, type Worker } from "@/lib/stora-api";
import { Alert, Button, Card, Field, Input } from "@/components/ui-bits";
import { Plus, Trash2, ChevronRight } from "lucide-react";

export const Route = createFileRoute("/workers/")({
  component: () => (
    <RequireAuth>
      <WorkersPage />
    </RequireAuth>
  ),
  head: () => ({ meta: [{ title: "Workers — Stora" }] }),
});

function WorkersPage() {
  const { storeId } = useStoreId();
  const qc = useQueryClient();
  if (storeId == null) return null;

  const workersQ = useQuery({
    queryKey: ["workers", storeId],
    queryFn: () => listStoreWorkers(storeId),
  });

  const [form, setForm] = useState({ name: "", department: "", pay: "" });
  const [error, setError] = useState<string | null>(null);

  const addMut = useMutation({
    mutationFn: () =>
      addWorker(storeId, {
        name: form.name,
        department: form.department,
        pay: Number(form.pay),
      }),
    onSuccess: () => {
      setForm({ name: "", department: "", pay: "" });
      qc.invalidateQueries({ queryKey: ["workers", storeId] });
    },
    onError: (e) => setError(e instanceof Error ? e.message : "Add failed"),
  });

  const removeMut = useMutation({
    mutationFn: (id: number) => removeWorker(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["workers", storeId] }),
  });

  const workers: Worker[] = Array.isArray(workersQ.data) ? workersQ.data : [];

  return (
    <div className="space-y-8">
      <div>
        <div className="text-xs uppercase tracking-widest text-muted-foreground">Team</div>
        <h1 className="font-display text-4xl">Workers</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Manage the people who make your store run.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
        <Card className="p-0">
          <div className="flex items-center justify-between border-b border-border px-6 py-4">
            <h2 className="font-display text-lg">Roster</h2>
            <span className="text-xs text-muted-foreground">
              {workers.length} total
            </span>
          </div>

          {workersQ.isLoading ? (
            <p className="p-6 text-sm text-muted-foreground">Loading…</p>
          ) : workers.length === 0 ? (
            <p className="p-6 text-sm text-muted-foreground">
              No workers yet. Add one on the right.
            </p>
          ) : (
            <ul className="divide-y divide-border">
              {workers.map((w) => (
                <li
                  key={w.id}
                  className="flex items-center justify-between gap-3 px-6 py-3"
                >
                  <Link
                    to="/workers/$workerId"
                    params={{ workerId: String(w.id) }}
                    className="flex flex-1 items-center gap-3 hover:opacity-80"
                  >
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-secondary font-medium">
                      {w.name?.[0]?.toUpperCase() ?? "?"}
                    </div>
                    <div className="min-w-0">
                      <div className="truncate font-medium">{w.name}</div>
                      <div className="text-xs text-muted-foreground capitalize">
                        {w.department} · ${Number(w.pay).toLocaleString()}
                      </div>
                    </div>
                    <ChevronRight className="ml-auto h-4 w-4 text-muted-foreground" />
                  </Link>
                  <Button
                    variant="ghost"
                    aria-label={`Remove ${w.name}`}
                    onClick={() => {
                      if (confirm(`Remove ${w.name}?`)) removeMut.mutate(w.id);
                    }}
                  >
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card>
          <h2 className="font-display text-lg">Add worker</h2>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              setError(null);
              addMut.mutate();
            }}
            className="mt-4 space-y-3"
          >
            {error && <Alert tone="error">{error}</Alert>}
            <Field label="Name">
              <Input
                required
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
              />
            </Field>
            <Field label="Department" hint="e.g. manager, cashier, floor">
              <Input
                required
                value={form.department}
                onChange={(e) => setForm({ ...form, department: e.target.value })}
              />
            </Field>
            <Field label="Pay">
              <Input
                required
                inputMode="numeric"
                value={form.pay}
                onChange={(e) => setForm({ ...form, pay: e.target.value })}
              />
            </Field>
            <Button type="submit" disabled={addMut.isPending} className="w-full">
              <Plus className="h-4 w-4" />
              {addMut.isPending ? "Adding…" : "Add worker"}
            </Button>
          </form>
        </Card>
      </div>
    </div>
  );
}
