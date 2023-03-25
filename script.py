import sys
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

argparser.add_argument(
    "--next", help="read previous results from file and print pairings to stdout in json format", metavar="path"
)
# for testing
argparser.add_argument(
    "-rr", "--random_res", help="set this (additional) flag to immeadiately add random results", action="store_true"
)

args = argparser.parse_args()


def main():
    if args.next:
        path = args.next
        random_res = args.random_res
        next(path, random_res)
    else:
        argparser.print_help()


def new(player_number, random_res=False):
    # shutil.rmtree("json_dumps", ignore_errors=True)
    TO = TournamentOrganizer(player_number, printing=False)
    TO.get_pairings()

    # debug only
    if random_res:
        TO.set_random_results()
        TO.process_results(TO.results_dict["rounds"][-1])
        TO.get_standings()


def next(path, random_res=False):
    # read from file
    with open(path, "r") as f:
        res = json.load(f)

    # read from stdin
    # for line in sys.stdin:
    #     res = json.loads(line)

    # first round
    if len(res["rounds"]) == 0:
        new(res["players"])
    # other rounds
    else:
        # check for dropped players
        original_player_ids = []
        for table in res["rounds"][0]:
            for id in table["players"]:
                if not id in original_player_ids:
                    original_player_ids.append(id)
        current_player_ids = res["players"]
        dropped_player_ids = list(set(original_player_ids) - set(current_player_ids))

        # recretate tournament history
        TO = TournamentOrganizer(original_player_ids, printing=False)
        for current_round in res["rounds"]:
            TO.round += 1
            TO.tables = [[TO.get_player_by_id(i) for i in table["players"]] for table in current_round]
            TO.pairing_dict = res
            TO.track_opponents()
            TO.process_results(current_round)

        # get new pairings
        TO.drop_players(dropped_player_ids)
        TO.get_standings()
        TO.get_pairings()

        # debug only
        if random_res:
            TO.results_dict = res
            TO.set_random_results()
            TO.process_results(TO.results_dict["rounds"][-1])
            TO.get_standings()


main()
