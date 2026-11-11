# Face Log

Yuz orqali davomat ilovasi. Foydalanuvchi o'z rasmini yuklaydi, admin uni tasdiqlaydi. Shundan keyin ilova kamera orqali foydalanuvchining yuzini taniydi va uning **kelgan va ketgan vaqtini** yozib boradi.

> **Holat:** ishlab chiqilmoqda. Ro'yxatdan o'tish, rasm yuklash va adminning rasmni tasdiqlashi tayyor. Yuzni tanish va davomat hali yozilmagan, profildagi "Davomatdan o'tish" tugmasi hozircha hech narsa qilmaydi.

## Qanday ishlaydi

1. Foydalanuvchi ro'yxatdan o'tadi (ism, familiya, username, parol).
2. Profil sahifasida o'z yuzining rasmini yuklaydi. Rasm holati **Kutilmoqda** bo'ladi.
3. Admin rasmni ko'rib chiqadi va uni **tasdiqlaydi** yoki sababini yozib **bekor qiladi**.
4. Rasm bekor qilinsa, foydalanuvchi sababni profilida ko'radi va yangi rasm yuklaydi.
5. Rasm tasdiqlangandan keyin "Davomatdan o'tish" tugmasi faollashadi. Ilova yuzni taniydi va kelgan yoki ketgan vaqtni yozadi *(rejada)*.

### Rasm qoidalari

- Rasm hajmi 50 MB dan oshmasligi kerak.
- Rasm holati **Kutilmoqda** yoki **Tasdiqlangan** bo'lsa, uni almashtirib ham, o'chirib ham bo'lmaydi.
- Yangi rasmni faqat admin oldingisini bekor qilgandan keyin yuklash mumkin.

## Texnologiyalar

- Python 3.12 yoki yangisi (3.13 da sinovdan o'tgan)
- Django 6.1
- Pillow (rasmlar bilan ishlash uchun)
- python-dotenv (sozlamalarni `.env` dan o'qish uchun)
- SQLite (standart), PostgreSQL'ga `.env` orqali o'tiladi

## O'rnatish

```bash
git clone <repo-url> face-log
cd face-log

python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
```

`.env` faylidagi `SECRET_KEY` ni yangi kalit bilan almashtiring:

```bash
python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
```

Bazani yarating, admin qo'shing va serverni ishga tushiring:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Sayt http://127.0.0.1:8000 manzilida, admin panel esa http://127.0.0.1:8000/admin/ manzilida ochiladi.

## Sozlamalar (`.env`)

| O'zgaruvchi | Vazifasi | Misol |
|---|---|---|
| `SECRET_KEY` | Django maxfiy kaliti (majburiy) | — |
| `DEBUG` | Ishlab chiqish rejimi | `True` |
| `ALLOWED_HOSTS` | Ruxsat etilgan domenlar, vergul bilan | `localhost,127.0.0.1` |
| `CSRF_TRUSTED_ORIGINS` | HTTPS domenlar (production uchun) | `https://example.com` |
| `DB_ENGINE` | Baza turi | `django.db.backends.sqlite3` |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Baza ulanishi | — |

`.env` git'ga tushmaydi. Namunasi `.env.example` faylida.

## Sahifalar

| URL | Sahifa |
|---|---|
| `/register/` | Ro'yxatdan o'tish |
| `/login/` | Kirish |
| `/logout/` | Chiqish (faqat POST, menyudagi tugma orqali) |
| `/profile/` | Profil: rasm yuklash, rasm holati, davomat tugmasi |
| `/admin/` | Admin panel: rasmlarni tasdiqlash yoki bekor qilish |

## Testlar

```bash
python manage.py test accounts
```

## Loyiha tuzilmasi

```
face-log/
├── accounts/              # foydalanuvchilar: model, formalar, view'lar, admin
│   ├── models.py          # User modeli (rasm, rasm holati, bekor qilish sababi)
│   ├── views.py           # register, login, logout, profile (class-based)
│   ├── forms.py
│   ├── admin.py
│   ├── validators.py      # rasm hajmi limiti (50 MB)
│   └── password_validation.py
├── root/                  # Django sozlamalari va asosiy URL'lar
├── templates/             # HTML shablonlar
├── static/                # CSS, JS, rasmlar
├── media/                 # yuklangan rasmlar (git'ga tushmaydi)
├── .env.example
└── requirements.txt
```

## Rejalar

- [ ] Kamera orqali yuzni tanish
- [ ] Kelgan va ketgan vaqtni yozish
- [ ] Davomat tarixi va hisobotlar
