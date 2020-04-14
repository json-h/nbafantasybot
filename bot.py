from discord.ext import commands
import discord
import config
import sql
import nba
import cogs

bot = commands.Bot(command_prefix='!')
bot.remove_command('help')

@bot.event
async def on_ready():
    print("Logged in as", bot.user.name)

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="NBAbot", color=0x000000)
    embed.add_field(name="!stats (player name)", value="Retrieves the stats of the player's current season.", inline=False)
    embed.add_field(name="!create (name)", value="Creates your team. You can only own one team.", inline=False)
    embed.add_field(name="!delete", value="Deletes your team.", inline=False)
    embed.add_field(name="!addp (player name)", value="Adds the player to your team.", inline=False)
    embed.add_field(name="!removep (player name)", value="Deletes the player from your team.", inline=False)
    embed.add_field(name="!teams", value="Lists all of the teams currently in the server.", inline=False)
    embed.add_field(name="!avg (team)", value="Gets the average stats calculated from all the players currently on your team.", inline=False)
    embed.add_field(name="!players (team name)", value="Lists all the players on the specified team. If no team is specified, finds the players from your team.", inline=False)
    embed.set_footer(text="Created by Jason Han (big guy#1196)")
    await ctx.send(embed=embed)

@bot.command()
async def stats(ctx, *p_name):
    player_name = " ".join(p_name)
    try:
        p_data = nba.search_for_player(" ".join(p_name))
    except:
        embed = discord.Embed(description="I couldn't find the player \"" + player_name + "\"  :(\nHe probably hasn't played any games this season.", color=0x000000)
        await ctx.send(embed=embed)
        return
    #making percentages look nice
    if p_data[0][19] < 1:
        ftpct = str(p_data[0][19])[1:]
    else:
        ftpct = str(p_data[0][19]) + "00"
    if p_data[0][17] < 1:
        fgpct = str(p_data[0][17])[1:]
    else:
        fgpct = str(p_data[0][17]) + "00"
    #creating the message
    embed = discord.Embed(title=str(p_data[0][1]), description=str(p_data[0][4]), color=0x000000)
    embed.add_field(name="**FG%**", value=fgpct, inline=True)
    embed.add_field(name="**FT%**", value=ftpct, inline=True)
    embed.add_field(name="**3PM**", value=str(p_data[0][15]), inline=True)
    embed.add_field(name="**PTS**", value=str(p_data[0][9]), inline=True)
    embed.add_field(name="**REB**", value=str(p_data[0][10]), inline=True)
    embed.add_field(name="**AST**", value=str(p_data[0][11]), inline=True)
    embed.add_field(name="**STL**", value=str(p_data[0][13]), inline=True)
    embed.add_field(name="**BLK**", value=str(p_data[0][12]), inline=True)
    embed.add_field(name="**TOV**", value=str(p_data[0][14]), inline=True)
    embed.set_thumbnail(url=f"https://nba-players.herokuapp.com/players/"+p_data[0][1].split(" ")[1]+"/"+p_data[0][1].split(" ")[0])
    await ctx.send(embed=embed)

@bot.command()
async def create(ctx, *t_name_input):
    t_owner = str(ctx.author)
    t_server = str(ctx.guild)
    if not t_name_input:
        embed = discord.Embed(description= "You need to input a name.", color=0x000000)
        await ctx.send(embed=embed)
        return
    already_owned = sql.check_if_already_own(t_server, t_owner)
    if already_owned == True:
        embed = discord.Embed(description= "You already own a team in this server!", color=0x000000)
        await ctx.send(embed=embed)
        return
    t_name = " ".join(t_name_input)
    name_exists = sql.check_if_name_exists(t_server, t_name)
    if name_exists == True:
        embed = discord.Embed(description= "Someone already owns a team with that name!", color=0x000000)
        await ctx.send(embed=embed)
        return
    sql.add_team(t_name, t_owner, t_server)
    embed = discord.Embed(title=t_name + " has been created!", description= "List of current teams in this server:", color=0x000000)
    server_teams = sql.get_teams_in_server(t_server)    
    for teams in server_teams:
            embed.add_field(name=str(teams[1]).strip("'"), value=str(teams[0]).strip("'"), inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def delete(ctx):
    t_owner = str(ctx.author)
    t_server = str(ctx.guild)
    is_owner = sql.check_if_already_own(t_server, t_owner)
    if is_owner == False:
        embed = discord.Embed(description= "You don't currently have a team.", color=0x000000)
        await ctx.send(embed=embed)
        return
    sql.delete_team(t_owner, t_server)
    embed = discord.Embed(description= "Your team has been deleted :(" , color=0x000000)
    await ctx.send(embed=embed)
    return

@bot.command()
async def teams(ctx):
    t_server = str(ctx.guild)
    embed = discord.Embed(title="Current teams in this server:", color=0x000000)
    server_teams = sql.get_teams_in_server(t_server)
    if not server_teams:
        embed.add_field(name = "None", value=":(", inline=True)
    else:
        for teams in server_teams:
            embed.add_field(name=str(teams[1]).strip("'"), value=str(teams[0]).strip("'"), inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def addp(ctx, *p_name):
    t_owner = str(ctx.author)
    t_server = str(ctx.guild)
    is_owner = sql.check_if_already_own(t_server, t_owner)
    player_name = " ".join(p_name)
    if is_owner == False:
        embed = discord.Embed(description= "You don't have a team to add players to!", color=0x000000)
        await ctx.send(embed=embed)
        return
    t_name = sql.find_team_name(t_server, t_owner)[0].strip("'")
    t_id = sql.find_team_id(t_name, t_server)
    num_players = sql.find_number_of_players_on_team(t_id)[0]
    if num_players >= 13:
        embed = discord.Embed(description= "You can only have up to 13 players on your team.", color=0x000000)
        await ctx.send(embed=embed)
        return
    try:
        p_data = nba.search_for_player(player_name)
    except:
        embed = discord.Embed(description="I couldn't find the player \"" + player_name + "\"  :(", color=0x000000)
        await ctx.send(embed=embed)
        return
    p_id = sql.find_player_ids_on_team(t_id)
    for ids in p_id:
        if ids[0] == p_data[0][0]:
            embed = discord.Embed(description=str(p_data[0][1]) + " is already on your team!", color=0x000000)
            await ctx.send(embed=embed)
            return
    sql.add_player_to_team(t_server, t_name, p_data[0][0])
    embed = discord.Embed(description= str(p_data[0][1]) + " has been added to your team!", color=0x000000)
    await ctx.send(embed=embed)
    return

@bot.command()
async def removep(ctx, *p_name):
    t_owner = str(ctx.author)
    t_server = str(ctx.guild)
    is_owner = sql.check_if_already_own(t_server, t_owner)
    player_name = " ".join(p_name)
    if is_owner == False:
        embed = discord.Embed(description= "You don't have a team to remove players from!", color=0x000000)
        await ctx.send(embed=embed)
        return
    try:
        p_data = nba.search_for_player(player_name)
    except:
        embed = discord.Embed(description="I couldn't find the player \"" + player_name + "\"  :(", color=0x000000)
        await ctx.send(embed=embed)
        return
    t_name = sql.find_team_name(t_server, t_owner)[0].strip("'")
    t_id = sql.find_team_id(t_name, t_server)
    p_id = sql.find_player_ids_on_team(t_id)
    for ids in p_id:
        if ids[0] == p_data[0][0]:
            sql.remove_player_from_team(t_server, t_name, p_data[0][0])
            embed = discord.Embed(description=str(p_data[0][1]) + " has been removed from your team!", color=0x000000)
            await ctx.send(embed=embed)
            return
    embed = discord.Embed(description="It doesn't look like " + str(p_data[0][1]) + " is on your team.", color=0x000000)
    await ctx.send(embed=embed)
    
@bot.command()
async def players(ctx, *t_name_input):
    t_server = str(ctx.guild)
    if len(t_name_input) == 0:
        t_owner = str(ctx.author)
        is_owner = sql.check_if_already_own(t_server, t_owner)
        if is_owner == False:
            embed = discord.Embed(description= "You don't have a team. You can create one using !create (name)", color=0x000000)
            await ctx.send(embed=embed)
            return
        t_name = sql.find_team_name(t_server, t_owner)[0].strip("'")
    else:
        t_name = " ".join(t_name_input)
        name_exists = sql.check_if_name_exists(t_server, t_name)
        if name_exists == False:
            embed = discord.Embed(description= "That team doesn't exist!", color=0x000000)
            await ctx.send(embed=embed)
            return
        t_owner = sql.find_team_owner(t_server, t_name)[0].strip("'")
    t_id = sql.find_team_id(t_name, t_server)
    players_on_team = sql.find_player_ids_on_team(t_id)
    embed = discord.Embed(title=t_name, description=t_owner, color=0x000000)
    if not players_on_team:
        embed.add_field(name = "None", value=":(", inline=True)
    else:
        for player in players_on_team:
            p_data = nba.search_for_player_by_id(player[0])
            embed.add_field(name="**" + str(p_data[0][2]) + "**", value=str(p_data[0][1]), inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def avg(ctx, *t_name_input):
    t_server = str(ctx.guild)
    t_name = " ".join(t_name_input)
    name_exists = sql.check_if_name_exists(t_server, t_name)
    if name_exists == False:
        embed = discord.Embed(description= "That team doesn't exist!", color=0x000000)
        await ctx.send(embed=embed)
        return
    t_owner = sql.find_team_owner(t_server, t_name)[0].strip("'")
    t_id = sql.find_team_id(t_name, t_server)
    fgm, fga, ftm, fta, three_pm, pts, reb, ast, stl, blk, tov = (0.0,)*11
    num_players = 0
    players_on_team = sql.find_player_ids_on_team(t_id)
    embed = discord.Embed(title="**" + t_name + "**",description=t_owner + "'s team", color=0x000000)
    if not players_on_team:
        embed.add_field(name = "None", value=":(", inline=True)
        await ctx.send(embed=embed)
    else:
        for player in players_on_team:
            p_data = nba.search_for_player_by_id(player[0])
            num_players = num_players + 1
            #fgm = fga * fg%
            fgm += p_data[0][16] * p_data[0][17]
            fga += p_data[0][16]
            #ftm = fta * ft%
            ftm += p_data[0][18] * p_data[0][19]
            fta += p_data[0][18]
            three_pm += p_data[0][15]
            pts += p_data[0][9]
            reb += p_data[0][10]
            ast += p_data[0][11]
            stl += p_data[0][13]
            blk += p_data[0][12]
            tov += p_data[0][14]
    fgpct = cogs.formatFloat(str(fgm/fga))
    ftpct = cogs.formatFloat(str(ftm/fta))
    embed.add_field(name="**FG%**", value=fgpct, inline=True)
    embed.add_field(name="**FT%**", value=ftpct, inline=True)
    embed.add_field(name="**3PM**", value="{:.1f}".format(three_pm/num_players), inline=True)
    embed.add_field(name="**PTS**", value="{:.1f}".format(pts/num_players), inline=True)
    embed.add_field(name="**REB**", value="{:.1f}".format(reb/num_players), inline=True)
    embed.add_field(name="**AST**", value="{:.1f}".format(ast/num_players), inline=True)
    embed.add_field(name="**STL**", value="{:.1f}".format(stl/num_players), inline=True)
    embed.add_field(name="**BLK**", value="{:.1f}".format(blk/num_players), inline=True)
    embed.add_field(name="**TOV**", value="{:.1f}".format(tov/num_players), inline=True)
    await ctx.send(embed=embed)


#will be needed if users are allowed to have more than one team

#@bot.command()
#async def delete(ctx, *t_name_input):
#    t_owner = str(ctx.author)
#    t_server = str(ctx.guild)
#    t_name = " ".join(t_name_input)
#    name_exists = data.check_if_name_exists(t_server, t_name)
#    if name_exists == False:
#        embed = discord.Embed(description= "That team doesn't exist :(", color=0x000000)
#        await ctx.send(embed=embed)
#        return
#    is_owner = data.check_if_user_owns_team(t_server, t_name, t_owner)
#    if is_owner == False:
#        embed = discord.Embed(description= "That's not your team!", color=0x000000)
#        await ctx.send(embed=embed)
#        return
#    data.delete_team(t_name, t_server)
#    embed = discord.Embed(description= "Your team \"" + t_name + "\" has been deleted :(" , color=0x000000)
#    await ctx.send(embed=embed)
#    return


#need a config file with the token inside
bot.run(config.token["token"])
