import discord
import dotenv
import os
import requests

dir_path = os.path.dirname(os.path.realpath(__file__))
env_path = os.path.join(dir_path, "../.credential")
# Load environment variables from .credentials file
dotenv.load_dotenv(dotenv_path=env_path)
BOT_TOKEN = os.getenv("BOT_TOKEN", None)
assert BOT_TOKEN is not None, "BOT_TOKEN environment variable not found"
print("BOT_TOKEN:", BOT_TOKEN)


# Create a Discord client
intents = discord.Intents.default()
intents.message_content = True
# intents.presences = False
client = discord.Client(intents=intents)
# client = discord.Client()


# Event handler for when the bot is ready
@client.event
async def on_ready():
    print(f"Logged in as {client.user.name}")


allowed_channels = ["test", "naxon", "ktktour-demo"]


def post_chatbot(product_id, client_id, chat_session_id, message):
    base_url = "http://localhost:9300"

    # Replace these with the actual product ID and client ID you want to use
    # product_id = "product_a"
    # product_id = "washing_machine_haier"
    # client_id = "customer_1"
    # chat_session_id = "session_1"
    # # The message you want to send
    # message = "what is the dimension of product?"
    # message = "ขนาดของรุ่น EWF9024P5WB ?"
    # message = "what is the maximum capacity of this EWF9024P5WB?"
    # message = "what is the maximum capacity of this EWF8024P5WB for daily39?"

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
    message = response.json()["data"]["message"]
    return message


async def send_message(message, response, is_private=False):
    try:
        await message.author.send(
            response
        ) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


# Event handler for when a message is received
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    user_message = str(message.content)
    print("message:", user_message)
    # print channel
    if message.channel.name not in allowed_channels:
        return
    print("channel:", message.channel.name)
    if message.channel.name == "ktktour-demo":
        message += "!tourist_visa "
    if not user_message.startswith("!"):
        return
    product_id = user_message.split()[0][1:]
    question = " ".join(user_message.split()[1:])
    response = post_chatbot(product_id, message.author, "discord", question)
    print("response:", response)
    await send_message(message, response)


# Replace 'YOUR_BOT_TOKEN' with your actual bot token
client.run(BOT_TOKEN)
