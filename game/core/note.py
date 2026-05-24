class Note:
    def __init__(self, time, lane, end_time=None):
        self.time = int(time)
        self.lane = int(lane)

        self.end_time = int(end_time) if end_time else None

        self.hit = False
        self.missed = False

        self.started = False
        self.held = False

        self.holding = False
        self.completed = False

        self.chord = False

    @property
    def is_ln(self):
        return self.end_time is not None