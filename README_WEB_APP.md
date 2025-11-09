# Merge Activity Dashboard - Web Application

A Material-UI based web dashboard to visualize organization merge activity data.

## Features

- Interactive wave graphs showing merges per day vs merge date
- Material-UI components for modern, responsive design
- Real-time data from organization_merge_dates table
- Organization selector to view different organizations
- Responsive design that works on all devices

## Setup

### 1. Install Python Dependencies

```bash
pip install flask flask-cors
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

### 2. Install Node.js Dependencies

Navigate to the frontend directory and install dependencies:

```bash
cd frontend
npm install
```

### 3. Run the Application

#### Start the Flask API Server

In the project root directory:

```bash
python -m app.api.server
```

The API will run on `http://localhost:5000`

#### Start the React Frontend

In a new terminal, navigate to the frontend directory:

```bash
cd frontend
npm start
```

The frontend will run on `http://localhost:3000` and automatically open in your browser.

## API Endpoints

- `GET /api/organizations` - Get list of all organizations
- `GET /api/organizations/<org_slug>/data` - Get merge data for a specific organization
- `GET /api/organizations/<org_slug>/stats` - Get statistics for a specific organization
- `GET /api/overall/stats` - Get overall statistics across all organizations

## Usage

1. Start both the Flask server and React app
2. Open `http://localhost:3000` in your browser
3. Select an organization from the dropdown
4. View the wave graph showing merges per day over time
5. See statistics cards showing total, average, max, and min values

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: React with Material-UI
- **Charts**: Recharts
- **Database**: PostgreSQL (via SQLAlchemy)

## Project Structure

```
.
├── app/
│   └── api/
│       └── server.py          # Flask API server
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js             # Main React component
│   │   ├── App.css
│   │   ├── index.js
│   │   └── index.css
│   └── package.json
└── requirements.txt
```

