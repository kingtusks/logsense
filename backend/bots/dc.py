import discord
import asyncio
import os
import sys
from discord import app_commands
from decouple import config

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import agent_chat

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

@tree.command(name="logs", description="Ask logsense about your servers and containers")
@app_commands.describe(query="What do you want to check?")
async def ops(interaction: discord.Interaction, query: str):
    await interaction.response.defer()  
    response = await agent_chat(query)
    await interaction.followup.send(response[:2000])

@bot.event
async def on_ready():
    await tree.sync()
    print(f"logged in as {bot.user}")

if __name__ == "__main__":
    bot.run(config("DISCORD_TOKEN"))