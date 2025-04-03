import requests

API_URL = "http://localhost:8000/v1/chat/completions"
headers = {
    "Authorization": "ollama"
}
data = {
    "model": "DeepSeek-R1",
    "messages": [{"role": "user", "content": "你是谁？"}],
    "stream": True,
}

response = requests.post(API_URL, headers=headers, json=data)
# print(response.json())
with requests.post(API_URL, headers=headers, json=data, stream=True) as response:
    for line in response.iter_lines():
        if line:
            print(line.decode('utf-8'))
