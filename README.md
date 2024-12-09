# Ottawa Lane Swim Scheduler

This project provides a comprehensive lane swim schedule dashboard for swimmers in Ottawa. It combines a **Flask backend** and a **Svelte frontend** to deliver a seamless user experience.

## Features

- Filter swim schedules by pool, day, start time, and end time.
- View pool locations on an interactive Mapbox map.
- Sort schedules dynamically by start time.
- Integration with Mapbox for geolocation and mapping.
- Real-time updates with a script that fetches the latest schedules.

## Live Deployment

The application is live and accessible here:  
[Ottawa Lane Swim Scheduler](https://lane-swim-webapp.vercel.app/)

## Project Structure

1. **Backend (Flask):**  
   The Flask backend handles API requests, fetching pool schedules, and geocoding addresses for mapping.

2. **Frontend (Svelte):**  
   The Svelte frontend provides an interactive user interface, including:
   - Schedule table with sorting and filtering.
   - Map with pool markers and details.
