class TimingSegment:
    def __init__(
        self,
        start,
        end,
        bpm,
        sv,
        accumulated
    ):
        self.start = start
        self.end = end

        self.bpm = bpm
        self.sv = sv

        self.accumulated = accumulated


class TimingManager:
    def __init__(self, timing_points):

        self.points = timing_points
        self.segments = []

        self.build_segments()

    def build_segments(self):

        current_bpm = 120
        current_sv = 1.0

        accumulated = 0.0

        for i, point in enumerate(self.points):

            if point.uninherited:
                current_bpm = point.bpm
            else:
                current_sv = point.sv

            end = 999999999

            if i + 1 < len(self.points):
                end = self.points[i + 1].time

            segment = TimingSegment(
                point.time,
                end,
                current_bpm,
                current_sv,
                accumulated
            )

            self.segments.append(segment)

            delta = end - point.time

            accumulated += (
                delta *
                current_sv *
                (current_bpm / 120.0)
            )

    def get_segment(self, time):

        for seg in self.segments:

            if seg.start <= time < seg.end:
                return seg

        return self.segments[-1]

    def scroll_position(self, time):

        seg = self.get_segment(time)

        return (
            seg.accumulated +
            (
                (time - seg.start) *
                seg.sv *
                (seg.bpm / 120.0)
            )
        )