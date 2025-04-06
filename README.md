# ElevenLabs RAG API

A FastAPI-based API for handling conversations with ElevenLabs agents and RAG processing.

## Features

- User authentication (register, login)
- Agent management (create, list, get)
- Real-time conversation via WebSocket
- RAG processing

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the application:

```bash
uvicorn app.main:app --reload
```

## Google OAuth Setup

To enable Google login functionality, follow these steps:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Credentials"
4. Click "Create Credentials" and select "OAuth client ID"
5. Set the application type to "Web application"
6. Add your application's domain to the "Authorized JavaScript origins" (e.g., http://localhost:3000 for development)
7. Add your redirect URI to the "Authorized redirect URIs" (e.g., http://localhost:3000 for development)
8. Click "Create" and note your Client ID
9. Create a `.env.local` file in the root of your project and add:
   ```
   REACT_APP_GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID
   ```
10. Replace `YOUR_GOOGLE_CLIENT_ID` with the Client ID you obtained from Google Cloud Console

## Backend CORS Configuration

To allow your frontend to communicate with your backend, you need to configure CORS on your backend server. Here's how to do it for different frameworks:

### For FastAPI (Python)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### For Express (Node.js)

```javascript
const express = require("express");
const cors = require("cors");
const app = express();

// Configure CORS
app.use(
  cors({
    origin: "http://localhost:3000", // Frontend URL
    credentials: true,
  })
);
```

Make sure to install the necessary packages:

- For Node.js: `npm install cors`
- For Python: FastAPI includes CORS middleware

## API Endpoints

### Authentication

#### Register a new user

```
POST /auth/register
```

Request body:

```json
{
  "username": "your_username",
  "password": "your_password",
  "name": "Your Name",
  "email": "your.email@example.com"
}
```

#### Login and get access token

```
POST /auth/token
```

Form data:

- `username`: Your username
- `password`: Your password

### Agent Management

#### Create a new agent

```
POST /agents
```

Request body:

```json
{
  "name": "Agent Name",
  "description": "Agent Description"
}
```

Headers:

- `Authorization`: Bearer {your_access_token}

#### List all agents

```
GET /agents
```

Headers:

- `Authorization`: Bearer {your_access_token}

#### Get agent details

```
GET /agents/{agent_id}
```

Headers:

- `Authorization`: Bearer {your_access_token}

### WebSocket Conversation

Connect to:

```
WebSocket /ws/conversation/{agent_id}
```

Message format:

```json
{
  "api_key": "Your ElevenLabs API key",
  "messages": [{ "role": "user", "content": "Your message" }]
}
```

## API Documentation

- Swagger UI: `/docs`
- ReDoc: `/redoc`
