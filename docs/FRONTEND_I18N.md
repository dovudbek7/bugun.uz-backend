# Frontend — Til (i18n) integratsiyasi

Backend endi javoblarni foydalanuvchi tiliga moslab qaytaradi. Frontend
**har bir so'rovda** tilni `Accept-Language` header orqali yuboradi. Field
nomlari **o'zgarmaydi** — `description`, `name`, `title` o'sha-o'sha qoladi,
faqat qiymati tanlangan tilda keladi.

## 1. Header

Har bir API so'roviga shu header qo'shiladi:

```
Accept-Language: <lang>
```

Qo'llab-quvvatlanadigan qiymatlar (User.language bilan bir xil):

| Qiymat     | Til                |
|------------|--------------------|
| `uz_latn`  | O'zbekcha (lotin)  |
| `uz_cyrl`  | O'zbekcha (kirill) |
| `ru`       | Ruscha             |
| `en`       | Inglizcha          |

Qisqa variantlar ham normalize qilinadi: `uz` → `uz_latn`, `uz-Cyrl` →
`uz_cyrl`, `en-US` → `en`. Lekin **tavsiya** — to'liq kodni yuboring
(`uz_latn`, `uz_cyrl`, `ru`, `en`).

## 2. Sozlash (bir marta)

Til o'zgarganda header global o'rnatiladi.

### Axios
```js
import axios from "axios";

export const api = axios.create({ baseURL: "https://api.bugun.uz" });

// til o'zgarganda chaqir
export function setLanguage(lang) {
  api.defaults.headers.common["Accept-Language"] = lang; // "uz_latn" | "uz_cyrl" | "ru" | "en"
  localStorage.setItem("lang", lang);
}

// ilova ochilganda
setLanguage(localStorage.getItem("lang") || "uz_latn");
```

### Fetch
```js
function apiFetch(url, options = {}) {
  const lang = localStorage.getItem("lang") || "uz_latn";
  return fetch(url, {
    ...options,
    headers: { ...(options.headers || {}), "Accept-Language": lang },
  });
}
```

## 3. Javob nimaga o'zgaradi

Field nomlari o'zgarmaydi — qiymat tilga mos keladi.

### Event (`GET /api/events/`, `GET /api/events/{id}/`)
```jsonc
// Accept-Language: ru
{
  "id": 42,
  "title": "...",
  "description": "Состоится встреча разработчиков...",  // <- tanlangan tilda
  "category": { "id": 3, "name": "Онлайн шахматы" }      // <- kategoriya ham
}
```
```jsonc
// Accept-Language: en
{
  "description": "A developers meetup will take place...",
  "category": { "id": 3, "name": "Online chess" }
}
```

### Category (`GET /api/categories/`)
- `name` → tanlangan tilda
- `title_ru`, `title_en` ham javobda bor (kerak bo'lsa), lekin asosiy field — `name`

### Interest (`GET /api/interests/`)
- `title` → tanlangan tilda

## 4. Muhim xulq-atvor

- **Bitta field:** frontend `description_ru` / `description_en` bilan ishlamaydi.
  Faqat `description` (yo `name` / `title`) o'qiydi. Til header bilan boshqariladi.
- **Fallback:** tarjima hali tayyor bo'lmasa yoki bo'sh bo'lsa → kanonik
  `uz_latn` qiymat qaytadi (hech qachon bo'sh kelmaydi).
- **Kirill avtomatik:** `uz_cyrl` so'ralganda backend lotin'dan generatsiya
  qiladi — alohida saqlanmaydi, lekin frontend uchun farqi yo'q.
- **Tarjima kechikishi:** yangi event yaratilganda tarjima fonда (Celery)
  bo'ladi, bir necha soniya olishi mumkin. Shu oraliqda `ru`/`en` so'ralsa
  ham `uz_latn` fallback keladi, keyin to'liq tarjima paydo bo'ladi.

## 5. Til tanlash (UI)

Foydalanuvchi tilni almashtirsa:
1. `setLanguage(newLang)` chaqir (header + localStorage yangilanadi)
2. Joriy ekrandagi ma'lumotlarni qayta yukla (refetch) — yangi tilda keladi

Misol (React):
```jsx
function LangSwitcher() {
  const onChange = (lang) => {
    setLanguage(lang);
    queryClient.invalidateQueries(); // react-query: hammasini qayta yukla
  };
  return (
    <select onChange={(e) => onChange(e.target.value)} defaultValue={localStorage.getItem("lang") || "uz_latn"}>
      <option value="uz_latn">O'zbekcha</option>
      <option value="uz_cyrl">Ўзбекча</option>
      <option value="ru">Русский</option>
      <option value="en">English</option>
    </select>
  );
}
```

## 6. POST/PUT (yozish)

Event yaratish/tahrirlashda `description` **bitta** matn sifatida yuboriladi
(istalgan tilda — backend AI bilan avtomatik 3 tilga tarjima qiladi). Frontend
ko'p tilli input qilmaydi:
```jsonc
POST /api/events/
{ "title": "...", "description": "Foydalanuvchi yozган matn", ... }
```
Tarjima backend tomonda avtomatik bo'ladi (Accept-Language bu yerda muhim emas).
