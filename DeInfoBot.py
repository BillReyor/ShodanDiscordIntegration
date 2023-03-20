import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv
import random
import multiprocessing

BOT_NAME = "BOTNAMEHERE"
DISCORD_TOKEN = "YOURTOKENHERE
load_dotenv()

bot_help_message = """
:: Bot Usage ::
`!db help`           : shows help
`!db whosonline`     : shows who is online within the channel
`!db serverusage`    : shows statistics of the bot host
`!db search_query`   : shows system load in percentage
`!db total_count`    : shows the total count of results
`!db set_query`      : sets the search query for the application
`!db dump`           : returns all results on a query for a specific date
"""

available_commands = ['help', 'whosonline', 'serverusage', 'search_query', 'total_count', 'set_query', 'dump']
bot = commands.Bot(command_prefix="!",intents=discord.Intents.default())

@bot.event
async def on_ready():
    print(f'{bot.user} succesfully logged in!')

@bot.event
async def on_message(message):
    print(f'User: {message.author}, Message: {message.content}')
    if message.author == bot.user:
        return
    if message.content == '!db':
        await message.channel.send(bot_help_message)
    if 'whosonline' in message.content:
        print(f'{message.author} used {message.content}')
    await bot.process_commands(message)

# Executes when the command mc is used and we trigger specific functions
# when specific arguments are caught in our if statements
@bot.command()
async def dd(ctx, arg):
    if arg == 'help':
        await ctx.send(bot_help_message)

    if arg == 'serverusage':
        cpu_count = multiprocessing.cpu_count()
        one, five, fifteen = os.getloadavg()
        load_percentage = int(five / cpu_count * 100)
        await ctx.send(f'Server load is at {load_percentage}%')

    if arg == 'search_query':
        response = requests.get(f'https://api.mcsrvstat.us/2/{minecraft_server_url}').json()
        server_status = response['online']
        if server_status == True:
            server_status = 'online'
        await ctx.send(f'Server is {server_status}')

    if arg == 'total_count':
        response = requests.get('https://api.mcsrvstat.us/2/{minecraft_server_url}').json()
        players_status = response['players']
        if players_status['online'] == 0:
            players_online_message = 'No one is online'
        if players_status['online'] == 1:
            players_online_username = players_status['list'][0]
            players_online_message = f'1 player is online: {players_online_username}'
        if players_status['online'] > 1:
            po = players_status['online']
            players_online_usernames = players_status['list']
            joined_usernames = ", ".join(players_online_usernames)
            players_online_message = f'{po} players are online: {joined_usernames}'
        await ctx.send(f'{players_online_message}')

    if arg == 'set_query':
        cpu_count = multiprocessing.cpu_count()

    if arg == 'dump':
        cpu_count = multiprocessing.cpu_count()


bot.run(DISCORD_TOKEN)
