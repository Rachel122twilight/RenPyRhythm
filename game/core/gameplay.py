import os

import pygame_sdl2 as pygame

import renpy
import renpy.exports as renpy_exports

from renpy.exports import play
from renpy.exports import play as play_sound

from renpy.display.displayable import Displayable
from renpy.display.render import Render
from renpy.display import render
from renpy.display.core import IgnoreEvent

from renpy.display.image import Solid
from renpy.display.transform import Transform
from renpy.display.im import Image
from renpy.text.text import Text

from core.constants import (
    LANES,
    WINDOW_W,
    WINDOW_H,
    PLAYFIELD_X,
    PLAYFIELD_Y,
    PLAYFIELD_H,
    LANE_W,
    LANE_GAP,
    JUDGE_Y,
    NOTE_H,
    NOTE_W,
    SCROLL_SPEED,
    MISS,
    KEYS,
)

from core.parser import OsuParser
from core.timing import TimingManager
from core.scoring import ScoreManager
from core.skin import Skin


class ManiaGame(Displayable):

    def __init__(
        self,
        chart_path,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.chart_path = chart_path

        self.chart = OsuParser(
            chart_path
        ).parse()

        self.timing = TimingManager(
            self.chart.timing_points
        )

        self.notes = self.chart.notes

        self.score = ScoreManager()

        self.skin = Skin()

        self.started = False
        self.finished = False

        self.song_time = 0

        self.autoplay = False

        if renpy_exports.loadable(
            "offset.txt"
        ):

            try:

                f = renpy_exports.open_file(
                    "offset.txt"
                )

                self.audio_offset = int(
                    f.read().decode(
                        "utf-8"
                    ).strip()
                )

            except:

                self.audio_offset = 0

        else:

            self.audio_offset = 0

        self.scroll_speed = 1.0

        self.last_judge = ""
        self.last_judge_timer = 0

        self.key_states = [False] * LANES

        self.hit_effects = []

    def save_offset(self):

        path = os.path.join(
            renpy.config.gamedir,
            "offset.txt"
        )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                str(self.audio_offset)
            )

    def start(self):

        if self.started:
            return

        self.started = True

        audio_path = self.chart.audio

        base = self.chart_path.rsplit(
            "/",
            1
        )[0]

        full_audio_path = (
            base + "/" + audio_path
        )

        play(
            full_audio_path,
            channel="music"
        )

    def get_music_time(
        self,
        st
    ):

        return (
            st * 1000
        ) + self.audio_offset

    def spawn_hit_effect(
        self,
        lane
    ):

        effect_x = PLAYFIELD_X + (
            lane * (
                LANE_W
                + LANE_GAP
            )
        ) + (LANE_W // 2)

        effect_y = JUDGE_Y

        self.hit_effects.append({

            "x": effect_x,
            "y": effect_y,
            "time": self.song_time,

        })

    def autoplay_update(self):

        if not self.autoplay:
            return

        for note in self.notes:

            if (
                note.hit
                or
                note.missed
            ):
                continue

            delta = (
                self.song_time
                - note.time
            )

            if delta < 0:
                break

            lane = note.lane

            if note.is_ln:

                if not note.holding:

                    note.holding = True

                    note.last_hold_effect = (
                        self.song_time
                    )

                    self.key_states[
                        lane
                    ] = True

                    play_sound(
                        "audio/hit.ogg",
                        channel="sound"
                    )

                    self.spawn_hit_effect(
                        lane
                    )

                    self.last_judge = (
                        self.score.judge(0)
                    )

                    self.last_judge_timer = (
                        self.song_time
                    )

                elif (
                    self.song_time
                    >= note.end_time
                ):

                    note.hit = True
                    note.completed = True

                    self.key_states[
                        lane
                    ] = False

            else:

                note.hit = True

                self.key_states[
                    lane
                ] = True

                play_sound(
                    "audio/hit.ogg",
                    channel="sound"
                )

                self.spawn_hit_effect(
                    lane
                )

                self.last_judge = (
                    self.score.judge(0)
                )

                self.last_judge_timer = (
                    self.song_time
                )

                self.key_states[
                    lane
                ] = False

    def update(
        self,
        st
    ):

        self.song_time = (
            self.get_music_time(st)
        )

        self.autoplay_update()

        alive_notes = []

        for note in self.notes:

            if (
                note.hit
                or
                note.missed
            ):

                remove_time = (
                    note.end_time
                    if note.is_ln
                    else note.time
                )

                if (
                    self.song_time
                    - remove_time
                ) < 120:

                    alive_notes.append(
                        note
                    )

                continue

            if note.is_ln:

                if note.holding:

                    if not hasattr(
                        note,
                        "last_hold_effect"
                    ):

                        note.last_hold_effect = 0

                    if (
                        self.song_time
                        - note.last_hold_effect
                    ) >= 100:

                        self.spawn_hit_effect(
                            note.lane
                        )

                        play_sound(
                            "audio/hit.ogg",
                            channel="sound"
                        )

                        note.last_hold_effect = (
                            self.song_time
                        )

                    if not self.key_states[
                        note.lane
                    ]:

                        note.missed = True

                        note.completed = True

                        self.score.judge(
                            999
                        )

                        alive_notes.append(
                            note
                        )

                        continue

                    if (
                        self.song_time
                        >= note.end_time
                    ):

                        note.hit = True
                        note.completed = True

                        alive_notes.append(
                            note
                        )

                        continue

                else:

                    if (
                        self.song_time
                        - note.time
                    ) > MISS:

                        note.missed = True

                        self.score.judge(
                            999
                        )

                        alive_notes.append(
                            note
                        )

                        continue

            else:

                if (
                    self.song_time
                    - note.time
                ) > MISS:

                    note.missed = True

                    self.score.judge(
                        999
                    )

                    alive_notes.append(
                        note
                    )

                    continue

            alive_notes.append(
                note
            )

        self.notes = alive_notes

        if len(self.notes) == 0:

            self.finished = True

    def hit_lane(
        self,
        lane
    ):

        for note in self.notes:

            if note.lane != lane:
                continue

            if (
                note.hit
                or
                note.missed
            ):
                continue

            delta = (
                self.song_time
                - note.time
            )

            if abs(delta) <= MISS:

                play_sound(
                    "audio/hit.ogg",
                    channel="sound"
                )

                self.spawn_hit_effect(
                    lane
                )

                if note.is_ln:

                    note.holding = True

                    note.last_hold_effect = (
                        self.song_time
                    )

                else:

                    note.hit = True

                self.last_judge = (
                    self.score.judge(
                        delta
                    )
                )

                self.last_judge_timer = (
                    self.song_time
                )

                return

            if (
                note.time
                > self.song_time
            ):
                return

    def draw_lane(
        self,
        r,
        lane,
        st,
        at
    ):

        x = PLAYFIELD_X + (
            lane * (
                LANE_W
                + LANE_GAP
            )
        )

        lane_render = render.render(
            Solid("#1f1f1f"),
            LANE_W,
            PLAYFIELD_H,
            st,
            at
        )

        r.blit(
            lane_render,
            (
                int(x),
                PLAYFIELD_Y
            )
        )

        if self.key_states[lane]:

            press_render = render.render(
                Solid("#444444"),
                LANE_W,
                PLAYFIELD_H,
                st,
                at
            )

            r.blit(
                press_render,
                (
                    int(x),
                    PLAYFIELD_Y
                )
            )

    def draw_judge_line(
        self,
        r,
        st,
        at
    ):

        judge_render = render.render(
            Solid("#ffffff"),
            (
                LANE_W * LANES
            ) + (
                LANE_GAP
                * (LANES - 1)
            ),
            4,
            st,
            at
        )

        r.blit(
            judge_render,
            (
                PLAYFIELD_X,
                JUDGE_Y
            )
        )

    def draw_note(
        self,
        r,
        note,
        current_scroll,
        st,
        at
    ):

        note_scroll = (
            self.timing.scroll_position(
                note.time
            )
        )

        delta = (
            note_scroll
            - current_scroll
        )

        y = JUDGE_Y - (
            delta
            * SCROLL_SPEED
            * self.scroll_speed
        )

        if y < -400:
            return

        if y > WINDOW_H + 400:
            return

        x = PLAYFIELD_X + (
            note.lane * (
                LANE_W
                + LANE_GAP
            )
        )

        if note.chord:

            note_image = self.skin.note_h
            hold_image = self.skin.hold_h

        else:

            note_image = self.skin.note
            hold_image = self.skin.hold

        note_render = render.render(
            note_image,
            NOTE_W,
            NOTE_W,
            st,
            at
        )

        nw = note_render.width
        nh = note_render.height

        note_x = int(
            x + (
                (
                    NOTE_W - nw
                ) / 2
            )
        )

        note_y = int(
            y + (
                (
                    NOTE_W - nh
                ) / 2
            )
        )

        if note.is_ln:

            end_scroll = (
                self.timing.scroll_position(
                    note.end_time
                )
            )

            end_delta = (
                end_scroll
                - current_scroll
            )

            end_y = JUDGE_Y - (
                end_delta
                * SCROLL_SPEED
                * self.scroll_speed
            )

            body_top = min(
                note_y + (nh // 2),
                int(end_y)
            )

            body_bottom = max(
                note_y + (nh // 2),
                int(end_y)
            )

            ln_height = (
                body_bottom
                - body_top
            )

            if ln_height > 0:

                hold_render = render.render(
                    hold_image,
                    NOTE_W,
                    ln_height,
                    st,
                    at
                )

                hw = hold_render.width

                hold_x = int(
                    x + (
                        (
                            NOTE_W - hw
                        ) / 2
                    )
                )

                r.blit(
                    hold_render,
                    (
                        hold_x,
                        body_top
                    )
                )

        r.blit(
            note_render,
            (
                note_x,
                note_y
            )
        )

    def draw_hit_effects(
        self,
        r,
        st,
        at
    ):

        alive = []

        for effect in self.hit_effects:

            elapsed = (
                self.song_time
                - effect["time"]
            )

            if elapsed > 220:
                continue

            alive.append(effect)

            progress = (
                elapsed / 220.0
            )

            size = int(
                40 + (
                    progress * 180
                )
            )

            alpha = (
                1.0 - progress
            )

            effect_image = Transform(

                Image("images/hit.png"),

                fit="contain",

                xysize=(
                    size,
                    size
                ),

                alpha=alpha,

            )

            effect_render = render.render(

                effect_image,

                size,
                size,
                st,
                at

            )

            w = effect_render.width
            h = effect_render.height

            r.blit(

                effect_render,

                (
                    int(effect["x"] - (w / 2)),
                    int(effect["y"] - (h / 2)),
                )

            )

        self.hit_effects = alive

    def draw_ui(
        self,
        r,
        st,
        at
    ):

        combo_text = Text(
            str(
                self.score.combo
            ),
            size=52,
            color="#ffffff"
        )

        combo_render = render.render(
            combo_text,
            300,
            80,
            st,
            at
        )

        r.blit(
            combo_render,
            (
                920,
                280
            )
        )

        acc_text = Text(
            "{:.2f}%".format(
                self.score.accuracy
            ),
            size=34,
            color="#ffffff"
        )

        acc_render = render.render(
            acc_text,
            300,
            60,
            st,
            at
        )

        r.blit(
            acc_render,
            (
                920,
                360
            )
        )

        score_text = Text(
            str(
                self.score.score
            ),
            size=28,
            color="#ffffff"
        )

        score_render = render.render(
            score_text,
            300,
            60,
            st,
            at
        )

        r.blit(
            score_render,
            (
                920,
                420
            )
        )

        if (
            self.song_time
            - self.last_judge_timer
        ) < 500:

            judge_text = Text(
                self.last_judge.upper(),
                size=40,
                color="#ffff00"
            )

            judge_render = render.render(
                judge_text,
                300,
                60,
                st,
                at
            )

            r.blit(
                judge_render,
                (
                    900,
                    500
                )
            )

        speed_text = Text(
            "Speed {:.1f}x".format(
                self.scroll_speed
            ),
            size=26,
            color="#00ffff"
        )

        speed_render = render.render(
            speed_text,
            300,
            50,
            st,
            at
        )

        r.blit(
            speed_render,
            (
                920,
                620
            )
        )

        offset_text = Text(
            "Offset {}ms".format(
                self.audio_offset
            ),
            size=26,
            color="#ffaaaa"
        )

        offset_render = render.render(
            offset_text,
            300,
            50,
            st,
            at
        )

        r.blit(
            offset_render,
            (
                920,
                660
            )
        )

        if self.autoplay:

            auto_text = Text(
                "AUTO",
                size=30,
                color="#00ff00"
            )

            auto_render = render.render(
                auto_text,
                200,
                60,
                st,
                at
            )

            r.blit(
                auto_render,
                (
                    920,
                    120
                )
            )

    def render(
        self,
        width,
        height,
        st,
        at
    ):

        if not self.started:
            self.start()

        self.update(st)

        r = Render(
            WINDOW_W,
            WINDOW_H
        )

        bg_render = render.render(
            Solid("#000000"),
            WINDOW_W,
            WINDOW_H,
            st,
            at
        )

        r.blit(
            bg_render,
            (
                0,
                0
            )
        )

        for lane in range(LANES):

            self.draw_lane(
                r,
                lane,
                st,
                at
            )

        self.draw_judge_line(
            r,
            st,
            at
        )

        current_scroll = (
            self.timing.scroll_position(
                self.song_time
            )
        )

        for note in self.notes:

            if (
                note.hit
                or
                note.missed
            ):
                continue

            self.draw_note(
                r,
                note,
                current_scroll,
                st,
                at
            )

        self.draw_hit_effects(
            r,
            st,
            at
        )

        self.draw_ui(
            r,
            st,
            at
        )

        renpy_exports.redraw(
            self,
            0
        )

        return r

    def event(
        self,
        ev,
        x,
        y,
        st
    ):

        if (
            ev.type
            == pygame.KEYDOWN
        ):

            if ev.key == pygame.K_F2:

                self.autoplay = (
                    not self.autoplay
                )

                raise IgnoreEvent()

            if ev.key == pygame.K_F3:

                self.scroll_speed = max(
                    0.5,
                    self.scroll_speed - 0.1
                )

                raise IgnoreEvent()

            if ev.key == pygame.K_F4:

                self.scroll_speed = min(
                    5.0,
                    self.scroll_speed + 0.1
                )

                raise IgnoreEvent()

            if ev.key == pygame.K_MINUS:

                self.audio_offset -= 5

                self.save_offset()

                raise IgnoreEvent()

            if ev.key == pygame.K_EQUALS:

                self.audio_offset += 5

                self.save_offset()

                raise IgnoreEvent()

            if self.autoplay:
                raise IgnoreEvent()

            mods = pygame.key.get_mods()

            ctrl = (
                mods & pygame.KMOD_CTRL
            )

            if ctrl and ev.key in KEYS:
                raise IgnoreEvent()

            if ev.key in KEYS:

                lane = KEYS[
                    ev.key
                ]

                self.key_states[
                    lane
                ] = True

                self.hit_lane(
                    lane
                )

                raise IgnoreEvent()

        elif (
            ev.type
            == pygame.KEYUP
        ):

            if ev.key in KEYS:

                lane = KEYS[
                    ev.key
                ]

                self.key_states[
                    lane
                ] = False

                raise IgnoreEvent()

        return None