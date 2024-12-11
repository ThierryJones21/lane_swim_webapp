# Ottawa Lane Swim Scheduler

This project provides a lane swim schedule dashboard web application with a Flask backend and a Svelte frontend.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Backend Setup (Flask)](#backend-setup-flask)
3. [Frontend Setup (Svelte)](#frontend-setup-svelte)
4. [Running the Application](#running-the-application)

## Getting Started

### Prerequisites

- **Python** (3.7 or later) - [Download here](https://www.python.org/downloads/)
- **Node.js** (16 or later) and npm - [Download here](https://nodejs.org/)

Ensure both `python` and `node` are in your system path.
---

**Clone the Repository** (if you haven't already):
   ```bash
   git clone https://github.com/thierryjones21/lane-swim-webapp.git
   ```
   ```bash
   cd lane_swim_webapp
   ```

## Backend Setup (Flask)

**Install Dependencies and Run the WebScraper to get the database (.db) file**
   ```bash
   pip install -r requirements.txt
   ```
   ```bash
   python pool_scraper.py
   ```

**Run Flask Server**
   ```bash
   python flask_app.py
   ```

## Frontend Setup (Svelte)

**Install Dependencies and Run Svelte Server**
Open a new terminal, then navigate to webapp folder. Install the node modules required to run the svelte app.
   ```bash
   cd /webapp_svelte
   ```
   ```bash
   npm install
   npm run dev
   ```

## Running the Application

Once both the Flask backend and Svelte frontend are running, you can access the application by navigating to [http://localhost:5173](http://localhost:5173) in your browser.

- **To stop the Flask server:** Press `Ctrl+C` in the terminal where it's running.
- **To stop the Svelte server:** Press `Ctrl+C` in the terminal where it's running.

## API Endpoints

| Endpoint     | Method | Description                |
|--------------|--------|----------------------------|
| `/schedules` | GET    | Get a list of all schedules |
| `/pools`     | GET    | Get a list of available pools |

## Additional Notes

- **Database Reset:** If you need to reset the database, delete `lane_swim_database.db` in the backend directory and rerun the commands in the **Backend Setup** section.


