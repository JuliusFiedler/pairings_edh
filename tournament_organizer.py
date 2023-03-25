import sys
import numpy as np
import pandas as pd
import json
import shutil
from ipydex import IPS

from player import Player
from util import *


class TournamentOrganizer:
    def __init__(self, players, printing=None, seed=None):
        # load config file
        with open("config.json", "r") as f:
            config = json.load(f)
        if printing is None:
            self.printing = config["console_printing"] == "True"
        else:
            self.printing = printing
        if seed is None:
            self.seed = config["seed"]
        else:
            self.seed = seed
        self.pairing_variant = config["pairing_variant"]
        self.seating_variant = config["seating_variant"]

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
        assert self.number_of_players > 5, "too few players, tournament is canceled"

        # setup json dir
        self.json_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), config["relative_json_path"])
        os.makedirs(self.json_path, exist_ok=True)

        # points
        self.p_win = 3
        self.p_draw = 1

        # weights for evaluation
        self.weight_badness = 1
        self.weight_variance = 1

        # rounds and tables:
        self.setup_tables()

        # get initial (random) standings
        np.random.seed(self.seed)
        self.standings = list(np.copy(self.players))
        np.random.shuffle(self.standings)

        self.round = 0

        self.initialize_players()
        self.results_dict = {"rounds": [], "players": [p.id for p in self.players]}

    def drop_players(self, players_ids):
        if isinstance(players_ids, int):
            players_ids = [players_ids]
        for id in players_ids:
            player = self.get_player_by_id(id)
            self.players.remove(player)
            self.standings.remove(player)
        # reevaluate table setup with fewer players
        self.setup_tables()

    def setup_tables(self):
        """calculate appropriate table layout for given number of players"""
        self.number_of_rounds = int(np.ceil(np.log2(self.number_of_players)))
        self.number_of_tables = int(np.ceil(self.number_of_players / 4))
        """
        players = x*4 + y*3
        tables = x + y
        """
        n4 = int(self.number_of_players - 3 * self.number_of_tables)
        n3 = int(self.number_of_tables - n4)

        assert n4 * 4 + n3 * 3 == self.number_of_players, "Math doesnt check out."

        self.table_layout = np.array(np.hstack((4 * np.ones(n4), 3 * np.ones(n3))), dtype=int)

    def initialize_players(self):
        for i, p in enumerate(self.players):
            p.TO = self

    def get_standings(self):
        """calculate standings using the tiebreaker system: score, OMW%, TSN
        Also dump standing to json file"""

        def get_tiebreaker_score(player: Player):
            # 1. sort by score
            # 2. add first tiebreaker
            # 3. add second tiebreaker

            return player.get_score(), player.get_OMWP(), player.total_seating_number

        self.standings.sort(key=get_tiebreaker_score, reverse=True)

        self.print_standings()

        # json export
        standing_dict = {
            "header": ["#", "Name", "Score", "OMW%", "TSN"],
            "header_description": [
                "Place",
                "Player Name",
                f"Player Score ({self.p_win}/{self.p_draw}/0)",
                "Opponents Match Win Percentage",
                "Total Seating Number (high=harder=better)",
            ],
            "standings": {},
        }
        for i, p in enumerate(self.standings):
            p: Player
            standing_dict["standings"][i + 1] = [p.id, p.score, p.get_OMWP(), p.total_seating_number]
        # with open(os.path.join(self.json_path, f"Standings_after_Round_{self.round}.json"), "w") as f:
        #     json.dump(standing_dict, f, indent=4)

    def print_standings(self):
        """print standings in console"""
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

                row_template = "{:<2} {:<15} ID {:<2} Score {:<2}  OMWP: {:<6}  TSN: {:<2}  Badness Sum: {:<2}"

                if i == 4:
                    print("--------------------------------")
                print(row_template.format(i + 1, *player_stats))

    def get_pairings(self):
        """generate pairings using the selected method. Dump pairings to json file"""
        # sort players by points
        self.standings = list(np.copy(self.players))
        # We shuffle the standings before sorting to prevent registration order mattering.
        # This assumes, that during the swiss only scores matter, and no tiebreakers are used.
        # Therefore we shuffle here after standings have been sorted and posted
        np.random.shuffle(self.standings)

        def get_player_score(player: Player):
            return player.get_score()

        self.standings.sort(key=get_player_score, reverse=True)

        self.round += 1
        self.tables = []
        # Variante 1
        # pair from top to bottom, first against next best 3 and so on (very basic)
        if self.pairing_variant == 1:
            index = 0
            for n in self.table_layout:
                self.tables.append(self.standings[index : index + n])
                index += n

        # Variante 2
        # pair from the top, but select the player with the least badness for the next open spot
        # on the table
        elif self.pairing_variant == 2:
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
        elif self.pairing_variant == 3:
            open_players = self.standings.copy()
            for n in self.table_layout:
                table = []
                # select the n best suited players for this table
                for i in range(n):
                    # table is empty, take player with highest badness so far
                    if len(table) == 0:
                        worst_badness = 0
                        selected_player = open_players[0]
                        for p in open_players:
                            if p.badness_sum > worst_badness:
                                worst_badness = p.badness_sum
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
        # combination of 2 and 3: select first player from among those with the highest score, but take the worst
        elif self.pairing_variant == 4:
            open_players = self.standings.copy()
            for n in self.table_layout:
                table = []
                # select the n best suited players for this table
                for i in range(n):
                    # empty table: look for hight score players, take the one with highest badness
                    if len(table) == 0:
                        best_score = open_players[0].get_score()
                        worst_badness = 0
                        selected_player = open_players[0]
                        for p in open_players:
                            if p.get_score() == best_score and p.badness_sum > worst_badness:
                                worst_badness = p.badness_sum
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

        self.track_opponents()

        # print result
        if self.printing:
            print(yellow(f"\nPairings for Round {self.round}"))
            print(self.pairings_to_dataframe())

        # json dump
        self.pairing_dict = {"placements": [{"players": [player.id for player in table]} for table in self.tables]}
        json.dump(self.pairing_dict, sys.stdout)
        # with open(os.path.join(self.json_path, f"Pairings_Round_{self.round}.json"), "w") as f:
        #     json.dump(self.pairing_dict, f, indent=4)

    def track_opponents(self):
        """Track who played against whom and their seating position."""
        # calc player badness and track player seatings
        for i, t in enumerate(self.tables):
            for pos, p in enumerate(t):
                p: Player
                badness = 0
                for current_op in t:
                    badness += flatten(p.opponents).count(current_op) ** 2
                p.current_badness = badness
                p.badness_sum += badness

                p.total_seating_number += self.get_seating_number(pos, t)
                # TODO is this only relevant if you win?
                # TODO Meaning does your player seating only count if you won from that position?

        # safe opponents of players
        for t in self.tables:
            for p in t:
                ops = t.copy()
                ops.remove(p)
                p.add_opponents(ops)

    def get_seating_number(self, pos, table):
        if self.seating_variant == 1:
            return pos + 1  # +1 in order to have positions 1 to 4 for the plebs
        elif self.seating_variant == 2:
            if pos == 0:
                sn = 1
            elif pos < len(table) - 1:
                sn = 2
            elif pos == len(table):
                sn = 3
            else:
                raise ValueError(f"position {pos} at a table of {len(table)} does not work.")
            return sn

    def evaluate_pairings(self):
        # TODO remove this?
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

    def set_random_results(self):
        """randomly produce results and dump them to json file"""
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
        """load results.json and process the contents"""
        with open(os.path.join(self.json_path, file_name), "r") as f:
            res = json.load(f)
        self.process_results(res["rounds"][-1])

    def process_results(self, current_round):
        """add points to winners and drawer of current round"""
        # turn up the round counter
        for p in self.players:
            p: Player
            p.rounds_played += 1
        # results of last round
        for table in current_round:
            # sanity check
            # assert {"players": table["players"]} in self.pairing_dict[
            #     "placements"
            # ], "Results table does not match pairing table!"
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
        """visualize pairings in dataframe for console printout"""
        # compact visualization of the pairing tables
        df = pd.DataFrame(self.tables).T
        df.columns = [f"Table {i+1}" for i in range(self.number_of_tables)]

        # replace player object with name and data
        def pretty(player):
            if player is not None:
                return [player.id, player.name, player.score, player.current_badness]
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
            self.set_random_results()
            self.load_results(f"Results_Round_{self.round}.json")
            # skip standing after last round
            self.get_standings()

        s = 0
        for p in self.players:
            s += p.badness_sum
        if self.printing:
            print(f"\nav. player badness sum: {s / self.number_of_players}")
