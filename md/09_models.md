# Database Models

---

## User

```python
User (AbstractUser'dan meros)
├── telegram_id         BigInteger  UNIQUE  # Telegram user ID
├── telegram_username   CharField           # @username (opsional)
├── full_name           CharField           # To'liq ism
├── avatar              URLField            # Telegram foto URL
├── age                 PositiveSmallInt    # Yosh
├── region              CharField           # Shahar/viloyat
├── phone_number        CharField           # Telefon raqam
├── language            CharField           # uz_latn/uz_cyrl/ru/en
├── show_telegram       Boolean  default=True
├── is_organizer        Boolean  default=False
├── total_attended      PositiveInt  default=0  # Qatnashgan eventlar (computed)
├── rating              Decimal(3,2) default=0  # O'rtacha baho (computed)
├── last_latitude       Decimal(9,6)  null=True  # Bot orqali saqlangan
├── last_longitude      Decimal(9,6)  null=True
├── created_at          DateTimeField auto_now_add
└── updated_at          DateTimeField auto_now
```

> `total_attended` va `rating` — o'zgartirish bo'lganda yangilanadi. DB'da saqlanadi.

---

## Category

```python
Category
├── title       CharField UNIQUE   # uz_latn (asosiy)
├── title_ru    CharField blank    # Ruscha
├── title_en    CharField blank    # Inglizcha
├── icon        CharField blank    # Emoji yoki icon nomi
└── color       CharField blank    # HEX rang kodi
```

> `uz_cyrl` → `title`dan `latin_to_cyrillic()` orqali dinamik hisoblanadi.

---

## Interest

```python
Interest
├── title       CharField UNIQUE
├── title_ru    CharField blank
├── title_en    CharField blank
└── icon        CharField blank

UserInterest
├── user        FK → User
└── interest    FK → Interest
UNIQUE(user, interest)
```

---

## Location

```python
Location
├── title       CharField
├── latitude    DecimalField(9,6)
├── longitude   DecimalField(9,6)
├── address     CharField blank
└── created_at  DateTimeField auto_now_add
```

---

## Event

```python
Event
├── organizer   FK → User (related_name: organized_events)
├── category    FK → Category
├── location    FK → Location
├── title       CharField(180)
├── description TextField
├── image       ImageField(upload_to='events/')  null=True
├── event_date  DateField
├── event_time  TimeField
├── total_seats PositiveInteger
├── status      CharField  # upcoming / completed / cancelled
├── is_draft    Boolean  default=False
├── reminder_sent Boolean default=False  # Celery task uchun
├── created_at  DateTimeField auto_now_add
└── updated_at  DateTimeField auto_now

# Computed properties (DB'da saqlanmaydi):
@property seats_left = total_seats - joined_count
@property joined_count = attendances.filter(status__in=['joined','attended']).count()
@property starts_at → datetime object
```

---

## Attendance

```python
Attendance
├── user        FK → User (related_name: attendances)
├── event       FK → Event (related_name: attendances)
├── status      CharField  # joined / attended / cancelled
└── joined_at   DateTimeField auto_now_add

UNIQUE(user, event)
```

---

## WaitingList

```python
WaitingList
├── user        FK → User (related_name: waiting_entries)
├── event       FK → Event (related_name: waiting_list)
└── created_at  DateTimeField auto_now_add

UNIQUE(user, event)
Ordering: created_at ASC  # FIFO — birinchi kelgan birinchi chiqadi
```

---

## OrganizerApplication

```python
OrganizerApplication
├── user        FK → User (related_name: organizer_applications)
├── message     TextField
├── status      CharField  # pending / approved / rejected
└── created_at  DateTimeField auto_now_add
```

---

## Rating

```python
Rating
├── from_user   FK → User (related_name: ratings_given)
├── to_user     FK → User (related_name: ratings_received)
├── event       FK → Event (related_name: ratings)
├── stars       PositiveSmallInt (1-5)
└── created_at  DateTimeField auto_now_add

UNIQUE(from_user, to_user, event)
```

---

## Report

```python
Report
├── reporter    FK → User (related_name: reports_sent)
├── target_user FK → User (related_name: reports_received)
├── message     TextField
└── created_at  DateTimeField auto_now_add
```

---

## Achievement

```python
Achievement
├── title       CharField UNIQUE
├── icon        CharField blank
└── description TextField blank

UserAchievement
├── user        FK → User (related_name: user_achievements)
├── achievement FK → Achievement
└── created_at  DateTimeField auto_now_add

UNIQUE(user, achievement)
```

---

## Muhim Qoidalar

### seats_left hech qachon DB'da saqlanmaydi
```python
# Model property orqali:
event.seats_left = event.total_seats - event.attendances.filter(...).count()
```

### user_history alohida jadval emas
```python
# Attendance va Event'dan quriladi:
Attendance.objects.filter(user=user).select_related('event')
```

### Attendance unique_together
```python
# Bir user bir eventga faqat bir marta (status: joined/attended/cancelled)
# Qaytib qo'shilishda: cancelled bo'lgan entry update qilinadi
```

### WaitingList FIFO
```python
# created_at bo'yicha tartiblangan
# Kimdir chiqsa → birinchi waiting user avtomatik joined'ga o'tadi
```
