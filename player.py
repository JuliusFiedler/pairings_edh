import numpy as np
import names

class Player():
    def __init__(self, name=None) -> None:
        if name is None:
            self.name = names.get_first_name()
        else:
            self.name = name
        self.score = 0
        self.opp_score = 0
        self.opponents = []
    
    def get_score(self):
        return self.score
    
    def print_player(self):
        row_template = "{:<15}: {}"
        print(row_template.format(self.name, self.score))
        print()	