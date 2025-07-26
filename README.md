# Overview
This project is a full-stack app that uses React, Python, and MongoDB.

When run for the first time, the DB would be empty and not pre-seeded. For ease of use, I added a few presets that can be inserted from `/debug` URL on the web app. If you wish to feed in your own data, you can do that via Postman or Open API docs page (refer to quick links section below for direct links).

## Technical details
Frontend uses only React and no other framework for JS or CSS. This was intentional in order to showcase my coding skills. The website is adequately responsive as it uses CSS container queries to arrange contents.

Backend uses FastAPI as its Python framework. I chose this over Flask because of its convenience in defining endpoints and adding OpenAPI spec. Having very little knowledge of Python, I relied heavily on examples from the internet. Code is a bit of a mess and has room for a lot of improvement.

## How to run the services

### [Production] Build and start all services
After cloning the repo, switch to the directory and run these commands after ensuring Docker Daemon is up and running:
```
docker-compose build
docker-compose up -d
```
This will build both frontend and backend code in the Docker image, so you don't have to worry about installing dependencies on your system.

Verify that all 3 services are running by running:
```
docker-compose ps
```

Personally, I use Docker Desktop GUI to monitor the services after running them in detached state.

### [Production] Stop all services
Run this command to stop all the services from CLI:
```
docker-compose down
```
This is as good as stopping the services from the GUI.

### [Development] Frontend
Run these commands to start the dev server with HMR:
```
cd frontend
npm install
npm run dev
```

The backend URL is hardcoded in `vite.config.js`. If you wish to change your backend port for local development, make sure to update the config file.

### [Development] Backend
Your best bet is to run the backend server and mongo inside Docker to begin with, especially if you're developing on a Windows machine like me. Docs indicate this is the right way to do it:
```
# Terminal window 1
docker-compose up mongo

# Terminal window 2
docker-compose run --rm --service-ports backend uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

# Additional information

## Quick reference links
* Frontend (dev) - http://localhost:5173
* Frontend - http://localhost:3000
* Backend - http://localhost:8000
* API Docs - http://localhost:8000/docs
* MongoDB - http://localhost:27017

## Pending improvements:
* Ability to filter by multiple cast members. Right now, you can only apply one cast member as a filter for movie list.
* Comprehensive error handling. Current behaviour is to show a generic error on the page directly.
* Persist filters on page reload by storing them in URL query params.