# Malka Money — Personal Wealth Management

Full-stack MVP with a FastAPI backend and a React + Tailwind frontend. Tracks accounts, transactions, budgets, net worth, and reports with features like Shabbat Mode, Tzedakah, Maaser calculator, and holiday reminders.

## Tech Stack
- Backend: FastAPI, SQLAlchemy, SQLite (MVP), JWT auth
- Frontend: React (Vite), TailwindCSS, react-chartjs-2

## Quick Start (Windows PowerShell)

### 1) Backend
1. Create and activate a virtual environment
```
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```
2. Install dependencies
```
pip install -r backend/requirements.txt
```
3. Run the server
```
uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000
```
The API will be available at http://localhost:8000 and docs at http://localhost:8000/docs

Environment variables (optional) can be set via a `.env` file in `backend/`:
```
SECRET_KEY=change-me
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALGORITHM=HS256
SQLALCHEMY_DATABASE_URI=sqlite:///./app.db
BACKEND_CORS_ORIGINS=http://localhost:5173
DEFAULT_LAT=31.778
DEFAULT_LON=35.235
DEFAULT_TZ=Asia/Jerusalem
```

### 2) Frontend
1. Install Node deps
```
cd frontend; npm install
```
2. Start the dev server
```
npm run dev
```
Open http://localhost:5173

### Default Categories
- Income
- Tzedakah (expense)
- Cash, Savings, Credit Card, Loan (account types)

## Notes
- Shabbat Mode: When enabled in Settings, the app prevents modifying financial data from Friday sundown to Saturday nightfall (approx sunset + 40m), based on user location/timezone or default to Jerusalem.
- Holidays: Uses Hebcal if available; otherwise shows a simple local list.
- SQLite for dev; switch `SQLALCHEMY_DATABASE_URI` to PostgreSQL for prod.
