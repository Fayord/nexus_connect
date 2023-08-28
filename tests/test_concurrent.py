import concurrent.futures
import requests
import time


def send_api_request(url, data, headers):
    response = requests.post(url, json=data, headers=headers)
    print(response.status_code, response.elapsed.total_seconds())
    return response


if __name__ == "__main__":
    # Replace with your actual FastAPI server URL
    base_url = "http://localhost:9300"
    url1 = url2 = f"{base_url}/chat"
    product_name_map = {
        "product_a": "elextrolux washing machine",
        "product_b": "lg washing machine",
    }
    chat_session_id = "session_1"

    product_id = "product_b"
    message = f"what is the maximum capacity of this {product_name_map[product_id]}?"
    data1 = data2 = {"message": message}
    client_id = "customer_1"
    headers1 = {
        "X-Client-ID": f"{client_id}",
        "X-Product-ID": f"{product_id}",
        "X-Chat-Session-ID": f"{chat_session_id}",
    }
    client_id = "customer_2"
    headers2 = {
        "X-Client-ID": f"{client_id}",
        "X-Product-ID": f"{product_id}",
        "X-Chat-Session-ID": f"{chat_session_id}",
    }
    print("single post request")
    send_api_request(url1, data1, headers1)
    print()
    print("concurrent post request")
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future1 = executor.submit(send_api_request, url1, data1, headers1)
        future2 = executor.submit(send_api_request, url2, data2, headers2)

        response1 = future1.result()
        response2 = future2.result()
    print("total time used: {}".format(time.time() - start_time))
