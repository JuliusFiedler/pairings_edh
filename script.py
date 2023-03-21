import numpy as np
import argparse
import json

from util import *
from tournament_organizer import TournamentOrganizer
from player import Player

argparser = argparse.ArgumentParser()

argparser.add_argument("--new", help="start new tournament also specify", action="store_true")
argparser.add_argument("--next", help="specify results path and calculate next rounds pairings", metavar="path")
args = argparser.parse_args()


if args.new:
    player_number = args.new
    TO = TournamentOrganizer()
elif args.next:
    path = args.next
    with open(path, "r") as f:
        res = json.load(f)
    player_number = len(res["players"])
else:
    argparser.print_help()
