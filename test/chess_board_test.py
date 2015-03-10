import unittest
import sys
sys.path.append(".")
from ChessBoard import ChessBoard

class ChessBoardTest(unittest.TestCase):

    def setUp(self):
        self.chess_board = ChessBoard()


if __name__ == '__main__':
    unittest.main()