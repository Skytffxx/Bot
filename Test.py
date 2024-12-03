import discord
from discord.ext import commands
import random

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Economy system
economy = {}

# Admin commands
admin_roles = ["Admin", "Moderator"]  # Add the roles that are allowed to use admin commands

# Helper functions for economy system
def get_balance(user_id):
    return economy.get(user_id, 1000)  # Default starting balance is 1000

def update_balance(user_id, amount):
    if user_id in economy:
        economy[user_id] += amount
    else:
        economy[user_id] = 1000 + amount  # Default starting balance for new users

# Economy commands
@bot.command(name="balance")
async def balance(ctx):
    user_balance = get_balance(ctx.author.id)
    await ctx.send(f"{ctx.author.name}, your balance is: ${user_balance}")

@bot.command(name="daily")
async def daily(ctx):
    user_id = ctx.author.id
    daily_reward = random.randint(50, 200)
    update_balance(user_id, daily_reward)
    await ctx.send(f"Here's your daily reward of ${daily_reward}, {ctx.author.name}! Your new balance is ${get_balance(user_id)}.")

@bot.command(name="work")
async def work(ctx):
    user_id = ctx.author.id
    earnings = random.randint(10, 150)
    update_balance(user_id, earnings)
    await ctx.send(f"{ctx.author.name}, you worked hard and earned ${earnings}. Your new balance is ${get_balance(user_id)}.")

@bot.command(name="rob")
async def rob(ctx, member: discord.Member):
    if member.id == ctx.author.id:
        await ctx.send(f"You cannot rob yourself, {ctx.author.name}.")
        return
    user_id = ctx.author.id
    victim_balance = get_balance(member.id)
    if victim_balance < 50:
        await ctx.send(f"{member.name} doesn't have enough money to rob.")
        return
    rob_amount = random.randint(10, victim_balance // 2)  # rob half of victim's balance
    update_balance(user_id, rob_amount)
    update_balance(member.id, -rob_amount)
    await ctx.send(f"{ctx.author.name} successfully robbed ${rob_amount} from {member.name}. New balances - You: ${get_balance(user_id)}, {member.name}: ${get_balance(member.id)}.")

@bot.command(name="send")
async def send(ctx, member: discord.Member, amount: int):
    user_id = ctx.author.id
    sender_balance = get_balance(user_id)
    if sender_balance < amount:
        await ctx.send(f"{ctx.author.name}, you don't have enough money to send.")
        return
    update_balance(user_id, -amount)
    update_balance(member.id, amount)
    await ctx.send(f"{ctx.author.name} sent ${amount} to {member.name}. Your new balance is ${get_balance(user_id)}.")

@bot.command(name="bet")
async def bet(ctx, amount: int):
    user_id = ctx.author.id
    user_balance = get_balance(user_id)
    if user_balance < amount:
        await ctx.send(f"{ctx.author.name}, you don't have enough money to bet.")
        return
    result = random.choice(["win", "lose"])
    if result == "win":
        earnings = amount * 2  # Double the bet if won
        update_balance(user_id, earnings)
        await ctx.send(f"{ctx.author.name} bet ${amount} and won! Your new balance is ${get_balance(user_id)}.")
    else:
        update_balance(user_id, -amount)
        await ctx.send(f"{ctx.author.name} bet ${amount} and lost. Your new balance is ${get_balance(user_id)}.")

# Admin commands
@bot.command(name="setbalance")
@commands.has_permissions(administrator=True)
async def set_balance(ctx, member: discord.Member, amount: int):
    update_balance(member.id, amount)
    await ctx.send(f"{ctx.author.name} set {member.name}'s balance to ${amount}.")

@bot.command(name="give")
@commands.has_permissions(administrator=True)
async def give(ctx, member: discord.Member, amount: int):
    update_balance(member.id, amount)
    await ctx.send(f"{ctx.author.name} gave {member.name} ${amount}. New balance: ${get_balance(member.id)}.")

@bot.command(name="resetbalance")
@commands.has_permissions(administrator=True)
async def reset_balance(ctx, member: discord.Member):
    economy[member.id] = 1000  # Reset to default starting balance
    await ctx.send(f"{ctx.author.name} reset {member.name}'s balance to $1000.")

@bot.command(name="deleteuser")
@commands.has_permissions(administrator=True)
async def delete_user(ctx, member: discord.Member):
    if member.id in economy:
        del economy[member.id]
        await ctx.send(f"{ctx.author.name} deleted {member.name}'s economy data.")
    else:
        await ctx.send(f"{member.name} doesn't have any economy data.")

@bot.command(name="transfer")
@commands.has_permissions(administrator=True)
async def transfer(ctx, from_member: discord.Member, to_member: discord.Member, amount: int):
    from_balance = get_balance(from_member.id)
    if from_balance < amount:
        await ctx.send(f"{from_member.name} doesn't have enough money to transfer.")
        return
    update_balance(from_member.id, -amount)
    update_balance(to_member.id, amount)
    await ctx.send(f"{ctx.author.name} transferred ${amount} from {from_member.name} to {to_member.name}.")

# Error handling for admin commands
@set_balance.error
@give.error
@reset_balance.error
@delete_user.error
@transfer.error
async def admin_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to use this command.")

# Run bot
bot.run('YOUR_BOT_TOKEN')
