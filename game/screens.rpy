# 2026 (c) Tasuda
﻿screen song_select():

    tag menu

    add "#000000"

    text "4K MANIA":
        size 52
        xalign 0.5
        yalign 0.15

    textbutton "START":

        xalign 0.5
        yalign 0.5

        action Jump(
            "play_song"
        )
    
    text "F3/F4 调整流速"
    text "-/+ 调整延迟"


screen result_screen(game):

    tag menu

    add "#000000"

    text "RESULT":
        size 64
        xalign 0.5
        yalign 0.08

    text "Perfect [game.score.perfect]":
        size 34
        xalign 0.5
        yalign 0.28

    text "Great [game.score.great]":
        size 34
        xalign 0.5
        yalign 0.36

    text "Good [game.score.good]":
        size 34
        xalign 0.5
        yalign 0.44

    text "Miss [game.score.miss]":
        size 34
        xalign 0.5
        yalign 0.52

    text "Max Combo [game.score.max_combo]":
        size 36
        xalign 0.5
        yalign 0.66

    text "Accuracy [\"%.2f\" % game.score.accuracy]%":
        size 36
        xalign 0.5
        yalign 0.74

    text "[game.score.grade]":
        size 96
        xalign 0.5
        yalign 0.88

    textbutton "Retry":

        xalign 0.4
        yalign 0.95

        action Jump(
            "play_song"
        )

    textbutton "Exit":

        xalign 0.6
        yalign 0.95

        action Return()


label play_song:

    $ game = ManiaGame(
        "chart/song1/chart.osu"
    )

    scene black

    show expression game

    while not game.finished:

        $ renpy.pause(
            0.01,
            hard=True
        )

    hide expression game

    call screen result_screen(
        game
    )

    return
