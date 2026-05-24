import renpy.exports as renpy

from core.note import Note


class TimingPoint:

    def __init__(
        self,
        time,
        beat_length,
        uninherited
    ):

        self.time = float(time)

        self.beat_length = float(
            beat_length
        )

        self.uninherited = uninherited

        if uninherited:

            self.bpm = (
                60000.0 /
                self.beat_length
            )

            self.sv = 1.0

        else:

            self.bpm = None

            self.sv = (
                100.0 /
                abs(self.beat_length)
            )


class Chart:

    def __init__(self):

        self.audio = ""

        self.title = ""
        self.artist = ""
        self.version = ""

        self.timing_points = []

        self.notes = []


class OsuParser:

    def __init__(self, path):

        self.path = path

    def parse(self):

        chart = Chart()

        section = None

        f = renpy.file(self.path)

        lines = (
            f.read()
            .decode("utf-8")
            .splitlines()
        )

        for raw in lines:

            line = raw.strip()

            if not line:
                continue

            if (
                line.startswith("[")
                and
                line.endswith("]")
            ):

                section = line

                continue

            if section == "[General]":

                if line.startswith(
                    "AudioFilename:"
                ):

                    chart.audio = (
                        line.split(
                            ":",
                            1
                        )[1]
                        .strip()
                    )

            elif section == "[Metadata]":

                if line.startswith(
                    "Title:"
                ):

                    chart.title = (
                        line.split(
                            ":",
                            1
                        )[1]
                        .strip()
                    )

                elif line.startswith(
                    "Artist:"
                ):

                    chart.artist = (
                        line.split(
                            ":",
                            1
                        )[1]
                        .strip()
                    )

                elif line.startswith(
                    "Version:"
                ):

                    chart.version = (
                        line.split(
                            ":",
                            1
                        )[1]
                        .strip()
                    )

            elif section == "[TimingPoints]":

                parts = line.split(",")

                if len(parts) < 7:
                    continue

                tp = TimingPoint(
                    parts[0],
                    parts[1],
                    int(parts[6]) == 1
                )

                chart.timing_points.append(tp)

            elif section == "[HitObjects]":

                parts = line.split(",")

                x = int(parts[0])

                time = int(parts[2])

                obj_type = int(parts[3])

                lane = min(
                    3,
                    int(x / 128)
                )

                if obj_type & 128:

                    end_time = int(
                        parts[5]
                        .split(":")[0]
                    )

                    note = Note(
                        time,
                        lane,
                        end_time
                    )

                else:

                    note = Note(
                        time,
                        lane
                    )

                chart.notes.append(note)

        chart.notes.sort(
            key=lambda n: n.time
        )

        groups = {}

        for note in chart.notes:

            key = note.time

            if key not in groups:
                groups[key] = []

            groups[key].append(note)

        for group in groups.values():

            if len(group) >= 2:

                for note in group:

                    note.chord = True

        chart.timing_points.sort(
            key=lambda t: t.time
        )

        return chart