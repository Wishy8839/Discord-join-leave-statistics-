import discord
from discord import app_commands
import discord.ext
from discord.ext import commands
import datetime
import sqlite3
#bro i copy and pasted from my other bot LOSER


intents = discord.Intents().all()
bot = commands.Bot(intents=intents,command_prefix="!",case_insensitive=False,)

conn = sqlite3.connect('member_data.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS members
             (user_id TEXT, username TEXT, join_time TEXT, leave_time TEXT, duration TEXT)''')
conn.commit()

async def on_ready():
    print('Bot is ready.')


@bot.command()
async def sync(ctx):
    print("sync command")
    await bot.tree.sync()
    bot.remove_command("help")
    bot.remove_command("add_members")

conn.commit()
@bot.event
async def on_member_join(member):
    c.execute("SELECT user_id FROM members WHERE user_id=?", (str(member.id),))
    existing_user = c.fetchone()
    if not existing_user:
        join_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        c.execute("INSERT INTO members VALUES (?, ?, ?, NULL, NULL)", (str(member.id), member.name, join_time))
        conn.commit()


@bot.command()
async def shortest_stays(ctx):
    c.execute("SELECT username, duration FROM members WHERE duration IS NOT NULL")
    rows = c.fetchall()
    if rows:
        sorted_rows = sorted(rows, key=lambda x: datetime.datetime.strptime(x[1], '%H:%M:%S'))
        message = "Shorest stays:\n"
        for index, row in enumerate(sorted_rows, start=1): # stolen from stakc overflow 
            message += f"{index}. {row[0]} - {row[1]}\n"
            if index >= 10:
                break
        await ctx.send(message)
    else:
        await ctx.send("No durations recorded in the database.")


@bot.event
async def on_member_remove(member):
    leave_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    c.execute("SELECT join_time FROM members WHERE username=?", (member.name,))
    join_time = c.fetchone()[0]
    duration = datetime.datetime.strptime(leave_time, '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(join_time, '%Y-%m-%d %H:%M:%S')
    c.execute("UPDATE members SET leave_time=?, duration=? WHERE user_id=?", (leave_time, str(duration), member.id))
    conn.commit()

@bot.tree.command(name='update_commands', description='Owner only')
async def sync(interaction: discord.Interaction):
    if interaction.user.id == 647863394241609750:
        await bot.tree.sync()
        print('Command tree synced.')
        await interaction.response.send_message('bot tree sync',ephemeral=True)
    else:
        await interaction.response.send_message('Sorry g you aint me',ephemeral=True)

@bot.tree.command(name="update",description="add everyone to server")
async def user(interaction:discord.Interaction):
    if interaction.user.id == 647863394241609750:
        guild = interaction.guild
        print(f"Number of members in the guild: {len(guild.members)}")
        for member in guild.members:
            if member.joined_at:
                c.execute("INSERT INTO members VALUES (?, ?, ?, NULL, NULL)", (str(member.id), member.name, member.joined_at.strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        await interaction.response.send_message("All existing members have been added to the database.")
    else:
        await interaction.response.send_message("ARE YOU WISHY??")
bot.run("TEehee")
