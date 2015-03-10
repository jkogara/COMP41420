import unittest
import sys

sys.path.append(".")
from ChessBoard import ChessBoard


class ChessBoardTest(unittest.TestCase):
    def setUp(self):
        self.chess_board = ChessBoard()

    def test_reset_board_is_valid(self):
        # act
        self.chess_board.resetBoard()
        # assert
        assert len(self.chess_board._moves) == 0
        assert self.chess_board._game_result == 0
        assert self.chess_board._reason == 0
        assert self.chess_board._ep == [0,0]
        assert self.chess_board._fifty == 0

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

    def test_gotoFirst(self):
        # act
        self.chess_board.gotoFirst()
        # assert
        assert self.chess_board._state_stack_pointer == 1

    def test_addTextMove_returns_false_when_move_is_invalid(self):
        # arrange
        invalid_txt = "wtf"
        # assert
        self.assertFalse(self.chess_board.addTextMove(invalid_txt))

        
    def test_addTextMove_returns_true_when_move_is_valid(self):
        # arrange
        valid_txt = "e2e4"
        # assert
        self.assertTrue(self.chess_board.addTextMove(valid_txt))

    def test_getLastMove(self):
        self.assertEqual(self.chess_board.getLastMove(), None)
        self.assertTrue(self.chess_board.addTextMove('e2e4'))
        self.assertEqual(self.chess_board.getLastMove(), ((4, 6), (4, 4)))
        self.assertTrue(self.chess_board.addTextMove('f7f5'))
        self.assertEqual(self.chess_board.getLastMove(), ((5, 1), (5, 3)))

    def test_getAllTextMoves(self):
        #
        self.assertFalse(self.chess_board.getAllTextMoves())



if __name__ == '__main__':
    unittest.main()
