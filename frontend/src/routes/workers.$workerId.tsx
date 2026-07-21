import { createFileRoute, Link, useParams } from "@tanstack/react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { RequireAuth } from "@/components/AppShell";
import {
  getWorker,
  setSchedule,
  updateWorker,
  type DayKey,
  type Schedule,
} from "@/lib/stora-api";
import { Alert, Button, Card, Field, Input } from "@/components/ui-bits";

export const Route = createFileRoute("/workers/$workerId")({
  component: () => (
    <RequireAuth>
      <WorkerDetail />
    </RequireAuth>
  ),
  head: () => ({ meta: [{ title: "Worker — Stora" }] }),
});

const DAYS: DayKey[] = [
  "monday",
  "tuesday",
  "wednesday",
  "thursday",
  "friday",
  "saturday",
  "sunday",
];

const emptySchedule = (): Schedule =>
  Object.fromEntries(
    DAYS.map((d) => [d, { shift_start: 9, shift_end: 17, is_off: false, reason: "" }]),
  ) as Schedule;

function WorkerDetail() {
  const { workerId } = useParams({ from: "/workers/$workerId" });
  const id = Number(workerId);
  const qc = useQueryClient();

  const q = useQuery({ queryKey: ["worker", id], queryFn: () => getWorker(id) });

  const [profile, setProfile] = useState({ name: "", department: "", pay: "" });
  const [schedule, setLocalSchedule] = useState<Schedule>(emptySchedule());
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (q.data) {
      setProfile({
        name: q.data.name ?? "",
        department: q.data.department ?? "",
        pay: String(q.data.pay ?? ""),
      });
      if (q.data.schedule) setLocalSchedule({ ...emptySchedule(), ...q.data.schedule });
    }
  }, [q.data]);

  const updateMut = useMutation({
    mutationFn: () =>
      updateWorker(id, {
        name: profile.name,
        department: profile.department,
        pay: Number(profile.pay),
      }),
    onSuccess: () => {
      setMsg("Profile saved.");
      qc.invalidateQueries({ queryKey: ["worker", id] });
    },
    onError: (e) => setErr(e instanceof Error ? e.message : "Update failed"),
  });

  const scheduleMut = useMutation({
    mutationFn: () => setSchedule(id, schedule),
    onSuccess: () => {
      setMsg("Schedule saved.");
      qc.invalidateQueries({ queryKey: ["worker", id] });
    },
    onError: (e) => setErr(e instanceof Error ? e.message : "Schedule save failed"),
  });

  function updateDay<K extends keyof Schedule[DayKey]>(
    day: DayKey,
    key: K,
    value: Schedule[DayKey][K],
  ) {
    setLocalSchedule((s) => ({ ...s, [day]: { ...s[day], [key]: value } }));
  }

  return (
    <div className="space-y-6">
      <Link to="/workers" className="text-sm text-muted-foreground hover:text-foreground">
        ← All workers
      </Link>

      {q.isLoading ? (
        <p className="text-sm text-muted-foreground">Loading…</p>
      ) : q.isError ? (
        <Alert tone="error">Couldn't load worker.</Alert>
      ) : (
        <>
          <div>
            <div className="text-xs uppercase tracking-widest text-muted-foreground">
              Worker
            </div>
            <h1 className="font-display text-4xl">{q.data?.name}</h1>
            <p className="text-sm text-muted-foreground">ID · {id}</p>
          </div>

          {msg && <Alert tone="success">{msg}</Alert>}
          {err && <Alert tone="error">{err}</Alert>}

          <Card>
            <h2 className="font-display text-xl">Profile</h2>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                setMsg(null);
                setErr(null);
                updateMut.mutate();
              }}
              className="mt-4 grid gap-4 sm:grid-cols-3"
            >
              <Field label="Name">
                <Input
                  value={profile.name}
                  onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                  required
                />
              </Field>
              <Field label="Department">
                <Input
                  value={profile.department}
                  onChange={(e) =>
                    setProfile({ ...profile, department: e.target.value })
                  }
                  required
                />
              </Field>
              <Field label="Pay">
                <Input
                  inputMode="numeric"
                  value={profile.pay}
                  onChange={(e) => setProfile({ ...profile, pay: e.target.value })}
                  required
                />
              </Field>
              <div className="sm:col-span-3">
                <Button type="submit" disabled={updateMut.isPending}>
                  {updateMut.isPending ? "Saving…" : "Save profile"}
                </Button>
              </div>
            </form>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <h2 className="font-display text-xl">Weekly schedule</h2>
              <Button
                onClick={() => {
                  setMsg(null);
                  setErr(null);
                  scheduleMut.mutate();
                }}
                disabled={scheduleMut.isPending}
              >
                {scheduleMut.isPending ? "Saving…" : "Save schedule"}
              </Button>
            </div>

            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="text-xs uppercase text-muted-foreground">
                  <tr>
                    <th className="py-2 text-left">Day</th>
                    <th className="py-2 text-left">Off</th>
                    <th className="py-2 text-left">Start</th>
                    <th className="py-2 text-left">End</th>
                    <th className="py-2 text-left">Reason</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {DAYS.map((day) => {
                    const d = schedule[day];
                    return (
                      <tr key={day}>
                        <td className="py-2 pr-3 font-medium capitalize">{day}</td>
                        <td className="py-2 pr-3">
                          <input
                            type="checkbox"
                            checked={d.is_off}
                            onChange={(e) => updateDay(day, "is_off", e.target.checked)}
                          />
                        </td>
                        <td className="py-2 pr-3">
                          <Input
                            type="number"
                            min={0}
                            max={23}
                            value={d.shift_start}
                            disabled={d.is_off}
                            onChange={(e) =>
                              updateDay(day, "shift_start", Number(e.target.value))
                            }
                            className="w-20"
                          />
                        </td>
                        <td className="py-2 pr-3">
                          <Input
                            type="number"
                            min={0}
                            max={23}
                            value={d.shift_end}
                            disabled={d.is_off}
                            onChange={(e) =>
                              updateDay(day, "shift_end", Number(e.target.value))
                            }
                            className="w-20"
                          />
                        </td>
                        <td className="py-2">
                          <Input
                            value={d.reason}
                            placeholder={d.is_off ? "e.g. break" : ""}
                            onChange={(e) => updateDay(day, "reason", e.target.value)}
                          />
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Card>
        </>
      )}
    </div>
  );
}
