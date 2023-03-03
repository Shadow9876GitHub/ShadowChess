from chessBoard import *

#This function generates all pseudo-legal moves, it doesn't check for checks or attacked squares
#generate: It needs a turn, the last move and pieces that moved during the game as input
def generate(chess,turn,lastMove,castling,include_pawns_at_promotion=False):
    all_moves=[]
    sign=1 if turn else -1
    num:cython.int;char:cython.int;sign:cython.int
    for num in range(8):
        for char in range(8):
            if (chess.board[char,num])==0:
                continue
            if (turn and np.sign(chess.board[char,num])==1) or (not turn and np.sign(chess.board[char,num])==-1):
                match abs(chess.board[char,num]):
                    case 10: all_moves+=pawn(chess,char,num,sign,lastMove,include_pawns_at_promotion)
                    case 30: all_moves+=knight(chess,char,num,sign)
                    case 35: all_moves+=bishop(chess,char,num,sign)
                    case 50: all_moves+=rook(chess,char,num,sign)
                    case 90: all_moves+=queen(chess,char,num,sign)
                    case 15: all_moves+=king(chess,char,num,sign,castling)
    for move in all_moves:
        if len(move)==4:
            move+=[chess.board[move[0],move[1]],chess.board[move[2],move[3]]]
        elif len(move)==5: move.append(chess.board[move[2],move[3]])
    return all_moves

def pawn(chess,char,num,sign,lastMove,include_pawns_at_promotion):
    baseRank:cython.int
    baseRank=1 if sign==-1 else 6
    moves=[]
	#Move direction
    mdir:cython.int
    mdir=-sign
    i:cython.int
    prom_list=(30,35,50,90,15) if not include_pawns_at_promotion else (10,30,35,50,90,15)
    if num+mdir in (0,1,2,3,4,5,6,7) and chess.board[char,num+mdir]==0:
        #Default move (and promotion)
        if num!=baseRank+5*mdir:
            moves.append([char,num,char,num+mdir])
        else:
            for i in prom_list:
                moves.append([char,num,char,num+mdir,sign*i])
        #Move two squares
        if num==baseRank and num+2*mdir in (0,1,2,3,4,5,6,7) and chess.board[char,num+2*mdir]==0:
            moves.append([char,num,char,num+2*mdir])
    for i in (-1,1):
        #Capture (and promotion)
        if char+i in (0,1,2,3,4,5,6,7) and num+mdir in (0,1,2,3,4,5,6,7) and np.sign(chess.board[char+i,num+mdir])==-sign:
            if num!=baseRank+5*mdir:
                moves.append([char,num,char+i,num+mdir])
            else:
                for j in prom_list:
                    moves.append([char,num,char+i,num+mdir,sign*j])
        #En passant
        elif char+i in (0,1,2,3,4,5,6,7) and num==baseRank+mdir*3 and lastMove[4]==mdir*10 and abs(lastMove[1]-lastMove[3])==2 and char+i==lastMove[0]:
            moves.append([char,num,char+i,num+mdir])
    return moves

def knight(chess,char,num,sign):
    i:cython.int;j:cython.int
    moves=[]
    for i in (1,-1):
        for j in (2,-2):
            if char+i in (0,1,2,3,4,5,6,7) and num+j in (0,1,2,3,4,5,6,7) and sign!=np.sign(chess.board[char+i,num+j]):
                moves.append([char,num,char+i,num+j])
            if char+j in (0,1,2,3,4,5,6,7) and num+i in (0,1,2,3,4,5,6,7) and sign!=np.sign(chess.board[char+j,num+i]):
                moves.append([char,num,char+j,num+i])
    return moves

def bishop(chess,char,num,sign):
    moves=[]
    i:cython.int;j:cython.int;length:cython.int
    for i in (-1,1):
        for j in (-1,1):
            for length in (1,2,3,4,5,6,7):
                if length*i+char in (0,1,2,3,4,5,6,7) and length*j+num in (0,1,2,3,4,5,6,7) and (chessSign:=np.sign(chess.board[length*i+char,length*j+num]))!=sign:
                    moves.append([char,num,length*i+char,length*j+num])
                    #Necessary to avoide moving through pieces
                    if chessSign==-sign:
                        break
                else:
                    break
    return moves

def rook(chess,char,num,sign):
    moves=[]
    i:cython.int;length:cython.int
    for i in (-1,1):
        for length in range(1,8):
            if char+length*i in (0,1,2,3,4,5,6,7) and (chessSign:=np.sign(chess.board[char+length*i,num]))!=sign:
                moves.append([char,num,char+length*i,num])
                if chessSign==-sign:
                    break
            else:
                break
        for length in range(1,8):
            if num+length*i in (0,1,2,3,4,5,6,7) and (chessSign:=np.sign(chess.board[char,num+length*i]))!=sign:
                moves.append([char,num,char,num+length*i])
                #Necessary to avoide moving through pieces
                if chessSign==-sign:
                    break
            else:
                break
    return moves

def queen(chess,char,num,sign):
    moves=[]
    moves+=bishop(chess,char,num,sign)
    moves+=rook(chess,char,num,sign)
    return moves

def king(chess,char,num,sign,castling):
	moves=[]
	i:cython.int;j:cython.int
	for i in (-1,0,1):
		for j in (-1,0,1):
			if i==j==0:
				continue
			#Default move
			if char+i in (0,1,2,3,4,5,6,7) and num+j in (0,1,2,3,4,5,6,7) and np.sign(chess.board[char+i,num+j])!=sign:
				moves.append([char,num,char+i,num+j])
	#movedPiece: 2,3: black rooks (a8 and h8); 5,7: white rooks (a1 and h1); 11,13: white and black king
	if castling%143!=0:
		#Castling (left side)
		if (sign+1 and castling%5!=0 and castling%11!=0) or (sign-1 and castling%2!=0 and castling%13!=0):
			if char-2 in (0,1,2,3,4,5,6,7):
				for i in range(1,char):
					if chess.board[char-i][num]!=0: break
				else: moves.append([char,num,char-2,num])
		#Castling (right side)
		if (sign+1 and castling%7!=0 and castling%11!=0) or (sign-1 and castling%3!=0 and castling%13!=0):
			if char+2 in (0,1,2,3,4,5,6,7):
				for i in range(1,7-char):
					if chess.board[char+i][num]!=0: break
				else: moves.append([char,num,char+2,num])
	return moves
