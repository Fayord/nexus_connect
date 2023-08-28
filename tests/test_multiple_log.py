import requests

# Replace with your actual FastAPI server URL
base_url = "http://localhost:9300"

product_name_map = {
    "product_a": "elextrolux washing machine",
    "product_b": "lg washing machine",
}
chat_session_id = "session_1"

for product_id in ["product_a", "product_b"]:
    for client_id in ["customer_1", "customer_2"]:
        # The message you want to send
        message = (
            f"what is the maximum capacity of this {product_name_map[product_id]}?"
        )

        # Data to send in the POST request
        data = {"message": message}

        headers = {
            "X-Client-ID": f"{client_id}",
            "X-Product-ID": f"{product_id}",
            "X-Chat-Session-ID": f"{chat_session_id}",
        }
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
        print("\n\ttime used: {}\n".format(response.elapsed.total_seconds()))
