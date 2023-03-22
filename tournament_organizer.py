import numpy as np
import pandas as pd
import json

from player import Player
from util import *


class TournamentOrganizer:
    def __init__(self, players, printing=True) -> None:
        # players
        if isinstance(players, list):
            # list of players
            if all([isinstance(p, Player) for p in players]):
                self.players = players
            # list of player ids
            elif all([isinstance(p, int) for p in players]):
                self.players = [Player(id=i) for i in players]
            else:
                raise TypeError("players is of wrong type.")
        elif isinstance(players, int):
            # playernumber given
            self.players = [Player(id=i + 1) for i in range(players)]
        else:
            raise TypeError("players is of wrong type.")

        self.number_of_players = len(self.players)

        self.printing = printing
        self.json_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "json_dumps")
        os.makedirs(self.json_path, exist_ok=True)

        # points
        self.p_win = 3
        self.p_draw = 1

        # weights for evaluation
        self.weight_badness = 1
        self.weight_variance = 1

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

        self.round = 0

        self.initialize_players()
        self.results_dict = {"rounds": [], "players": [p.id for p in self.players]}

    def initialize_players(self):
        for i, p in enumerate(self.players):
            p.id = i + 1  # 0 is prohibited
            p.TO = self

    def get_standings(self):
        # sort players by points
        self.standings = list(np.copy(self.players))
        # we shuffle the standings before sorting to prevent registration order mattering
        # TODO: this assumes, that during the swiss only scores matter, and no tiebreakers are used.
        np.random.shuffle(self.standings)

        def get_player_score(player: Player):
            return player.get_score()

        self.standings.sort(key=get_player_score, reverse=True)

        # print result
        self.print_standings()

    def get_final_standings(self):
        def get_tiebreaker_score(player: Player):
            # 1. sort by score
            # 2. add first tiebreaker
            # 3. add second tiebreaker

            return player.get_score(), player.get_OMWP(), player.total_seating_number

        self.standings.sort(key=get_tiebreaker_score, reverse=True)

        self.print_standings(show_tiebreakers=True)

    def print_standings(self, show_tiebreakers=False):
        if self.printing:
            print(yellow(f"\nStandings after Round {self.round}"))
            for i, p in enumerate(self.standings):
                p: Player
                player_stats = p.get_player_stats()
                # color high badness
                if player_stats[-1] >= 10:
                    player_stats[-1] = bred(player_stats[-1])
                elif player_stats[-1] >= 5:
                    player_stats[-1] = bmagenta(player_stats[-1])

                if show_tiebreakers:
                    row_template = "{:<2} {:<15} ID {:<2} Score {:<2}  OMWP: {:<6}  TSN: {:<2}  Badness Sum: {:<2}"
                else:
                    row_template = "{:<2} {:<15} ID {:<2} Score {:<2}  Badness Sum: {:<2}"
                    del player_stats[3:5]
                if i == 4 and show_tiebreakers:
                    print("--------------------------------")
                print(row_template.format(i + 1, *player_stats))

    def get_pairings(self, v=4):
        self.round += 1
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
        elif v == 2:
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
        elif v == 3:
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
        # Variante 4
        # combination of 2 and 3: select first player from among those with the highest score, but take the badest
        elif v == 4:
            open_players = self.standings.copy()
            for n in self.table_layout:
                table = []
                # select the n best suited players for this table
                for i in range(n):
                    # empty table: look for hight score players, take the one with highest badness
                    if len(table) == 0:
                        best_score = open_players[0].get_score()
                        badest_badness = 0
                        selected_player = open_players[0]
                        for p in open_players:
                            if p.get_score() == best_score and p.badness_sum > badest_badness:
                                badest_badness = p.badness_sum
                                selected_player = p
                            elif p.get_score() < best_score:
                                break
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
            print(yellow(f"\nPairings for Round {self.round}"))
            print(self.pairings_to_dataframe())

        # safe opponents of players
        for t in self.tables:
            for p in t:
                ops = t.copy()
                ops.remove(p)
                p.add_opponents(ops)

        self.old_pairings.append(self.tables)

        # json dump
        self.pairing_dict = {"placements": [{"players": [player.id for player in table]} for table in self.tables]}
        with open(os.path.join(self.json_path, f"Pairings_Round_{self.round}.json"), "w") as f:
            json.dump(self.pairing_dict, f, indent=4)

    def evaluate_pairings(self):
        table_badness = np.zeros(self.number_of_tables)
        table_variances = np.zeros(self.number_of_tables)
        for i, t in enumerate(self.tables):
            table_scores = []
            for p in t:
                table_badness[i] += p.current_badness
                table_scores.append(p.get_score())
            table_variances[i] = np.var(table_scores)

        J = self.weight_badness * sum(table_badness) + self.weight_variance * sum(table_variances)

        return J

    def set_results(self):
        # random results for testing
        current_round = []
        for t in self.tables:
            # draw
            if np.random.rand() > 0.8:
                current_round.append({"players": [p.id for p in t], "winner": 0})
            # win
            else:
                winner = np.random.choice(t)
                current_round.append({"players": [p.id for p in t], "winner": winner.id})

        self.results_dict["rounds"].append(current_round)

        with open(os.path.join(self.json_path, f"Results_Round_{self.round}.json"), "w") as f:
            json.dump(self.results_dict, f, indent=4)

    def load_results(self, file_name):
        # turn up the round counter
        for p in self.players:
            p: Player
            p.rounds_played += 1
        with open(os.path.join(self.json_path, file_name), "r") as f:
            res = json.load(f)
        # results of last round
        for table in res["rounds"][-1]:
            # sanity check
            assert {"players": table["players"]} in self.pairing_dict[
                "placements"
            ], "Results table does not match pairing table!"
            # draw
            if table["winner"] == 0:
                for player in table["players"]:
                    self.get_player_by_id(player).score += self.p_draw
            # win
            else:
                self.get_player_by_id(table["winner"]).score += self.p_win

    def get_player_by_id(self, id):
        # TODO: this can be done more efficient
        for player in self.players:
            if id == player.id:
                return player
        raise ValueError(f"ID {id} not found among players.")

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
        table_variances = np.zeros(self.number_of_tables)
        for i, t in enumerate(self.tables):
            table_scores = []
            for p in t:
                table_badness[i] += p.current_badness
                table_scores.append(p.get_score())
            table_variances[i] = np.var(table_scores)
        df.loc[len(df.index)] = table_badness
        df.loc[len(df.index)] = table_variances

        # df.index = ["Player 1", "Player 2", "Player 3", "Player 4", "Table Badness", "Table Score"]
        df.index = [*[f"Player {i+1}" for i in range(max(self.table_layout))], "Table Badness", "Tab. Sc. Var."]
        return df

    def get_badness_single_player(self, seated_players: list, possible_player: Player):
        badness = 0
        for p in seated_players:
            badness += flatten(p.opponents).count(possible_player) ** 2
            # square to prevent seeing the same op 3x or more
        return badness

    def get_best_next_player(self, seated_players: list, possible_players: list):
        # compare all open players w.r.t. their badness and select the best option
        badness_list = np.zeros_like(possible_players)
        for i, possible_player in enumerate(possible_players):
            badness_list[i] = self.get_badness_single_player(seated_players, possible_player)

        # argmin selects the first occurance if multiple occur, prioritizing the highest rated player
        best_player = possible_players[np.argmin(badness_list)]

        return best_player

    def simulate_tournament(self):
        for i in range(self.number_of_rounds):
            self.get_pairings()
            self.set_results()
            self.load_results(f"Results_Round_{i+1}.json")
            # skip standing after last round
            if i + 1 < self.number_of_rounds:
                self.get_standings()

        self.get_final_standings()
        s = 0
        for p in self.players:
            s += p.badness_sum
        if self.printing:
            print(f"\nav. player badness sum: {s / self.number_of_players}")
