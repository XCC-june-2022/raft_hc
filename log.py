from logentry import LogEntry

class Log:
    def __init__(self, log=[LogEntry(0, None)]):
        self.log = log

    def append_log(self, term, action) -> None:
        log = self.log
        log.append(LogEntry(term, action))
    
    def pop_log(self):
        log = self.log
        log.pop()

