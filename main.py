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



bot.remove_command("help")
async def on_ready():
    print('Bot is ready.')


@bot.command()
async def sync(ctx):
    print("sync command")
    await bot.tree.sync()
    bot.remove_command("help")
    bot.remove_command("add_members")


conn.commit()
# ---------------------------------------------------------------------------------------------------------
@bot.event
async def on_member_join(member):
    c.execute("SELECT user_id FROM members WHERE user_id=?", (str(member.id),))
    existing_user = c.fetchone()
    if not existing_user:
        join_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        c.execute("INSERT INTO members VALUES (?, ?, ?, NULL, NULL)", (str(member.id), member.name, join_time))
        conn.commit()
    elif existing_user: # if they do exist
        join_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        c.execute("UPDATE members SET username = ?, join_time = ?, leave_time = NULL, duration = NULL WHERE user_id = ?",(member.name, join_time, str(member.id)))
        conn.commit()

@bot.event
async def on_member_remove(member):
    leave_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    c.execute("SELECT join_time FROM members WHERE user_id=?", (member.id,))
    join_time = c.fetchone()[0]
    duration = datetime.datetime.strptime(leave_time, '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(join_time, '%Y-%m-%d %H:%M:%S')
    days = duration.days
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if days > 0:
        duration_str = f"{days} days {hours} hours {minutes} minutes"
    elif hours > 0:
        duration_str = f"{hours} hours {minutes} minutes"
    elif hours > 0 and minutes == 1:
        duration_str = f"{hours} hours {minutes} minute"
    elif minutes > 0:
        duration_str = f"{minutes} minute {seconds} seconds"
    else:
        duration_str = f"{seconds} seconds "
    c.execute("UPDATE members SET leave_time=?, duration=? WHERE user_id=?", (leave_time, str(duration_str), member.id))
    conn.commit()

# commands --------------------------------------------------------------------------------------------------------------------
@bot.command(name="longest_stays", description="Displays the first joins of members")
async def first_joins(ctx):
    c.execute("SELECT username, join_time FROM members WHERE join_time IS NOT NULL AND leave_time IS NULL")
    rows = c.fetchall()
    
    if rows:
        sorted_rows = sorted(rows, key=lambda x: datetime.datetime.utcnow() - datetime.datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S'), reverse=True)
        embed = discord.Embed(title="Longest stay", color=discord.Color.green())
        
        for index, row in enumerate(sorted_rows[:10], start=1):
            time_stayed = datetime.datetime.utcnow() - datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
            days = time_stayed.days
            hours, remainder = divmod(time_stayed.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            if days > 0:
                duration_str = f"{days} days {hours} hours {minutes} minutes"
            elif hours > 0:
                duration_str = f"{hours} hours {minutes} minutes"
            elif minutes > 0:
                duration_str = f"{minutes} minutes {seconds} seconds"
            else:
                duration_str = f"{seconds} seconds"
            
            embed.add_field(name=f"{index}. {row[0]}", value=duration_str, inline=False)
        
        await ctx.send(embed=embed)
    else:
        await ctx.send("No members recorded in the database.")
         
@bot.command(name="ls", description="Displays the first joins of members")
async def first_joins(ctx):
    c.execute("SELECT username, join_time FROM members WHERE join_time IS NOT NULL AND leave_time IS NULL")
    rows = c.fetchall()
    
    if rows:
        sorted_rows = sorted(rows, key=lambda x: datetime.datetime.utcnow() - datetime.datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S'), reverse=True)
        embed = discord.Embed(title="Longest stay", color=discord.Color.green())
        
        for index, row in enumerate(sorted_rows[:10], start=1):
            time_stayed = datetime.datetime.utcnow() - datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
            days = time_stayed.days
            hours, remainder = divmod(time_stayed.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            if days > 0:
                duration_str = f"{days} days {hours} hours {minutes} minutes"
            elif hours > 0:
                duration_str = f"{hours} hours {minutes} minutes"
            elif minutes > 0:
                duration_str = f"{minutes} minute {seconds} seconds"
            else:
                duration_str = f"{seconds} seconds "
            
            embed.add_field(name=f"{index}. {row[0]}", value=duration_str, inline=False)
        
        await ctx.send(embed=embed)
    else:
        await ctx.send("No members recorded in the database.")


@bot.command(name="latest_joins", description="Shows the last people who joined")
async def latest_joins(ctx):
    c.execute("SELECT username, join_time FROM members WHERE join_time IS NOT NULL")
    rows = c.fetchall()
    
    if rows:
        sorted_rows = sorted(rows, key=lambda x: datetime.datetime.utcnow() - datetime.datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S'), reverse=False)
        embed = discord.Embed(title="Latest Joins", color=discord.Color.orange())
        
        for index, row in enumerate(sorted_rows[:10], start=1):
            join_time = datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
            time_since_join = datetime.datetime.utcnow() - join_time
            days = time_since_join.days
            hours, remainder = divmod(time_since_join.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            if days > 0:
                duration_str = f"{days} days {hours} hours {minutes} minutes ago"
            elif hours > 0:
                duration_str = f"{hours} hours {minutes} minutes ago"
            elif minutes > 0:
                duration_str = f"{minutes} minutes {seconds} seconds ago"
            else:
                duration_str = f"{seconds} seconds ago"
            
            embed.add_field(name=f"{index}. {row[0]}", value=duration_str, inline=False)
        
        await ctx.send(embed=embed)
    else:
        await ctx.send("No members recorded in the database.")


@bot.command(name="lj", description="Shows the last people who joined")
async def latest_joins(ctx):
    c.execute("SELECT username, join_time FROM members WHERE join_time IS NOT NULL")
    rows = c.fetchall()
    
    if rows:
        sorted_rows = sorted(rows, key=lambda x: datetime.datetime.utcnow() - datetime.datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S'), reverse=False)
        embed = discord.Embed(title="Latest Joins", color=discord.Color.orange())
        
        for index, row in enumerate(sorted_rows[:10], start=1):
            join_time = datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
            time_since_join = datetime.datetime.utcnow() - join_time
            days = time_since_join.days
            hours, remainder = divmod(time_since_join.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            if days > 0:
                duration_str = f"{days} days {hours} hours {minutes} minutes ago"
            elif hours > 0:
                duration_str = f"{hours} hours {minutes} minutes ago"
            elif minutes > 0:
                duration_str = f"{minutes} minutes {seconds} seconds ago"
            else:
                duration_str = f"{seconds} seconds ago"
            
            embed.add_field(name=f"{index}. {row[0]}", value=duration_str, inline=False)
        
        await ctx.send(embed=embed)
    else:
        await ctx.send("No members recorded in the database.")







@bot.tree.command(name="lookup", description="Look up someone")
async def lookup(interaction: discord.Interaction, id: str):
    
    c.execute("SELECT join_time, leave_time, duration FROM members WHERE user_id = ?", (str(id),))
    person = c.fetchone()
    
    if not person:
        await interaction.response.send_message("User has never joined the server", ephemeral=True)
        return
    join_time = datetime.datetime.strptime(person[0], '%Y-%m-%d %H:%M:%S')
    join_time_str = join_time.strftime('%b %d %Y')
    info = await bot.fetch_user(int(id))
    embed = discord.Embed(title=f"{info.name}")
    embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url, url="https://github.com/Wishy8839")
    embed.add_field(name="Join time", value=f"{join_time_str}")
    if person[1]:
        leave_time = datetime.datetime.strptime(person[1], '%Y-%m-%d %H:%M:%S')
        leave_time_str = leave_time.strftime('%b %d, %Y')
        embed.add_field(name="Leave time", value=f"{leave_time_str}")
        embed.add_field(name="Total stay", value=person[2])
    else:
        time_stayed = datetime.datetime.utcnow() - datetime.datetime.strptime(person[0], '%Y-%m-%d %H:%M:%S')
        days = time_stayed.days
        hours, remainder = divmod(time_stayed.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if days > 0:
            duration_str = f"{days} days {hours} hours {minutes} minutes"
        elif hours > 0:
            duration_str = f"{hours} hours {minutes} minutes"
        elif hours > 0 and minutes == 1:
            duration_str = f"{hours} hours {minutes} minute"
        elif minutes > 0:
            duration_str = f"{minutes} minute {seconds} seconds"
        else:
            duration_str = f"{seconds} seconds "
        embed.add_field(name="Leave time", value="Never left")
        embed.add_field(name="Total stay", value=f"{duration_str}")

    embed.set_thumbnail(url=info.avatar.url)
    await interaction.response.send_message(embed=embed)




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

bot.run("SFJWO(9238f-2581r/!fn1F(!JHT(!HJT(!@HJTY(@HJTYHIIAMWISHYWHWOAREYOU")
