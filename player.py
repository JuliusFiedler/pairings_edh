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
        self.opponents = []
        self.badness_sum = 0
        self.current_badness = 0

    def get_score(self):
        return self.score

    def print_player(self):
        row_template = "{:<15}: Score {:<3},  Badness Sum: {}  "
        print(row_template.format(self.name, self.score, self.badness_sum))

    def add_opponents(self, ops):
        self.opponents.append(ops)

    def get_personal_badness(self):
        return self.badness_sum
