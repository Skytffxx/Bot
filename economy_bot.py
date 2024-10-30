import discord
from discord.ext import commands
import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Database setup
conn = sqlite3.connect('economy.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS economy (user_id INTEGER PRIMARY KEY, balance INTEGER)')
conn.commit()

# Bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

@bot.slash_command(name="balance", description="Check your balance")
async def balance(ctx: discord.ApplicationContext):
    user_id = ctx.author.id
    c.execute('SELECT balance FROM economy WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    if result:
        await ctx.respond(f'Your balance is: ${result[0]}')
    else:
        await ctx.respond('You have no balance yet. Use /work to earn some!')

@bot.slash_command(name="work", description="Work to earn money")
async def work(ctx: discord.ApplicationContext):
    user_id = ctx.author.id
    c.execute('SELECT balance FROM economy WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    
    if result:
        earnings = 100
        new_balance = result[0] + earnings
        c.execute('UPDATE economy SET balance = ? WHERE user_id = ?', (new_balance, user_id))
    else:
        c.execute('INSERT INTO economy (user_id, balance) VALUES (?, ?)', (user_id, 100))
    conn.commit()
    await ctx.respond('You worked hard and earned $100!')

# Start the bot
bot.run(TOKEN)
