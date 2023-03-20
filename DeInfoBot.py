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

@bot.command()
async def db(ctx, arg):
    if arg == 'help':
        await ctx.send(bot_help_message)

    if arg == 'serverusage':
        cpu_count = multiprocessing.cpu_count()
        one, five, fifteen = os.getloadavg()
        load_percentage = int(five / cpu_count * 100)
        await ctx.send(f'Server load is at {load_percentage}%')

    if arg == 'search_query':
        await ctx.send(f'Current search query is {QUERY}')

    if arg == 'total_count':
        await ctx.send(f'Total count of results in current query {TOTAL_COUNT}')

    if arg == 'set_query':
        await ctx.send(f'New search query is {QUERY}')

    if arg == 'dump':
        await ctx.send(f'Dumping total results: {TOTAL_COUNT} from {QUERY} db')


bot.run(DISCORD_TOKEN)
