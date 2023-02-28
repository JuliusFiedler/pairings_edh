# pairing script for cEDH tournaments
## Installation:
- run `pip install -r requirements.txt`

## Philosophy
- Use as many elements off the classicla swiss pairing system as possible
- Have a robust tiebreaker system
- adapt the system für 3-4 player tables

## Goals / Optimization Criteria (in no particular order yet)
- Pair players with "equal skill", meaning pair players with the same amounts of points against each other
- try to avoid playing against the same people each round
- avoid incentive for tactical concessions in early rounds

## Player Rating / Tiebreaker
1. points. 3 for a win, 1 for a draw, 0 for a loss
1. OMW% (this is also tricky, since we have multiple opponents and also not always the same amount each round -> average?)
1. (GW% and OGW% are useless in our case)
1. Seating Order on the Table?

https://www.mtgevent.com/blog/magic-the-gathering-tiebreakers-explained/

https://help.battlefy.com/en/articles/3367583-swiss-tie-breaker-formats

## Badness
is a means to measure how bad a table paring is, regarding seeing the same person multiple times.
A player has a personal current badness, which is the sum of players he would play against this round that he already faced in the tournament.
Table Badness is the sum of all player badnesses. Facing the same opponent more than 2 times could scale more heavily.
- same op twice: badness 1
- same op thrice: badness 4
- same op four times: badness 9

This obviously scales per player. Meaning a total average badness at the end of the tournament of 1 means each player, on average
did see a single other player twice in a single round, all other pairings were with new players.

## Current Usage (Development Stage)
- Run `main.py` to test a tournament, inspect pairings and standings
- Run `testing.py` for large scale testing (various player numbers, many random results)

## Open Questions
- How many player do we need before a cut to top 4 is no longer sensible? > 16?

## TODOS
- Validate pairing system, badness, etc.
- Build unittest?
- Track Oppscore and other tiebreakers
- implement user interface (names, results)

### Prblems
- sometimes very high badness still occurs with variante 2, (eg. 12 palyers, seed 9)

## Contributing
If you submit code, please note that this project uses automatic code formatting with the tool [black](https://github.com/psf/black), more precisely: `black -l 120 .`.