import numpy as np

from pairing import TournamentOrganizer
from player import Player

### --- Parameters --- ###
players_range = [8, 25]
runs_per_player_number = 30

for number_of_players in range(*players_range, 1):
    av_badness_list = []
    for i in range(runs_per_player_number):
        players = [Player() for i in range(number_of_players)]

        TO = TournamentOrganizer(players, printing=False)

        for i in range(TO.number_of_rounds):
            TO.calc_pairings()
            TO.set_results()
            TO.calc_standings()

        average_player_badness = 0
        for p in TO.players:
            average_player_badness += p.badness_sum
        average_player_badness = average_player_badness / number_of_players
        av_badness_list.append(average_player_badness)
    print(f"Players: {number_of_players}, av. badness: {sum(av_badness_list) / runs_per_player_number}")
