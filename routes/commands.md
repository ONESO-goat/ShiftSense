
---

# API Endpoint `curl` Requests

## @app.post("/stora/login")

```bash
curl -X POST http://localhost:8000/stora/login \
  -H "Content-Type: application/json" \
  -d '{
    "id": 3158418655,
    "password": "MyGoodPassword123"
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
curl -X GET "http://localhost:8000/stora/forgot/id?name=MyStore&location=MainSt" \
  -H "Accept: application/json"

```

---

## @app.get("/stora/forgot/password/{store_id}")

```bash
curl -X GET "http://localhost:8000/stora/forgot/password/1?new_password=newsecretpassword" \
  -H "Accept: application/json"

```

---

## @app.post("/stora/talk/{store_id}")

```bash
curl -X POST http://localhost:8000/stora/talk/3158418655 \
  -H "Content-Type: application/json"

```

---

## @app.post("/stora/review")

```bash
curl -X POST http://localhost:8000/stora/review \
  -H "Content-Type: application/json"

```

---

## @app.get("/stora/{store_id}")

```bash
curl -X GET http://localhost:8000/stora/1 \
  -H "Accept: application/json"

```

---

## @app.post("/stora/listen")

```bash
curl -X POST http://localhost:8000/stora/listen \
  -H "Content-Type: application/json"

```

---

## @app.get("/workers/shift-over")

```bash
curl -X GET http://localhost:8000/workers/shift-over \
  -H "Accept: application/json"

```

---

## @app.get("/workers")

```bash
curl -X GET http://localhost:8000/workers \
  -H "Accept: application/json"

```

---

## @app.get("/workers/get/{worker_id}")

```bash
curl -X GET http://localhost:8000/workers/1 \
  -H "Accept: application/json"

```
---

## @app.get("/workers/get/all/{store_id}")

```bash
curl -X GET http://localhost:8000/workers/1 \
  -H "Accept: application/json"

```
---

## @app.post("/worker/add/{store_id}")

```bash
curl -X POST http://localhost:8000/worker/add/3158418655 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe",
    "department": "sales",
    "pay": 25.50
  }'

```

---

## @app.delete("/worker/remove/{worker_id}")

```bash
curl -X DELETE http://localhost:8000/worker/remove/1 \
  -H "Accept: application/json"

```

---

## @app.post("/worker/schedule/{worker_id}")

```bash
curl -X POST http://localhost:8000/worker/schedule/1 \
  -H "Content-Type: application/json" \
  -d '{
    "worker_id": 1,
    "shifts": []
  }'

```

---

## @app.patch("/worker/update/{worker_id}")

```bash
curl -X PATCH http://localhost:8000/worker/update/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "department": "Management",
    "pay": 35.00
  }'

```