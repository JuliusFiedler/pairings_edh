import numpy as np
from ipydex import IPS, activate_ips_on_exception
from player import Player
from tournament_organizer import TournamentOrganizer
from util import namify_player_list

activate_ips_on_exception()

### ----- define some tournament parameters ----- ###
number_of_players = 16

### --------------------------------------------- ###

np.random.seed(19)  # for reproducibility

players = [Player(id=i + 1) for i in range(number_of_players)]

TO = TournamentOrganizer(players)

TO.simulate_tournament()

# IPS()
