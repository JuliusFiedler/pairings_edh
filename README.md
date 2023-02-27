# pairing script for cEDH tournaments
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
2. Oppscore?
3. ...


### Badness
is a means to measure how bad a table paring is, regarding seeing the same person multiple times.
A player has a personal current badness, which is the sum of players he would play against this round that he already faced in the tournament.
Table Badness is the sum of all player badnesses. Facing the same opponent more than 2 times could scale more heavily.
- same op twice: badness 1
- same op thrice: badness 4
- same op four times: badness 9
This obviously scales per player. Meaning a total average badness at the end of the tournament of 1 means each player, on average
did see a single other player twice in a single round, all other pairings were with new players.

## TODOS
- Validate pairing system, badness, etc.
- Build unittest?
- Track Oppscore and other tiebreakers
- implement user interface (names, results)