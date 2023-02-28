import numpy as np
import names


class Player:
    def __init__(self, name=None) -> None:
        if name is None:
            self.name = names.get_first_name()
        else:
            self.name = name
        self.score = 0
        self.opp_score = 0
        self.opponents = []  # list of lists, one list for each round
        self.badness_sum = 0
        self.current_badness = 0
        self.total_seating_number = 0  # winning from pos 4 is harder than from pos 1, this is used in tiebreaker
        # high is good
        self.match_win_perc = 1 / 3
        self.opp_match_win_perc = 1 / 3
        self.rounds_palyed = 0

    def set_TO(self, TO):
        self.TO = TO

    def get_score(self):
        return self.score

    def get_player_stats(self):
        return [self.name, self.score, round(self.get_OMWP(), 3), self.total_seating_number, self.badness_sum]

    def add_opponents(self, ops):
        self.opponents.append(ops)

    def get_personal_badness(self):
        return self.badness_sum

    def get_MWP(self):
        """personal Match Win Percentage
        MWP cannot be lower than 0.33, see https://www.mtgevent.com/blog/magic-the-gathering-tiebreakers-explained/
        """
        self.match_win_perc = max(self.score / (self.rounds_palyed * self.TO.p_win), 1 / 3)
        assert self.match_win_perc <= 1
        return self.match_win_perc

    def get_OMWP(self):
        """personal Opponents Match Win Percentage
        since we have multiple (2-3) opponents each round, the average of the MWP of all opps at the table is summed
        per round
        """
        OMWP_sum = 0
        for op_list in self.opponents:
            table_MW_sum = 0
            for p in op_list:
                p: Player
                table_MW_sum += p.get_MWP()
            # average MW% at the table
            OMWP_sum += table_MW_sum / len(op_list)

        self.opp_match_win_perc = OMWP_sum / self.rounds_palyed

        assert self.opp_match_win_perc <= 1

        return self.opp_match_win_perc
