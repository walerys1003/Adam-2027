# API Contracts · Adam Frontend ↔ Backend

**Base URL:** `https://api.silvertech.pl` (prod) · `http://localhost:3001` (dev)
**Auth:** Bearer JWT · `Authorization: Bearer <token>`
**Content-Type:** `application/json`
**Version:** v1

---

## 🔐 Autentykacja

### POST /api/auth/login

```json
Request:
{
  "email": "anna.chmielewska@gmail.com",
  "password": "•••••••••••",
  "otpCode": "123456"
}

Response 200:
{
  "accessToken": "eyJ...",
  "refreshToken": "eyJ...",
  "expiresIn": 900,
  "user": {
    "id": "u_abc123",
    "email": "anna.chmielewska@gmail.com",
    "role": "caregiver_primary" | "caregiver" | "coordinator" | "admin",
    "name": "Anna Chmielewska",
    "phoneVerified": true,
    "twoFactorEnabled": true,
    "createdAt": "2026-03-12T14:23:47Z"
  }
}
```

### POST /api/auth/refresh
### POST /api/auth/logout
### POST /api/auth/biometric-challenge (dla Face ID)

---

## 👥 Seniors (Panel Opiekuna)

### GET /api/seniors/mine

Lista seniorów przypisanych do zalogowanego opiekuna.

```json
Response:
{
  "seniors": [
    {
      "id": "HW-01247",
      "firstName": "Halina",
      "lastName": "Wójcik",
      "age": 78,
      "district": "Wilda",
      "package": "family",
      "semaphore": "green",
      "mood": 0.72,
      "adherence30d": 96,
      "heartRate": 72,
      "spo2": 97,
      "wearable": { "brand": "xiaomi", "model": "Band 8", "syncStatus": "ok" },
      "lastCall": { "at": "2026-07-12T08:14:00Z", "duration": 202 },
      "coordinator": null
    }
  ],
  "total": 3
}
```

### GET /api/seniors/:id
Pełny detail (z 8 tabów Panel Opiekuna widok seniora).

### GET /api/seniors/:id/mood?range=7d|14d|30d|90d
### GET /api/seniors/:id/calls?limit=20&offset=0
### GET /api/seniors/:id/medications
### GET /api/seniors/:id/alerts?limit=30
### GET /api/seniors/:id/reports
### WSS /ws/wearable/:seniorId (live vitals)

### POST /api/seniors/:id/contextual-notes
Opiekun dodaje soft context (nie edytuje progów).

```json
Request: { "note": "Mama chodzi na basen we wtorki 10-11" }
Response 201: { "id": "n_abc", "createdAt": "..." }
```

---

## 📦 Orders (Marketplace)

### GET /api/orders?status=active|history

### POST /api/orders

```json
Request:
{
  "seniorId": "HW-01247",
  "categoryId": "meds-delivery" | "groceries" | "taxi-med" | "doctor-home" | "nurse" | "cleaning" | "physio" | "repairs" | "appointment" | "psychology",
  "requestSource": "adam-call" | "caregiver-panel",
  "preferences": {
    "when": "2026-07-13T09:00:00Z",
    "notes": "Metformina 500mg · 1 opakowanie",
    "partnerId": "p_doz_wilda"    // opcjonalny · preferowany partner
  }
}

Response 201:
{
  "orderId": "O-8472",
  "status": "auto_confirmed" | "waiting_manual_confirm",
  "cancellationWindowEndsAt": "2026-07-12T14:52:07Z",  // ISO 8601, +30 min
  "partner": {
    "id": "p_doz_wilda",
    "name": "DOZ · Apteka św. Marcin",
    "nip": "7831234567",
    "ocValid": true,
    "rating": 4.8
  },
  "estimatedPrice": "34 zł",
  "estimatedDelivery": "45 min",
  "confirmedAt": null,
  "coordinator": null
}
```

### DELETE /api/orders/:id
Cancel — działa tylko w 30-min oknie.

```
Response 200 OK  if within window
Response 403 Forbidden { "error": "cancellation_window_expired" }
```

### GET /api/orders/:id/status (polling / SSE)

---

## 💬 Messages

### GET /api/messages?source=all|adam|coordinator|family|partner&status=all|unread

```json
Response:
{
  "messages": [
    {
      "id": "m_abc",
      "source": "adam",
      "sourceDetail": "welfare-morning v7.4.2",
      "category": "report" | "alert" | "order",
      "subject": "Wszystko dobrze u Twojej mamy",
      "preview": "Właśnie zakończyłem rozmowę z Twoją mamą...",
      "sentAt": "2026-07-12T08:20:00Z",
      "read": false,
      "relatedTo": { "type": "call", "id": "C-847288" }
    }
  ],
  "unreadCount": 4
}
```

### GET /api/messages/:id/thread
### POST /api/messages/:id/reply (dla wiadomości Adam — trafia do kontekstu)

---

## 📊 Reports

### GET /api/reports?limit=20
### GET /api/reports/:id (JSON summary)
### GET /api/reports/:id.pdf (application/pdf)
### GET /api/reports/:id.fhir (application/fhir+json — HL7 R4 Bundle)

### POST /api/reports/:id/send-to-doctor
```json
Request: { "doctorId": "dr_chmielewska_poz" }
Response 200: { "deliveredAt": "...", "readAt": null, "status": "delivered" }
```

### POST /api/reports/:id/share-link
```json
Response 201:
{
  "url": "https://adam.silvertech.pl/r/hw-2026-07-12/abc123def456",
  "expiresAt": "2026-08-11T14:22:07Z",  // 30 days default
  "viewCount": 0
}
```

---

## 🚨 Alerts (Semafor)

### GET /api/alerts/active
### GET /api/alerts/history?limit=50

### POST /api/alerts/:id/acknowledge
Rodzina potwierdza otrzymanie push (dla Purple wymagane do zatrzymania repeat).

### POST /api/alerts/:id/escalate
Manualnie eskaluj (koordynator z Panelu Admina).

---

## 📱 Wearables

### GET /api/wearables/mine (dla opiekuna — devices ich seniorów)

### PATCH /api/seniors/:id/wearable/thresholds
**⚠ TYLKO koordynator lub lekarz.** Opiekun NIE może wywołać (403).

```json
Request:
{
  "hrLow": 55,
  "hrHigh": 130,
  "reason": "Rozpoznana arytmia · konsultacja z lekarzem POZ 12.03",
  "verifiedBy": "dr_chmielewska_poz@fhir"
}

Response 200:
{
  "thresholds": { ... },
  "mode": "manual_override",
  "auditLog": {
    "id": "audit_87231",
    "userId": "coord_krzysztof",
    "sha256": "abc..."
  }
}
```

### WSS /ws/wearable/:seniorId

```
← {"type":"vitals","hr":72,"spo2":97,"steps":3247,"ts":"..."}
← {"type":"fall_detected","confidence":0.94,"accel":8.7,"ts":"..."}
← {"type":"threshold_breach","kind":"hr_high","value":126,"threshold":110}
← {"type":"battery_low","level":15}
← {"type":"offline","lastSeenAt":"..."}
```

---

## 👤 Account (Panel Opiekuna)

### GET /api/me
### PATCH /api/me
### GET /api/me/subscription
### POST /api/me/subscription/upgrade { "plan": "premium" }
### GET /api/me/invoices
### GET /api/me/sessions
### DELETE /api/me/sessions/:id
### GET /api/me/referral-link
### POST /api/me/gdpr/export-request → 202 Accepted (email w 30 dni)
### DELETE /api/me (soft delete + 30-day grace period)

---

## ⚙️ Admin API (Panel Admina)

### GET /api/admin/dashboard/metrics
### GET /api/admin/seniors?filters=... (pagination + filters)
### GET /api/admin/orders?filter=waiting_manual|auto_confirmed|all
### POST /api/admin/orders/:id/confirm (koordynator zatwierdza high-risk)
### POST /api/admin/orders/:id/reject { "reason": "..." }

### GET /api/admin/agents
### PUT /api/admin/agents/:id/prompt (YAML editor)
### POST /api/admin/agents/:id/deploy?target=prod|staging|ab

### GET /api/admin/providers
### GET /api/admin/providers/:name/health
### PUT /api/admin/providers/:name/config

### GET /api/admin/wearables/fleet
### PATCH /api/admin/wearables/thresholds/:seniorId (z powyższą walidacją audit)

### GET /api/admin/system/metrics
### GET /api/admin/system/containers
### POST /api/admin/system/containers/:name/restart

### GET /api/admin/logs?level=error,warn&category=call,provider (SSE)

---

## Error responses

```json
{
  "error": "cancellation_window_expired",
  "message": "Zamówienie można anulować tylko w ciągu 30 minut od złożenia",
  "code": 403,
  "requestId": "req_abc123",
  "timestamp": "2026-07-12T14:22:07Z"
}
```

**Standard error codes:**
- 400 `validation_error` — pola źle wypełnione
- 401 `unauthorized` — brak tokena
- 403 `forbidden` — brak uprawnień (np. opiekun edytuje progi)
- 404 `not_found`
- 409 `conflict` — np. senior już ma opiekuna głównego
- 429 `rate_limited` — retry after `Retry-After` header
- 500 `server_error` — Sentry alert

---

## Rate limiting

- Panel Opiekuna: 100 req/min per user
- Panel Admina: 500 req/min per user (data-dense views)
- Public endpoints (landing): 60 req/min per IP
- Auth: 5 login/godz. → captcha, 10 → blokada
- WebSocket: 1 połączenie per session

Header: `X-RateLimit-Remaining: 87` · `X-RateLimit-Reset: 1720795200`
