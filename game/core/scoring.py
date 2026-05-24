from core.constants import PERFECT
from core.constants import GREAT
from core.constants import GOOD

from core.constants import SCORE_VALUES


class ScoreManager:

    def __init__(self):

        self.perfect = 0
        self.great = 0
        self.good = 0
        self.miss = 0

        self.combo = 0
        self.max_combo = 0

        self.score = 0

        self.total_notes = 0

    def judge(self, delta):

        d = abs(delta)

        if d <= PERFECT:
            result = "perfect"

        elif d <= GREAT:
            result = "great"

        elif d <= GOOD:
            result = "good"

        else:
            result = "miss"

        if result == "perfect":
            self.perfect += 1

        elif result == "great":
            self.great += 1

        elif result == "good":
            self.good += 1

        else:
            self.miss += 1

        if result == "miss":

            self.combo = 0

        else:

            self.combo += 1

            if self.combo > self.max_combo:
                self.max_combo = self.combo

        self.score += SCORE_VALUES[result]

        self.total_notes += 1

        return result

    @property
    def accuracy(self):

        if self.total_notes == 0:
            return 0.0

        total = (
            self.perfect * 300 +
            self.great * 200 +
            self.good * 100
        )

        max_total = self.total_notes * 300

        return (total / max_total) * 100

    @property
    def grade(self):

        acc = self.accuracy

        if acc >= 99:
            return "SS"

        elif acc >= 95:
            return "S"

        elif acc >= 90:
            return "A"

        elif acc >= 80:
            return "B"

        elif acc >= 70:
            return "C"

        return "D"