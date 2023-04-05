from log import Log
from logentry import LogEntry


class Server:
    def __init__(self, name, state, next_index, neighbours, log=Log(), current_term=0, voted_for=None, match_index=0, leader_index = None):
        self.name = name
        self.log= log
        self.state = state
        self.current_term = current_term
        self.voted_for = voted_for
        self.neighbours = neighbours
        self.next_index = next_index
        self.match_index = match_index
        self.leader_index = leader_index


