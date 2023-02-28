import numpy as np
from player import Player
from util import *
import pandas as pd


class TournamentOrganizer:
    def __init__(self, players, printing=True) -> None:
        self.players = players
        self.number_of_players = len(players)

        self.printing = printing

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
        n4 = int(self.number_of_players - 3 * self.number_of_tables)
        n3 = int(self.number_of_tables - n4)

        self.table_layout = np.array(np.hstack((4 * np.ones(n4), 3 * np.ones(n3))), dtype=int)
        self.old_pairings = []

        # get initial (random) standings
        self.standings = list(np.copy(self.players))
        np.random.shuffle(self.standings)

        self.round = 1

        self.say_hello_to_players()

    def say_hello_to_players(self):
        for p in self.players:
            p.TO = self

    def calc_standings(self):
        # sort players by points
        self.standings = list(np.copy(self.players))

        def get_player_score(player: Player):
            return player.get_score()

        self.standings.sort(key=get_player_score, reverse=True)

        # print result
        self.print_standings()

    def calc_final_standings(self):
        def get_tiebreaker_score(player: Player):
            numerical_key = 0
            # 1. sort by score
            numerical_key += player.get_score()
            # 2. add first tiebreaker
            numerical_key += player.get_OMWP()  # 0.33 < OMWP <= 1
            # 3. add second tiebreaker
            numerical_key += (
                player.total_seating_number * 1e-3
            )  # make sure this is always smaller than first tiebreaker

            return numerical_key

        self.standings.sort(key=get_tiebreaker_score, reverse=True)

        self.print_standings(show_tiebreakers=True)

    def print_standings(self, show_tiebreakers=False):
        if self.printing:
            print(yellow(f"Standings after Round {self.round -1}"))
            for i, p in enumerate(self.standings):
                p: Player
                player_stats = p.get_player_stats()
                # color high badness
                if player_stats[-1] >= 10:
                    player_stats[-1] = bred(player_stats[-1])
                elif player_stats[-1] >= 5:
                    player_stats[-1] = bmagenta(player_stats[-1])

                if show_tiebreakers:
                    row_template = "{:<2} {:<15} Score {:<2}  OMWP: {:<5}  TSN: {:<2}  Badness Sum: {:<2}"
                else:
                    row_template = "{:<2} {:<15} Score {:<2}  Badness Sum: {:<2}"
                    del player_stats[2:4]
                if i == 4 and show_tiebreakers:
                    print("--------------------------------")
                print(row_template.format(i + 1, *player_stats))

    def calc_pairings(self, v=2):
        self.tables = []
        # Variante 1
        # pair from top to bottom, first against next best 3 and so on (very basic)
        if v == 1:
            index = 0
            for n in self.table_layout:
                self.tables.append(self.standings[index : index + n])
                index += n

        # Variante 2
        # pair from the top, but select the player with the least badness for the next open spot
        # on the table
        if v == 2:
            open_players = self.standings.copy()
            for n in self.table_layout:
                table = []
                # select the n best suited players for this table
                for i in range(n):
                    # table is empty, take first placed player
                    if len(table) == 0:
                        table.append(open_players.pop(0))
                    # search for least badness among open players
                    else:
                        next_player = self.get_best_next_player(table, open_players)
                        table.append(next_player)
                        open_players.remove(next_player)

                # randomize seating
                np.random.shuffle(table)
                self.tables.append(table)

        # Variante 3
        # start pairing with the person with the highest badness sum so far and minimize
        # their badness
        if v == 3:
            open_players = self.standings.copy()
            for n in self.table_layout:
                table = []
                # select the n best suited players for this table
                for i in range(n):
                    # table is empty, take player with highest badness so far
                    if len(table) == 0:
                        badest_badness = 0
                        selected_player = open_players[0]
                        for p in open_players:
                            if p.badness_sum > badest_badness:
                                badest_badness = p.badness_sum
                                selected_player = p
                        table.append(selected_player)
                        open_players.remove(selected_player)
                    # search for least badness among open players
                    else:
                        next_player = self.get_best_next_player(table, open_players)
                        table.append(next_player)
                        open_players.remove(next_player)

                # randomize seating
                np.random.shuffle(table)
                self.tables.append(table)

        # calc player badness and track player seatings
        for i, t in enumerate(self.tables):
            for pos, p in enumerate(t):
                p: Player
                badness = 0
                for current_op in t:
                    badness += flatten(p.opponents).count(current_op) ** 2
                p.current_badness = badness
                p.badness_sum += badness

                p.total_seating_number += pos + 1  # +1 in order to have positions 1 to 4 for the plebs
                # TODO is this only relevant if you win?

        # print result
        if self.printing:
            print(yellow(f"Pairings for Round {self.round}"))
            print(self.pairings_to_dataframe())

        # safe opponents of players
        for t in self.tables:
            for p in t:
                ops = t.copy()
                ops.remove(p)
                p.add_opponents(ops)

        self.old_pairings.append(self.tables)

    def set_results(self):
        # turn up the round counter
        self.round += 1
        for p in self.players:
            p: Player
            p.rounds_palyed += 1

        # random results for testing
        winners = []
        drawers = []
        for t in self.tables:
            # draw
            if np.random.rand() > 0.8:
                for p in t:
                    p.score += self.p_draw
                    drawers.append(p.name)
            # win
            else:
                winner = np.random.choice(t)
                winner.score += self.p_win
                winners.append(winner.name)
        # df = self.pairings_to_dataframe()
        # def color_by_res(entry):
        #     try:
        #         if entry[0] in winners:
        #             return bgreen(entry)
        #         elif entry[0] in drawers:
        #             return bblue(entry)
        #         else:
        #             return entry
        #     except TypeError:
        #         return entry

        # df = df.applymap(color_by_res)
        # if self.printing:
        #     print(df)

    def pairings_to_dataframe(self):
        # compact visualization of the pairing tables
        df = pd.DataFrame(self.tables).T
        df.columns = [f"Table {i+1}" for i in range(self.number_of_tables)]

        # replace player object with name and data
        def pretty(player):
            if player is not None:
                return [player.name, player.score, player.current_badness]
            else:
                return player

        df = df.applymap(pretty)

        # add row for badness of table
        # add row for total table score (see if strong players play eachother)
        table_badness = np.zeros(self.number_of_tables)
        table_score = np.zeros(self.number_of_tables)
        for i, t in enumerate(self.tables):
            for p in t:
                table_badness[i] += p.current_badness
                table_score[i] += p.score
        df.loc[len(df.index)] = table_badness
        df.loc[len(df.index)] = table_score

        # df.index = ["Player 1", "Player 2", "Player 3", "Player 4", "Table Badness", "Table Score"]
        df.index = [*[f"Player {i+1}" for i in range(max(self.table_layout))], "Table Badness", "Table Score"]
        return df

    def calc_badness_single_player(self, seated_players: list, possible_player: Player):
        badness = 0
        for p in seated_players:
            badness += flatten(p.opponents).count(possible_player) ** 2
            # square to prevent seeing the same op 3x or more
        return badness

    def get_best_next_player(self, seated_players: list, possible_players: list):
        # compare all open players w.r.t. their badness and select the best option
        badness_list = np.zeros_like(possible_players)
        for i, possible_player in enumerate(possible_players):
            badness_list[i] = self.calc_badness_single_player(seated_players, possible_player)

        # argmin selects the first occurance if multiple occur, prioritizing the highest rated player
        best_player = possible_players[np.argmin(badness_list)]

        return best_player

    def simulate_tournament(self):
        for i in range(self.number_of_rounds):
            self.calc_pairings()
            self.set_results()
            self.calc_standings()

        self.calc_final_standings()
