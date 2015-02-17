from copy import deepcopy

class Sequence(object):
    def __init__(self, generators, schedule):
        self.generators = generators
        self.schedule = schedule

    def __deepcopy__(self, memo):
        generators = [deepcopy(g) for g in self.generators]
        schedule = self.schedule
        return Sequence(generators, schedule)

    def get_pairs(self):
        return zip(self.schedule, self.generators)
