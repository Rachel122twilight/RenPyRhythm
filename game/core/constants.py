import pygame_sdl2 as pygame

WINDOW_W = 1280
WINDOW_H = 720

LANES = 4

LANE_W = 96
LANE_GAP = 8

PLAYFIELD_W = (
    (LANE_W * LANES)
    + (LANE_GAP * (LANES - 1))
)

PLAYFIELD_X = (
    (WINDOW_W - PLAYFIELD_W) // 2
)

PLAYFIELD_Y = 40
PLAYFIELD_H = 640

JUDGE_Y = 620

NOTE_W = LANE_W
NOTE_H = 24

SCROLL_SPEED = 0.35

PERFECT = 32
GREAT = 64
GOOD = 96
MISS = 140

SCORE_VALUES = {
    "perfect": 300,
    "great": 200,
    "good": 100,
    "miss": 0,
}

KEYS = {
    pygame.K_d: 0,
    pygame.K_f: 1,
    pygame.K_j: 2,
    pygame.K_k: 3,
}