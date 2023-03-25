# pairing script for cEDH tournaments
## Installation:
- run `pip install -r requirements.txt`

## Usage
### In combination with User Interface
This project invokes the cedh tournament protocal as presented [here](https://github.com/RememberOfLife/cedh_matching).
Input and output are serialized json objects.

- To progress to the next round, call `python script.py --next <path_to_results.json>`, specifying the path to a json file with the tournament history so far. This will print out the pairings in json format

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