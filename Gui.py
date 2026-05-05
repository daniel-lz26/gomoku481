# gui.py — Pygame interface for human-vs-AI play

import pygame
from gomoku.game import GomokuGame, BLACK, WHITE, EMPTY
from gomoku.ai import GomokuAI

CELL_SIZE = 40
MARGIN = 40
WINDOW_SIZE = CELL_SIZE * 14 + MARGIN * 2  # 15 lines = 14 gaps

BLACK_COLOR = (0, 0, 0)
WHITE_COLOR = (255, 255, 255)
BOARD_COLOR = (220, 179, 92)
LINE_COLOR = (0, 0, 0)


def draw_board(screen, game):
    """Draw the grid and all placed pieces."""
    pass


def pixel_to_cell(x, y):
    """Convert a mouse click pixel to (row, col). Returns None if out of bounds."""
    pass


def run_game():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Gomoku AI — CPSC 481")

    game = GomokuGame()
    ai = GomokuAI(simulation_budget=500)
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # TODO: handle mouse click → human move → ai move

        draw_board(screen, game)
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()