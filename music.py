import discord
from discord.ext import commands
import youtube_dl
from dotenv import load_dotenv
from discord.ext import bot
import os

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


client = bot.Bot(command_prefix='.')

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await client.change_presence(activity=discord.Streaming(name="spotify playlists", url="https://amogus.org"))

@client.command()
async def ping(ctx):
    await ctx.send("sus")


client.run(TOKEN)