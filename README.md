# BOO 키우기

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# if app.db already exists from old local runs: rm app.db
alembic upgrade head
uvicorn app.main:app --reload
http://127.0.0.1:8000/docs
```

## Key APIs
- `POST /auth/signup`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `GET /users/me`
- `GET /quiz/questions`
- `POST /quiz/submit`
- `GET /meals/availability`
- `POST /meals/feed`
- `GET /boo/state`
