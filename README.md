# pairing script for cEDH tournaments
## Installation:
- run `pip install -r requirements.txt`

## Usage
### In combination with User Interface
This project invokes the cedh tournament protocal as presented [here](https://github.com/RememberOfLife/cedh_matching).
Input and output are serialized json objects.

- Use `config.json` to specify a path, where the following files will be expected.
- To start a new tournaments call `python script.py --new <number_of_players>`. This will generate a file `Pairings_Round_1.json`.
<!-- - The results have to provided in the form of `Results_Round_<n>.json` -->
- To progress to the next round, call `python script.py --next <path_to_results.json>`, specifying the path to the results. This will generate two files:
    - A file containing the pairings for the next round `Pairings_Round_<n+1>.json`
    - **NEW** A file containing the standings of the current round, `Standings_after_Round_<n>.json`, which looks like this:
        ````json
        {
            "header": [
                "#",
                "Name",
                "Score",
                "OMW%",
                "TSN"
            ],
            "header_description": [
                "Place",
                "Player Name",
                "Player Score (3/1/0)",
                "Opponents Match Win Percentage",
                "Total Seating Number (high=harder=better)"
            ],
            "standings": {
                "1": [
                    1,
                    6,
                    0.3333333333333333,
                    6
                ],
                "2": [
                    4,
                    3,
                    0.4074074074074074,
                    12
                ],
                "3": [
                    3,
                    3,
                    0.4074074074074074,
                    5
                ],
                "4": [
                    6,
                    3,
                    0.3703703703703704,
                    7
                ],
                "5": [
                    5,
                    3,
                    0.3333333333333333,
                    10
                ],
                "6": [
                    7,
                    0,
                    0.4074074074074074,
                    8
                ],
                "7": [
                    8,
                    0,
                    0.3703703703703703,
                    6
                ],
                "8": [
                    2,
                    0,
                    0.3703703703703703,
                    6
                ]
            }
        }
        ````
        `header` is a list of categories that make up the standings table. `header_description` is a list of descriptions corresponding with the header list. `standings` is a dictionary with keys keys 1 to n where n is the number of players. Each value is a list of player_id, player_score, player_omw%, player_tsn (see header).

        A corresponding table would ideally be displayed on the UI.


### Testing
- Run `main.py` to test a tournament, inspect pairings and standings
- Run `testing.py` for large scale testing (various player numbers, many random results)
- Run `python script.py --new <number_of_players>` and manually create the results file or add the `--random_res` flag for random results. Continue by running `python script.py --next <path_to_results.json> [--random_res]` to progress the tournament.

## Philosophy
- Use as many elements off the classical swiss pairing system as possible
- Have a robust tiebreaker system
- adapt the system für 3-4 player tables

## Goals / Optimization Criteria (in no particular order yet)
- Pair players with "equal skill", meaning pair players with the same amounts of points against each other
- try to avoid playing against the same people each round
- avoid incentive for tactical concessions in early rounds

## Player Rating / Tiebreaker
1. points. 3 for a win, 1 for a draw, 0 for a loss
1. OMW% (this is also tricky, since we have multiple opponents and also not always the same amount each round -> average!)
1. (GW% and OGW% are useless in our case)
1. Sum of Seating Positions in all rounds

https://www.mtgevent.com/blog/magic-the-gathering-tiebreakers-explained/

https://help.battlefy.com/en/articles/3367583-swiss-tie-breaker-formats

## Badness
is a means to measure how bad a table paring is, regarding playing the same person multiple times.
A player has a personal current badness, which is the sum of players he would play against this round that he already faced in the tournament.
Table Badness is the sum of all player badnesses. Facing the same opponent more than 2 times could scale more heavily.
- same op twice: badness 1
- same op thrice: badness 4
- same op four times: badness 9

This obviously scales per player. Meaning a total average badness at the end of the tournament of 1 means each player, on average
did see a single other player twice in a single round, all other pairings were with new players.

## Open Questions
- How many player do we need before a cut to top 4 is no longer sensible? > 16?

## TODOS
- Validate pairing system, badness, etc.
- Build unittest?
- implement user interface (names, results) see https://urs-kober.de/p/cedh_matching/

## Wishlist
- UI button to set / randomize seed in config

## Contributing
If you submit code, please note that this project uses automatic code formatting with the tool [black](https://github.com/psf/black), more precisely: `black -l 120 .`.