import numpy as np
import matplotlib.pyplot as plt
from ipydex import IPS, activate_ips_on_exception

from tournament_organizer import TournamentOrganizer
from player import Player

activate_ips_on_exception()

### --- Parameters --- ###
players_range = [8, 25]
runs_per_player_number = 30
data_list = []

for number_of_players in range(*players_range, 1):
    badness_sum = 0
    clean_cut_sum = 0
    score_to_top_4_sum = 0
    number_badly_paired_player_sum = 0
    number_really_badly_paired_player_sum = 0
    for i in range(runs_per_player_number):
        players = [Player() for i in range(number_of_players)]

        TO = TournamentOrganizer(players, printing=False)
        TO.simulate_tournament()

        # average pairing badness per player
        average_player_badness = 0
        for p in TO.players:
            average_player_badness += p.badness_sum
        average_player_badness = average_player_badness / number_of_players
        badness_sum += average_player_badness

        # clean cut to top 4?
        if TO.standings[3].score > TO.standings[4].score:
            clean_cut_sum += 1

        # score needed to top 4 (make sure all well placed players are in)
        score_to_top_4_sum += TO.standings[3].score

        # look at worst pairings
        badness_list = []
        for p in TO.players:
            badness_list.append(p.badness_sum)
        number_badly_paired_player_sum += sum(np.where(np.array(badness_list) >= 5, 1, 0))
        number_really_badly_paired_player_sum += sum(np.where(np.array(badness_list) >= 14, 1, 0))

        # s

    row_template = (
        "Players: {:<3}   "
        + "Tables: {:<2}   "
        + "Av. Badness: {:<4}   "
        + "Clean cut %: {:<5}   "
        + "av. worst Score to top: {:<4} / {:<3}   "
        + "badly paired players: {:<4}   "
        + "worse paired players: {:<4}"
    )
    data = [
        number_of_players,
        TO.number_of_tables,
        round(badness_sum / runs_per_player_number, 2),
        round(clean_cut_sum / runs_per_player_number * 100, 2),
        round(score_to_top_4_sum / runs_per_player_number, 2),
        TO.number_of_rounds * TO.p_win,
        round(number_badly_paired_player_sum / runs_per_player_number, 2),
        round(number_really_badly_paired_player_sum / runs_per_player_number, 2),
    ]
    print(row_template.format(*data))
    data_list.append(data)

data_list = np.array(data_list, dtype=float)
plt.scatter(data_list[:, 0], data_list[:, 1], label="Tables")
plt.scatter(data_list[:, 0], data_list[:, 2], label="Av. Badness")
plt.scatter(data_list[:, 0], data_list[:, 3] / 100, label="Clean Cut", color="green")
plt.hlines(0.5, 7.8, 24.2, colors="green")
plt.legend()
plt.xlim(7.8, 24.2)
plt.show()
