import numpy as np
import cython

#ChessBoard class + quality of life functions, variables
class ChessBoard:
    def __init__(self,board):
        #self.board=np.array(list(reversed(board)))
        #self.board=self.board.transpose()
        self.board=board
    def __str__(self):
        return str(np.array(list(reversed(self.board.transpose()))))

#Variables to help differenciate the two dimensions of the chessboard
a:cython.int;b:cython.int;c:cython.int;d:cython.int;e:cython.int;f:cython.int;g:cython.int;h:cython.int
a,b,c,d,e,f,g,h=list(range(0,8))

turns=[False,True,True,False]

#Default chessboard
default_board=np.array([[50,30,35,15,90,35,30,50],[10,10,10,10,10,10,10,10],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[-10,-10,-10,-10,-10,-10,-10,-10],[-50,-30,-35,-90,-15,-35,-30,-50]][::-1]).transpose()