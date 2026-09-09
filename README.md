
# 🎬 Netflix Tudum — Django Web Application

## 🚀 Live Demo
👉 https://netflix-tudum.onrender.com

> Educational parody project. Not affiliated with, endorsed by, or connected to Netflix, Inc. in any way.

https://github.com/user-attachments/assets/1a28eac8-a70d-425b-864e-a8b8a051e135

## 📌 About the Project

**Netflix Tudum** is a Django-based practice project inspired by Netflix's browsing
experience: a database-backed show catalog, genre rows, a Top 10 list, live search,
a personal "My List" watchlist, and real user accounts — all wrapped in a
Netflix-style dark UI with Bootstrap 5.

---

## ✨ Features

- 🏠 Netflix-style browse page — hero banner, Top 10 row, 10 genre rows, all pulled from the database
- 🔎 Instant client-side search across the whole catalog (no page reload)
- 📌 "My List" watchlist, saved in the browser, with its own page
- 🔐 Real authentication — Register creates an actual account, Login/Logout work end-to-end
- ✉️ Contact & Feedback forms that save submissions to the database (visible in Django admin)
- 🖼️ 30 seeded titles across 10 genres, with cast, synopsis, match score, and maturity rating
- 🎨 Responsive, animated UI: hero rotator, hover previews, scroll reveals, toasts
- ☁️ Production-ready static file serving (WhiteNoise) — this is what actually fixes
  the broken/plain styling that shows up when deployed without it
- 🗄️ SQLite by default; optional Postgres support via `DATABASE_URL`

---

## 🛠️ Tech Stack

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, Bootstrap 5, vanilla JS
- **Database:** SQLite (default) / PostgreSQL (optional)
- **Static files:** WhiteNoise
- **Deployment:** Render + Gunicorn

---

## 📂 Project Structure

```
netflix-tudum/
├── build.sh                 # Render build script (install, collectstatic, migrate, seed)
├── render.yaml               # Optional Render Blueprint
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── home/
│   ├── models.py             # Show, Profile, ContactMessage, Feedback
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── management/commands/seed_shows.py   # re-runnable catalog seeder
│   ├── static/{css,js}
│   └── templates/
├── manage.py
├── requirements.txt
└── Procfile
```

---

## ⚙️ Local Installation

```bash
git clone https://github.com/Arjunkalliyadath/netflix-tudum.git
cd netflix-tudum

python -m venv venv
source venv/bin/activate   # venv\Scripts\activate on Windows

pip install -r requirements.txt
python manage.py migrate
python manage.py seed_shows      # loads the 30-title demo catalog
python manage.py createsuperuser # optional, for /admin/
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`.

---

## 🌐 Deployment (Render)

This is the part that fixes the broken styling you saw live: Render's default
Python setup does **not** automatically collect static files or run migrations,
so `style.css` never loaded and the auth tables never existed. Fix it with:

1. In your Render service settings, set:
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn config.wsgi:application`
2. Add an environment variable `DJANGO_DEBUG` = `False`.
3. (Recommended) Add a `SECRET_KEY` environment variable with a random value.
4. Redeploy. `build.sh` will install dependencies, collect static files,
   run migrations, and seed the show catalog automatically on every deploy.

`RENDER_EXTERNAL_HOSTNAME` (which Render sets automatically) is already trusted
for `ALLOWED_HOSTS` and CSRF, so Login/Register/Contact keep working over HTTPS.

> ⚠️ Render's free tier disk is **ephemeral** — SQLite data (registered users,
> contact messages, feedback) resets on every deploy/restart. For persistence,
> attach a free Render PostgreSQL database and Render will provide a
> `DATABASE_URL` environment variable, which this project picks up automatically.

### Procfile
```
web: gunicorn config.wsgi:application
```

---

## 🔄 Updating the Show Catalog

Add or edit titles in `home/management/commands/seed_shows.py`, then run:

```bash
python manage.py seed_shows
```

It's safe to re-run any time — existing titles are matched by slug and updated
in place rather than duplicated.

---

## 📊 Why This Project Matters (For Data Roles)

Although this is a web project, it demonstrates:

- 🔹 Backend data modeling & handling using the Django ORM
- 🔹 User data management, validation, and authentication
- 🔹 Structured, maintainable project design
- 🔹 Production deployment concerns (static files, environment config, CSRF)
- 🔹 Real-world, end-to-end application building

---

## 👨‍💻 Author

**Arjun K**
- GitHub: [@Arjunkalliyadath](https://github.com/Arjunkalliyadath)
- Email: arjunkalliyadath2001@gmail.com
