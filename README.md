# Journey: A Digital Thought Companion

Journey is a Digital AI Diary that help people to keep track of how they feel and how their thoughts are influence by the external world. Journey
besides interactive (you will speak with your diary), also comes with an integrated calendar where users can track past conversations and also understand with the blink of an eye they feel.

## About Journey

In order to run it you need to perform quite some steps:

1. Installation Backend

Install the packages in the `backend-api-service` directory:

- cd backend-api-service
- python3.11 -m venv .vevn
- source .venv/bin/activate
- pip install -r requirements.txt

Create an .env file (inside `backend-api-service`) and add

1. An **ELEVENLABS_API_KEY**
2. an **OPENAI_API_KEY**

Then, from the same wdir run "python run.py"

2. Installation Frontend

- npm i

To run it, you need to (should be improved):

1. `cd backend-api-service && python run.py

2. copy the ngrok host name in the logs, and run inside the frontend directory `REACT_APP_API_BASE_URL=that_ngrok_host npm start`

3) Finally go to elevenlabs UI >> Conversation AI >> Conversational AI Settings >> Post-Call Webhook >> create a webhook with a random name and
   the following URL: that_ngrok_host/webhook/elevenlabs

4) Go to http://localhost:3000/ and start using the app
