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
        self.assertEqual(len(self.chess_board._moves),0)
        self.assertEqual(self.chess_board._game_result, 0)
        self.assertEqual( self.chess_board._reason, 0)
        self.assertEqual( self.chess_board._ep,[0,0])
        self.assertEqual( self.chess_board._fifty, 0)

    def test_getMoveCount(self):
        self.assertEqual(self.chess_board.getMoveCount(), 0)
        self.chess_board.addTextMove('a4')
        self.assertEqual(self.chess_board.getMoveCount(), 1)
        self.chess_board.addTextMove('g5')
        self.assertEqual(self.chess_board.getMoveCount(), 2)
    
    def test_getFEN(self):
        self.chess_board.setFEN('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEquals(self.chess_board.getFEN(), 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1' )

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

    def test_goToLast(self):
        self.assertEqual(self.chess_board._state_stack_pointer, len(self.chess_board._state_stack))

    def test_getLastMove(self):
        self.assertEqual(self.chess_board.getLastMove(), None)
        self.assertTrue(self.chess_board.addTextMove('e2e4'))
        self.assertEqual(self.chess_board.getLastMove(), ((4, 6), (4, 4)))
        self.assertTrue(self.chess_board.addTextMove('f7f5'))
        self.assertEqual(self.chess_board.getLastMove(), ((5, 1), (5, 3)))

    def test_undo(self):
        self.assertEqual(self.chess_board.undo(), False)
        self.assertTrue(self.chess_board.addTextMove('e2e4'))
        p1 = self.chess_board._state_stack_pointer
        self.assertEqual(self.chess_board.undo(), True)
        p0 = self.chess_board._state_stack_pointer
        self.assertEqual((p1 - 1), p0)

    def test_redo(self):
        self.assertEqual(self.chess_board.redo(), False)
        self.assertTrue(self.chess_board.addTextMove('e2e4'))
        self.assertTrue(self.chess_board.undo())
        p1 = self.chess_board._state_stack_pointer
        self.assertTrue(self.chess_board.redo())
        p0 = self.chess_board._state_stack_pointer
        self.assertEqual((p1 + 1), p0)

    def test_getLastMoveType(self):
        self.assertEqual(self.chess_board.getLastMoveType(), None)

        self.assertTrue(self.chess_board.addTextMove('e2e4'))
        self.assertEqual(self.chess_board.getLastMoveType(), self.chess_board.EP_MOVE)

        self.assertTrue(self.chess_board.addTextMove('f7f5'))
        self.assertEqual(self.chess_board.getLastMoveType(), self.chess_board.EP_MOVE)

        self.assertTrue(self.chess_board.addTextMove('e4f5'))
        self.assertEqual(self.chess_board.getLastMoveType(), self.chess_board.NORMAL_MOVE)

    def test_getAllTextMoves_returns_false_when_no_moves(self):
        self.assertFalse(self.chess_board.getAllTextMoves())

    def test_getAllTextMoves_returns_true_after_move(self):
        self.chess_board.addTextMove("e2e4")
        self.assertTrue(self.chess_board.getAllTextMoves())
    
    def test_setPromotion(self):
        self.chess_board.setPromotion(1)
        self.assertEqual(self.chess_board._promotion_value,1)
        self.chess_board.setPromotion(4)
        self.assertEqual(self.chess_board._promotion_value,4)

    def test_getPromotion(self):
        self.chess_board.setPromotion(1)
        self.assertEqual(self.chess_board.getPromotion(),1)
        self.chess_board.setPromotion(4)
        self.assertEqual(self.chess_board.getPromotion(),4)

    def test_isCheck(self):
        self.assertEqual(self.chess_board.isCheck(), False)
        self.chess_board.setFEN('rnb1kbnr/pppp1ppp/8/4p3/5PPq/8/PPPPP2P/RNBQKBNR w KQkq - 1 3')
        self.assertTrue(self.chess_board.isCheck())

    def test_isGameOver(self):
        self.chess_board.addTextMove('f4')
        self.chess_board.addTextMove('e5')
        self.chess_board.addTextMove('g4')
        self.assertFalse(self.chess_board.isGameOver())
        self.chess_board.addTextMove('Qh4')
        self.assertTrue(self.chess_board.isGameOver())

    def test_getGameResult_returns_false_when_game_is_not_over(self):
        self.assertEqual(self.chess_board.getGameResult(), False)

    def test_getGameResult_returns_true_when_game_is_over(self):
        # arrange
        self.chess_board._game_result = 1
        # assert
        self.assertTrue(self.chess_board.getGameResult())

    def test_getBoard_returns_object(self):
        # assert
        self.assertTrue(len(self.chess_board.getBoard()) > 0)

    def test_getTurn(self):
        self.chess_board._turn = self.chess_board.WHITE
        self.assertEqual(self.chess_board.getTurn(), self.chess_board.WHITE)

    def test_getLastTextMove_format_AN(self):
        format = self.chess_board.AN
        self.assertEqual(self.chess_board.getLastTextMove(format), None)

        self.assertTrue(self.chess_board.addTextMove('e2e4'))
        self.assertEqual(self.chess_board.getLastTextMove(format), 'e2e4')

        self.assertTrue(self.chess_board.addTextMove('f7f5'))
        self.assertEqual(self.chess_board.getLastTextMove(format), 'f7f5')

        self.assertTrue(self.chess_board.addTextMove('f1d3'))
        self.assertEqual(self.chess_board.getLastTextMove(format), 'f1d3')

    def test_getLastTextMove_format_LAN(self):
        format = self.chess_board.LAN
        self.assertEqual(self.chess_board.getLastTextMove(format), None)

        self.assertTrue(self.chess_board.addTextMove('e2e4'))
        self.assertEqual(self.chess_board.getLastTextMove(format), 'e2-e4')

        self.assertTrue(self.chess_board.addTextMove('f7f5'))
        self.assertEqual(self.chess_board.getLastTextMove(format), 'f7-f5')

        self.assertTrue(self.chess_board.addTextMove('f1d3'))
        self.assertEqual(self.chess_board.getLastTextMove(format), 'Bf1-d3')

    def test_getLastTextMove_format_SAN(self):
        self.assertEqual(self.chess_board.getLastTextMove(), None)

        self.assertTrue(self.chess_board.addTextMove('e2e4'))
        self.assertEqual(self.chess_board.getLastTextMove(), 'e4')

        self.assertTrue(self.chess_board.addTextMove('f7f5'))
        self.assertEqual(self.chess_board.getLastTextMove(), 'f5')

        self.assertTrue(self.chess_board.addTextMove('f1d3'))
        self.assertEqual(self.chess_board.getLastTextMove(), 'Bd3')

    def test_getReason(self):
        # testing 3 of the 7 possible reasons
        self.chess_board.addTextMove('i9')
        self.assertEqual(self.chess_board.getReason(), 1)
        self.chess_board.addMove('a7', 'a5')
        self.assertEqual(self.chess_board.getReason(), 3)
        self.chess_board.setFEN('7K/2P5/k7/7p/8/8/8/8 w - - 1 30')
        self.chess_board.addTextMove('c8')
        self.assertEqual(self.chess_board.getReason(), 5)

if __name__ == '__main__':
    unittest.main()
