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

    def test_getMoveCount(self):
        self.assertEqual(self.chess_board.getMoveCount(), 0)
        self.chess_board.addTextMove('a4')
        self.assertEqual(self.chess_board.getMoveCount(), 1)
        self.chess_board.addTextMove('g5')
        self.assertEqual(self.chess_board.getMoveCount(), 2)

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

    def test_gotoMove(self):
        self.chess_board.addTextMove('e4')
        self.chess_board.addTextMove('c5')
        self.assertFalse(self.chess_board.gotoMove(-1))
        self.assertFalse(self.chess_board.gotoMove(3))
        self.chess_board.gotoMove(0)
        self.assertEqual(self.chess_board.getFEN(), 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.chess_board.gotoMove(1)
        self.assertEqual(self.chess_board.getFEN(), 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1')
        self.chess_board.gotoMove(2)
        self.assertEqual(self.chess_board.getFEN(), 'rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2')

    def test_getLastMove(self):
        self.assertEqual(self.chess_board.getLastMove(), None)
        self.assertTrue(self.chess_board.addTextMove('e2e4'))
        self.assertEqual(self.chess_board.getLastMove(), ((4, 6), (4, 4)))
        self.assertTrue(self.chess_board.addTextMove('f7f5'))
        self.assertEqual(self.chess_board.getLastMove(), ((5, 1), (5, 3)))

    def test_getLastMoveType(self):
        self.assertEqual(self.chess_board.getLastMoveType(), None)

        self.assertTrue(self.chess_board.addTextMove('e2e4'))
        self.assertEqual(self.chess_board.getLastMoveType(), self.chess_board.EP_MOVE)

        self.assertTrue(self.chess_board.addTextMove('f7f5'))
        self.assertEqual(self.chess_board.getLastMoveType(), self.chess_board.EP_MOVE)

        self.assertTrue(self.chess_board.addTextMove('e4f5'))
        self.assertEqual(self.chess_board.getLastMoveType(), self.chess_board.NORMAL_MOVE)




if __name__ == '__main__':
    unittest.main()
