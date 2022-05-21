#!/usr/bin/env python
# coding: utf-8




from pydoc import cli
from unittest import result
import requests
import datetime
from urllib.parse import urlencode
import base64
import json
import discord
import os
from dotenv import load_dotenv
from discord.ext import bot
import youtube_dl
import asyncio
from requests import get
from youtubesearchpython import VideosSearch
from discord.ext import tasks
import random

client_id = 'a86f6f33bcd94096838e367597e7130a'
client_secret = '54a591ac5b4b4771bf9aeb11719db5f2'



class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"
    
    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

    def get_client_credentials(self):
        """
        Returns a base64 encoded string
        """
        client_id = self.client_id
        client_secret = self.client_secret
        if client_secret == None or client_id == None:
            raise Exception("You must set client_id and client_secret")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()
    
    def get_token_headers(self):
        client_creds_b64 = self.get_client_credentials()
        return {
            "Authorization": f"Basic {client_creds_b64}"
        }
    
    def get_token_data(self):
        return {
            "grant_type": "client_credentials"
        } 
    
    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        r = requests.post(token_url, data=token_data, headers=token_headers)
        if r.status_code not in range(200, 299):
            raise Exception("Could not authenticate client.")
            # return False
        data = r.json()
        now = datetime.datetime.now()
        access_token = data['access_token']
        expires_in = data['expires_in'] # seconds
        expires = now + datetime.timedelta(seconds=expires_in)
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True
    
    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if expires < now:
            self.perform_auth()
            return self.get_access_token()
        elif token == None:
            self.perform_auth()
            return self.get_access_token() 
        return token




spotify = SpotifyAPI(client_id, client_secret)





spotify.perform_auth()




access_token = spotify.access_token
access_token




headers = {
    "Authorization": f"Bearer {access_token}"
}
endpoint = "https://api.spotify.com/v1/playlists/"




#yt mustic init 

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


#discord tings

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


client = bot.Bot(command_prefix='.')
voice_clients = {}

yt_dl_opts = {'format': 'bestaudio/best'}
ytdl = youtube_dl.YoutubeDL(yt_dl_opts)

ffmpeg_options = {'options': "-vn"}
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await client.change_presence(activity=discord.Streaming(name="spotify playlists", url="https://amogus.org"))

@client.command()
async def ping(ctx,args):
    await ctx.send("sus")

i = 0
names = None
voice_is_paused = False
@client.command()
async def sp(ctx):


        N = 2
        count = 0
        res = ""
        for ele in ctx.message.content:
            if ele == ' ':
                count = count + 1
                if count == N:
                    break
                res = ""
            else :
                res = res + ele
        link = res
        plide = link[34:]
        n = 22
        a, plide = plide[:n], plide[n:]
        playlist_id = a
        await ctx.send("your playlist has been added to queue, " + playlist_id+ " is your playlist ID")

        data = playlist_id+"/tracks?fields=items(track(name))"
        lookup_url = f"{endpoint}{data}"
        print(lookup_url)
        r = requests.get(lookup_url, headers=headers)
        print(r.status_code)
        Listjson = r.json()
        global names
        names = [track['track']['name'] for track in Listjson['items']]
        noOfSongs = len(names)
        print(names)
        print (noOfSongs)
        print(names[5])
        try:
            voice_client = await ctx.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client
        except:
            print("error")
        guild = client.get_guild(int(ctx.guild.id))
        voice = discord.utils.get(client.voice_clients, guild=guild)   
        global i
        print (voice.is_playing())
        global voice_is_paused
        
        if i<noOfSongs:
            @tasks.loop(seconds=1.0)
            async def MusicLoop():
                global i
                if voice_is_paused == False:
                    if not voice.is_playing():
                        global video
                        query = names[0]
                            
                        with ytdl as ydl:
                                try:
                                    get(query) 
                                except:
                                    video = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
                                else:
                                    video = ydl.extract_info(query, download=False)

                        try:


                            #song = video
                                dumpedvideo = json.dumps(video)
                        #namesSUS = [formats['url'] for formats in video['id']]
                        # print(namesSUS)
                                listSusURl = [formats['url'] for formats in video['formats']]
                                url = listSusURl[0]
                            
                                loop = asyncio.get_event_loop()
                                data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

                                song = data['url']
                                player = discord.FFmpegPCMAudio(song, **ffmpeg_options)

                                voice_clients[ctx.guild.id].play(player)
                                print(i)
                                names.pop(0)
                                print(names)
                                i = i + 1
                        except Exception as err:
                                print(err)
            MusicLoop.start() 
@client.command(pass_contents=True, name='stop', help="Stops the music")
async def stop( ctx):
    channel = ctx.message.author.voice.channel
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
      await voice.disconnect()
      print(f'Bot left {channel}')
      await ctx.send(f'Left {channel}')
    else:
      await ctx.send(f'Not in voice channel')
@client.command(pass_contents=True, name='pause', help="pauses the music")
async def pause( ctx):
    channel = ctx.message.author.voice.channel
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
      voice.pause()
      global voice_is_paused
      voice_is_paused = True
      await ctx.send("paused")
    else:
      await ctx.send(f'Not in voice channel')
@client.command(pass_contents=True, name='resume', help="resumes the music")
async def resume( ctx):
    channel = ctx.message.author.voice.channel
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
      voice.resume()
      await ctx.send("resumed")
      global voice_is_paused
      voice_is_paused = False
    else:
      await ctx.send(f'Not in voice channel')
@client.command(pass_contents=True, name='shuffle', help="shuffles the playlist")
async def shuffle( ctx):
    channel = ctx.message.author.voice.channel
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
      random.shuffle(names)
      print(names)
      await ctx.send("shuffled")
    else:
      await ctx.send(f'Not in voice channel')
video = None
@client.command(name='search', help='Plays any song or url')
async def search( ctx):
        global video
        query = ctx.message.content.split(' ', 1)[1]
        try:
            voice_client = await ctx.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client
        except:
            print("error")
        with ytdl as ydl:
            try:
                get(query) 
            except:
                video = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            else:
                video = ydl.extract_info(query, download=False)

        try:


            #song = video
            dumpedvideo = json.dumps(video)
           #namesSUS = [formats['url'] for formats in video['id']]
           # print(namesSUS)
            listSusURl = [formats['url'] for formats in video['formats']]
            url = listSusURl[0]
            
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

            song = data['url']
            player = discord.FFmpegPCMAudio(song, **ffmpeg_options)

            voice_clients[ctx.guild.id].play(player)

        except Exception as err:
            print(err)


client.run(TOKEN)







    