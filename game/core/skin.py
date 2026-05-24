from renpy.display.im import Image
from renpy.display.transform import Transform

from core.constants import NOTE_W


class Skin:

    def __init__(self):

        base = int(NOTE_W)

        self.note = Transform(
            Image("images/note.png"),
            fit="contain",
            xysize=(base, base),
        )

        self.hold = Transform(
            Image("images/hold.png"),
            fit="contain",
            xysize=(base, base),
        )

        self.note_h = Transform(
            Image("images/noteh.png"),
            fit="contain",
            xysize=(
                int(base * 1.32),
                int(base * 1.32),
            ),
        )

        self.hold_h = Transform(
            Image("images/holdh.png"),
            fit="contain",
            xysize=(
                int(base * 1.12),
                int(base * 1.12),
            ),
        )

        self.hit = Transform(
            Image("images/hit.png"),
            fit="contain",
            xysize=(220, 220),
        )