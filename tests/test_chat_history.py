import requests

# Replace with your actual FastAPI server URL
base_url = "http://localhost:9300"

# Replace these with the actual product ID and client ID you want to use
product_id = "product_a"
client_id = "customer_1"
chat_session_id = "session_1"
# The message you want to send
message = "ผมชื่อฟอร์ด"

# Data to send in the POST request
data = {"message": message}

headers = {
    "X-Client-ID": f"{client_id}",
    "X-Product-ID": f"{product_id}",
    "X-Chat-Session-ID": f"{chat_session_id}",
}
#
# response = requests.get(base_url)
# print(response.json())
# # Make the POST request
# response = requests.post(
#     f"{base_url}/chat",
#     json=data,
#     headers=headers,
# )

message = "ผมชื่อว่าอะไร?"

# Data to send in the POST request
data = {"message": message}

headers = {
    "X-Client-ID": f"{client_id}",
    "X-Product-ID": f"{product_id}",
    "X-Chat-Session-ID": f"{chat_session_id}",
}
#
response = requests.get(base_url)
print(response.json())
# Make the POST request
response = requests.post(
    f"{base_url}/chat",
    json=data,
    headers=headers,
)

# Check the response
if response.status_code == 200:
    data = response.json()
    print("Response:", data)
else:
    print("Request failed with status code:", response.status_code)
print(f"time used: {response.elapsed.total_seconds()}")
