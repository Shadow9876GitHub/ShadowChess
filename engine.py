import cProfile
from movegen import *

with open("data/eval.txt","r") as file:
    weights=file.read().splitlines()
    weights=[i.split() for i in weights]
weights=np.array(weights,np.int32)
evaluated_positions={}

def change_turns(new_turns):
    global turns
    turns=new_turns

def hash_position(position,depth):
	last=position.move[:4]+[position.move[4]+90,position.move[5]+90] if abs(position.move[4])==10 and abs(position.move[3]-position.move[1])==2 else [0,0,0,0,0,0]
	moved=143 if position.castling%143==0 else position.castling
	arr=[position.wLeader,position.tIndex,depth,moved]
	arr+=[position.chess.board[x,y]+90 for x in range(8) for y in range(8)]
	arr+=last
	return tuple(arr)

def execute_move(chess,move):
    #En passant
    if abs(chess.board[move[0],move[1]])==10 and (abs(move[0]-move[2]),abs(move[1]-move[3]))==(1,1) and chess.board[move[2],move[3]]==0:
        chess.board[move[2],move[1]]=0
    #Promotion
    if (chess.board[move[0],move[1]]==10 and move[3]==0) or (chess.board[move[0],move[1]]==-10 and move[3]==7):
        chess.board[move[0],move[1]]=move[4]
    #Castling
    if abs(chess.board[move[0],move[1]])==15 and abs(move[0]-move[2])==2:
        ch1=a if move[0]-move[2]>0 else h
        ch2=move[2]+np.sign(move[0]-move[2])
        chess.board[ch2,move[1]]=chess.board[ch1,move[1]]
        chess.board[ch1,move[1]]=0
    #Normal moves
    chess.board[move[2],move[3]]=chess.board[move[0],move[1]]
    chess.board[move[0],move[1]]=0
    #END
    return chess

#The next move
def next_move(position,move,char=False):
	#If position is a win for either side
	if -15 not in position.chess.board: return 1
	elif position.wLeader not in position.chess.board: return -1
	newChess=ChessBoard(np.copy(position.chess.board))
	execute_move(newChess,move)
	if position.castling%143!=0 and abs(current:=position.chess.board[move[0],move[1]]) in (15,50):
		if current==15 and position.castling%11!=0:
			position.castling*=11
		elif current==-15 and position.castling%13!=0:
			position.castling*=13
		elif current==50 and move[0]==a and position.castling%5!=0:
			position.castling*=5
		elif current==50 and move[0]==h and position.castling%7!=0:
			position.castling*=7
		elif current==-50 and move[0]==a and position.castling%2!=0:
			position.castling*=2
		elif current==-50 and move[0]==h and position.castling%3!=0:
			position.castling*=3
	return Position(newChess,position.castling,move,(position.tIndex+1)%len(turns),position.wLeader)

class Position:
	def __init__(self,chess,castling,move,tIndex,wLeader):
		self.chess=chess
		self.castling=castling
		self.move=move
		self.tIndex=tIndex
		self.wLeader=wLeader

def evaluate(position):
	if -15 not in position.chess.board: return 99999
	elif position.wLeader not in position.chess.board: return -99999
	return np.sum(np.matmul(weights,position.chess.board))

def move_ordering(moves):
	return sorted(moves,key=lambda x:abs(x[5])-abs(x[4]),reverse=True)

def alphaBetaMax(position,alpha,beta,depthleft,main=True):
	if depthleft==0: return evaluate(position)
	func=alphaBetaMax if turns[(position.tIndex+1)%len(turns)] else alphaBetaMin
	moves=move_ordering(generate(position.chess,turns[position.tIndex],position.move,position.castling))
	if main and len(moves)!=0: bestMove=moves[0]
	for move in moves:
		child=next_move(position,move)
		if child==99999:
			if main: return move,child
			return child
		if type(child)!=int:
			HASH=hash_position(child,depthleft)
			if HASH in evaluated_positions:
				score=evaluated_positions[HASH]
			else:
				score=func(child,alpha,beta,depthleft-1,False)
				evaluated_positions[HASH]=score
		else: score=child*99999
		if score>=beta:
			if not main: return beta
		if score>alpha:
			if main: bestMove=move
			alpha=score
	if main: return bestMove,alpha
	return alpha

def alphaBetaMin(position,alpha,beta,depthleft,main=True):
	if depthleft==0: return evaluate(position)
	func=alphaBetaMax if turns[(position.tIndex+1)%len(turns)] else alphaBetaMin
	moves=move_ordering(generate(position.chess,turns[position.tIndex],position.move,position.castling))
	if main and len(moves)!=0: bestMove=moves[0]
	for move in moves:
		child=next_move(position,move)
		if child==-99999:
			if main: return move,child
			return child
		if type(child)!=int:
			HASH=hash_position(child,depthleft)
			if HASH in evaluated_positions:
				score=evaluated_positions[HASH]
			else:
				score=func(child,alpha,beta,depthleft-1,False)
				evaluated_positions[HASH]=score
		else: score=child*99999
		if score<=alpha:
			if not main: return alpha
		if score<beta:
			if main: bestMove=move
			beta = score
	if main: return bestMove,beta
	return beta

def clear_evaluated_positions():
	evaluated_positions.clear()

def main():
	wLeader=15
	chess=ChessBoard(default_board)
	tIndex=0
	lastMove=[-1]*6
	castling=1
	depth=4
	position=Position(chess,castling,lastMove,tIndex,wLeader)

	for _ in range(1):
		func=alphaBetaMax if turns[position.tIndex] else alphaBetaMin
		move,val=func(position,-100000,100000,depth)
		position=next_move(position,move)
		if type(position)==int:
			print(f"Winner: {position}")
			break
		print(position.chess)
		print(move,val,("black","white")[turns[(position.tIndex-1)%len(turns)]])
		#print(evaluated_positions)

if __name__=="__main__":
	cProfile.run("main()")