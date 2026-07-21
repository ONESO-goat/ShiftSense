import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { RequireAuth } from "@/components/AppShell";
import { useStoreId } from "@/lib/auth";
import { requestReview } from "@/lib/stora-api";
import { Alert, Button, Card } from "@/components/ui-bits";
import { Sparkles, RefreshCw } from "lucide-react";

export const Route = createFileRoute("/reviews")({
  component: () => (
    <RequireAuth>
      <ReviewsPage />
    </RequireAuth>
  ),
  head: () => ({ meta: [{ title: "Reviews — Stora" }] }),
});

interface Entry {
  at: string;
  text: string;
}

function ReviewsPage() {
  const { storeId } = useStoreId();

  // 1. Declare ALL hooks first
  const [entries, setEntries] = useState<Entry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 2. Early returns go AFTER all hooks are declared
  if (storeId == null) return null;

  async function generate() {
    setError(null);
    setLoading(true);
    try {
      // TS safely knows storeId is string here due to the check above
      const res = await requestReview(storeId); 
      const text =
        res.review ??
        res.message ??
        (typeof res === "string" ? res : JSON.stringify(res, null, 2));

      setEntries((e) => [
        { id: crypto.randomUUID(), at: new Date().toLocaleString(), text },
        ...e,
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Review failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="text-xs uppercase tracking-widest text-muted-foreground">
            Performance
          </div>
          <h1 className="font-display text-4xl">Stora reviews</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Ask Stora for an honest snapshot of how the store is doing.
          </p>
        </div>
        <Button onClick={generate} disabled={loading}>
          {loading ? (
            <RefreshCw className="h-4 w-4 animate-spin" />
          ) : (
            <Sparkles className="h-4 w-4" />
          )}
          {loading ? "Reviewing…" : "Generate review"}
        </Button>
      </div>

      {error && <Alert tone="error">{error}</Alert>}

      {entries.length === 0 && !loading && (
        <Card>
          <p className="text-sm text-muted-foreground">
            No reviews yet. Tap <b>Generate review</b> and Stora will look at your store.
          </p>
        </Card>
      )}

      <div className="space-y-4">
        {entries.map((e, i) => (
          <Card key={i}>
            <div className="mb-3 flex items-center gap-2 text-xs uppercase tracking-widest text-muted-foreground">
              <Sparkles className="h-3.5 w-3.5 text-brand" />
              Review · {e.at}
            </div>
            <div className="whitespace-pre-wrap text-sm leading-relaxed">{e.text}</div>
          </Card>
        ))}
      </div>
    </div>
  );
}
