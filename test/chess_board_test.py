import unittest
import sys

sys.path.append(".")
from ChessBoard import ChessBoard


class ChessBoardTest(unittest.TestCase):
    def setUp(self):
        self.chess_board = ChessBoard()


    def test_setFEN(self):
        self.assertEqual(self.chess_board._board,
                         [['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'], ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
                          ['.', '.', '.', '.', '.', '.', '.', '.'], ['.', '.', '.', '.', '.', '.', '.', '.'],
                          ['.', '.', '.', '.', '.', '.', '.', '.'], ['.', '.', '.', '.', '.', '.', '.', '.'],
                          ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'], ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']])

        self.chess_board.setFEN('rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2')

        self.assertEqual(self.chess_board._board,
                         [['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'], ['p', 'p', '.', 'p', 'p', 'p', 'p', 'p'],
                          ['.', '.', '.', '.', '.', '.', '.', '.'], ['.', '.', 'p', '.', '.', '.', '.', '.'],
                          ['.', '.', '.', '.', 'P', '.', '.', '.'], ['.', '.', '.', '.', '.', 'N', '.', '.'],
                          ['P', 'P', 'P', 'P', '.', 'P', 'P', 'P'], ['R', 'N', 'B', 'Q', 'K', 'B', '.', 'R']])

    def test_getCurrentMove(self):
        self.assertEqual(self.chess_board.getCurrentMove(), 0)

        self.assertTrue(self.chess_board.addTextMove('e2e4'))
        self.assertEqual(self.chess_board.getCurrentMove(), 1)

        self.assertTrue(self.chess_board.addTextMove('f7f5'))
        self.assertEqual(self.chess_board.getCurrentMove(), 2)

        self.assertTrue(self.chess_board.addTextMove('e4f5'))
        self.assertEqual(self.chess_board.getCurrentMove(), 3)

        self.assertTrue(self.chess_board.addTextMove('g8h6'))
        self.assertEqual(self.chess_board.getCurrentMove(), 4)



if __name__ == '__main__':
    unittest.main()
