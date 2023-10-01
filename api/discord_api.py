import discord
import dotenv
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
env_path = os.path.join(dir_path, "../.credential")
# Load environment variables from .credentials file
dotenv.load_dotenv(dotenv_path=env_path)
BOT_TOKEN = os.getenv("BOT_TOKEN", None)
assert BOT_TOKEN is not None, "BOT_TOKEN environment variable not found"
print("BOT_TOKEN:", BOT_TOKEN)


# Create a Discord client
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
client = discord.Client(intents=intents)


# Event handler for when the bot is ready
@client.event
async def on_ready():
    print(f"Logged in as {client.user.name}")


# Event handler for when a message is received
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!hello"):
        await message.channel.send("Hello!")


# Replace 'YOUR_BOT_TOKEN' with your actual bot token
client.run(BOT_TOKEN)
