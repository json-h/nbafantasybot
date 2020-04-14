import mysql.connector
import config
import nba

bot_db = mysql.connector.connect(
  host="localhost",
  user=config.mysql["user"],
  passwd=config.mysql["passwd"],
  database=config.mysql["database"]
)

cur = bot_db.cursor()

#most team searches will be by name in case i allow owners to own more than one team

def add_team(t_name, t_owner, t_server):
    cur.execute("INSERT INTO teams(name, owner, server) VALUES (\"%s\", \"%s\", \"%s\")", (t_name, t_owner, t_server))
    bot_db.commit()

def delete_team(t_owner, t_server): 
    t_name = find_team_name(t_server, t_owner)[0].strip("'")
    t_id = find_team_id(t_name, t_server)[0]
    cur.execute("DELETE FROM teams WHERE owner = \"%s\" AND server = \"%s\"", (t_owner, t_server))
    cur.execute("DELETE FROM players WHERE tid =" + str(t_id))
    bot_db.commit()

#returns name of player added
def add_player_to_team(t_server, t_name, p_id):
    cur.execute("SELECT id FROM teams WHERE name = \"%s\" AND server = \"%s\"", (t_name, t_server))
    t_id = cur.fetchone()[0]
    cur.execute("INSERT INTO players(tid, pid) VALUES(\"%s\", \"%s\")", (t_id, p_id))
    bot_db.commit()

def remove_player_from_team(t_server, t_name, p_id):
    cur.execute("SELECT id FROM teams WHERE name = \"%s\" AND server = \"%s\"", (t_name, t_server))
    t_id = cur.fetchone()[0]
    cur.execute("DELETE FROM players WHERE tid = \"%s\" AND pid = \"%s\"", (t_id, p_id))
    bot_db.commit()

def get_teams_in_server(t_server):
    cur.execute("SELECT name, owner FROM teams WHERE server = \"%s\"", (t_server,))
    return cur.fetchall()
    
def check_if_already_own(t_server, t_owner):
    cur.execute("SELECT owner FROM teams WHERE owner = \"%s\" AND server = \"%s\"", (t_owner, t_server))
    for owners in cur:
        if owners[0].strip("'") == t_owner:
            return True
    return False

def check_if_name_exists(t_server, t_name):
    cur.execute("SELECT name FROM teams WHERE name = \"%s\" AND server = \"%s\"", (t_name, t_server))
    for names in cur:
        if names[0].strip("'") == t_name:
            return True
    return False

def find_team_name(t_server, t_owner):
    cur.execute("SELECT name FROM teams WHERE owner = \"%s\" AND server = \"%s\"", (t_owner, t_server))
    return cur.fetchone()

def find_team_owner(t_server, t_name):
    cur.execute("SELECT owner FROM teams WHERE name = \"%s\" AND server = \"%s\"", (t_name, t_server))
    return cur.fetchone()

def find_team_id(t_name, t_server):
    cur.execute("SELECT id FROM teams WHERE name = \"%s\" AND server = \"%s\"", (t_name, t_server))
    return cur.fetchone()

def find_player_ids_on_team(t_id):
    cur.execute("SELECT pid FROM players WHERE tid = \"%s\"", (t_id))
    return cur.fetchall()

def find_number_of_players_on_team(t_id):
    cur.execute("SELECT COUNT(*) FROM players WHERE tid = \"%s\"", (t_id))
    return cur.fetchone()
        


#def check_if_user_owns_team(t_server, t_name, t_owner):
#    cur.execute("SELECT owner FROM teams WHERE name = \"\'" + t_name + "\'\" AND owner = \"\'" + t_owner + "\'\" AND server = \"\'"+ t_server + "\'\"")
#    for teams in cur:
#        print (teams[0])
#        if teams[0].strip("'") == t_owner:
#            return True
#    return False
