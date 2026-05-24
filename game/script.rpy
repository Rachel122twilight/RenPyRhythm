# 2026 (c) Tasuda
﻿init python:

    import sys
    import os

    sys.path.append(
        os.path.join(
            config.gamedir,
            "core"
        )
    )

    from gameplay import ManiaGame


label start:

    scene black

    call screen song_select

    return
