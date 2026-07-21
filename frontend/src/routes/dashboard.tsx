import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { RequireAuth } from "@/components/AppShell";
import { useStoreId } from "@/lib/auth";
import {
  getStore,
  listStoreWorkers,
  shiftOver,
  talkToStora,
  type Worker,
} from "@/lib/stora-api";
import { Card, StatCard, Alert, Button } from "@/components/ui-bits";
import { Cloud, CloudRain, Sun, Users, Clock, MapPin, Sparkles } from "lucide-react";
import { useState } from "react";

export const Route = createFileRoute("/dashboard")({
  component: () => (
    <RequireAuth>
      <Dashboard />
    </RequireAuth>
  ),
  head: () => ({ meta: [{ title: "Dashboard — Stora" }] }),
});

interface WeatherNow {
  temperature: number;
  weathercode: number;
  windspeed: number;
}

async function fetchWeather(city: string): Promise<WeatherNow | null> {
  try {
    const geo = await fetch(
      `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(city)}&count=1`,
    ).then((r) => r.json());
    const loc = geo?.results?.[0];
    if (!loc) return null;
    const wx = await fetch(
      `https://api.open-meteo.com/v1/forecast?latitude=${loc.latitude}&longitude=${loc.longitude}&current_weather=true&temperature_unit=fahrenheit`,
    ).then((r) => r.json());
    return wx?.current_weather ?? null;
  } catch {
    return null;
  }
}

function weatherLabel(code: number): { label: string; Icon: typeof Sun } {
  if (code === 0) return { label: "Clear", Icon: Sun };
  if (code < 50) return { label: "Cloudy", Icon: Cloud };
  return { label: "Rain / storm", Icon: CloudRain };
}

function Dashboard() {
  const { storeId } = useStoreId();
  const activeStoreId = storeId;

  // 1. All hooks defined FIRST
  const storeQ = useQuery({
    queryKey: ["store", activeStoreId],
    queryFn: () => getStore(activeStoreId!),
    enabled: activeStoreId != null, // Only run query when activeStoreId exists
  });

  const workersQ = useQuery({
    queryKey: ["workers", activeStoreId],
    queryFn: () => listStoreWorkers(activeStoreId!),
    enabled: activeStoreId != null,
  });

  const shiftOverQ = useQuery({
    queryKey: ["shift-over", activeStoreId],
    queryFn: () => shiftOver(activeStoreId!),
    enabled: activeStoreId != null,
  });

  const weatherQ = useQuery({
    queryKey: ["weather", storeQ.data?.city],
    queryFn: () => fetchWeather(String(storeQ.data?.city ?? "")),
    enabled: !!storeQ.data?.city && activeStoreId != null,
  });

  const [insight, setInsight] = useState<string | null>(null);
  const [insightLoading, setInsightLoading] = useState(false);

  // 2. NOW you can safely check for missing storeId and early return!
  if (activeStoreId == null) return null;

  const workers: Worker[] = Array.isArray(workersQ.data) ? workersQ.data : [];
  const shiftOverList: Worker[] = Array.isArray(shiftOverQ.data) ? shiftOverQ.data : [];

  async function askStora() {
    setInsightLoading(true);
    try {
      const res = await talkToStora(activeStoreId!, false, "Give me a quick overview of how the store is doing.");
      setInsight(
        res.response ??
          res.message ??
          (typeof res === "string" ? res : JSON.stringify(res)),
      );
    } catch (err) {
      setInsight(err instanceof Error ? err.message : "Stora is unavailable.");
    } finally {
      setInsightLoading(false);
    }
  }

  const wx = weatherQ.data;
  const { label: wxLabel, Icon: WxIcon } = wx
    ? weatherLabel(wx.weathercode)
    : { label: "—", Icon: Cloud };
    
  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="text-xs uppercase tracking-widest text-muted-foreground">
            Store overview
          </div>
          <h1 className="font-display text-4xl">
            {storeQ.data?.name ?? "Your store"}
          </h1>
          {storeQ.data && (
            <div className="mt-1 flex items-center gap-1 text-sm text-muted-foreground">
              <MapPin className="h-3.5 w-3.5" />
              {storeQ.data.address}, {storeQ.data.city} {storeQ.data.zip}
            </div>
          )}
        </div>
        <Button onClick={askStora} disabled={insightLoading}>
          <Sparkles className="h-4 w-4" />
          {insightLoading ? "Thinking…" : "Ask Stora"}
        </Button>
      </div>

      {insight && (
        <Card className="border-brand/30 bg-brand/5">
          <div className="flex items-start gap-3">
            <Sparkles className="mt-0.5 h-5 w-5 text-brand" />
            <div className="text-sm leading-relaxed whitespace-pre-wrap">{insight}</div>
          </div>
        </Card>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Workers"
          value={workers.length}
          hint="On the roster"
          icon={<Users className="h-4 w-4" />}
        />
        <StatCard
          label="Shift ending"
          value={shiftOverList.length}
          hint="Wrapping up soon"
          icon={<Clock className="h-4 w-4" />}
        />
        <StatCard
          label="Weather"
          value={wx ? `${Math.round(wx.temperature)}°F` : "—"}
          hint={wxLabel}
          icon={<WxIcon className="h-4 w-4" />}
        />
        <StatCard
          label="Wind"
          value={wx ? `${Math.round(wx.windspeed)} mph` : "—"}
          hint={storeQ.data?.city ? `In ${storeQ.data.city}` : "—"}
          icon={<Cloud className="h-4 w-4" />}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-display text-xl">Roster</h2>
            <span className="text-xs text-muted-foreground">
              {workers.length} worker{workers.length === 1 ? "" : "s"}
            </span>
          </div>
          {workersQ.isLoading ? (
            <p className="text-sm text-muted-foreground">Loading…</p>
          ) : workers.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No workers yet. Add your first hire from the Workers page.
            </p>
          ) : (
            <ul className="divide-y divide-border">
              {workers.slice(0, 6).map((w) => (
                <li key={w.id} className="flex items-center justify-between py-2 text-sm">
                  <span className="font-medium">{w.name}</span>
                  <span className="text-muted-foreground capitalize">{w.department}</span>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card>
          <h2 className="font-display text-xl">Shift ending soon</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Workers whose shift is wrapping up right now.
          </p>
          <div className="mt-4">
            {shiftOverQ.isLoading ? (
              <p className="text-sm text-muted-foreground">Loading…</p>
            ) : shiftOverList.length === 0 ? (
              <Alert>All clear — no shifts ending right now.</Alert>
            ) : (
              <ul className="divide-y divide-border">
                {shiftOverList.map((w) => (
                  <li
                    key={w.id}
                    className="flex items-center justify-between py-2 text-sm"
                  >
                    <span className="font-medium">{w.name}</span>
                    <span className="text-muted-foreground capitalize">{w.department}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
