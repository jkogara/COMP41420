# /usr/bin/env python

# ####################################################################
# ChessBoard v2.05 is created by John Eriksson - http://arainyday.se
# It's released under the Gnu Public Licence (GPL)
# Have fun!
#####################################################################

from copy import deepcopy
from pprint import pprint


class MoveType:
    def __init__(self, move_int):
        self.moveInt = move_int


class EPCaptureMove(MoveType):
    def __init__(self):
        MoveType.__init__(self, 2)


class EPMove(MoveType):
    def __init__(self):
        MoveType.__init__(self, 1)


class NormalMove(MoveType):
    def __init__(self):
        MoveType.__init__(self, 0)


class KingCastleMove(MoveType):
    def __init__(self):
        MoveType.__init__(self, 4)
        self.moveString = "0-0"


class PromotionMove(MoveType):
    def __init__(self):
        MoveType.__init__(self, 3)


class QueenCastleMove(MoveType):
    def __init__(self):
        MoveType.__init__(self, 5)
        self.moveString = "0-0-0"


class ChessMove:
    EP_CAPTURE_MOVE = 2
    EP_MOVE = 1
    KING_CASTLE_MOVE = 4
    NORMAL_MOVE = 0
    PROMOTION_MOVE = 3
    QUEEN_CASTLE_MOVE = 5

    def __init__(self):
        # Piece,  "K" "Q" "R" "N" "B" "P"
        self.piece = None
        # from tuple (fx,fy)
        self.from_pos = None
        # to tuple (tx,ty)
        self.to_pos = None
        # Take True/False
        self.take = False
        # Promotion to, only for pawns "Q" "R" "N" "B" "P"
        self.promotion = None
        # check "+" "#"
        self.check = None
        # Special move type
        self.special_move_type = NormalMove().moveInt


class ChessBoard:
    # Color values
    WHITE = 0
    BLACK = 1
    NOCOLOR = -1

    # Promotion values
    BISHOP = 4
    KNIGHT = 3
    QUEEN = 1
    ROOK = 2

    # Reason values
    AMBIGUOUS_MOVE = 7
    GAME_IS_OVER = 6
    INVALID_COLOR = 2
    INVALID_FROM_LOCATION = 3
    INVALID_MOVE = 1
    INVALID_TO_LOCATION = 4
    MUST_SET_PROMOTION = 5

    # Result values
    NO_RESULT = 0
    WHITE_WIN = 1
    BLACK_WIN = 2
    STALEMATE = 3
    FIFTY_MOVES_RULE = 4
    THREE_REPETITION_RULE = 5

    # Text move output type
    AN = 0  # g4-e3
    SAN = 1  # Bxe3
    LAN = 2  # Bg4xe3

    _game_result = 0
    _reason = 0

    # States
    _turn = WHITE
    _white_king_castle = True
    _white_queen_castle = True
    _black_king_castle = True
    _black_queen_castle = True
    _board = None
    _ep = [0, 0]  # none or the location of the current en pessant pawn
    _fifty = 0

    _black_king_location = (0, 0)
    _white_king_location = (0, 0)

    # three rep stack
    _three_rep_stack = []

    # full state stack
    _state_stack = []
    _state_stack_pointer = 0

    # all moves, stored to make it easier to build textmoves
    #[piece,from,to,takes,promotion,check/checkmate,specialmove]
    #["KQRNBP",(fx,fy),(tx,ty),True/False,"QRNB"/None,"+#"/None,0-5]
    _cur_move = ChessMove()
    _moves = []

    # test comment
    _promotion_value = 0

    def __init__(self):
        self.resetBoard()

    def state2str(self):

        b = ""
        for l in self._board:
            b += "%s%s%s%s%s%s%s%s" % (l[0], l[1], l[2], l[3], l[4], l[5], l[6], l[7])

        d = (b,
             self._turn,
             self._white_king_castle,
             self._white_queen_castle,
             self._black_king_castle,
             self._black_queen_castle,
             self._ep[0],
             self._ep[1],
             self._game_result,
             self._fifty)

        #turn,wkc,wqc,bkc,bqc,epx,epy,game_result,fifty
        s = "%s%d%d%d%d%d%d%d%d:%d" % d

        return s

    def _load_cur_state(self):
        s = self._state_stack[self._state_stack_pointer - 1]
        b = s[:64]
        v = s[64:72]
        f = int(s[73:])

        idx = 0
        for r in range(8):
            for c in range(8):
                self._board[r][c] = b[idx]
                idx += 1

        self._turn = int(v[0])
        self._white_king_castle = int(v[1])
        self._white_queen_castle = int(v[2])
        self._black_king_castle = int(v[3])
        self._black_queen_castle = int(v[4])
        self._ep[0] = int(v[5])
        self._ep[1] = int(v[6])
        self._game_result = int(v[7])

        self._fifty = f

    def _push_state(self):

        if self._state_stack_pointer != len(self._state_stack):
            self._state_stack = self._state_stack[:self._state_stack_pointer]
            self._three_rep_stack = self._three_rep_stack[:self._state_stack_pointer]
            self._moves = self._moves[:self._state_stack_pointer - 1]

        three_state = [self._white_king_castle,
                       self._white_queen_castle,
                       self._black_king_castle,
                       self._black_queen_castle,
                       deepcopy(self._board),
                       deepcopy(self._ep)]
        self._three_rep_stack.append(three_state)

        state_str = self.state2str()
        self._state_stack.append(state_str)

        self._state_stack_pointer = len(self._state_stack)

    def _push_move(self):
        self._moves.append(deepcopy(self._cur_move))

    def _three_repetitions(self):

        ts = self._three_rep_stack[:self._state_stack_pointer]

        if not len(ts):
            return False

        last = ts[len(ts) - 1]
        if (ts.count(last) == 3):
            return True
        return False


    def _update_king_locations(self):
        # sets the king locations
        for y in range(0, 8):
            for x in range(0, 8):
                if self._board[y][x] == "K":
                    self._white_king_location = (x, y)
                if self._board[y][x] == "k":
                    self._black_king_location = (x, y)

    def _set_ep(self, epPos):
        self._ep[0], self._ep[1] = epPos

    def _clear_ep(self):
        self._ep[0] = 0
        self._ep[1] = 0

    def _end_game(self, reason):
        self._game_result = reason

    def _check_king_guard(self, fromPos, moves, specialMoves={}):
        result = []

        if self._turn == self.WHITE:
            kx, ky = self._white_king_location
        else:
            kx, ky = self._black_king_location

        fx, fy = fromPos

        done = False
        fp = self._board[fy][fx]
        self._board[fy][fx] = "."
        if not self._is_threatened(kx, ky):
            done = True
        self._board[fy][fx] = fp

        if done:
            return moves

        for m in moves:
            tx, ty = m
            sp = None
            fp = self._board[fy][fx]
            tp = self._board[ty][tx]

            self._board[fy][fx] = "."
            self._board[ty][tx] = fp

            if specialMoves.has_key(m) and specialMoves[m] == ChessMove.EP_CAPTURE_MOVE:
                sp = self._board[self._ep[1]][self._ep[0]]
                self._board[self._ep[1]][self._ep[0]] = "."

            if not self._is_threatened(kx, ky):
                result.append(m)

            if sp:
                self._board[self._ep[1]][self._ep[0]] = sp

            self._board[fy][fx] = fp
            self._board[ty][tx] = tp

        return result

    def _is_free(self, x, y):
        return self._board[y][x] == '.'

    def _get_color(self, x, y):
        if self._board[y][x] == '.':
            return self.NOCOLOR
        elif self._board[y][x].isupper():
            return self.WHITE
        elif self._board[y][x].islower():
            return self.BLACK


    def _is_threatened(self, lx, ly, player=None):
    #returns if there is check
        if player == None:
            player = self._turn

        if player == self.WHITE:
            if lx < 7 and ly > 0 and self._board[ly - 1][lx + 1] == 'p':
                return True
            elif lx > 0 and ly > 0 and self._board[ly - 1][lx - 1] == 'p':
                return True
        else:
            if lx < 7 and ly < 7 and self._board[ly + 1][lx + 1] == 'P':
                return True
            elif lx > 0 and ly < 7 and self._board[ly + 1][lx - 1] == 'P':
                return True

        m = [(lx + 1, ly + 2), (lx + 2, ly + 1), (lx + 2, ly - 1), (lx + 1, ly - 2), (lx - 1, ly + 2), (lx - 2, ly + 1),
             (lx - 1, ly - 2), (lx - 2, ly - 1)]
        for p in m:
            if p[0] >= 0 and p[0] <= 7 and p[1] >= 0 and p[1] <= 7:
                if self._board[p[1]][p[0]] == "n" and player == self.WHITE:
                    return True
                elif self._board[p[1]][p[0]] == "N" and player == self.BLACK:
                    return True

        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
        for d in dirs:
            x = lx
            y = ly
            dx, dy = d
            steps = 0
            while True:
                steps += 1
                x += dx
                y += dy
                if x < 0 or x > 7 or y < 0 or y > 7:
                    break
                if self._is_free(x, y):
                    continue
                elif self._get_color(x, y) == player:
                    break
                else:
                    p = self._board[y][x].upper()
                    if p == 'K' and steps == 1:
                        return True
                    elif p == 'Q':
                        return True
                    elif p == 'R' and abs(dx) != abs(dy):
                        return True
                    elif p == 'B' and abs(dx) == abs(dy):
                        return True
                    break
        return False

    def _has_any_valid_moves(self, player=None):
        if player == None:
            player = self._turn

        for y in range(0, 8):
            for x in range(0, 8):
                if self._get_color(x, y) == player:
                    if len(self.getValidMoves((x, y))):
                        return True
        return False

    #-----------------------------------------------------------------

    def traceValidMoves(self, fromPos, dirs, maxSteps=8):
        moves = []
        for d in dirs:
            x, y = fromPos
            dx, dy = d
            steps = 0
            while True:
                x += dx
                y += dy
                if x < 0 or x > 7 or y < 0 or y > 7:
                    break
                if self._is_free(x, y):
                    moves.append((x, y))
                elif self._get_color(x, y) != self._turn:
                    moves.append((x, y))
                    break
                else:
                    break
                steps += 1
                if steps == maxSteps:
                    break
        return moves

    def getValidQueenMoves(self, fromPos):
        moves = []
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]

        moves = self.traceValidMoves(fromPos, dirs)

        moves = self._check_king_guard(fromPos, moves)

        return moves

    def getValidRookMoves(self, fromPos):
        moves = []
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        moves = self.traceValidMoves(fromPos, dirs)

        moves = self._check_king_guard(fromPos, moves)

        return moves

    def getValidBishopMoves(self, fromPos):
        moves = []
        dirs = [(1, 1), (-1, 1), (1, -1), (-1, -1)]

        moves = self.traceValidMoves(fromPos, dirs)

        moves = self._check_king_guard(fromPos, moves)

        return moves

    def getValidPawnMoves(self, fromPos):
        moves = []
        specialMoves = {}
        fx, fy = fromPos

        if self._turn == self.WHITE:
            movedir = -1
            startrow = 6
            ocol = self.BLACK
            eprow = 3
        else:
            movedir = 1
            startrow = 1
            ocol = self.WHITE
            eprow = 4

        if self._is_free(fx, fy + movedir):
            moves.append((fx, fy + movedir))

        if fy == startrow:
            if self._is_free(fx, fy + movedir) and self._is_free(fx, fy + (movedir * 2)):
                moves.append((fx, fy + (movedir * 2)))
                specialMoves[(fx, fy + (movedir * 2))] = ChessMove.EP_MOVE
        if fx < 7 and self._get_color(fx + 1, fy + movedir) == ocol:
            moves.append((fx + 1, fy + movedir))
        if fx > 0 and self._get_color(fx - 1, fy + movedir) == ocol:
            moves.append((fx - 1, fy + movedir))

        if fy == eprow and self._ep[1] != 0:
            if self._ep[0] == fx + 1:
                moves.append((fx + 1, fy + movedir))
                specialMoves[(fx + 1, fy + movedir)] = ChessMove.EP_CAPTURE_MOVE
            if self._ep[0] == fx - 1:
                moves.append((fx - 1, fy + movedir))
                specialMoves[(fx - 1, fy + movedir)] = ChessMove.EP_CAPTURE_MOVE

        moves = self._check_king_guard(fromPos, moves, specialMoves)

        return (moves, specialMoves)

    def getValidKnightMoves(self, fromPos):
        moves = []
        fx, fy = fromPos
        m = [(fx + 1, fy + 2), (fx + 2, fy + 1), (fx + 2, fy - 1), (fx + 1, fy - 2), (fx - 1, fy + 2), (fx - 2, fy + 1),
             (fx - 1, fy - 2), (fx - 2, fy - 1)]
        for p in m:
            if p[0] >= 0 and p[0] <= 7 and p[1] >= 0 and p[1] <= 7:
                if self._get_color(p[0], p[1]) != self._turn:
                    moves.append(p)

        moves = self._check_king_guard(fromPos, moves)

        return moves

    def getValidKingMoves(self, fromPos):
        moves = []
        specialMoves = {}

        if self._turn == self.WHITE:
            c_row = 7
            c_king = self._white_king_castle
            c_queen = self._white_queen_castle
            k = "K"
        else:
            c_row = 0
            c_king = self._black_king_castle
            c_queen = self._black_queen_castle
            k = "k"

        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]

        t_moves = self.traceValidMoves(fromPos, dirs, 1)
        moves = []

        self._board[fromPos[1]][fromPos[0]] = '.'

        for m in t_moves:
            if not self._is_threatened(m[0], m[1]):
                moves.append(m)

        if c_king:
            if self._is_free(5, c_row) and self._is_free(6, c_row) and self._board[c_row][7].upper() == 'R':
                if not self._is_threatened(4, c_row) and not self._is_threatened(5, c_row) and not self._is_threatened(6,
                                                                                                                 c_row):
                    moves.append((6, c_row))
                    specialMoves[(6, c_row)] = ChessMove.KING_CASTLE_MOVE
        if c_queen:
            if self._is_free(3, c_row) and self._is_free(2, c_row) and self._is_free(1, c_row) and self._board[c_row][
                0].upper() == 'R':
                if not self._is_threatened(4, c_row) and not self._is_threatened(3, c_row) and not self._is_threatened(2,
                                                                                                                 c_row):
                    moves.append((2, c_row))
                    specialMoves[(2, c_row)] = ChessMove.QUEEN_CASTLE_MOVE

        self._board[fromPos[1]][fromPos[0]] = k

        return (moves, specialMoves)

    # -----------------------------------------------------------------------------------

    def movePawn(self, fromPos, toPos):
        moves, specialMoves = self.getValidPawnMoves(fromPos)

        if not toPos in moves:
            return False

        if specialMoves.has_key(toPos):
            t = specialMoves[toPos]
        else:
            t = 0

        if t == ChessMove.EP_CAPTURE_MOVE:
            self._board[self._ep[1]][self._ep[0]] = '.'
            self._cur_move.take = True
            #   self._cur_move.special_move_type = ChessMove.EP_CAPTURE_MOVE
            self._cur_move.special_move_type = EPCaptureMove().moveInt

        pv = self._promotion_value
        if self._turn == self.WHITE and toPos[1] == 0:
            if pv == 0:
                self._reason = self.MUST_SET_PROMOTION
                return False
            pc = ['Q', 'R', 'N', 'B']
            p = pc[pv - 1]
            self._cur_move.promotion = p
            # self._cur_move.special_move_type = ChessMove.PROMOTION_MOVE
            self._cur_move.special_move_type = PromotionMove().moveInt
        elif self._turn == self.BLACK and toPos[1] == 7:
            if pv == 0:
                self._reason = self.MUST_SET_PROMOTION
                return False
            pc = ['q', 'r', 'n', 'b']
            p = pc[pv - 1]
            self._cur_move.promotion = p
            # self._cur_move.special_move_type = ChessMove.PROMOTION_MOVE
            self._cur_move.special_move_type = PromotionMove().moveInt
        else:
            p = self._board[fromPos[1]][fromPos[0]]

        if t == ChessMove.EP_MOVE:
            self._set_ep(toPos)
            # self._cur_move.special_move_type = ChessMove.EP_MOVE
            self._cur_move.special_move_type = EPMove().moveInt
        else:
            self._clear_ep()

        if self._board[toPos[1]][toPos[0]] != '.':
            self._cur_move.take = True

        self._board[toPos[1]][toPos[0]] = p
        self._board[fromPos[1]][fromPos[0]] = "."

        self._fifty = 0
        return True

    def moveKnight(self, fromPos, toPos):
        moves = self.getValidKnightMoves(fromPos)

        if not toPos in moves:
            return False

        self._clear_ep()

        if self._board[toPos[1]][toPos[0]] == ".":
            self._fifty += 1
        else:
            self._fifty = 0
            self._cur_move.take = True

        self._board[toPos[1]][toPos[0]] = self._board[fromPos[1]][fromPos[0]]
        self._board[fromPos[1]][fromPos[0]] = "."
        return True

    def moveKing(self, fromPos, toPos):
        if self._turn == self.WHITE:
            c_row = 7
            k = "K"
            r = "R"
        else:
            c_row = 0
            k = "k"
            r = "r"

        moves, specialMoves = self.getValidKingMoves(fromPos)

        if specialMoves.has_key(toPos):
            t = specialMoves[toPos]
        else:
            t = 0

        if not toPos in moves:
            return False

        self._clear_ep()

        if self._turn == self.WHITE:
            self._white_king_castle = False
            self._white_queen_castle = False
        else:
            self._black_king_castle = False
            self._black_queen_castle = False

        if t == ChessMove.KING_CASTLE_MOVE:
            self._fifty += 1
            self._board[c_row][4] = "."
            self._board[c_row][6] = k
            self._board[c_row][7] = "."
            self._board[c_row][5] = r
            # self._cur_move.special_move_type = ChessMove.KING_CASTLE_MOVE
            self._cur_move.special_move_type = KingCastleMove.get_id()
        elif t == ChessMove.QUEEN_CASTLE_MOVE:
            self._fifty += 1
            self._board[c_row][4] = "."
            self._board[c_row][2] = k
            self._board[c_row][0] = "."
            self._board[c_row][3] = r
            #self._cur_move.special_move_type = ChessMove.QUEEN_CASTLE_MOVE
            self._cur_move.special_move_type = QueenCastleMove.get_id(
            )
        else:
            if self._board[toPos[1]][toPos[0]] == ".":
                self._fifty += 1
            else:
                self._fifty = 0
                self._cur_move.take = True

            self._board[toPos[1]][toPos[0]] = self._board[fromPos[1]][fromPos[0]]
            self._board[fromPos[1]][fromPos[0]] = "."

        self._update_king_locations()
        return True

    def moveQueen(self, fromPos, toPos):

        moves = self.getValidQueenMoves(fromPos)

        if not toPos in moves:
            return False

        self._clear_ep()

        if self._board[toPos[1]][toPos[0]] == ".":
            self._fifty += 1
        else:
            self._fifty = 0
            self._cur_move.take = True

        self._board[toPos[1]][toPos[0]] = self._board[fromPos[1]][fromPos[0]]
        self._board[fromPos[1]][fromPos[0]] = "."
        return True

    def moveBishop(self, fromPos, toPos):
        moves = self.getValidBishopMoves(fromPos)

        if not toPos in moves:
            return False

        self._clear_ep()

        if self._board[toPos[1]][toPos[0]] == ".":
            self._fifty += 1
        else:
            self._fifty = 0
            self._cur_move.take = True

        self._board[toPos[1]][toPos[0]] = self._board[fromPos[1]][fromPos[0]]
        self._board[fromPos[1]][fromPos[0]] = "."
        return True

    def moveRook(self, fromPos, toPos):

        moves = self.getValidRookMoves(fromPos)

        if not toPos in moves:
            return False

        fx, fy = fromPos
        if self._turn == self.WHITE:
            if fx == 0:
                self._white_queen_castle = False
            if fx == 7:
                self._white_king_castle = False
        if self._turn == self.BLACK:
            if fx == 0:
                self._black_queen_castle = False
            if fx == 7:
                self._black_king_castle = False

        self._clear_ep()

        if self._board[toPos[1]][toPos[0]] == ".":
            self._fifty += 1
        else:
            self._fifty = 0
            self._cur_move.take = True

        self._board[toPos[1]][toPos[0]] = self._board[fromPos[1]][fromPos[0]]
        self._board[fromPos[1]][fromPos[0]] = "."
        return True

    def _parseTextMove(self, txt):

        txt = txt.strip()
        promotion = None
        dest_x = 0
        dest_y = 0
        h_piece = "P"
        h_rank = -1
        h_file = -1

        # handle the special
        if txt == "O-O":
            if self._turn == 0:
                return (None, 4, 7, 6, 7, None)
            if self._turn == 1:
                return (None, 4, 0, 6, 0, None)
        if txt == "O-O-O":
            if self._turn == 0:
                return (None, 4, 7, 2, 7, None)
            if self._turn == 1:
                return (None, 4, 0, 2, 0, None)

        files = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
        ranks = {"8": 0, "7": 1, "6": 2, "5": 3, "4": 4, "3": 5, "2": 6, "1": 7}

        # Clean up the textmove
        "".join(txt.split("e.p."))
        t = []
        for ch in txt:
            if ch not in "KQRNBabcdefgh12345678":
                continue
            t.append(ch)

        if len(t) < 2:
            return None

        # Get promotion if any
        if t[-1] in ('Q', 'R', 'N', 'B'):
            promotion = {'Q': 1, 'R': 2, 'N': 3, 'B': 4}[t.pop()]

        if len(t) < 2:
            return None

        # Get the destination
        if not files.has_key(t[-2]) or not ranks.has_key(t[-1]):
            return None

        dest_x = files[t[-2]]
        dest_y = ranks[t[-1]]

        # Pick out the hints
        t = t[:-2]
        for h in t:
            if h in ('K', 'Q', 'R', 'N', 'B', 'P'):
                h_piece = h
            elif h in ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'):
                h_file = files[h]
            elif h in ('1', '2', '3', '4', '5', '6', '7', '8'):
                h_rank = ranks[h]

        # If we have both a source and destination we don't need the piece hint.
        # This will make us make the move directly.
        if h_rank > -1 and h_file > -1:
            h_piece = None

        return (h_piece, h_file, h_rank, dest_x, dest_y, promotion)

    def _formatTextMove(self, move, format):
        #piece, from, to, take, promotion, check

        piece = move.piece
        fpos = move.from_pos
        tpos = move.to_pos
        take = move.take
        promo = move.promotion
        check = move.check
        special = move.special_move_type

        files = "abcdefgh"
        ranks = "87654321"
        if format == self.AN:
            res = "%s%s%s%s" % (files[fpos[0]], ranks[fpos[1]], files[tpos[0]], ranks[tpos[1]])
        elif format == self.LAN:

            if special == ChessMove.KING_CASTLE_MOVE:
                return "O-O"
            elif special == ChessMove.QUEEN_CASTLE_MOVE:
                return "O-O-O"

            #if isinstance((special,KingCastleMove) or isinstance(special, QueenCastleMove)):
            #    return special.moveString


            tc = "-"
            if take:
                tc = "x"
            pt = ""
            if promo:
                pt = "=%s" % promo
            if piece == "P":
                piece = ""
            if not check:
                check = ""
            res = "%s%s%s%s%s%s%s%s" % (
                piece, files[fpos[0]], ranks[fpos[1]], tc, files[tpos[0]], ranks[tpos[1]], pt, check)
        elif format == self.SAN:

            if special == ChessMove.KING_CASTLE_MOVE:
                return "O-O"
            elif special == ChessMove.QUEEN_CASTLE_MOVE:
                return "O-O-O"

            tc = ""
            if take:
                tc = "x"
            pt = ""
            if promo:
                pt = "=%s" % promo.upper()
            p = piece
            if self._turn == self.BLACK:
                p = p.lower()
            if piece == "P":
                piece = ""
            if not check:
                check = ""
            fx, fy = fpos
            hint_f = ""
            hint_r = ""
            for y in range(8):
                for x in range(8):
                    if self._board[y][x] == p:
                        if x == fx and y == fy:
                            continue
                        vm = self.getValidMoves((x, y))
                        if tpos in vm:
                            if fx == x:
                                hint_r = ranks[fy]
                            else:
                                hint_f = files[fx]
            if piece == "" and take:
                hint_f = files[fx]
            res = "%s%s%s%s%s%s%s%s" % (piece, hint_f, hint_r, tc, files[tpos[0]], ranks[tpos[1]], pt, check)
        return res

    def _get_last_move(self):
        if self._state_stack_pointer <= 1:  # No move has been done at thos pointer
            return None
        return self._moves[self._state_stack_pointer - 2]

    #----------------------------------------------------------------------------
    # PUBLIC METHODS
    #----------------------------------------------------------------------------

    def resetBoard(self):
        """
        Resets the chess board and all states.
        """
        self._board = [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p'] * 8,
            ['.'] * 8,
            ['.'] * 8,
            ['.'] * 8,
            ['.'] * 8,
            ['P'] * 8,
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        ]
        self._turn = self.WHITE
        self._white_king_castle = True
        self._white_queen_castle = True
        self._black_king_castle = True
        self._black_queen_castle = True
        self._ep = [0, 0]
        self._fifty = 0
        self._three_rep_stack = []
        self._state_stack = []
        self._moves = []
        self._reason = 0
        self._game_result = 0
        self._push_state()
        self._update_king_locations()

    def setFEN(self, fen):
        """
        Sets the board and states according to a Forsyth-Edwards Notation string.
        Ex. 'rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2'
        """
        self._three_rep_stack = []
        self._state_stack = []
        self._moves = []
        self._reason = 0
        self._game_result = 0

        fparts = fen.split()
        newstate = ""

        #BOARD
        for c in fparts[0]:
            if c in "kqrnbpKQRNBP":
                newstate += c
            elif c in "12345678":
                newstate += '.' * int(c)
        #TURN
        newstate += str("wb".index(fparts[1]))

        #CASTLING
        kq = "KQkq"
        for p in kq:
            if p in fparts[2]:
                newstate += "1"
            else:
                newstate += "0"

        #EN PASSANT
        if len(fparts[3]) == 2:
            newstate += str("abcdefgh".index(fparts[3][0].lower()))
            newstate += str("87654321".index(fparts[3][1]))
        else:
            newstate += "00"

        #GAME RESULT
        newstate += "0"

        #HALF COUNT
        newstate += ":%s" % fparts[4]

        self._state_stack.append(newstate)
        self._state_stack_pointer = 1
        self._load_cur_state()

        three_state = [self._white_king_castle,
                       self._white_queen_castle,
                       self._black_king_castle,
                       self._black_queen_castle,
                       deepcopy(self._board),
                       deepcopy(self._ep)]

        self._three_rep_stack.append(three_state)

        self._update_king_locations()

    def getFEN(self):
        """
        Returns the current state as Forsyth-Edwards Notation string.
        """
        s = self._state_stack[self._state_stack_pointer - 1]

        b = s[:64]
        v = s[64:72]
        fifty = s[73:]

        rows = []
        for i in range(8):
            row = b[i * 8:(i + 1) * 8]
            cnt = 0;
            res = ""
            for c in row:
                if c == ".":
                    cnt += 1
                else:
                    if cnt:
                        res += str(cnt);
                        cnt = 0
                    res += c
            if cnt:
                res += str(cnt)
            rows.append(res)
        board = "/".join(rows)

        turn = (["w", "b"])[int(v[0])]

        kq = ""
        if int(v[1]): kq += "K"
        if int(v[2]): kq += "Q"
        if int(v[3]): kq += "k"
        if int(v[4]): kq += "q"
        if not kq:
            kq = "-"

        x = int(v[5])
        y = int(v[6])
        ep = "-"
        if not (x == 0 and y == 0):
            if turn == "b" and (self._board[y][x - 1] == 'p' or self._board[y][x + 1] == 'p'):
                ep = "%s%s" % ( ("abcdefgh")[x], ("87654321")[y + 1])
            elif turn == "w" and (self._board[y][x - 1] == 'P' or self._board[y][x + 1] == 'P'):
                ep = "%s%s" % ( ("abcdefgh")[x], ("87654321")[y - 1])

        move = (self._state_stack_pointer + 1) / 2

        return "%s %s %s %s %s %d" % (board, turn, kq, ep, fifty, move)

    def getMoveCount(self):
        """
        Returns the number of halfmoves in the stack.
        Zero (0) means no moves has been made.
        """
        return len(self._state_stack) - 1

    def getCurrentMove(self):
        """
        Returns the current halfmove number. Zero (0) means before first move.
        """
        return len(self._state_stack) - 1

    def gotoMove(self, move):
        """
        Goto the specified halfmove. Zero (0) is before the first move.
        Return False if move is out of range.
        """
        move += 1
        if move > len(self._state_stack):
            return False
        if move < 1:
            return False

        self._state_stack_pointer = move
        self._load_cur_state()

    def gotoFirst(self):
        """
        Goto before the first known move.
        """
        self._state_stack_pointer = 1
        self._load_cur_state()

    def gotoLast(self):
        """
        Goto after the last known move.
        """
        self._state_stack_pointer = len(self._state_stack)
        self._load_cur_state()

    def undo(self):
        """
        Undoes the last move. Can be used to step back until the initial board setup.
        Returns True or False if no more moves can be undone.
        """
        if self._state_stack_pointer <= 1:
            return False
        self._state_stack_pointer -= 1
        self._load_cur_state()
        return True

    def redo(self):
        """
        If you used the undo method to step backwards you can use this method to step forward until the last move is reached.
        Returns True or False if no more moves can be redone.
        """
        if self._state_stack_pointer == len(self._state_stack):
            return False
        self._state_stack_pointer += 1
        self._load_cur_state()
        return True

    def setPromotion(self, promotion):
        """
        Tells the chessboard how to promote a pawn.
        1=QUEEN, 2=ROOK, 3=KNIGHT, 4=BISHOP
        You can also set promotion to 0 (zero) to reset the promotion value.
        """
        self._promotion_value = promotion

    def getPromotion(self):
        """
        Returns the current promotion value.
        1=QUEEN, 2=ROOK, 3=KNIGHT, 4=BISHOP
        """
        return self._promotion_value

    def isCheck(self):
        """
        Returns True if the current players king is checked.
        """
        if self._turn == self.WHITE:
            kx, ky = self._white_king_location
        else:
            kx, ky = self._black_king_location

        return self._is_threatened(kx, ky, self._turn)

    def isGameOver(self):
        """
        Returns True if the game is over by either checkmate or draw.
        """
        if self._game_result:
            return True
        return False

    def getGameResult(self):
        """
        Returns the reason for game over.
        It can be the following reasons: 1=WHITE_WIN , 2=BLACK_WIN, 3=STALEMATE, 4=FIFTY_MOVES_RULE,5=THREE_REPETITION_RULE.
        If game is not over this method returns zero(0).
        """
        return self._game_result

    def getBoard(self):
        """
        Returns a copy of the current board layout. Uppercase letters for white, lovercase for black.
        K=King, Q=Queen, B=Bishop, N=Night, R=Rook, P=Pawn.
        Empty squares are markt with a period (.)
        """
        return deepcopy(self._board)

    def getTurn(self):
        """
        Returns the current player. 0=WHITE, 1=BLACK.
        """
        return self._turn

    def getReason(self):
        """
        Returns the reason to why addMove returned False.
        1=INAVLID_MOVE,2=INVALID_COLOR,3=INVALID_FROM_LOCATION,4=INVALID_TO_LOCATION,5=MUST_SET_PROMOTION,5=GAME_IS_OVER
        """
        return self._reason

    def getValidMoves(self, location):
        """
        Returns a list of valid moves. (ex [ [3,4], [3, 5], [3, 6] ... ] ) If there isn't a valid piece on that location or the piece on the selected
        location hasn't got any valid moves an empty list is returned.
        The location argument must be a tuple containing an x, y value Ex. (3, 3)
        """
        if self._game_result:
            return []

        x, y = location

        if x < 0 or x > 7 or y < 0 or y > 7:
            return False

        self._update_king_locations()

        if self._get_color(x, y) != self._turn:
            return []

        p = self._board[y][x].upper()
        if p == 'P':
            m, s = self.getValidPawnMoves(location)
            return m
        elif p == 'R':
            return self.getValidRookMoves(location)
        elif p == 'B':
            return self.getValidBishopMoves(location)
        elif p == 'Q':
            return self.getValidQueenMoves(location)
        elif p == 'K':
            m, s = self.getValidKingMoves(location)
            return m
        elif p == 'N':
            return self.getValidKnightMoves(location)
        else:
            return []

    def addMove(self, fromPos, toPos):
        """
        Tries to move the piece located om fromPos to toPos. Returns True if that was a valid move.
        The position arguments must be tuples containing x, y value Ex. (4, 6).
        This method also detects game over.

        If this method returns False you can use the getReason method to determin why.
        """
        self._reason = 0
        #                piece,from,to,take,promotion,check,specialmove
        self._cur_move = ChessMove()

        if self._game_result:
            self._result = self.GAME_IS_OVER
            return False

        self._update_king_locations()

        fx, fy = fromPos
        tx, ty = toPos

        self._cur_move.from_pos = fromPos
        self._cur_move.to_pos = toPos

        #check invalid coordinates
        if fx < 0 or fx > 7 or fy < 0 or fy > 7:
            self._reason = self.INVALID_FROM_LOCATION
            return False

        #check invalid coordinates
        if tx < 0 or tx > 7 or ty < 0 or ty > 7:
            self._reason = self.INVALID_TO_LOCATION
            return False

        #check if any move at all
        if fx == tx and fy == ty:
            self._reason = self.INVALID_TO_LOCATION
            return False

        #check if piece on location
        if self._is_free(fx, fy):
            self._reason = self.INVALID_FROM_LOCATION
            return False

        #check color of piece
        if self._get_color(fx, fy) != self._turn:
            self._reason = self.INVALID_COLOR
            return False

        # Call the correct handler
        p = self._board[fy][fx].upper()
        self._cur_move.piece = p
        if p == 'P':
            if not self.movePawn((fx, fy), (tx, ty)):
                if not self._reason:
                    self._reason = self.INVALID_MOVE
                return False
        elif p == 'R':
            if not self.moveRook((fx, fy), (tx, ty)):
                self._reason = self.INVALID_MOVE
                return False
        elif p == 'B':
            if not self.moveBishop((fx, fy), (tx, ty)):
                self._reason = self.INVALID_MOVE
                return False
        elif p == 'Q':
            if not self.moveQueen((fx, fy), (tx, ty)):
                self._reason = self.INVALID_MOVE
                return False
        elif p == 'K':
            if not self.moveKing((fx, fy), (tx, ty)):
                self._reason = self.INVALID_MOVE
                return False
        elif p == 'N':
            if not self.moveKnight((fx, fy), (tx, ty)):
                self._reason = self.INVALID_MOVE
                return False
        else:
            return False

        if self._turn == self.WHITE:
            self._turn = self.BLACK
        else:
            self._turn = self.WHITE

        if self.isCheck():
            self._cur_move.check = "+"

        if not self._has_any_valid_moves():
            if self.isCheck():
                self._cur_move.check = "#"
                if self._turn == self.WHITE:
                    self._end_game(self.BLACK_WIN)
                else:
                    self._end_game(self.WHITE_WIN)
            else:
                self._end_game(self.STALEMATE)
        else:
            if self._fifty == 100:
                self._end_game(self.FIFTY_MOVES_RULE)
            elif self._three_repetitions():
                self._end_game(self.THREE_REPETITION_RULE)

        self._push_state()
        self._push_move()

        return True

    def getLastMoveType(self):
        """
        Returns a value that indicates if the last move was a "special move".
        Returns -1 if no move has been done.
        Return value can be:
        0=NORMAL_MOVE
        1=EP_MOVE (Pawn is moved two steps and is valid for en passant strike)
        2=EP_CAPTURE_MOVE (A pawn has captured another pawn by using the en passant rule)
        3=PROMOTION_MOVE (A pawn has been promoted. Use getPromotion() to see the promotion piece.)
        4=KING_CASTLE_MOVE (Castling on the king side.)
        5=QUEEN_CASTLE_MOVE (Castling on the queen side.)
        """

        move = self._get_last_move()
        if move is None:
            return None

        return move.special_move_type

    def getLastMove(self):
        move = self._get_last_move()
        if move is None:
            return None

        return move.from_pos, move.to_pos

    def addTextMove(self, txt):
        """
        Adds a move using several different standards of the Algebraic chess notation.
        AN Examples: 'e2e4' 'f1d1' 'd7-d8' 'g1-f3'
        SAN Examples: 'e4' 'Rfxd1' 'd8=Q' 'Nxf3+'
        LAN Examples: 'Pe2e4' 'Rf1xd1' 'Pd7d8=Q' 'Ng1xf3+'
        """
        res = self._parseTextMove(txt)
        if not res:
            self._reason = self.INVALID_MOVE
            return False
        else:
            piece, fx, fy, tx, ty, promo = res

        if promo:
            self.setPromotion(promo)

        if not piece:
            return self.addMove((fx, fy), (tx, ty))

        if self._turn == self.BLACK:
            piece = piece.lower()

        move_to = None
        move_from = None
        found_move = False
        for y in range(8):
            for x in range(8):
                if self._board[y][x] == piece:
                    if fx > -1 and fx != x:
                        continue
                    if fy > -1 and fy != y:
                        continue
                    vm = self.getValidMoves((x, y))
                    for m in vm:
                        if m[0] == tx and m[1] == ty:
                            if found_move:
                                self._reason = self.AMBIGUOUS_MOVE
                                return False
                            found_move = True
                            move_from = (x, y)
                            move_to = (tx, ty)

        if found_move:
            return self.addMove(move_from, move_to)

        self._reason = self.INVALID_MOVE
        return False

    def getAllTextMoves(self, format=1):
        """
        Returns a list of all moves done so far in Algebraic chess notation.
        Returns None if no moves has been made.
        """
        if self._state_stack_pointer <= 1:  # No move has been done at this pointer
            return None

        res = []

        point = self._state_stack_pointer

        self.gotoFirst()
        while True:
            move = self._moves[self._state_stack_pointer - 1]
            res.append(self._formatTextMove(move, format))
            if self._state_stack_pointer >= len(self._state_stack) - 1:
                break
            self.redo()

        self._state_stack_pointer = point
        self._load_cur_state()

        return res

    def getLastTextMove(self, format=1):
        """
        Returns the latest move as Algebraic chess notation.
        Returns None if no moves has been made.
        """
        if self._state_stack_pointer <= 1:  # No move has been done at this pointer
            return None

        self.undo()
        move = self._moves[self._state_stack_pointer - 1]
        res = self._formatTextMove(move, format)
        self.redo()
        return res

    def printBoard(self):
        """
        Print the current board layout.
        """
        print "  +-----------------+"
        rank = 8
        for l in self._board:
            print "%d | %s %s %s %s %s %s %s %s |" % (rank, l[0], l[1], l[2], l[3], l[4], l[5], l[6], l[7])
            rank -= 1
        print "  +-----------------+"
        print "    A B C D E F G H"

    def printLastTextMove(self, format=1):
        """
        Prints the latest move as Algebraic chess notation.
        Print None if no moves has been made.
        """
        if self._state_stack_pointer <= 1:  # No move has been done at this pointer
            print 'Changed item'

        self.undo()
        move = self._moves[self._state_stack_pointer - 1]
        res = self._formatTextMove(move, format)
        self.redo()
        print res


if __name__ == "__main__":
    cb = ChessBoard()
    cb.printBoard()
    cb.addTextMove('e2e4')
    cb.printBoard()
    cb.addTextMove('f7f5')
    cb.printBoard()
    cb.addTextMove('e4f5')
    cb.printBoard()
    cb.addTextMove('g8h6')
    cb.printBoard()
    cb.addTextMove('f1d3')
    cb.printBoard()
    cb.addTextMove('h6f5')
    cb.printBoard()
    cb.addTextMove('d3f5')
    cb.printBoard()
