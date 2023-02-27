import numpy as np
from ipydex import IPS, activate_ips_on_exception
from player import Player
from pairing import TournamentOrganizer

activate_ips_on_exception()

### ----- define some tournament parameters ----- ### 
number_of_players = 15


### --------------------------------------------- ###
np.random.seed(1)
players = [Player() for i in range(number_of_players)]

TO = TournamentOrganizer(players)
TO.calc_pairings()

print("end")
IPS()