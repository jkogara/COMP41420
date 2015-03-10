import unittest
import sys

sys.path.append(".")
from ChessBoard import ChessBoard


class ChessBoardTest(unittest.TestCase):
    def setUp(self):
        self.chess_board = ChessBoard()

    def test_getMoveCount(self):
        self.assertEqual(self.chess_board.getMoveCount(), 0)
        self.chess_board.addTextMove('a4')
        self.assertEqual(self.chess_board.getMoveCount(), 1)
        self.chess_board.addTextMove('g5')
        self.assertEqual(self.chess_board.getMoveCount(), 2)

    def test_setFEN(self):
        self.assertEqual(self.chess_board._board,
                         [['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'], ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
                          ['.', '.', '.', '.', '.', '.', '.', '.'], ['.', '.', '.', '.', '.', '.', '.', '.'],
                          ['.', '.', '.', '.', '.', '.', '.', '.'], ['.', '.', '.', '.', '.', '.', '.', '.'],
                          ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'], ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']])

        self.chess_board.setFEN('rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2')

        print self.chess_board._board

        self.assertEqual(self.chess_board._board,
                         [['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'], ['p', 'p', '.', 'p', 'p', 'p', 'p', 'p'],
                          ['.', '.', '.', '.', '.', '.', '.', '.'], ['.', '.', 'p', '.', '.', '.', '.', '.'],
                          ['.', '.', '.', '.', 'P', '.', '.', '.'], ['.', '.', '.', '.', '.', 'N', '.', '.'],
                          ['P', 'P', 'P', 'P', '.', 'P', 'P', 'P'], ['R', 'N', 'B', 'Q', 'K', 'B', '.', 'R']])


if __name__ == '__main__':
    unittest.main()
