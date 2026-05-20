# Telegram WebApp Auth — Bot + React Integration

## Umumiy flow

```
User → /start bot → registratsiya (til, telefon)
Bot → "Ilovani ochish" tugmasi yuboradi
User bosadi → React Mini App ochiladi
React → initData → Django API
Django → HMAC verify → JWT qaytaradi
React → JWT saqlaydi → onboarding yoki home
```

---

## 1. Bot tomoni (allaqachon tayyor)

`apps/telegram_bot/handlers/start.py` da `contact_handler` tugagandan keyin:

```python
mini_app_kb = _mini_app_keyboard(lang)
if mini_app_kb:
    await message.answer(t("open_app", lang), reply_markup=mini_app_kb)
```

`MINI_APP_URL=https://bugunuz.vercel.app/` env var set qilingan → tugma shu URLni ochadi.

---

## 2. Django API endpoint

**URL:** `POST /api/auth/telegram-webapp/`

**Request:**
```json
{
  "init_data": "query_id=AAH...&user=%7B%22id%22...&hash=abc123"
}
```

**Response (muvaffaqiyatli):**
```json
{
  "access": "eyJhbGc...",
  "refresh": "eyJhbGc...",
  "needs_onboarding": true,
  "user": {
    "id": 1,
    "full_name": "Ali Valiyev",
    "is_organizer": false
  }
}
```

**needs_onboarding:** `true` → user telefon raqamini botda to'ldirmagan, onboardingga yo'naltir.

**Response (xato):**
```json
{ "init_data": ["invalid hash"] }
```

---

## 3. React tomoni

### 3.1 HTML ga Telegram SDK qo'sh

`index.html`:
```html
<script src="https://telegram.org/js/telegram-web-app.js"></script>
```

### 3.2 Auth hook

`src/hooks/useTelegramAuth.js`:
```javascript
import { useState, useEffect } from "react";

const API_BASE = "https://bugunuz.fly.dev";

export function useTelegramAuth() {
  const [status, setStatus] = useState("loading"); // loading | ok | error
  const [user, setUser] = useState(null);
  const [needsOnboarding, setNeedsOnboarding] = useState(false);

  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    if (!tg) {
      setStatus("error");
      return;
    }

    tg.ready();
    tg.expand();

    const initData = tg.initData;
    if (!initData) {
      setStatus("error");
      return;
    }

    fetch(`${API_BASE}/api/auth/telegram-webapp/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ init_data: initData }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.access) {
          localStorage.setItem("access", data.access);
          localStorage.setItem("refresh", data.refresh);
          setUser(data.user);
          setNeedsOnboarding(data.needs_onboarding);
          setStatus("ok");
        } else {
          setStatus("error");
        }
      })
      .catch(() => setStatus("error"));
  }, []);

  return { status, user, needsOnboarding };
}
```

### 3.3 App.jsx da ishlatish

```jsx
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useTelegramAuth } from "./hooks/useTelegramAuth";

export default function App() {
  const navigate = useNavigate();
  const { status, needsOnboarding } = useTelegramAuth();

  useEffect(() => {
    if (status === "ok") {
      navigate(needsOnboarding ? "/onboarding" : "/home");
    }
    if (status === "error") {
      navigate("/error");
    }
  }, [status]);

  if (status === "loading") return <div>Yuklanmoqda...</div>;
  return null;
}
```

### 3.4 API so'rovlarda JWT ishlatish

```javascript
// src/api/client.js
const API_BASE = "https://bugunuz.fly.dev";

export async function apiFetch(path, options = {}) {
  const access = localStorage.getItem("access");
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${access}`,
      ...options.headers,
    },
  });

  // Token muddati o'tgan bo'lsa refresh qil
  if (res.status === 401) {
    const refresh = localStorage.getItem("refresh");
    const refreshRes = await fetch(`${API_BASE}/api/auth/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    });
    if (refreshRes.ok) {
      const tokens = await refreshRes.json();
      localStorage.setItem("access", tokens.access);
      return apiFetch(path, options); // qayta urinish
    } else {
      localStorage.clear();
      window.location.reload();
    }
  }

  return res.json();
}
```

### 3.5 Onboarding sahifasi misol

```jsx
// src/pages/Onboarding.jsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../api/client";

export default function Onboarding() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ full_name: "", age: "", region: "" });

  const handleSubmit = async (e) => {
    e.preventDefault();
    await apiFetch("/api/auth/onboarding/", {
      method: "POST",
      body: JSON.stringify(form),
    });
    navigate("/home");
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        placeholder="Ism familiya"
        value={form.full_name}
        onChange={(e) => setForm({ ...form, full_name: e.target.value })}
      />
      <input
        placeholder="Yosh"
        type="number"
        value={form.age}
        onChange={(e) => setForm({ ...form, age: e.target.value })}
      />
      <button type="submit">Davom etish</button>
    </form>
  );
}
```

---

## 4. Vercel environment

`vercel.json` yoki `.env`:
```
VITE_API_BASE=https://bugunuz.fly.dev
```

---

## 5. CORS — Django ga qo'shish kerak

`requirements.txt` ga:
```
django-cors-headers>=4.3,<5.0
```

`settings.py` ga:
```python
INSTALLED_APPS = [
    ...
    "corsheaders",
    ...
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # eng birinchi bo'lishi kerak
    "django.middleware.security.SecurityMiddleware",
    ...
]

CORS_ALLOWED_ORIGINS = [
    "https://bugunuz.vercel.app",
]
```

---

## 6. Test qilish (localhost)

Telegram Mini App ni localhost da test qilish uchun ngrok kerak:

```bash
ngrok http 5173
```

BotFather → Bot Settings → Menu Button → URL → ngrok URL.

Yoki `@userinfobot` ga `/start` yuborib o'z `initData` ni simulyatsiya qilish uchun:
`https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app`

---

## API endpointlar xulosa

| Endpoint | Method | Auth | Maqsad |
|----------|--------|------|--------|
| `/api/auth/telegram-webapp/` | POST | Yo'q | initData → JWT |
| `/api/auth/refresh/` | POST | Yo'q | Token yangilash |
| `/api/auth/onboarding/` | POST | JWT | Profil to'ldirish |
| `/api/profile/me/` | GET | JWT | Profil olish |
| `/api/profile/me/` | PUT | JWT | Profil yangilash |
