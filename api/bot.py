import dotenv
import random
import os
import discord
import requests

dir_path = os.path.dirname(os.path.realpath(__file__))
env_path = os.path.join(dir_path, "../.credential")
dotenv.load_dotenv(dotenv_path=env_path)
TOKEN = os.getenv("TOKEN", None)
assert TOKEN is not None, "TOKEN environment variable not found"
print("TOKEN:", TOKEN)
chat_api_url = "http://localhost:9300"


# def get_response(message: str) -> str:
#     p_message = message.lower()
#     if p_message == "hello":
#         return "Hello!"
#     elif p_message == "roll":
#         return str(random.randint(1, 6))
#     elif p_message == "!help":
#         return "Hello! I'm a bot. I can roll a dice for you. Just type 'roll' and I'll roll a dice for you."
#     default_message = (
#         "Sorry, I don't understand what you mean. Type '!help' to see what I can do."
#     )
#     return default_message


def get_response(
    message: str,
    product_id: str,
    client_id: str,
) -> str:
    data = {"message": message}
    chat_session_id = "session_1"
    headers = {
        "X-Client-ID": f"{client_id}",
        "X-Product-ID": f"{product_id}",
        "X-Chat-Session-ID": f"{chat_session_id}",
    }
    response = requests.post(
        f"{chat_api_url}/chat",
        json=data,
        headers=headers,
    )
    try:
        response_dict = response.json()
        source_data_list = response_dict["data"]["source_data"]
        source_data_list
        response_text = response_dict["data"]["message"] + "\nSource data:"

        for source_data in source_data_list:
            response_text += f"\n   {source_data}"
        print(response_text)
    except:
        response_text = "failed to get response from chat api"
    return response_text


async def send_message(message, user_message, product_id, client_id, is_private=False):
    # await message.channel.send(user_message)
    try:
        response = get_response(user_message, product_id, client_id)
        await message.author.send(
            response
        ) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


def run_discord_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    # raise

    @client.event
    async def on_ready():
        print(f"Logged in as {client.user.name}")

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        # if channel != "test":
        if channel not in ["test", "naxon", "ktktour-demo"]:
            return
        if channel == "ktktour-demo":
            if user_message[0] == "!":
                return
            else:
                user_message = "!tourist_visa " + user_message
        print(f"{username}: {user_message} (from {channel})")
        if user_message[0] not in ["!", "?"]:
            return
        is_private = False
        if user_message[0] == "?":
            is_private = True
        user_message = user_message[1:]
        product_id = user_message.split(" ")[0]
        user_message = user_message[len(product_id) + 1 :]
        client_id = f"{message.author}"
        await send_message(message, user_message, product_id, client_id, is_private)

    client.run(TOKEN)


if __name__ == "__main__":
    run_discord_bot()
