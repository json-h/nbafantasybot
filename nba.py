from nba_api.stats.endpoints import commonplayerinfo, fantasywidget
from nba_api.stats.static import players
import json
import requests

def search_for_player(p_name):
    try:
        player = players.find_players_by_full_name(p_name)[0]
        id = player['id']
        info = fantasywidget.FantasyWidget(player_id_nullable=id)
        p_data = info.fantasy_widget_result.get_dict()['data']
        if not p_data:
            raise Exception("player probably not active")
        return p_data
    except:
        raise Exception("couldn't find the player")

def search_for_player_by_id(p_id):
    info = fantasywidget.FantasyWidget(player_id_nullable=p_id)
    p_data = info.fantasy_widget_result.get_dict()['data']
    if not p_data:
        raise Exception("player probably not active")
    return p_data