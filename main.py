import os
import discord
import re
import asyncio
from discord.ext import commands
from discord.ext import tasks
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)

# Function to load the replacement count from a file
def load_replacement_count():
    try:
        with open('replacement_count.txt', 'r') as file:
            return int(file.read())
    except FileNotFoundError:
        return 0

# Function to save the replacement count to a file
def save_replacement_count(count):
    with open('replacement_count.txt', 'w') as file:
        file.write(str(count))

replacement_count = load_replacement_count()  # Load the initial count

@tasks.loop(minutes=5)
async def change_presence_task():
    global replacement_count
    await bot.change_presence(activity=discord.Game(name=f"{replacement_count} links replaced"))
    await asyncio.sleep(30)  # Wait for 30 seconds
    await bot.change_presence(activity=discord.Game(name="Replacing twitter links"))

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    change_presence_task.start()  # Start the presence-changing task)

@bot.event
async def on_message(message):
    global replacement_count  # Declare the variable as global

    if message.author == bot.user:
        return  # Skip processing messages sent by the bot itself

    # Define the URLs to check for and the replacement text
    urls_to_replace = {
        'x.com': 'https://fixupx.com',
        'twitter.com': 'https://fxtwitter.com'
    }

    for url, replacement in urls_to_replace.items():
        # Use regular expressions to find URLs with the specified domains
        pattern = re.compile(f'https?://(www\.)?{re.escape(url)}', re.IGNORECASE)
        replaced_content = pattern.sub(replacement, message.content)

        if replaced_content != message.content:
            #print(f'Replaced "{url}" with "{replacement}" in message: {message.content}')
            
            # Increment the replacement count
            replacement_count += 1
            save_replacement_count(replacement_count) # Save the updated count to the file

            # Get the user's nickname or username
            user_nick = message.author.nick
            user_name = message.author.name

            # Construct the new message content
            if user_nick:
                user_display_name = f"{user_nick} [{user_name}]"
            else:
                user_display_name = user_name

            # Delete the original message
            await message.delete()

            # Send a new message with the replaced content
            await message.channel.send(f"{user_display_name}:\n{replaced_content}")

    await bot.process_commands(message)

# Command to check the replacement count
@bot.command()
async def linkcount(ctx):
    global replacement_count
    await ctx.send(f"The bot has replaced {replacement_count} links.")

load_dotenv()
bot.run(os.getenv('TOKEN'))
