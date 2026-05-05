# heuristic.py — Board evaluation function
# This is the main intellectual contribution of the project.

from gomoku.game import BLACK, WHITE, BOARD_SIZE, EMPTY

# Pattern scores
FIVE        = 1_000_000
OPEN_FOUR   = 100_000
BLOCKED_FOUR =  10_000
OPEN_THREE  =   1_000
BLOCKED_THREE =   100
OPEN_TWO    =      10
BLOCKED_TWO =       5


def evaluate(board, player) -> float:
    """
    Score the board from `player`'s perspective.
    Higher = better for player.
    """
    opponent = WHITE if player == BLACK else BLACK
    return _score_for(board, player, opponent) - _score_for(board, opponent, player)


def _score_for(board, player, opponent):
    """Sum heuristic score across all lines for one player."""
    score = 0
    for line in _all_lines(board):
        score += _score_line(line, player, opponent)
    return score


def _all_lines(board):
    """Yield all rows, columns, and diagonals of length >= 5."""
    # Rows
    for r in range(BOARD_SIZE):
        yield board[r]

    # Columns
    for c in range(BOARD_SIZE):
        yield [board[r][c] for r in range(BOARD_SIZE)]

    # Diagonals ↘ (top-left to bottom-right)
    for start_r in range(BOARD_SIZE):
        diag = []
        r, c = start_r, 0
        while r < BOARD_SIZE and c < BOARD_SIZE:
            diag.append(board[r][c])
            r += 1
            c += 1
        if len(diag) >= 5:
            yield diag

    for start_c in range(1, BOARD_SIZE):
        diag = []
        r, c = 0, start_c
        while r < BOARD_SIZE and c < BOARD_SIZE:
            diag.append(board[r][c])
            r += 1
            c += 1
        if len(diag) >= 5:
            yield diag

    # Anti-diagonals ↗ (top-right to bottom-left)
    for start_r in range(BOARD_SIZE):
        anti = []
        r, c = start_r, BOARD_SIZE - 1
        while r < BOARD_SIZE and c >= 0:
            anti.append(board[r][c])
            r += 1
            c -= 1
        if len(anti) >= 5:
            yield anti

    for start_c in range(BOARD_SIZE - 2, -1, -1):
        anti = []
        r, c = 0, start_c
        while r < BOARD_SIZE and c >= 0:
            anti.append(board[r][c])
            r += 1
            c -= 1
        if len(anti) >= 5:
            yield anti


def _score_line(line, player, opponent):
    """Score a single line for `player`."""
    score = 0
    n = len(line)
    i = 0

    while i < n:
        if line[i] != player:
            i += 1
            continue

        # Count the run of player's pieces starting at i
        j = i
        while j < n and line[j] == player:
            j += 1
        count = j - i  # length of consecutive run

        # Check what's on each end of the run
        left_open  = (i > 0 and line[i - 1] == EMPTY)
        right_open = (j < n and line[j] == EMPTY)
        open_ends  = (1 if left_open else 0) + (1 if right_open else 0)

        if count >= 5:
            score += FIVE
        elif count == 4:
            if open_ends == 2:
                score += OPEN_FOUR
            elif open_ends == 1:
                score += BLOCKED_FOUR
        elif count == 3:
            if open_ends == 2:
                score += OPEN_THREE
            elif open_ends == 1:
                score += BLOCKED_THREE
        elif count == 2:
            if open_ends == 2:
                score += OPEN_TWO
            elif open_ends == 1:
                score += BLOCKED_TWO

        i = j  # skip past the run

    return score


def _count_pattern(board, player, dr, dc, length, open_ends):
    """
    Count occurrences of a pattern (sequence of `length` pieces for `player`
    with `open_ends` unblocked ends) across the board in direction (dr, dc).
    """
    count = 0
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            # Try to match a run of `length` pieces starting here
            cells = []
            nr, nc = r, c
            valid = True
            for _ in range(length):
                if not (0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE):
                    valid = False
                    break
                cells.append((nr, nc))
                nr += dr
                nc += dc

            if not valid:
                continue
            if any(board[cr][cc] != player for cr, cc in cells):
                continue

            # Check ends
            before_r = r - dr
            before_c = c - dc
            after_r  = nr
            after_c  = nc

            left_open  = (0 <= before_r < BOARD_SIZE and 0 <= before_c < BOARD_SIZE
                          and board[before_r][before_c] == EMPTY)
            right_open = (0 <= after_r < BOARD_SIZE and 0 <= after_c < BOARD_SIZE
                          and board[after_r][after_c] == EMPTY)

            actual_open = (1 if left_open else 0) + (1 if right_open else 0)
            if actual_open == open_ends:
                count += 1

    return count
