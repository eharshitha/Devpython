import pygame
import sys
import copy
import json
import os
import random
import math

# ============================================================
# PYTHON CHESS - FULL SINGLE FILE VERSION
# ============================================================

pygame.init()

try:
    pygame.mixer.init()
    SOUND_AVAILABLE = True
except Exception:
    SOUND_AVAILABLE = False


# ============================================================
# SETTINGS
# ============================================================

WIDTH = 1100
HEIGHT = 760

BOARD_SIZE = 640
SQUARE_SIZE = BOARD_SIZE // 8

PANEL_X = BOARD_SIZE
PANEL_WIDTH = WIDTH - BOARD_SIZE

FPS = 60

# Chess clock
CLOCK_TIME = 10 * 60
INCREMENT = 0

# AI
AI_ENABLED = True
AI_COLOR = "black"
AI_DEPTH = 2

SAVE_FILE = "chess_save.json"

# PNG directory
PIECE_FOLDER = "pieces"


# ============================================================
# SCREEN
# ============================================================

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Chess - Full Edition")


# ============================================================
# COLORS
# ============================================================

LIGHT_SQUARE = (235, 236, 208)
DARK_SQUARE = (115, 149, 82)

SELECTED = (246, 246, 105)
MOVE_DOT = (60, 60, 60)

CHECK_COLOR = (220, 70, 70)
CHECKMATE_COLOR = (190, 40, 40)

PANEL_COLOR = (238, 238, 238)
BUTTON_COLOR = (80, 120, 80)
BUTTON_HOVER = (100, 145, 100)

WHITE = (245, 245, 245)
BLACK = (25, 25, 25)
GRAY = (100, 100, 100)
DARK_GRAY = (55, 55, 55)

GREEN = (60, 140, 80)
GOLD = (220, 180, 50)
BLUE = (70, 120, 210)


# ============================================================
# FONTS
# ============================================================

piece_font = pygame.font.SysFont(
    "segoeuisymbol",
    64
)

title_font = pygame.font.SysFont(
    "arial",
    27,
    bold=True
)

info_font = pygame.font.SysFont(
    "arial",
    21,
    bold=True
)

small_font = pygame.font.SysFont(
    "arial",
    17
)

tiny_font = pygame.font.SysFont(
    "arial",
    14
)


# ============================================================
# UNICODE PIECES
# ============================================================

UNICODE = {
    "K": "♔",
    "Q": "♕",
    "R": "♖",
    "B": "♗",
    "N": "♘",
    "P": "♙",

    "k": "♚",
    "q": "♛",
    "r": "♜",
    "b": "♝",
    "n": "♞",
    "p": "♟"
}


# ============================================================
# STARTING POSITION
# ============================================================

STARTING_BOARD = [
    ["r", "n", "b", "q", "k", "b", "n", "r"],
    ["p", "p", "p", "p", "p", "p", "p", "p"],
    [".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
    ["P", "P", "P", "P", "P", "P", "P", "P"],
    ["R", "N", "B", "Q", "K", "B", "N", "R"]
]


# ============================================================
# GAME STATE
# ============================================================

board = copy.deepcopy(STARTING_BOARD)

turn = "white"

selected_square = None
dragging_piece = None
drag_mouse_pos = None

legal_moves_for_selected = []

move_history = []
redo_history = []

notation_history = []

white_castle_kingside = True
white_castle_queenside = True
black_castle_kingside = True
black_castle_queenside = True

en_passant_target = None

game_over = False
winner = None

move_number = 1

promotion_pending = False
promotion_start = None
promotion_end = None

paused = False

white_time = CLOCK_TIME
black_time = CLOCK_TIME

last_clock_tick = pygame.time.get_ticks()

captured_white = []
captured_black = []

resigned = False

ai_thinking = False

ai_depth = AI_DEPTH


# ============================================================
# SOUND
# ============================================================

def make_beep(frequency, duration=80):

    if not SOUND_AVAILABLE:
        return None

    try:
        sample_rate = 44100
        count = int(sample_rate * duration / 1000)

        buffer = bytearray()

        for i in range(count):

            value = int(
                10000 *
                math.sin(
                    2 * math.pi *
                    frequency *
                    i /
                    sample_rate
                )
            )

            value = max(
                -32767,
                min(32767, value)
            )

            buffer += int(value).to_bytes(
                2,
                byteorder="little",
                signed=True
            )

        return pygame.mixer.Sound(
            buffer=bytes(buffer)
        )

    except Exception:
        return None


move_sound = make_beep(600, 60)
capture_sound = make_beep(300, 100)
check_sound = make_beep(900, 130)
game_sound = make_beep(1200, 250)


def play_sound(sound):

    if sound is not None:

        try:
            sound.play()
        except Exception:
            pass


# ============================================================
# PIECE IMAGE LOADING
# ============================================================

piece_images = {}


def load_piece_images():

    if not os.path.exists(PIECE_FOLDER):
        return

    names = {
        "K": "white_king.png",
        "Q": "white_queen.png",
        "R": "white_rook.png",
        "B": "white_bishop.png",
        "N": "white_knight.png",
        "P": "white_pawn.png",

        "k": "black_king.png",
        "q": "black_queen.png",
        "r": "black_rook.png",
        "b": "black_bishop.png",
        "n": "black_knight.png",
        "p": "black_pawn.png"
    }

    for piece, filename in names.items():

        path = os.path.join(
            PIECE_FOLDER,
            filename
        )

        if os.path.exists(path):

            try:

                image = pygame.image.load(
                    path
                ).convert_alpha()

                image = pygame.transform.smoothscale(
                    image,
                    (
                        SQUARE_SIZE - 10,
                        SQUARE_SIZE - 10
                    )
                )

                piece_images[piece] = image

            except Exception:
                pass


load_piece_images()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def is_white(piece):

    return (
        piece != "."
        and piece.isupper()
    )


def is_black(piece):

    return (
        piece != "."
        and piece.islower()
    )


def piece_color(piece):

    if piece == ".":
        return None

    return (
        "white"
        if piece.isupper()
        else "black"
    )


def opponent(color):

    return (
        "black"
        if color == "white"
        else "white"
    )


def inside(r, c):

    return (
        0 <= r < 8
        and 0 <= c < 8
    )


def belongs_to_turn(piece):

    return (
        piece != "."
        and piece_color(piece) == turn
    )


def square_name(square):

    r, c = square

    return (
        chr(ord("a") + c)
        + str(8 - r)
    )


def find_king(position, color):

    king = (
        "K"
        if color == "white"
        else "k"
    )

    for r in range(8):

        for c in range(8):

            if position[r][c] == king:
                return r, c

    return None


# ============================================================
# ATTACK DETECTION
# ============================================================

def square_attacked(
    position,
    row,
    col,
    by_color
):

    # --------------------------------------------------------
    # PAWNS
    # --------------------------------------------------------

    if by_color == "white":

        pawn_row = row + 1

        for dc in [-1, 1]:

            c = col + dc

            if inside(pawn_row, c):

                if position[pawn_row][c] == "P":
                    return True

    else:

        pawn_row = row - 1

        for dc in [-1, 1]:

            c = col + dc

            if inside(pawn_row, c):

                if position[pawn_row][c] == "p":
                    return True

    # --------------------------------------------------------
    # KNIGHTS
    # --------------------------------------------------------

    knight = (
        "N"
        if by_color == "white"
        else "n"
    )

    offsets = [
        (-2, -1),
        (-2, 1),
        (-1, -2),
        (-1, 2),
        (1, -2),
        (1, 2),
        (2, -1),
        (2, 1)
    ]

    for dr, dc in offsets:

        r = row + dr
        c = col + dc

        if inside(r, c):

            if position[r][c] == knight:
                return True

    # --------------------------------------------------------
    # KING
    # --------------------------------------------------------

    king = (
        "K"
        if by_color == "white"
        else "k"
    )

    for dr in [-1, 0, 1]:

        for dc in [-1, 0, 1]:

            if dr == 0 and dc == 0:
                continue

            r = row + dr
            c = col + dc

            if inside(r, c):

                if position[r][c] == king:
                    return True

    # --------------------------------------------------------
    # ROOK / QUEEN
    # --------------------------------------------------------

    rook = (
        "R"
        if by_color == "white"
        else "r"
    )

    queen = (
        "Q"
        if by_color == "white"
        else "q"
    )

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    for dr, dc in directions:

        r = row + dr
        c = col + dc

        while inside(r, c):

            piece = position[r][c]

            if piece != ".":

                if (
                    piece == rook
                    or piece == queen
                ):
                    return True

                break

            r += dr
            c += dc

    # --------------------------------------------------------
    # BISHOP / QUEEN
    # --------------------------------------------------------

    bishop = (
        "B"
        if by_color == "white"
        else "b"
    )

    directions = [
        (-1, -1),
        (-1, 1),
        (1, -1),
        (1, 1)
    ]

    for dr, dc in directions:

        r = row + dr
        c = col + dc

        while inside(r, c):

            piece = position[r][c]

            if piece != ".":

                if (
                    piece == bishop
                    or piece == queen
                ):
                    return True

                break

            r += dr
            c += dc

    return False


# ============================================================
# CHECK
# ============================================================

def is_in_check(position, color):

    king_position = find_king(
        position,
        color
    )

    if king_position is None:
        return True

    r, c = king_position

    return square_attacked(
        position,
        r,
        c,
        opponent(color)
    )


# ============================================================
# RAW MOVES
# ============================================================

def generate_raw_moves(
    position,
    r,
    c,
    color
):

    piece = position[r][c]

    if piece == ".":
        return []

    if piece_color(piece) != color:
        return []

    moves = []

    upper = piece.upper()

    # ========================================================
    # PAWN
    # ========================================================

    if upper == "P":

        direction = (
            -1
            if color == "white"
            else 1
        )

        start_row = (
            6
            if color == "white"
            else 1
        )

        nr = r + direction

        if inside(nr, c):

            if position[nr][c] == ".":

                moves.append((nr, c))

                nr2 = r + direction * 2

                if (
                    r == start_row
                    and position[nr2][c] == "."
                ):

                    moves.append((nr2, c))

        # Captures
        for dc in [-1, 1]:

            nc = c + dc

            if inside(nr, nc):

                target = position[nr][nc]

                if (
                    target != "."
                    and piece_color(target) != color
                    and target.upper() != "K"
                ):

                    moves.append((nr, nc))

        # En passant
        if en_passant_target is not None:

            er, ec = en_passant_target

            if (
                er == nr
                and abs(ec - c) == 1
            ):

                moves.append((er, ec))

    # ========================================================
    # KNIGHT
    # ========================================================

    elif upper == "N":

        offsets = [
            (-2, -1),
            (-2, 1),
            (-1, -2),
            (-1, 2),
            (1, -2),
            (1, 2),
            (2, -1),
            (2, 1)
        ]

        for dr, dc in offsets:

            nr = r + dr
            nc = c + dc

            if inside(nr, nc):

                target = position[nr][nc]

                if (
                    target == "."
                    or (
                        piece_color(target) != color
                        and target.upper() != "K"
                    )
                ):

                    moves.append((nr, nc))

    # ========================================================
    # SLIDING PIECES
    # ========================================================

    elif upper in ("B", "R", "Q"):

        if upper == "B":

            directions = [
                (-1, -1),
                (-1, 1),
                (1, -1),
                (1, 1)
            ]

        elif upper == "R":

            directions = [
                (-1, 0),
                (1, 0),
                (0, -1),
                (0, 1)
            ]

        else:

            directions = [
                (-1, -1),
                (-1, 1),
                (1, -1),
                (1, 1),
                (-1, 0),
                (1, 0),
                (0, -1),
                (0, 1)
            ]

        for dr, dc in directions:

            nr = r + dr
            nc = c + dc

            while inside(nr, nc):

                target = position[nr][nc]

                if target == ".":

                    moves.append((nr, nc))

                else:

                    if (
                        piece_color(target) != color
                        and target.upper() != "K"
                    ):

                        moves.append((nr, nc))

                    break

                nr += dr
                nc += dc

    # ========================================================
    # KING
    # ========================================================

    elif upper == "K":

        for dr in [-1, 0, 1]:

            for dc in [-1, 0, 1]:

                if dr == 0 and dc == 0:
                    continue

                nr = r + dr
                nc = c + dc

                if inside(nr, nc):

                    target = position[nr][nc]

                    if (
                        target == "."
                        or (
                            piece_color(target) != color
                            and target.upper() != "K"
                        )
                    ):

                        moves.append((nr, nc))

    return moves


# ============================================================
# MAKE MOVE ON COPY
# ============================================================

def make_move_on_position(
    position,
    start,
    end
):

    new_position = copy.deepcopy(position)

    sr, sc = start
    er, ec = end

    piece = new_position[sr][sc]

    new_position[er][ec] = piece
    new_position[sr][sc] = "."

    # En passant
    if piece.upper() == "P":

        if (
            sc != ec
            and position[er][ec] == "."
        ):

            captured_row = (
                er + 1
                if piece == "P"
                else er - 1
            )

            if inside(captured_row, ec):

                new_position[
                    captured_row
                ][ec] = "."

    # Promotion
    if piece == "P" and er == 0:

        new_position[er][ec] = "Q"

    elif piece == "p" and er == 7:

        new_position[er][ec] = "q"

    # Castling
    if piece == "K" and sr == 7 and sc == 4:

        if ec == 6:

            new_position[7][5] = new_position[7][7]
            new_position[7][7] = "."

        elif ec == 2:

            new_position[7][3] = new_position[7][0]
            new_position[7][0] = "."

    elif piece == "k" and sr == 0 and sc == 4:

        if ec == 6:

            new_position[0][5] = new_position[0][7]
            new_position[0][7] = "."

        elif ec == 2:

            new_position[0][3] = new_position[0][0]
            new_position[0][0] = "."

    return new_position


# ============================================================
# LEGAL MOVES
# ============================================================

def legal_moves(
    position,
    r,
    c,
    color
):

    piece = position[r][c]

    if piece == ".":
        return []

    if piece_color(piece) != color:
        return []

    raw = generate_raw_moves(
        position,
        r,
        c,
        color
    )

    legal = []

    for move in raw:

        test_position = make_move_on_position(
            position,
            (r, c),
            move
        )

        if not is_in_check(
            test_position,
            color
        ):

            legal.append(move)

    # ========================================================
    # CASTLING
    # ========================================================

    if piece.upper() == "K":

        if not is_in_check(
            position,
            color
        ):

            if (
                color == "white"
                and r == 7
                and c == 4
            ):

                # Kingside
                if (
                    white_castle_kingside
                    and position[7][5] == "."
                    and position[7][6] == "."
                    and position[7][7] == "R"
                    and not square_attacked(
                        position,
                        7,
                        5,
                        "black"
                    )
                    and not square_attacked(
                        position,
                        7,
                        6,
                        "black"
                    )
                ):

                    legal.append((7, 6))

                # Queenside
                if (
                    white_castle_queenside
                    and position[7][1] == "."
                    and position[7][2] == "."
                    and position[7][3] == "."
                    and position[7][0] == "R"
                    and not square_attacked(
                        position,
                        7,
                        3,
                        "black"
                    )
                    and not square_attacked(
                        position,
                        7,
                        2,
                        "black"
                    )
                ):

                    legal.append((7, 2))

            elif (
                color == "black"
                and r == 0
                and c == 4
            ):

                # Kingside
                if (
                    black_castle_kingside
                    and position[0][5] == "."
                    and position[0][6] == "."
                    and position[0][7] == "r"
                    and not square_attacked(
                        position,
                        0,
                        5,
                        "white"
                    )
                    and not square_attacked(
                        position,
                        0,
                        6,
                        "white"
                    )
                ):

                    legal.append((0, 6))

                # Queenside
                if (
                    black_castle_queenside
                    and position[0][1] == "."
                    and position[0][2] == "."
                    and position[0][3] == "."
                    and position[0][0] == "r"
                    and not square_attacked(
                        position,
                        0,
                        3,
                        "white"
                    )
                    and not square_attacked(
                        position,
                        0,
                        2,
                        "white"
                    )
                ):

                    legal.append((0, 2))

    return legal


# ============================================================
# ALL LEGAL MOVES
# ============================================================

def all_legal_moves(
    position,
    color
):

    result = []

    for r in range(8):

        for c in range(8):

            if (
                position[r][c] != "."
                and piece_color(
                    position[r][c]
                ) == color
            ):

                for move in legal_moves(
                    position,
                    r,
                    c,
                    color
                ):

                    result.append(
                        ((r, c), move)
                    )

    return result


# ============================================================
# GAME STATUS
# ============================================================

def has_legal_moves(color):

    return bool(
        all_legal_moves(
            board,
            color
        )
    )


def update_game_status():

    global game_over
    global winner

    if not has_legal_moves(turn):

        game_over = True

        if is_in_check(
            board,
            turn
        ):

            winner = opponent(turn)

            play_sound(game_sound)

        else:

            winner = "draw"

            play_sound(game_sound)

    else:

        game_over = False
        winner = None


# ============================================================
# POSITION VALUE FOR AI
# ============================================================

PIECE_VALUES = {
    "P": 100,
    "N": 320,
    "B": 330,
    "R": 500,
    "Q": 900,
    "K": 20000
}


def evaluate(position):

    score = 0

    for row in position:

        for piece in row:

            if piece == ".":
                continue

            value = PIECE_VALUES[
                piece.upper()
            ]

            if piece.isupper():

                score += value

            else:

                score -= value

    return score


# ============================================================
# MINIMAX
# ============================================================

def minimax(
    position,
    depth,
    maximizing
):

    if depth == 0:

        return evaluate(position), None

    color = (
        "white"
        if maximizing
        else "black"
    )

    moves = all_legal_moves(
        position,
        color
    )

    if not moves:

        if is_in_check(
            position,
            color
        ):

            if color == "black":

                return 1000000, None

            return -1000000, None

        return 0, None

    best_move = None

    if maximizing:

        best_score = -float("inf")

        for start, end in moves:

            new_position = make_move_on_position(
                position,
                start,
                end
            )

            score, _ = minimax(
                new_position,
                depth - 1,
                False
            )

            if score > best_score:

                best_score = score
                best_move = (
                    start,
                    end
                )

        return best_score, best_move

    else:

        best_score = float("inf")

        for start, end in moves:

            new_position = make_move_on_position(
                position,
                start,
                end
            )

            score, _ = minimax(
                new_position,
                depth - 1,
                True
            )

            if score < best_score:

                best_score = score
                best_move = (
                    start,
                    end
                )

        return best_score, best_move


# ============================================================
# AI MOVE
# ============================================================

def get_ai_move():

    moves = all_legal_moves(
        board,
        AI_COLOR
    )

    if not moves:
        return None

    if ai_depth <= 1:

        return random.choice(moves)

    _, move = minimax(
        board,
        ai_depth,
        AI_COLOR == "white"
    )

    if move is None:

        return random.choice(moves)

    return move


# ============================================================
# SAVE STATE
# ============================================================

def save_state():

    return {
        "board": copy.deepcopy(board),
        "turn": turn,

        "white_ks": white_castle_kingside,
        "white_qs": white_castle_queenside,

        "black_ks": black_castle_kingside,
        "black_qs": black_castle_queenside,

        "en_passant": en_passant_target,

        "move_number": move_number,

        "white_time": white_time,
        "black_time": black_time,

        "captured_white": copy.deepcopy(
            captured_white
        ),

        "captured_black": copy.deepcopy(
            captured_black
        ),

        "notation_history": copy.deepcopy(
            notation_history
        )
    }


# ============================================================
# RESTORE STATE
# ============================================================

def restore_state(state):

    global board
    global turn

    global white_castle_kingside
    global white_castle_queenside

    global black_castle_kingside
    global black_castle_queenside

    global en_passant_target
    global move_number

    global white_time
    global black_time

    global captured_white
    global captured_black

    global notation_history

    board = copy.deepcopy(
        state["board"]
    )

    turn = state["turn"]

    white_castle_kingside = state[
        "white_ks"
    ]

    white_castle_queenside = state[
        "white_qs"
    ]

    black_castle_kingside = state[
        "black_ks"
    ]

    black_castle_queenside = state[
        "black_qs"
    ]

    en_passant_target = state[
        "en_passant"
    ]

    move_number = state[
        "move_number"
    ]

    white_time = state.get(
        "white_time",
        CLOCK_TIME
    )

    black_time = state.get(
        "black_time",
        CLOCK_TIME
    )

    captured_white = copy.deepcopy(
        state.get(
            "captured_white",
            []
        )
    )

    captured_black = copy.deepcopy(
        state.get(
            "captured_black",
            []
        )
    )

    notation_history = copy.deepcopy(
        state.get(
            "notation_history",
            []
        )
    )


# ============================================================
# NOTATION
# ============================================================

def create_notation(
    start,
    end,
    piece,
    captured,
    promotion=None
):

    start_name = square_name(start)
    end_name = square_name(end)

    # Castling
    if (
        piece.upper() == "K"
        and abs(
            start[1] - end[1]
        ) == 2
    ):

        if end[1] == 6:
            return "O-O"

        return "O-O-O"

    letter = ""

    if piece.upper() != "P":

        letter = piece.upper()

    capture_symbol = (
        "x"
        if captured != "."
        else ""
    )

    if (
        piece.upper() == "P"
        and captured != "."
    ):

        letter = start_name[0]

    result = (
        letter
        + capture_symbol
        + end_name
    )

    if promotion:

        result += "=" + promotion.upper()

    return result


# ============================================================
# REAL MOVE
# ============================================================

def make_move(
    start,
    end,
    promotion=None
):

    # IMPORTANT:
    # white_time and black_time MUST be global because
    # this function modifies them.

    global board
    global turn
    global en_passant_target
    global move_number

    global white_castle_kingside
    global white_castle_queenside
    global black_castle_kingside
    global black_castle_queenside

    global captured_white
    global captured_black

    global white_time
    global black_time

    global game_over
    global winner

    sr, sc = start
    er, ec = end

    piece = board[sr][sc]

    captured = board[er][ec]

    # --------------------------------------------------------
    # Save undo state
    # --------------------------------------------------------

    move_history.append(
        save_state()
    )

    redo_history.clear()

    # --------------------------------------------------------
    # Captured rook affects castling
    # --------------------------------------------------------

    if captured == "R":

        if er == 7 and ec == 0:

            white_castle_queenside = False

        if er == 7 and ec == 7:

            white_castle_kingside = False

    elif captured == "r":

        if er == 0 and ec == 0:

            black_castle_queenside = False

        if er == 0 and ec == 7:

            black_castle_kingside = False

    # --------------------------------------------------------
    # Piece castling rights
    # --------------------------------------------------------

    if piece == "K":

        white_castle_kingside = False
        white_castle_queenside = False

    elif piece == "k":

        black_castle_kingside = False
        black_castle_queenside = False

    elif piece == "R":

        if sr == 7 and sc == 0:

            white_castle_queenside = False

        if sr == 7 and sc == 7:

            white_castle_kingside = False

    elif piece == "r":

        if sr == 0 and sc == 0:

            black_castle_queenside = False

        if sr == 0 and sc == 7:

            black_castle_kingside = False

    # --------------------------------------------------------
    # En passant capture
    # --------------------------------------------------------

    is_en_passant = (
        piece.upper() == "P"
        and sc != ec
        and board[er][ec] == "."
    )

    if is_en_passant:

        captured_row = (
            er + 1
            if piece == "P"
            else er - 1
        )

        if inside(
            captured_row,
            ec
        ):

            captured = board[
                captured_row
            ][ec]

            board[
                captured_row
            ][ec] = "."

    # --------------------------------------------------------
    # Capture list
    # --------------------------------------------------------

    if captured != ".":

        if captured.isupper():

            captured_white.append(
                captured
            )

        else:

            captured_black.append(
                captured
            )

    # --------------------------------------------------------
    # Move piece
    # --------------------------------------------------------

    board[er][ec] = piece
    board[sr][sc] = "."

    # --------------------------------------------------------
    # Castling rook
    # --------------------------------------------------------

    if (
        piece == "K"
        and sr == 7
        and sc == 4
    ):

        if ec == 6:

            board[7][5] = board[7][7]
            board[7][7] = "."

        elif ec == 2:

            board[7][3] = board[7][0]
            board[7][0] = "."

    elif (
        piece == "k"
        and sr == 0
        and sc == 4
    ):

        if ec == 6:

            board[0][5] = board[0][7]
            board[0][7] = "."

        elif ec == 2:

            board[0][3] = board[0][0]
            board[0][0] = "."

    # --------------------------------------------------------
    # Promotion
    # --------------------------------------------------------

    if piece == "P" and er == 0:

        board[er][ec] = (
            promotion
            if promotion
            else "Q"
        ).upper()

    elif piece == "p" and er == 7:

        board[er][ec] = (
            promotion
            if promotion
            else "q"
        ).lower()

    # --------------------------------------------------------
    # En passant target
    # --------------------------------------------------------

    en_passant_target = None

    if piece.upper() == "P":

        if abs(er - sr) == 2:

            middle = (
                er + sr
            ) // 2

            en_passant_target = (
                middle,
                sc
            )

    # --------------------------------------------------------
    # Notation
    # --------------------------------------------------------

    notation = create_notation(
        start,
        end,
        piece,
        captured,
        promotion
    )

    notation_history.append(
        notation
    )

    # --------------------------------------------------------
    # Sound
    # --------------------------------------------------------

    if captured != "." or is_en_passant:

        play_sound(capture_sound)

    else:

        play_sound(move_sound)

    # --------------------------------------------------------
    # Change turn
    # --------------------------------------------------------

    if turn == "white":

        turn = "black"

    else:

        turn = "white"
        move_number += 1

    # --------------------------------------------------------
    # Add clock increment
    #
    # If turn changed to black, white just moved.
    # If turn changed to white, black just moved.
    # --------------------------------------------------------

    if turn == "black":

        white_time += INCREMENT

    else:

        black_time += INCREMENT

    # --------------------------------------------------------
    # Game status
    # --------------------------------------------------------

    update_game_status()

    if (
        not game_over
        and is_in_check(
            board,
            turn
        )
    ):

        play_sound(check_sound)


# ============================================================
# UNDO
# ============================================================

def undo():

    global selected_square
    global legal_moves_for_selected
    global game_over
    global winner
    global last_clock_tick

    if not move_history:
        return

    current = save_state()

    redo_history.append(
        current
    )

    state = move_history.pop()

    restore_state(state)

    selected_square = None
    legal_moves_for_selected = []

    game_over = False
    winner = None

    last_clock_tick = pygame.time.get_ticks()


# ============================================================
# REDO
# ============================================================

def redo():

    global selected_square
    global legal_moves_for_selected
    global last_clock_tick

    if not redo_history:
        return

    current = save_state()

    move_history.append(
        current
    )

    state = redo_history.pop()

    restore_state(state)

    selected_square = None
    legal_moves_for_selected = []

    update_game_status()

    last_clock_tick = pygame.time.get_ticks()


# ============================================================
# RESTART
# ============================================================

def restart():

    global board
    global turn

    global selected_square
    global legal_moves_for_selected

    global move_history
    global redo_history
    global notation_history

    global white_castle_kingside
    global white_castle_queenside

    global black_castle_kingside
    global black_castle_queenside

    global en_passant_target

    global game_over
    global winner

    global move_number

    global white_time
    global black_time

    global captured_white
    global captured_black

    global paused
    global resigned

    global promotion_pending
    global promotion_start
    global promotion_end

    global dragging_piece
    global drag_mouse_pos

    global last_clock_tick

    board = copy.deepcopy(
        STARTING_BOARD
    )

    turn = "white"

    selected_square = None
    legal_moves_for_selected = []

    move_history = []
    redo_history = []
    notation_history = []

    white_castle_kingside = True
    white_castle_queenside = True

    black_castle_kingside = True
    black_castle_queenside = True

    en_passant_target = None

    game_over = False
    winner = None

    move_number = 1

    white_time = CLOCK_TIME
    black_time = CLOCK_TIME

    captured_white = []
    captured_black = []

    paused = False
    resigned = False

    promotion_pending = False
    promotion_start = None
    promotion_end = None

    dragging_piece = None
    drag_mouse_pos = None

    last_clock_tick = pygame.time.get_ticks()


# ============================================================
# RESIGN
# ============================================================

def resign():

    global game_over
    global winner
    global resigned

    if game_over:
        return

    game_over = True
    winner = opponent(turn)
    resigned = True

    play_sound(game_sound)


# ============================================================
# SAVE GAME
# ============================================================

def save_game():

    data = save_state()

    data["paused"] = paused
    data["game_over"] = game_over
    data["winner"] = winner

    try:

        with open(
            SAVE_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )

        return True

    except Exception:

        return False


# ============================================================
# LOAD GAME
# ============================================================

def load_game():

    global game_over
    global winner
    global paused

    global selected_square
    global legal_moves_for_selected

    global resigned
    global last_clock_tick

    if not os.path.exists(
        SAVE_FILE
    ):

        return False

    try:

        with open(
            SAVE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        restore_state(data)

        game_over = data.get(
            "game_over",
            False
        )

        winner = data.get(
            "winner",
            None
        )

        paused = data.get(
            "paused",
            False
        )

        resigned = False

        selected_square = None
        legal_moves_for_selected = []

        move_history.clear()
        redo_history.clear()

        last_clock_tick = pygame.time.get_ticks()

        return True

    except Exception:

        return False


# ============================================================
# CLOCK
# ============================================================

def format_time(seconds):

    seconds = max(
        0,
        int(seconds)
    )

    minutes = seconds // 60
    secs = seconds % 60

    return f"{minutes:02d}:{secs:02d}"


def update_clock():

    global white_time
    global black_time

    global game_over
    global winner

    global last_clock_tick

    if (
        game_over
        or paused
        or ai_thinking
        or promotion_pending
    ):

        last_clock_tick = pygame.time.get_ticks()

        return

    now = pygame.time.get_ticks()

    elapsed = (
        now - last_clock_tick
    ) / 1000.0

    last_clock_tick = now

    if turn == "white":

        white_time -= elapsed

        if white_time <= 0:

            white_time = 0
            game_over = True
            winner = "black"

            play_sound(game_sound)

    else:

        black_time -= elapsed

        if black_time <= 0:

            black_time = 0
            game_over = True
            winner = "white"

            play_sound(game_sound)


# ============================================================
# DRAW BOARD
# ============================================================

def draw_board():

    for row in range(8):

        for col in range(8):

            color = (
                LIGHT_SQUARE
                if (row + col) % 2 == 0
                else DARK_SQUARE
            )

            pygame.draw.rect(
                screen,
                color,
                (
                    col * SQUARE_SIZE,
                    row * SQUARE_SIZE,
                    SQUARE_SIZE,
                    SQUARE_SIZE
                )
            )

            # Files
            if row == 7:

                label = chr(
                    ord("a") + col
                )

                image = tiny_font.render(
                    label,
                    True,
                    (
                        DARK_SQUARE
                        if color == LIGHT_SQUARE
                        else LIGHT_SQUARE
                    )
                )

                screen.blit(
                    image,
                    (
                        col * SQUARE_SIZE
                        + SQUARE_SIZE - 14,
                        row * SQUARE_SIZE
                        + SQUARE_SIZE - 18
                    )
                )

            # Ranks
            if col == 0:

                label = str(
                    8 - row
                )

                image = tiny_font.render(
                    label,
                    True,
                    (
                        DARK_SQUARE
                        if color == LIGHT_SQUARE
                        else LIGHT_SQUARE
                    )
                )

                screen.blit(
                    image,
                    (
                        4,
                        row * SQUARE_SIZE + 3
                    )
                )


# ============================================================
# DRAW SELECTION
# ============================================================

def draw_selection():

    if selected_square is None:
        return

    r, c = selected_square

    pygame.draw.rect(
        screen,
        SELECTED,
        (
            c * SQUARE_SIZE,
            r * SQUARE_SIZE,
            SQUARE_SIZE,
            SQUARE_SIZE
        ),
        5
    )

    for mr, mc in legal_moves_for_selected:

        center = (
            mc * SQUARE_SIZE
            + SQUARE_SIZE // 2,

            mr * SQUARE_SIZE
            + SQUARE_SIZE // 2
        )

        if board[mr][mc] == ".":

            pygame.draw.circle(
                screen,
                MOVE_DOT,
                center,
                9
            )

        else:

            pygame.draw.circle(
                screen,
                MOVE_DOT,
                center,
                SQUARE_SIZE // 2 - 8,
                5
            )


# ============================================================
# DRAW CHECK
# ============================================================

def draw_check():

    if not is_in_check(
        board,
        turn
    ):

        return

    king = find_king(
        board,
        turn
    )

    if king:

        r, c = king

        pygame.draw.rect(
            screen,
            CHECK_COLOR,
            (
                c * SQUARE_SIZE + 5,
                r * SQUARE_SIZE + 5,
                SQUARE_SIZE - 10,
                SQUARE_SIZE - 10
            ),
            7
        )


# ============================================================
# DRAW PIECES
# ============================================================

def draw_pieces():

    for row in range(8):

        for col in range(8):

            piece = board[row][col]

            if piece == ".":
                continue

            x = (
                col * SQUARE_SIZE
                + SQUARE_SIZE // 2
            )

            y = (
                row * SQUARE_SIZE
                + SQUARE_SIZE // 2
            )

            # Don't draw dragged piece
            if (
                dragging_piece is not None
                and selected_square == (
                    row,
                    col
                )
            ):

                continue

            if piece in piece_images:

                image = piece_images[piece]

                rect = image.get_rect(
                    center=(x, y)
                )

                screen.blit(
                    image,
                    rect
                )

            else:

                symbol = UNICODE[piece]

                if piece.isupper():

                    text_color = WHITE
                    outline_color = BLACK

                else:

                    text_color = BLACK
                    outline_color = WHITE

                for ox, oy in [
                    (-2, 0),
                    (2, 0),
                    (0, -2),
                    (0, 2)
                ]:

                    outline = piece_font.render(
                        symbol,
                        True,
                        outline_color
                    )

                    rect = outline.get_rect(
                        center=(
                            x + ox,
                            y + oy
                        )
                    )

                    screen.blit(
                        outline,
                        rect
                    )

                image = piece_font.render(
                    symbol,
                    True,
                    text_color
                )

                rect = image.get_rect(
                    center=(x, y)
                )

                screen.blit(
                    image,
                    rect
                )


# ============================================================
# DRAW DRAGGED PIECE
# ============================================================

def draw_dragged_piece():

    if (
        dragging_piece is None
        or drag_mouse_pos is None
    ):

        return

    piece = dragging_piece

    x, y = drag_mouse_pos

    if piece in piece_images:

        image = piece_images[piece]

        rect = image.get_rect(
            center=(x, y)
        )

        screen.blit(
            image,
            rect
        )

    else:

        symbol = UNICODE[piece]

        text_color = (
            WHITE
            if piece.isupper()
            else BLACK
        )

        outline_color = (
            BLACK
            if piece.isupper()
            else WHITE
        )

        for ox, oy in [
            (-2, 0),
            (2, 0),
            (0, -2),
            (0, 2)
        ]:

            image = piece_font.render(
                symbol,
                True,
                outline_color
            )

            rect = image.get_rect(
                center=(
                    x + ox,
                    y + oy
                )
            )

            screen.blit(
                image,
                rect
            )

        image = piece_font.render(
            symbol,
            True,
            text_color
        )

        rect = image.get_rect(
            center=(x, y)
        )

        screen.blit(
            image,
            rect
        )


# ============================================================
# BUTTON
# ============================================================

def draw_button(
    text,
    rect,
    action=False
):

    mouse = pygame.mouse.get_pos()

    hover = rect.collidepoint(
        mouse
    )

    color = (
        BUTTON_HOVER
        if hover
        else BUTTON_COLOR
    )

    pygame.draw.rect(
        screen,
        color,
        rect,
        border_radius=6
    )

    image = small_font.render(
        text,
        True,
        WHITE
    )

    image_rect = image.get_rect(
        center=rect.center
    )

    screen.blit(
        image,
        image_rect
    )


# ============================================================
# DRAW PANEL
# ============================================================

def draw_panel():

    pygame.draw.rect(
        screen,
        PANEL_COLOR,
        (
            PANEL_X,
            0,
            PANEL_WIDTH,
            HEIGHT
        )
    )

    title = title_font.render(
        "PYTHON CHESS",
        True,
        BLACK
    )

    screen.blit(
        title,
        (
            PANEL_X + 18,
            15
        )
    )

    # --------------------------------------------------------
    # Clocks
    # --------------------------------------------------------

    white_box = pygame.Rect(
        PANEL_X + 15,
        55,
        145,
        48
    )

    black_box = pygame.Rect(
        PANEL_X + 170,
        55,
        145,
        48
    )

    pygame.draw.rect(
        screen,
        WHITE,
        white_box,
        border_radius=5
    )

    pygame.draw.rect(
        screen,
        BLACK,
        black_box,
        border_radius=5
    )

    white_text = info_font.render(
        format_time(white_time),
        True,
        BLACK
    )

    black_text = info_font.render(
        format_time(black_time),
        True,
        WHITE
    )

    screen.blit(
        white_text,
        white_text.get_rect(
            center=white_box.center
        )
    )

    screen.blit(
        black_text,
        black_text.get_rect(
            center=black_box.center
        )
    )

    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    if game_over:

        if winner == "draw":

            status = "STALEMATE"

        else:

            status = (
                winner.upper()
                + " WINS!"
            )

        if resigned:

            status += " (RESIGN)"

        color = CHECKMATE_COLOR

    elif paused:

        status = "PAUSED"
        color = BLUE

    elif ai_thinking:

        status = "AI THINKING..."
        color = BLUE

    else:

        status = (
            turn.upper()
            + " TO MOVE"
        )

        color = BLACK

    status_image = info_font.render(
        status,
        True,
        color
    )

    screen.blit(
        status_image,
        (
            PANEL_X + 18,
            120
        )
    )

    # --------------------------------------------------------
    # Check
    # --------------------------------------------------------

    if (
        not game_over
        and is_in_check(
            board,
            turn
        )
    ):

        check_image = info_font.render(
            "CHECK!",
            True,
            CHECK_COLOR
        )

        screen.blit(
            check_image,
            (
                PANEL_X + 18,
                150
            )
        )

    # --------------------------------------------------------
    # Move list
    # --------------------------------------------------------

    moves_title = small_font.render(
        "MOVE HISTORY",
        True,
        GRAY
    )

    screen.blit(
        moves_title,
        (
            PANEL_X + 18,
            185
        )
    )

    y = 212

    start_index = max(
        0,
        len(notation_history) - 12
    )

    visible = notation_history[
        start_index:
    ]

    for i in range(
        0,
        len(visible),
        2
    ):

        actual = start_index + i

        move_num = (
            actual // 2
            + 1
        )

        white_move = (
            notation_history[actual]
        )

        black_move = ""

        if (
            actual + 1
            < len(notation_history)
        ):

            black_move = notation_history[
                actual + 1
            ]

        text = (
            f"{move_num}. "
            f"{white_move:<8}"
            f"{black_move}"
        )

        image = tiny_font.render(
            text,
            True,
            BLACK
        )

        screen.blit(
            image,
            (
                PANEL_X + 18,
                y
            )
        )

        y += 19

    # --------------------------------------------------------
    # Buttons
    # --------------------------------------------------------

    button_y = 470

    buttons = [
        (
            "New Game",
            pygame.Rect(
                PANEL_X + 15,
                button_y,
                140,
                35
            )
        ),

        (
            "Undo",
            pygame.Rect(
                PANEL_X + 165,
                button_y,
                140,
                35
            )
        ),

        (
            "Redo",
            pygame.Rect(
                PANEL_X + 15,
                button_y + 42,
                140,
                35
            )
        ),

        (
            "Save",
            pygame.Rect(
                PANEL_X + 165,
                button_y + 42,
                140,
                35
            )
        ),

        (
            "Load",
            pygame.Rect(
                PANEL_X + 15,
                button_y + 84,
                140,
                35
            )
        ),

        (
            "Pause",
            pygame.Rect(
                PANEL_X + 165,
                button_y + 84,
                140,
                35
            )
        ),

        (
            "Resign",
            pygame.Rect(
                PANEL_X + 15,
                button_y + 126,
                290,
                35
            )
        )
    ]

    for text, rect in buttons:

        draw_button(
            text,
            rect
        )

    # --------------------------------------------------------
    # AI
    # --------------------------------------------------------

    ai_text = (
        "AI: ON"
        if AI_ENABLED
        else "AI: OFF"
    )

    ai_image = small_font.render(
        ai_text,
        True,
        GREEN
        if AI_ENABLED
        else GRAY
    )

    screen.blit(
        ai_image,
        (
            PANEL_X + 18,
            650
        )
    )

    difficulty = small_font.render(
        f"AI Depth: {ai_depth}",
        True,
        GRAY
    )

    screen.blit(
        difficulty,
        (
            PANEL_X + 100,
            650
        )
    )

    help_text = small_font.render(
        "U Undo | Y Redo | R Restart | S Save",
        True,
        GRAY
    )

    screen.blit(
        help_text,
        (
            PANEL_X + 18,
            680
        )
    )

    help2 = small_font.render(
        "L Load | P Pause | ESC Quit",
        True,
        GRAY
    )

    screen.blit(
        help2,
        (
            PANEL_X + 18,
            705
        )
    )


# ============================================================
# PROMOTION MENU
# ============================================================

def draw_promotion_menu():

    if not promotion_pending:
        return

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 150)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    box = pygame.Rect(
        210,
        250,
        380,
        220
    )

    pygame.draw.rect(
        screen,
        WHITE,
        box,
        border_radius=12
    )

    title = info_font.render(
        "Choose Promotion",
        True,
        BLACK
    )

    screen.blit(
        title,
        title.get_rect(
            center=(
                box.centerx,
                box.y + 35
            )
        )
    )

    pieces = [
        ("Q", "Queen"),
        ("R", "Rook"),
        ("B", "Bishop"),
        ("N", "Knight")
    ]

    for i, (piece, name) in enumerate(
        pieces
    ):

        rect = pygame.Rect(
            box.x + 20 + i * 87,
            box.y + 75,
            75,
            100
        )

        pygame.draw.rect(
            screen,
            LIGHT_SQUARE,
            rect,
            border_radius=6
        )

        symbol = UNICODE[piece]

        image = piece_font.render(
            symbol,
            True,
            BLACK
        )

        screen.blit(
            image,
            image.get_rect(
                center=(
                    rect.centerx,
                    rect.y + 42
                )
            )
        )

        label = tiny_font.render(
            name,
            True,
            BLACK
        )

        screen.blit(
            label,
            label.get_rect(
                center=(
                    rect.centerx,
                    rect.bottom - 16
                )
            )
        )


# ============================================================
# DRAW CAPTURED PIECES
# ============================================================

def draw_captured():

    text = small_font.render(
        "Captured:",
        True,
        GRAY
    )

    screen.blit(
        text,
        (
            PANEL_X + 18,
            380
        )
    )

    x = PANEL_X + 95

    for piece in captured_white:

        symbol = UNICODE.get(
            piece,
            piece
        )

        image = tiny_font.render(
            symbol,
            True,
            BLACK
        )

        screen.blit(
            image,
            (
                x,
                382
            )
        )

        x += 16

    x = PANEL_X + 95

    for piece in captured_black:

        symbol = UNICODE.get(
            piece,
            piece
        )

        image = tiny_font.render(
            symbol,
            True,
            BLACK
        )

        screen.blit(
            image,
            (
                x,
                405
            )
        )

        x += 16


# ============================================================
# DRAW EVERYTHING
# ============================================================

def draw():

    screen.fill(
        (40, 40, 40)
    )

    draw_board()
    draw_selection()
    draw_check()
    draw_pieces()
    draw_dragged_piece()
    draw_panel()
    draw_captured()
    draw_promotion_menu()

    pygame.display.flip()


# ============================================================
# BOARD POSITION FROM MOUSE
# ============================================================

def board_square_from_mouse(pos):

    x, y = pos

    if (
        x < 0
        or y < 0
        or x >= BOARD_SIZE
        or y >= BOARD_SIZE
    ):

        return None

    return (
        y // SQUARE_SIZE,
        x // SQUARE_SIZE
    )


# ============================================================
# START SELECTION
# ============================================================

def select_piece(square):

    global selected_square
    global legal_moves_for_selected

    r, c = square

    piece = board[r][c]

    if (
        piece != "."
        and piece_color(piece) == turn
    ):

        selected_square = square

        legal_moves_for_selected = legal_moves(
            board,
            r,
            c,
            turn
        )

        return True

    return False


# ============================================================
# CLICK HANDLING
# ============================================================

def handle_click(pos):

    global selected_square
    global legal_moves_for_selected

    # Promotion
    if promotion_pending:

        handle_promotion_click(pos)
        return

    # Panel
    if pos[0] >= BOARD_SIZE:

        handle_panel_click(pos)
        return

    if (
        game_over
        or paused
        or ai_thinking
    ):

        return

    square = board_square_from_mouse(
        pos
    )

    if square is None:
        return

    row, col = square

    if selected_square is None:

        select_piece(square)
        return

    if square in legal_moves_for_selected:

        start = selected_square

        piece = board[
            start[0]
        ][start[1]]

        if (
            piece.upper() == "P"
            and (
                row == 0
                or row == 7
            )
        ):

            begin_promotion(
                start,
                square
            )

        else:

            make_move(
                start,
                square
            )

            clear_selection()

        return

    if select_piece(square):

        return

    clear_selection()


# ============================================================
# PROMOTION
# ============================================================

def begin_promotion(
    start,
    end
):

    global promotion_pending
    global promotion_start
    global promotion_end

    promotion_pending = True
    promotion_start = start
    promotion_end = end


def handle_promotion_click(pos):

    global promotion_pending
    global promotion_start
    global promotion_end

    global selected_square
    global legal_moves_for_selected

    box = pygame.Rect(
        210,
        250,
        380,
        220
    )

    if not box.collidepoint(pos):

        return

    x = pos[0]

    relative = (
        x
        - (box.x + 20)
    )

    index = relative // 87

    if not (
        0 <= index < 4
    ):

        return

    choices = [
        "Q",
        "R",
        "B",
        "N"
    ]

    promotion = choices[index]

    if turn == "black":

        promotion = promotion.lower()

    make_move(
        promotion_start,
        promotion_end,
        promotion
    )

    promotion_pending = False
    promotion_start = None
    promotion_end = None

    selected_square = None
    legal_moves_for_selected = []


# ============================================================
# PANEL BUTTONS
# ============================================================

def handle_panel_click(pos):

    x, y = pos

    if x < PANEL_X:

        return

    button_y = 470

    buttons = [

        (
            pygame.Rect(
                PANEL_X + 15,
                button_y,
                140,
                35
            ),
            restart
        ),

        (
            pygame.Rect(
                PANEL_X + 165,
                button_y,
                140,
                35
            ),
            undo
        ),

        (
            pygame.Rect(
                PANEL_X + 15,
                button_y + 42,
                140,
                35
            ),
            redo
        ),

        (
            pygame.Rect(
                PANEL_X + 165,
                button_y + 42,
                140,
                35
            ),
            save_game
        ),

        (
            pygame.Rect(
                PANEL_X + 15,
                button_y + 84,
                140,
                35
            ),
            load_game
        ),

        (
            pygame.Rect(
                PANEL_X + 165,
                button_y + 84,
                140,
                35
            ),
            toggle_pause
        ),

        (
            pygame.Rect(
                PANEL_X + 15,
                button_y + 126,
                290,
                35
            ),
            resign
        )
    ]

    for rect, action in buttons:

        if rect.collidepoint(pos):

            action()
            return


def toggle_pause():

    global paused
    global last_clock_tick

    if game_over:

        return

    paused = not paused

    last_clock_tick = pygame.time.get_ticks()


# ============================================================
# DRAG AND DROP
# ============================================================

def handle_mouse_down(pos):

    global dragging_piece
    global drag_mouse_pos
    global selected_square
    global legal_moves_for_selected

    # FIX:
    # Allow panel buttons to work with the mouse.
    if pos[0] >= BOARD_SIZE:

        if promotion_pending:

            handle_promotion_click(pos)

        else:

            handle_panel_click(pos)

        return

    if (
        game_over
        or paused
        or ai_thinking
        or promotion_pending
    ):

        return

    square = board_square_from_mouse(
        pos
    )

    if square is None:

        return

    r, c = square

    piece = board[r][c]

    if (
        piece != "."
        and piece_color(piece) == turn
    ):

        selected_square = square

        legal_moves_for_selected = legal_moves(
            board,
            r,
            c,
            turn
        )

        dragging_piece = piece
        drag_mouse_pos = pos


def handle_mouse_motion(pos):

    global drag_mouse_pos

    if dragging_piece is not None:

        drag_mouse_pos = pos


def handle_mouse_up(pos):

    global dragging_piece
    global drag_mouse_pos

    if dragging_piece is None:

        return

    square = board_square_from_mouse(
        pos
    )

    if square is not None:

        if square in legal_moves_for_selected:

            r, c = square

            start = selected_square

            piece = board[
                start[0]
            ][start[1]]

            if (
                piece.upper() == "P"
                and (
                    r == 0
                    or r == 7
                )
            ):

                begin_promotion(
                    start,
                    square
                )

            else:

                make_move(
                    start,
                    square
                )

                clear_selection()

    dragging_piece = None
    drag_mouse_pos = None


def clear_selection():

    global selected_square
    global legal_moves_for_selected

    selected_square = None
    legal_moves_for_selected = []


# ============================================================
# AI TURN
# ============================================================

def process_ai():

    global ai_thinking

    if not AI_ENABLED:

        return

    if game_over:

        return

    if paused:

        return

    if turn != AI_COLOR:

        return

    if ai_thinking:

        return

    ai_thinking = True

    move = get_ai_move()

    ai_thinking = False

    if move is None:

        update_game_status()

        return

    start, end = move

    piece = board[
        start[0]
    ][start[1]]

    promotion = None

    if (
        piece == "p"
        and end[0] == 7
    ):

        promotion = "q"

    make_move(
        start,
        end,
        promotion
    )


# ============================================================
# KEYBOARD
# ============================================================

def handle_key(key):

    global ai_depth

    if key == pygame.K_ESCAPE:

        pygame.quit()
        sys.exit()

    elif key == pygame.K_u:

        undo()

    elif key == pygame.K_y:

        redo()

    elif key == pygame.K_r:

        restart()

    elif key == pygame.K_s:

        save_game()

    elif key == pygame.K_l:

        load_game()

    elif key == pygame.K_p:

        toggle_pause()

    elif key == pygame.K_F1:

        ai_depth = 1

    elif key == pygame.K_F2:

        ai_depth = 2

    elif key == pygame.K_F3:

        ai_depth = 3


# ============================================================
# MAIN LOOP
# ============================================================

clock = pygame.time.Clock()

running = True

while running:

    for event in pygame.event.get():

        # ----------------------------------------------------
        # QUIT
        # ----------------------------------------------------

        if event.type == pygame.QUIT:

            running = False

        # ----------------------------------------------------
        # MOUSE DOWN
        # ----------------------------------------------------

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                handle_mouse_down(
                    event.pos
                )

        # ----------------------------------------------------
        # MOUSE MOTION
        # ----------------------------------------------------

        elif event.type == pygame.MOUSEMOTION:

            handle_mouse_motion(
                event.pos
            )

        # ----------------------------------------------------
        # MOUSE UP
        # ----------------------------------------------------

        elif event.type == pygame.MOUSEBUTTONUP:

            if event.button == 1:

                handle_mouse_up(
                    event.pos
                )

        # ----------------------------------------------------
        # KEYBOARD
        # ----------------------------------------------------

        elif event.type == pygame.KEYDOWN:

            handle_key(
                event.key
            )

    # --------------------------------------------------------
    # CLOCK
    # --------------------------------------------------------

    update_clock()

    # --------------------------------------------------------
    # AI
    # --------------------------------------------------------

    process_ai()

    # --------------------------------------------------------
    # DRAW
    # --------------------------------------------------------

    draw()

    clock.tick(FPS)


# ============================================================
# EXIT
# ============================================================

pygame.quit()
sys.exit()