# 🌟 Intizom Bot — Kunlik Odatlar va Intizom Nazorati Telegram Boti

Zamonaviy, toza kodli (clean-code), to‘liq asinxron (`aiogram 3.x`, `aiosqlite`) Telegram boti. Bot foydalanuvchilarga kunlik odatlarini shakllantirish, har kunlik intizomiy chek-listni boshqarish va o‘z natijalari (foiz, streak) statistikasini kuzatib borish imkonini beradi.

---

## 📌 Asosiy Xususiyatlar

1. **🚀 Tezkor va Asinxron:** Python 3.10+, `aiogram 3.x` va `aiosqlite` yordamida yuqori tezlikda ishlaydi.
2. **📝 Qulay Vazifalar Kiritish (FSM):** 
   - Har bir vazifani alohida qatordan kiritish orqali 50 tagacha kunlik intizomiy vazifani bir zumda rejalashtirish.
   - Nomerlash (`1. `, `1) `, `- `) yoki ortiqcha belgilarni avtomatik tozalash.
3. **✅ Interaktiv Kunlik Chek-list:**
   - Har bir vazifa uchun holat ko‘rsatkichi: `⬜` (kutilmoqda), `✅` (bajarildi), `❌` (o‘tkazib yuborildi).
   - Vazifa tugmasini bosish orqali holatni ketma-ket almashtirish (toggle).
   - Bir bosishda belgilash uchun maxsus `✅` va `❌` harakat tugmalari.
   - Vazifalar ko‘p bo‘lsa, qulay sahifalash (pagination) mexanizmi.
4. **📊 Jonli Statistika va Natijalar:**
   - Bugungi bajarilish foizi va grafik progress bar (`🟩🟩🟩⬜⬜⬜ 50%`).
   - Ketma-ketlik kunlari (Streak) hisoblagichi.
   - Barcha vaqtlar bo‘yicha umumiy hisobotlar va motivatsion iqtiboslar.
5. **🛡️ Mustahkam Ma'lumotlar Bazasi (SQLite):**
   - Foydalanuvchilar (`users`), Vazifalar (`tasks`), Kunlik hisobotlar (`daily_logs`).
   - Bir kunda bitta vazifani takroriy belgilashning oldini oluvchi `UNIQUE(user_id, task_id, date)` cheklovi va `ON CONFLICT` avtomatik yangilash mexanizmi.

---

## 🗂️ Loyiha Strukturasi

```
abdulahat ustoz intizom.bot/
│
├── main.py                # Botni ishga tushirish (entry point), buyruqlar va dispatcher
├── config.py              # Konfiguratsiya (token, vaqt mintaqasi, limitlar)
├── database.py            # SQLite aiosqlite asinxron DB boshqaruvi
├── requirements.txt       # Bog‘liqliklar ro‘yxati
├── .env                   # Muhit o‘zgaruvchilari (token va sozlamalar)
├── .env.example           # Namuna .env fayli
├── README.md              # Loyiha qo‘llanmasi
│
├── handlers/              # Aiogram 3 routerlari
│   ├── __init__.py        # Routerlarni birlashtirish
│   ├── start.py           # /start, /help va asosiy menyu
│   ├── setup_tasks.py     # Vazifalarni kiritish (FSM State)
│   ├── checklist.py       # Kunlik chek-list, sahifalash va inline callbacklar
│   └── stats.py           # Statistika va hisobotlar
│
├── keyboards/             # Foydalanuvchi interfeysi tugmalari
│   ├── __init__.py
│   ├── reply.py           # Asosiy menyu (Reply Keyboard)
│   └── inline.py          # Chek-list va statistika (Inline Keyboard)
│
└── utils/                 # Yordamchi modullar
    ├── __init__.py
    └── helpers.py         # Matnlarni tozalash, progress bar, motivatsion iqtiboslar
```

---

## ⚙️ O‘rnatish va Ishga Tushirish

### 1. Bog‘liqliklarni o‘rnatish:
```bash
pip install -r requirements.txt
```

### 2. Sozlamalarni tekshirish (.env):
`.env` faylida bot tokeningiz to‘g‘ri kiritilganligiga ishonch hosil qiling:
```ini
BOT_TOKEN=8926148570:AAERLgNV9Fz6TElf6VqDOd-MeMsa8e-Z3IM
DB_NAME=database.sqlite3
TIMEZONE=Asia/Tashkent
```

### 3. Botni ishga tushirish:
```bash
python main.py
```

---

## 📱 Botdan Foydalanish

1. Telegramda botga kiring: **[@intizom_app_bot](https://t.me/intizom_app_bot)**
2. `/start` buyrug‘ini yuboring.
3. **«📝 Topshiriqlarni kiritish»** tugmasini bosing va o‘zingizning kunlik rejalaringizni alohida qatorlarda yozib yuboring.
4. **«✅ Kunlik Intizom Chek-list»** bo‘limida vazifalarni belgilab boring.
5. **«📊 Statistikam»** bo‘limida natijalaringizni kuzating.
