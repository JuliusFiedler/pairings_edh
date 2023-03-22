import numpy as np
import argparse
import json
import shutil
from ipydex import IPS, activate_ips_on_exception

from util import *
from tournament_organizer import TournamentOrganizer
from player import Player

activate_ips_on_exception()

argparser = argparse.ArgumentParser()

argparser.add_argument("--new", help="start new tournament with given number of players", metavar="player_number")
argparser.add_argument("--next", help="specify results path and calculate next rounds pairings", metavar="path")
# for testing
argparser.add_argument("--random_res", help="set this flag to immeadiately add random results", action="store_true")

args = argparser.parse_args()


def main():
    if args.new:
        player_number = int(args.new)
        random_res = args.random_res
        new(player_number, random_res)
    elif args.next:
        path = args.next
        random_res = args.random_res
        next(path, random_res)
    else:
        argparser.print_help()


# TODO generate json printout for standings


def new(player_number, random_res=False):
    shutil.rmtree("json_dumps", ignore_errors=True)
    TO = TournamentOrganizer(player_number)
    TO.get_pairings()
    if random_res:
        TO.set_random_results()
        TO.process_results(TO.results_dict["rounds"][-1])
        TO.get_standings()


def next(path, random_res=False):
    with open(path, "r") as f:
        res = json.load(f)
    TO = TournamentOrganizer(res["players"])
    for current_round in res["rounds"]:
        TO.round += 1
        TO.tables = [[TO.get_player_by_id(i) for i in table["players"]] for table in current_round]
        TO.pairing_dict = res
        TO.track_opponents()
        TO.process_results(current_round)
    TO.get_standings()
    TO.get_pairings()
    if random_res:
        TO.results_dict = res
        TO.set_random_results()
        TO.process_results(TO.results_dict["rounds"][-1])
        TO.get_standings()


# def res(path):
#     with open(path, "r") as f:
#         parings = json.load(f)
#     player_ids = []
#     for table in parings["placements"]:
#         player_ids.extend(table["players"])
#     TO = TournamentOrganizer(player_ids)

#     r = int(path.split(".")[0].split("_")[-1])
#     TO.round = r
#     if r >= 2:
#         old_path = f"json_dumps/Results_Round_{r-1}.json"
#         with open(old_path, "r") as f:
#             old_res = json.load(f)
#         TO.results_dict = old_res

#     TO.tables = [[TO.get_player_by_id(i) for i in tables["players"]] for tables in parings["placements"]]

#     TO.set_random_results()
#     TO.get_standings()


main()
