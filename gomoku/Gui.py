# gui.py — Pygame interface for human-vs-AI play

import pygame
from gomoku.game import GomokuGame, BLACK, WHITE, EMPTY
from gomoku.ai import GomokuAI

CELL_SIZE = 40
MARGIN = 40
WINDOW_SIZE = CELL_SIZE * 14 + MARGIN * 2  # 640px

BLACK_COLOR  = (0,   0,   0)
WHITE_COLOR  = (255, 255, 255)
BOARD_COLOR  = (220, 179, 92)
LINE_COLOR   = (0,   0,   0)
RED_COLOR    = (220, 50,  50)
OVERLAY_COLOR = (240, 220, 140)

STAR_POINTS = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]


def _cell_to_pixel(row, col):
    return MARGIN + col * CELL_SIZE, MARGIN + row * CELL_SIZE


def draw_board(screen, game):
    """Draw the grid, star points, pieces, last-move marker, and win overlay."""
    screen.fill(BOARD_COLOR)

    # Grid lines
    for i in range(15):
        pygame.draw.line(screen, LINE_COLOR,
                         (MARGIN, MARGIN + i * CELL_SIZE),
                         (MARGIN + 14 * CELL_SIZE, MARGIN + i * CELL_SIZE), 1)
        pygame.draw.line(screen, LINE_COLOR,
                         (MARGIN + i * CELL_SIZE, MARGIN),
                         (MARGIN + i * CELL_SIZE, MARGIN + 14 * CELL_SIZE), 1)

    # Star points
    for r, c in STAR_POINTS:
        cx, cy = _cell_to_pixel(r, c)
        pygame.draw.circle(screen, LINE_COLOR, (cx, cy), 4)

    # Pieces
    radius = CELL_SIZE // 2 - 2
    for r in range(15):
        for c in range(15):
            piece = game.board[r][c]
            if piece == EMPTY:
                continue
            cx, cy = _cell_to_pixel(r, c)
            color = BLACK_COLOR if piece == BLACK else WHITE_COLOR
            pygame.draw.circle(screen, color, (cx, cy), radius)
            # Outline for white pieces so they're visible on the board
            if piece == WHITE:
                pygame.draw.circle(screen, BLACK_COLOR, (cx, cy), radius, 1)

    # Last-move red dot
    if game.last_move:
        r, c = game.last_move
        cx, cy = _cell_to_pixel(r, c)
        pygame.draw.circle(screen, RED_COLOR, (cx, cy), 5)

    # Win overlay
    if game.winner:
        font = pygame.font.SysFont(None, 64)
        msg = "Black wins!" if game.winner == BLACK else "White wins!"
        text = font.render(msg, True, (180, 0, 0))
        rect = text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2))
        bg_rect = rect.inflate(30, 20)
        pygame.draw.rect(screen, OVERLAY_COLOR, bg_rect, border_radius=8)
        pygame.draw.rect(screen, (180, 0, 0), bg_rect, 2, border_radius=8)
        screen.blit(text, rect)

    # Draw "AI thinking..." hint
    if not game.winner and game.current_player == WHITE:
        hint_font = pygame.font.SysFont(None, 28)
        hint = hint_font.render("AI thinking...", True, (80, 40, 0))
        screen.blit(hint, (MARGIN, WINDOW_SIZE - MARGIN + 4))


def pixel_to_cell(x, y):
    """Convert mouse pixel to (row, col), snapping to nearest intersection.
    Returns None if the click is outside the board area."""
    col = round((x - MARGIN) / CELL_SIZE)
    row = round((y - MARGIN) / CELL_SIZE)
    if 0 <= row < 15 and 0 <= col < 15:
        return (row, col)
    return None


def run_game():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + MARGIN))
    pygame.display.set_caption("Gomoku AI — CPSC 481")

    game = GomokuGame()
    ai = GomokuAI(simulation_budget=500)
    clock = pygame.time.Clock()

    ai_thinking = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if (event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and not game.is_terminal()
                    and not ai_thinking
                    and game.current_player == BLACK):

                cell = pixel_to_cell(*event.pos)
                if cell is not None and game.board[cell[0]][cell[1]] == EMPTY:
                    game.make_move(cell[0], cell[1])

                    # Trigger AI response on the next frame so the board redraws first
                    if not game.is_terminal():
                        ai_thinking = True

        # AI moves after the board redraws (so user sees their piece first)
        if ai_thinking and not game.is_terminal():
            draw_board(screen, game)
            pygame.display.flip()

            row, col = ai.get_best_move(game)
            game.make_move(row, col)
            ai_thinking = False

        draw_board(screen, game)
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
