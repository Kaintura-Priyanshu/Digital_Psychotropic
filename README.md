
# Police Intel Suite

##  Local Development Setup

Follow the steps below to run the **Police Intel Suite** backend and frontend locally.

### Prerequisites

Make sure you have the following installed:

* Python 3.x
* Node.js & npm
* Git

---

##  Backend Setup

Open **Terminal 1** and run:

```bash
cd police-intel-suite-backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt

# Start FastAPI development server
uvicorn app.main:app --reload --port 8000
```

The backend will be available at:

```text
http://localhost:8000
```

---

##  Frontend Setup

Open **Terminal 2** and run:

```bash
cd police-intel-suite

# Create local environment file
cp .env.local.example .env.local

# Install dependencies and start development server
npm install
npm run dev
```

The frontend will be available at the URL shown in your terminal, typically:

```text
http://localhost:3000
```

---



* Keep the backend running in **Terminal 1**.
* Keep the frontend running in **Terminal 2**.
* Activate the Python virtual environment before running backend commands.
* Do not commit `.env.local` or other files containing secrets.
