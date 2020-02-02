import sys

import chess
import chess.svg

from PyQt5.QtCore import pyqtSlot, Qt, QTimer
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QApplication, QWidget, QLabel

from deepchess import DeepChess


class MainWindow(QWidget):
    """
    Create a surface for the chessboard.
    """
    def __init__(self):
        """
        Initialize the chessboard.
        """
        super().__init__()

        self.setWindowTitle("DeepChess")
        self.setGeometry(300, 300, 800, 800)

        self.widgetSvg = QSvgWidget(parent=self)
        self.widgetSvg.setGeometry(10, 10, 600, 600)

        self.label = QLabel('---', parent=self)
        self.label.setGeometry(10, 600, 600, 100)

        self.boardSize = min(self.widgetSvg.width(),
                             self.widgetSvg.height())
        self.coordinates = True
        self.margin = 0.05 * self.boardSize if self.coordinates else 0
        self.squareSize = (self.boardSize - 2 * self.margin) / 8.0
        self.playerMove = True
        
        self.engine = DeepChess('b')
        #self.board = chess.Board()
        self.pieceToMove = [None, None]
        self.updateBoard()
        
    @pyqtSlot(QWidget)
    def mousePressEvent(self, event):
        """
        Handle left mouse clicks and enable moving chess pieces by
        clicking on a chess piece and then the target square.

        Moves must be made according to the rules of chess because
        illegal moves are suppressed.
        """
        if self.playerMove and event.x() <= self.boardSize and event.y() <= self.boardSize:
            if event.buttons() == Qt.LeftButton:
                if self.margin < event.x() < self.boardSize - self.margin and self.margin < event.y() < self.boardSize - self.margin:
                    file = int((event.x() - self.margin) / self.squareSize)
                    rank = 7 - int((event.y() - self.margin) / self.squareSize)
                    square = chess.square(file, rank)
                    piece = self.engine.board.piece_at(square)
                    coordinates = "{}{}".format(chr(file + 97), str(rank + 1))
                    if self.pieceToMove[0] is not None and self.pieceToMove[1]!=coordinates:
                        move = chess.Move.from_uci("{}{}".format(self.pieceToMove[1], coordinates))
                        if move in self.engine.board.legal_moves:
                            self.engine.board.push(move)
                            if self.engine.board.is_check():
                                self.label.setText("Check!")
                            self.playerMove = False
                            # start timer
                            self.label.setText('DeepChess evaluating move...')
                            QTimer.singleShot(200, self.deepchess_evaluate)
                        piece = None
                        coordinates = None
                    self.pieceToMove = [piece, coordinates]
                    self.updateBoard()
                else:
                    # Envoke the paint event.
                    #self.update()
                    self.updateBoard()
        else:
            QWidget.mousePressEvent(self, event)

    #@pyqtSlot(QWidget)
    #def paintEvent(self, event):
    def updateBoard(self):
        """
        Draw a chessboard with the starting position and then redraw
        it for every new move.
        """
        self.boardSvg = chess.svg.board(board=self.engine.board,
                                        size=self.boardSize).encode("UTF-8")
        self.widgetSvg.load(self.boardSvg)
        if self.playerMove:
            self.label.setText('player move: {}-{}'.format(self.pieceToMove[0], self.pieceToMove[1]))

    def deepchess_evaluate(self):
        self.engine.evaluate()
        self.playerMove = True        
        self.updateBoard()
        
if __name__ == "__main__":
    deepChessApp = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(deepChessApp.exec_())
