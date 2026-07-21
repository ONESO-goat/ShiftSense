// Thin client for the Stora FastAPI backend.
// Override the base URL with VITE_STORA_API_URL (e.g. https://api.stora.example.com).

export const STORA_API_BASE =
  (import.meta.env.VITE_STORA_API_URL as string | undefined)?.replace(/\/$/, "") ??
  "http://localhost:8000";

async function request<T = unknown>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const res = await fetch(`${STORA_API_BASE}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      ...(init.body ? { "Content-Type": "application/json" } : {}),
      ...(init.headers ?? {}),
    },
  });
  const text = await res.text();
  let data: unknown = text;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      /* keep as text */
    }
  }
  if (!res.ok) {
    const msg =
      (data && typeof data === "object" && "detail" in data
        ? String((data as { detail: unknown }).detail)
        : typeof data === "string"
          ? data
          : `Request failed (${res.status})`) || `Request failed (${res.status})`;
    throw new Error(msg);
  }
  return data as T;
}

// ---------- Types ----------
export interface Store {
  id: number;
  name: string;
  email: string;
  city: string;
  address: string;
  zip: number;
  [key: string]: unknown;
}

export interface Worker {
  id: number;
  name: string;
  department: string;
  pay: number;
  store_id?: number;
  schedule?: Schedule;
  [key: string]: unknown;
}

export interface DayShift {
  shift_start: number;
  shift_end: number;
  is_off: boolean;
  reason: string;
}
export type DayKey =
  | "monday"
  | "tuesday"
  | "wednesday"
  | "thursday"
  | "friday"
  | "saturday"
  | "sunday";
export type Schedule = Record<DayKey, DayShift>;

// ---------- Auth ----------
export const loginStore = (id: number, password: string) =>
  request<{ ok?: boolean; store_id?: number; message?: string } & Record<string, unknown>>(
    "/stora/login",
    { method: "POST", body: JSON.stringify({ id, password }) },
  );

export const createStore = (payload: {
  name: string;
  email: string;
  city: string;
  address: string;
  zip: number;
  password: string;
}) =>
  request<{ id?: number; store_id?: number } & Record<string, unknown>>("/stora/make", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const forgotId = (email: string) =>
  request<{ id?: number; store_id?: number; message?: string } & Record<string, unknown>>(
    `/stora/forgot/id?email=${encodeURIComponent(email)}`,
  );

export const resetPassword = (storeId: number, newPassword: string) =>
  request<Record<string, unknown>>(
    `/stora/forgot/password/${storeId}?new_password=${encodeURIComponent(newPassword)}`,
  );

// ---------- Store ----------
export const getStore = (storeId: number) => request<Store>(`/stora/${storeId}`);

export const talkToStora = (storeId: number) =>
  request<{ response?: string; message?: string } & Record<string, unknown>>(
    `/stora/talk/${storeId}`,
    { method: "POST", headers: { "Content-Type": "application/json" } },
  );

export const requestReview = (storeId: number) =>
  request<{ review?: string; message?: string } & Record<string, unknown>>(
    `/stora/review/${storeId}`,
    { method: "POST", headers: { "Content-Type": "application/json" } },
  );

// ---------- Workers ----------
export const listAllWorkers = () => request<Worker[]>(`/workers`);
export const getWorker = (workerId: number) =>
  request<Worker>(`/workers/get/${workerId}`);
export const listStoreWorkers = (storeId: number) =>
  request<Worker[]>(`/workers/get/all/${storeId}`);
export const shiftOver = (storeId: number) =>
  request<Worker[] | Record<string, unknown>>(`/workers/shift-over/${storeId}`);

export const addWorker = (
  storeId: number,
  payload: { name: string; department: string; pay: number },
) =>
  request<Worker>(`/worker/add/${storeId}`, {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const removeWorker = (workerId: number) =>
  request<Record<string, unknown>>(`/worker/remove/${workerId}`, { method: "DELETE" });

export const updateWorker = (
  workerId: number,
  payload: Partial<{ name: string; department: string; pay: number }>,
) =>
  request<Worker>(`/worker/update/${workerId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });

export const setSchedule = (workerId: number, schedule: Schedule) =>
  request<Worker>(`/worker/schedule/${workerId}`, {
    method: "POST",
    body: JSON.stringify(schedule),
  });
