import requests

# Replace with your actual FastAPI server URL
base_url = "http://localhost:9300"
# base_url = "http://localhost:9500"

# Replace these with the actual product ID and client ID you want to use
# product_id = "product_a"
product_id = "aum_wiki"
client_id = "customer_1"
chat_session_id = "session_1"
# The message you want to send


headers = {
    "X-Client-ID": f"{client_id}",
    "X-Product-ID": f"{product_id}",
    "X-Chat-Session-ID": f"{chat_session_id}",
}
website = "https://th.wikipedia.org/wiki/%E0%B8%9E%E0%B8%B1%E0%B8%8A%E0%B8%A3%E0%B8%B2%E0%B8%A0%E0%B8%B2_%E0%B9%84%E0%B8%8A%E0%B8%A2%E0%B9%80%E0%B8%8A%E0%B8%B7%E0%B9%89%E0%B8%AD"

data = {"website": website, "knowledge_name": "aum_wiki_1"}
# Make the POST request
response = requests.post(
    # f"{base_url}/chat",
    f"{base_url}/api/v1/clear_data",
    json=data,
    headers=headers,
)

# Check the response
if response.status_code == 200:
    data = response.json()
    print("Response:", data)
else:
    print("Request failed with status code:", response.status_code)
    print(response.text)

print(f"time used: {response.elapsed.total_seconds()}")
