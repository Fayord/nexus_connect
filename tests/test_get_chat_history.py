import requests

# Replace with your actual FastAPI server URL
base_url = "http://localhost:9300"

# Replace these with the actual product ID and client ID you want to use
product_id = "product_a"
client_id = "customer_1"
chat_session_id = "session_1"


headers = {
    "X-Client-ID": f"{client_id}",
    "X-Product-ID": f"{product_id}",
    "X-Chat-Session-ID": f"{chat_session_id}",
}
#
response = requests.get(f"{base_url}/chat_history", headers=headers)

# Check the response
if response.status_code == 200:
    data = response.json()
    print("Response:", data)
else:
    print("Request failed with status code:", response.status_code)
print(f"time used: {response.elapsed.total_seconds()}")
