import { createFileRoute } from "@tanstack/react-router";
import { useRef, useState } from "react";
import { RequireAuth } from "@/components/AppShell";
import { useStoreId } from "@/lib/auth";
import { talkToStora } from "@/lib/stora-api";
import { Button, Card } from "@/components/ui-bits";
import { Send, Sparkles, User } from "lucide-react";

export const Route = createFileRoute("/chat")({
  component: () => (
    <RequireAuth>
      <ChatPage />
    </RequireAuth>
  ),
  head: () => ({ meta: [{ title: "Talk to Stora" }] }),
});

interface Msg {
  role: "user" | "stora";
  text: string;
}

function ChatPage() {
  const { storeId } = useStoreId();
  const activeStoreId = storeId;
  if (activeStoreId == null) return null;
  const [messages, setMessages] = useState<Msg[]>([
    {
      role: "stora",
      text: "Hi, I'm Stora. Ask me anything about your store — I'll check your workers, the weather, and the day's flow.",
    },
  ]);
  const [pending, setPending] = useState(false);
  const [draft, setDraft] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  async function send() {
    const text = draft.trim();
    if (!text || pending) return;
    setMessages((m) => [...m, { role: "user", text }]);
    setDraft("");
    setPending(true);
    try {
      const res = await talkToStora(activeStoreId!);
      const reply =
        res.response ??
        res.message ??
        (typeof res === "string" ? res : JSON.stringify(res, null, 2));
      setMessages((m) => [...m, { role: "stora", text: reply }]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: "stora", text: err instanceof Error ? err.message : "I'm offline." },
      ]);
    } finally {
      setPending(false);
      setTimeout(() => scrollRef.current?.scrollTo(0, 99999), 50);
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <div className="text-xs uppercase tracking-widest text-muted-foreground">
          Copilot
        </div>
        <h1 className="font-display text-4xl">Talk to Stora</h1>
      </div>

      <Card className="p-0">
        <div ref={scrollRef} className="max-h-[60vh] space-y-4 overflow-y-auto p-6">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`flex gap-3 ${m.role === "user" ? "flex-row-reverse" : ""}`}
            >
              <div
                className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
                  m.role === "user"
                    ? "bg-secondary text-secondary-foreground"
                    : "bg-brand text-brand-foreground"
                }`}
              >
                {m.role === "user" ? (
                  <User className="h-4 w-4" />
                ) : (
                  <Sparkles className="h-4 w-4" />
                )}
              </div>
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap ${
                  m.role === "user"
                    ? "bg-secondary text-secondary-foreground"
                    : "bg-muted text-foreground"
                }`}
              >
                {m.text}
              </div>
            </div>
          ))}
          {pending && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Sparkles className="h-3.5 w-3.5 animate-pulse" />
              Stora is thinking…
            </div>
          )}
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            send();
          }}
          className="flex items-center gap-2 border-t border-border p-3"
        >
          <input
            className="field focus:field-focus flex-1"
            placeholder="Ask about workers, weather, or the day…"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
          />
          <Button type="submit" disabled={pending || !draft.trim()}>
            <Send className="h-4 w-4" />
            Send
          </Button>
        </form>
      </Card>
    </div>
  );
}
