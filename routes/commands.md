
---

# API Endpoint `curl` Requests

## @app.post("/stora/login")

```bash
curl -X POST http://localhost:8000/stora/login \
  -H "Content-Type: application/json" \
  -d '{
    "id": 8920501532,
    "password": "Newsecretpassword123"
  }'

```

## WORKS

✅

---

## @app.get("/stora/make")

> **Note:** FastAPI maps Pydantic models in `GET` requests to query parameters.



```bash
curl -X POST http://localhost:8000/stora/make \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Market Basket",
    "email": "marketbasket66666@gmail.com",
    "city": "boston",
    "address": "700 boston rd",
    "zip": 66666,
    "password": "MyGoodPassword123"
  }'

```

## WORKS

✅

---

## @app.get("/stora/forgot/id")

```bash
curl -X GET "http://localhost:8000/stora/forgot/id?email=marketbasket66666@gmail.com" \
  -H "Accept: application/json"

```

## WORKS

✅

---

## @app.get("/stora/forgot/password/{store_id}")

```bash
curl -X GET "http://localhost:8000/stora/forgot/password/8920501532?new_password=Newsecretpassword123" \
  -H "Accept: application/json"

```
## WORKS

✅

---

## @app.post("/stora/talk/{store_id}")

```bash
curl -X POST http://localhost:8000/stora/talk/8920501532 \
  -H "Content-Type: application/json"

```

## WORKS

✅

---

## @app.post("/stora/review/{store_id}")

```bash
curl -X POST http://localhost:8000/stora/review/8920501532 \
  -H "Content-Type: application/json"

```

## WORKS

✅

---

## @app.get("/stora/{store_id}")

```bash
curl -X GET http://localhost:8000/stora/8920501532 \
  -H "Accept: application/json"

```
## WORKS

✅



---

## @app.get("/workers/shift-over/{store_id}")

```bash

curl -X GET http://localhost:8000/workers/shift-over/8920501532 \
  -H "Accept: application/json"

```

## WORKS

✅

---

## @app.get("/workers")

```bash
curl -X GET http://localhost:8000/workers \
  -H "Accept: application/json"

```

## WORKS

✅

---

## @app.get("/workers/get/{worker_id}")

```bash
curl -X GET http://localhost:8000/workers/get/2333971677 \
  -H "Accept: application/json"

```

## WORKS

✅


---

## @app.get("/workers/get/all/{store_id}")

```bash
curl -X GET http://localhost:8000/workers/get/all/8920501532 \
  -H "Accept: application/json"

```

## WORKS

✅

---

## @app.post("/worker/add/{store_id}")

```bash
curl -X POST http://localhost:8000/worker/add/8920501532 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Julius Cylien",
    "department": "manager",
    "pay": 140000000
  }'

```

## WORKS

✅

---

## @app.delete("/worker/remove/{worker_id}")

```bash
curl -X DELETE http://localhost:8000/worker/remove/7272507764 \
  -H "Accept: application/json"

```

## WORKS

✅

---

## @app.post("/worker/schedule/{worker_id}")

```bash
curl -X POST http://localhost:8000/worker/schedule/2333971677 \
  -H "Content-Type: application/json" \
  -d '{
    "monday": {
      "shift_start": 8,
      "shift_end": 17,
      "is_off": false,
      "reason": ""
    },
    "tuesday": {
      "shift_start": 8,
      "shift_end": 17,
      "is_off": false,
      "reason": ""
    },
    "wednesday": {
      "shift_start": 8,
      "shift_end": 17,
      "is_off": false,
      "reason": ""
    },
    "thursday": {
      "shift_start": 8,
      "shift_end": 17,
      "is_off": false,
      "reason": ""
    },
    "friday": {
      "shift_start": 8,
      "shift_end": 17,
      "is_off": false,
      "reason": ""
    },
    "saturday": {
      "shift_start": 0,
      "shift_end": 0,
      "is_off": true,
      "reason": "break"
    },
    "sunday": {
      "shift_start": 0,
      "shift_end": 0,
      "is_off": true,
      "reason": "break"
    }
  }'

```

## WORKS

✅

---

## @app.patch("/worker/update/{worker_id}")

```bash
curl -X PATCH http://localhost:8000/worker/update/2333971677 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "department": "manager",
    "pay": 35.00
  }'


```

## WORKS

✅


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
      const res = await talkToStora(activeStoreId!);
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