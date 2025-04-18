
---

# 🎵 BeatVault

A pet project for buying and selling music, built with modern Python technologies.

## 🚀 Tech Stack

- **FastAPI** – high-performance web framework for building APIs  
- **PostgreSQL** – relational database for storing users, tracks, orders, etc.  
- **SQLAlchemy** (async) – ORM for working with the database  
- **Pydantic** – data validation and settings management  
- **Alembic** – database migrations management  
- **Docker** – containerization for easy deployment  
- **Stripe** – payment gateway integration  
- **Celery** – background task processing
- **Redis** – message broker for Celery tasks
- **AsyncIO** – for scalable and non-blocking operations

## 💡 Features

- User registration and authentication  
- View user profiles
- Upload music tracks
- Add and view track descriptions
- Stream music directly from the server
- Purchase tracks securely via Stripe
- Download purchased tracks
- Create and manage music albums
- Background tasks (email confirmation)
- Admin functionality

## 📂 Project Structure

```
.
├── backend
│   ├── alembic
│   │   ├── env.py
│   │   ├── README
│   │   └── script.py.mako
│   ├── alembic.ini
│   ├── compose.yaml
│   ├── data
│   │   └── cat.gif
│   ├── Dockerfile
│   ├── README.Docker.md
│   ├── requirements.txt
│   ├── src
│   │   ├── admin
│   │   │   ├── crud.py
│   │   │   ├── dependecies.py
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   └── service.py
│   │   ├── albums
│   │   │   ├── constants.py
│   │   │   ├── crud.py
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── auth
│   │   │   ├── config.py
│   │   │   ├── constants.py
│   │   │   ├── crud.py
│   │   │   ├── dependencies.py
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── celery
│   │   │   ├── celery_app.py
│   │   │   ├── email
│   │   │   │   ├── dependencies.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── service.py
│   │   │   │   └── tasks.py
│   │   │   ├── __init__.py
│   │   │   ├── redis_manager.py
│   │   │   └── worker.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── payments
│   │   │   ├── config.py
│   │   │   ├── crud.py
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── services.py
│   │   ├── songs
│   │   │   ├── constants.py
│   │   │   ├── crud.py
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   └── users
│   │       ├── crud.py
│   │       ├── __init__.py
│   │       └── router.py
│   ├── test.py
│   └── tests
│       ├── __init__.py
│       └── test_auth.py
└── README.md
```

## ✅ To Do

- Store uploaded audio in cloud
- Invoice and email receipt system
- Advanced search and filtering
- Unit and integration testing