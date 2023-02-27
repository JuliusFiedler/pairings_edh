import numpy as np

from tournament_organizer import TournamentOrganizer
from player import Player

### --- Parameters --- ###
players_range = [8, 25]
runs_per_player_number = 30

for number_of_players in range(*players_range, 1):
    badness_sum = 0
    clean_cut_sum = 0
    for i in range(runs_per_player_number):
        players = [Player() for i in range(number_of_players)]

        TO = TournamentOrganizer(players, printing=False)

        for i in range(TO.number_of_rounds):
            TO.calc_pairings()
            TO.set_results()
            TO.calc_standings()

        # average pairing badness per player
        average_player_badness = 0
        for p in TO.players:
            average_player_badness += p.badness_sum
        average_player_badness = average_player_badness / number_of_players
        badness_sum += average_player_badness

        # clean cut to top 4?
        if TO.standings[3].score > TO.standings[4].score:
            clean_cut_sum += 1
    row_template = "Players {:<3}, Av. Badness {:<4},  Clean cut %: {:<4}  "
    print(
        row_template.format(
            number_of_players,
            round(badness_sum / runs_per_player_number, 2),
            round(clean_cut_sum / runs_per_player_number * 100, 2),
        )
    )
