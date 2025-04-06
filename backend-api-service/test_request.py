import requests

response = requests.post(
    "http://localhost:8000/memory/get",
    json={
        "agent_id": "n3vBbsK8TE8VqZqn17Gb",
        "text": "What happened important in my life lately?",
    },
)

print(response.json())
