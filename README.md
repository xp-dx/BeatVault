
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
│   │   │   ├── __pycache__
│   │   │   │   ├── crud.cpython-312.pyc
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── router.cpython-312.pyc
│   │   │   │   └── service.cpython-312.pyc
│   │   │   ├── router.py
│   │   │   └── service.py
│   │   ├── albums
│   │   │   ├── constants.py
│   │   │   ├── crud.py
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── constants.cpython-312.pyc
│   │   │   │   ├── crud.cpython-312.pyc
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── router.cpython-312.pyc
│   │   │   │   ├── schemas.cpython-312.pyc
│   │   │   │   └── service.cpython-312.pyc
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── auth
│   │   │   ├── config.py
│   │   │   ├── constants.py
│   │   │   ├── crud.py
│   │   │   ├── dependencies.py
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── config.cpython-312.pyc
│   │   │   │   ├── constants.cpython-312.pyc
│   │   │   │   ├── crud.cpython-312.pyc
│   │   │   │   ├── dependencies.cpython-312.pyc
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── router.cpython-312.pyc
│   │   │   │   ├── schemas.cpython-312.pyc
│   │   │   │   └── service.cpython-312.pyc
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── celery
│   │   │   ├── celery_app.py
│   │   │   ├── email
│   │   │   │   ├── dependencies.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── __pycache__
│   │   │   │   │   ├── dependencies.cpython-312.pyc
│   │   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   │   ├── service.cpython-312.pyc
│   │   │   │   │   └── tasks.cpython-312.pyc
│   │   │   │   ├── service.py
│   │   │   │   └── tasks.py
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── celery_app.cpython-312.pyc
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── redis.cpython-312.pyc
│   │   │   │   ├── redis_manager.cpython-312.pyc
│   │   │   │   ├── tasks.cpython-312.pyc
│   │   │   │   └── utils.cpython-312.pyc
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
│   │   │   ├── __pycache__
│   │   │   │   ├── config.cpython-312.pyc
│   │   │   │   ├── crud.cpython-312.pyc
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── router.cpython-312.pyc
│   │   │   │   ├── schemas.cpython-312.pyc
│   │   │   │   └── service.cpython-312.pyc
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   ├── __pycache__
│   │   │   ├── config.cpython-312.pyc
│   │   │   ├── database.cpython-312.pyc
│   │   │   ├── dependencies.cpython-312.pyc
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── main.cpython-312.pyc
│   │   │   ├── models.cpython-312.pyc
│   │   │   ├── schemas.cpython-312.pyc
│   │   │   └── services.cpython-312.pyc
│   │   ├── services.py
│   │   ├── songs
│   │   │   ├── constants.py
│   │   │   ├── crud.py
│   │   │   ├── __init__.py
│   │   │   ├── __pycache__
│   │   │   │   ├── constants.cpython-312.pyc
│   │   │   │   ├── crud.cpython-312.pyc
│   │   │   │   ├── __init__.cpython-312.pyc
│   │   │   │   ├── router.cpython-312.pyc
│   │   │   │   ├── schemas.cpython-312.pyc
│   │   │   │   └── service.cpython-312.pyc
│   │   │   ├── router.py
│   │   │   ├── schemas.py
│   │   │   └── service.py
│   │   └── users
│   │       ├── crud.py
│   │       ├── __init__.py
│   │       ├── __pycache__
│   │       │   ├── crud.cpython-312.pyc
│   │       │   ├── __init__.cpython-312.pyc
│   │       │   └── router.cpython-312.pyc
│   │       └── router.py
│   ├── test.py
│   └── tests
│       ├── __init__.py
│       ├── __pycache__
│       │   ├── __init__.cpython-312.pyc
│       │   └── test_auth.cpython-312-pytest-8.3.5.pyc
│       └── test_auth.py
└── README.md
```

## ✅ To Do

- Store uploaded audio in cloud
- Invoice and email receipt system
- Advanced search and filtering
- Unit and integration testing