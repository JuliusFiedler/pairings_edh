import numpy as np
from player import Player
from util import *

class TournamentOrganizer():
    def __init__(self, players) -> None:
        self.players = players
        self.number_of_players = len(players)
        
        # points 
        self.p_win = 3
        self.p_draw = 1

        # players
        assert self.number_of_players > 5, "too few players, tournament is canceled"

        # rounds and tables:
        self.number_of_rounds = np.ceil(np.log2(self.number_of_players))
        self.number_of_tables = np.ceil(self.number_of_players / 4)
        """
        players = x*4 + y*3
        tables = x + y
        """
        n4 = int(self.number_of_players - 3 * self.number_of_rounds)
        n3 = int(self.number_of_tables - n4)

        self.table_layout = np.array(np.hstack((4 * np.ones(n4), 3 * np.ones(n3))), dtype=int)
        self.old_pairings = []
        
        # get initial (random) standings
        self.standings = list(np.copy(self.players))
        np.random.shuffle(self.standings)
    
    def calc_standings(self):
        self.standings = list(np.copy(self.players))
        def get_player_score(player: Player):
            return player.get_score()
        self.standings.sort(key=get_player_score, reverse=True)
        # print result
        for p in self.standings:
            p.print_player()
        
    def calc_pairings(self):
        self.tables = []
        index = 0
        for t in self.table_layout:
            self.tables.append(self.standings[index:index+t])
            index += t
        
        self.old_pairings.append(self.tables)
        # print result
        for i, t in enumerate(self.tables):
            print(bright(f"Table {i}"))
            for p in t:
                p.print_player()
    