import numpy as np
from player import Player
from util import *
import pandas as pd


class TournamentOrganizer:
    def __init__(self, players) -> None:
        self.players = players
        self.number_of_players = len(players)

        # points
        self.p_win = 3
        self.p_draw = 1

        # players
        assert self.number_of_players > 5, "too few players, tournament is canceled"

        # rounds and tables:
        self.number_of_rounds = int(np.ceil(np.log2(self.number_of_players)))
        self.number_of_tables = int(np.ceil(self.number_of_players / 4))
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
        print(yellow(f"Standings"))
        for p in self.standings:
            p.print_player()

    def calc_pairings(self):
        # pair from top to bottom, first against next best 3 and so on
        self.tables = []
        index = 0
        for t in self.table_layout:
            self.tables.append(self.standings[index : index + t])
            index += t

        # print result
        print(yellow(f"Pairings"))
        for i, t in enumerate(self.tables):
            # print(bright(f"Table {i}"))
            for p in t:
                # p.print_player()
                badness = 0
                if len(p.opponents) > 0:
                    for op in flatten(p.opponents):
                        if op in t:
                            badness += 1
                # print(f"  badness: {badness}")
                p.current_badness = badness
                p.badness_sum += badness

        print(self.pairings_to_dataframe())

        # safe opponents of players
        for t in self.tables:
            for p in t:
                ops = t.copy()
                ops.remove(p)
                p.add_opponents(ops)

        self.old_pairings.append(self.tables)

    def set_results(self):
        for t in self.tables:
            # draw
            if np.random.rand() > 0.8:
                for p in t:
                    p.score += self.p_draw
            # win
            else:
                np.random.choice(t).score += self.p_win

    def pairings_to_dataframe(self):
        df = pd.DataFrame(self.tables).T
        df.columns = [f"Table {i}" for i in range(self.number_of_tables)]

        def pretty(player):
            if player is not None:
                return [player.name, player.score, player.current_badness]
            else:
                return player

        df = df.applymap(pretty)
        table_badness = np.zeros(self.number_of_tables)
        for i, t in enumerate(self.tables):
            for p in t:
                table_badness[i] += p.current_badness

        df.loc[len(df.index)] = table_badness

        df.index = ["Player 1", "Player 2", "Player 3", "Player 4", "Table Badness"]
        return df
