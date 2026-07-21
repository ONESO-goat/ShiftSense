import { useEffect, useState } from "react";

const KEY = "stora.store_id";

export function getStoredStoreId(): number | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(KEY);
  if (!raw) return null;
  const n = Number(raw);
  return Number.isFinite(n) ? n : null;
}

export function setStoredStoreId(id: number) {
  window.localStorage.setItem(KEY, String(id));
  window.dispatchEvent(new Event("stora-auth-change"));
}

export function clearStoredStoreId() {
  window.localStorage.removeItem(KEY);
  window.dispatchEvent(new Event("stora-auth-change"));
}

/** Reactive hook — returns storeId once hydrated. `null` = signed out. */
export function useStoreId(): { storeId: number | null; ready: boolean } {
  const [ready, setReady] = useState(false);
  const [storeId, setStoreId] = useState<number | null>(null);

  useEffect(() => {
    setStoreId(getStoredStoreId());
    setReady(true);
    const sync = () => setStoreId(getStoredStoreId());
    window.addEventListener("stora-auth-change", sync);
    window.addEventListener("storage", sync);
    return () => {
      window.removeEventListener("stora-auth-change", sync);
      window.removeEventListener("storage", sync);
    };
  }, []);

  return { storeId, ready };
}
