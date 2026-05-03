# AquaSentinel: Advanced Marine Debris & Regional Risk Intelligence Platform

![AquaSentinel](https://img.shields.io/badge/Status-Active-brightgreen) ![License](https://img.shields.io/badge/License-MIT-blue)

AquaSentinel is a state-of-the-art marine intelligence operating system designed to detect, monitor, and mitigate marine ecological threats. By fusing artificial intelligence (AI), satellite earth data (NASA GIBS), localized weather APIs, and crowdsourced civilian intelligence, the platform generates dynamic, geospatial risk assessments.

## Key Features

- **Global Intelligence Map**: A real-time interactive Leaflet map that clusters and renders geolocated marine debris reports.
- **Dynamic Risk Engine**: Fuses OpenWeather data with AI-assessed debris density to calculate a 0-100 environmental risk score for any location.
- **Admin Simulation Engine**: Allows administrators to inject mock disaster scenarios (e.g., oil spills) into the map to test ecosystem response readiness.
- **AI Debris Intelligence**: Processes civilian image uploads through CV pipelines to identify object types (plastic, bio-hazard, nets) and assess severity.
- **Autonomous Alert System**: Instantly broadcasts critical threat warnings across the platform when risk thresholds are breached.
- **Cyber-Premium UI/UX**: Immersive dark-mode design ensuring high engagement and rapid operational capability.

## Tech Stack

- **Frontend**: HTML5, CSS3 (Vanilla + CSS Variables), JavaScript (ES6+), Leaflet.js, FontAwesome
- **Backend**: Python, FastAPI, Pydantic, Uvicorn
- **Database**: PostgreSQL, SQLAlchemy ORM, Alembic
- **External APIs**: OpenWeather API, NASA Earthdata GIBS

## Project Structure

```text
AQUQ-SENTINEL/
├── frontend/             # Vanilla JS/CSS/HTML web application
│   ├── index.html        # Public gateway
│   ├── dashboard.html    # Main Command Base
│   ├── map.html          # Global Intelligence Map
│   ├── report.html       # Debris submission form
│   ├── admin.html        # Admin Tower & Simulation Engine
│   └── assets/           # CSS stylesheets, JS logic, and images
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── main.py       # Application entry point
│   │   ├── models.py     # SQLAlchemy database models
│   │   ├── schemas.py    # Pydantic validation schemas
│   │   ├── routes/       # API endpoint routers (risk, nasa, admin, etc.)
│   │   └── services/     # Business logic (AI detection, NASA fetching, etc.)
│   └── .venv/            # Python virtual environment
└── AquaSentinel_Patent_Draft.pdf # Comprehensive technical/patent documentation
```

## Running the Project Locally

You will need to run the backend and the frontend simultaneously in two separate terminal windows.

### 1. Start the Backend

Ensure you have Python and PostgreSQL installed.

```bash
# Navigate to the backend directory
cd backend

# Activate the virtual environment
source .venv/bin/activate

# Install requirements (if not already installed)
# pip install -r requirements.txt

# Start the FastAPI server
uvicorn app.main:app --reload --port 8000
```
*The backend API runs on `http://localhost:8000` and docs are available at `http://localhost:8000/docs`.*

### 2. Start the Frontend

Open a new terminal window.

```bash
# Navigate to the frontend directory
cd frontend

# Start a local HTTP server
python3 -m http.server 3000

# Alternatively, using npx:
# npx serve . -p 3000
```
*The frontend application is accessible in your browser at `http://localhost:3000`.*

## Documentation

For a deep dive into the system architecture, AI modules, algorithmic logic, and patentable distinctive elements, please review the `AquaSentinel_Patent_Draft.pdf` included in the root of the repository.

## License

This project is licensed under the MIT License.
