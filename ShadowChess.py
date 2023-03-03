from engine import *
from Map import *
from tkinter import *
from tkinter import font
from tkinter import messagebox
import customtkinter
from PIL import Image,ImageTk,ImageDraw
import random
from os import walk
from sys import exit
from time import sleep,time
from pygame import mixer

#Window details
root = Tk()
isWindows=True
try:
	root.state('zoomed')
	root.iconbitmap("images/ShadowChess.ico")
except:
	root.attributes('-zoomed', True)
	isWindows=False
	photo=PhotoImage(file='images/ShadowChess.png')
	root.iconphoto(False, photo)
root.title("ShadowChess")
background_colour="gray97" #Stores original background colour
root['bg']=background_colour
root.config(cursor="circle")
customtkinter.set_appearance_mode("light")
customtkinter.set_default_color_theme("blue")

#Grid weights
for i in (0,6):	
	root.columnconfigure(i,weight=100)
for i in range(1,6):
	root.columnconfigure(i,weight=1)

for i in (0,11):
	root.rowconfigure(i,weight=100)
for i in range(1,11):
	root.rowconfigure(i,weight=1)

#Fullscreen toggle
def toggleFullScreen(event):
	root.attributes("-fullscreen",not root.attributes("-fullscreen"))

root.bind('<F11>',toggleFullScreen)

#Height, width of the tkinter window
height,width=root.winfo_screenwidth(),root.winfo_screenheight()  #I swapped the two accidentally
fullheight,fullwidth=root.winfo_screenwidth(),root.winfo_screenheight() #It's too late to go back now

#Tile size for the chessboard
tile_size=int(width*85/100)//8

#Canvas of the chessboard and promotion space
chessBoardCanvas=Canvas(root,width=tile_size*8,height=tile_size*8)
promotionCanvas=Canvas(root,width=tile_size*5,height=tile_size)

#Loading images (takes a lot of time)
images={}
def load_images():
	#Going through all subfolders in images and loading all images which are either .png or .jpg
	ch='\\' if isWindows else '/'
	for root, dirs, files in walk(f".{ch}images"):
		for file in files:
			if file[-4:] in (".jpg",'.png',"jpeg"):
				#Loading images in chess boards
				if "chess boards" in root:
					if "board" in file: images[file[:-4]]=ImageTk.PhotoImage(Image.open(f"{root}/{file}").resize((tile_size*8,tile_size*8),0))
					else: images[file[:-4]]=ImageTk.PhotoImage(Image.open(f"{root}/{file}").resize((tile_size*5,tile_size),0))
				#Loading images for chess pieces
				elif "chess pieces" in root:
					num=root.split(ch)[3] #essentially the name of the folder (6,7,8,9, ...) we're in
					if num!="chess":
						#If time effects is on load all images in chess pieces folder
						if settings["time_effects"]:
							images[f"{file[:-4]}_{num}"]=ImageTk.PhotoImage(Image.open(f"{root}/{file}").resize((tile_size*3,tile_size*3),1))
						#Otherwise only load fish images
						else:
							if num=="fish":
								images[f"{file[:-4]}_{num}"]=ImageTk.PhotoImage(Image.open(f"{root}/{file}").resize((tile_size*3,tile_size*3),1))

					else: images[f"{file[:-4]}"]=ImageTk.PhotoImage(Image.open(f"{root}/{file}").resize((tile_size,tile_size),1).convert("RGBA"))
				#Loading images for menu items
				elif "menu" in root:
					if "difficulty" in file:
						images[f"{file[:-5]}"]=ImageTk.PhotoImage(Image.open(f"{root}/{file}").resize((tile_size*3,int(tile_size*43/9)),1))
					elif "Title" in file:
						images[f"{file[:-4]}"]=ImageTk.PhotoImage(Image.open(f"{root}/{file}").resize((fullheight,fullwidth),1))
					else:
						images[f"{file[:-4]}"]=ImageTk.PhotoImage(Image.open(f"{root}/{file}").resize((tile_size,tile_size),1))
				elif "quien" in root:
					if "100" in file or "101" in file:
						images[f"{file[:-4]}"]=ImageTk.PhotoImage(Image.open(f"{root}/{file}").resize((fullheight,fullwidth),1))
					else:
						images[file[:-4]]=ImageTk.PhotoImage(Image.open(f"{root}/{file}").resize((fullwidth,fullwidth),1))
				#Loading images to graveyard
				else:
					if "credits" not in root and "tree" not in root and 'Interaction' not in file:
						images[file[:-4]]=ImageTk.PhotoImage(Image.open(f"{root}/{file}").resize((tile_size*3,tile_size*3),1))
					elif "Interaction" in file:
						images[file[:-4]]=ImageTk.PhotoImage(Image.open(f"{root}/{file}").resize((fullheight,fullwidth),1))
					elif "tree" in root:
						images[file[:-4]]=ImageTk.PhotoImage(Image.open(f"{root}/{file}").resize((int(fullwidth*4/3),fullwidth),1))
					else:
						size=(fullheight,int(fullheight*143/320)) if "Guernica" in file else ((int(fullwidth*399/292),fullwidth) if "Statistics" not in file else (fullheight,fullwidth))
						images[file[:-4]]=ImageTk.PhotoImage(Image.open(f"{root}/{file}").resize(size,1))

#  ----MUSIC----
#----------------------------------------------------

mixer.init()

music={}
stopsound=False
lastmusic=None

def load_music():
    for root, dirs, files in walk("./music"):
        for file in files:
            music[file[:-4]]=mixer.Sound(file=f"{root}/{file}")

def play_music(name):
    global lastmusic
    tracks_playing=0
    for i in music:
        tracks_playing+=mixer.Sound.get_num_channels(music[i])
    if not stopsound and tracks_playing==0:
        lastmusic=name
        music[name].play()
        return int(mixer.Sound.get_length(music[name]))
    return

def play_from_music_group(name,play_particular_song_first=None,main=True):
    global stopsound
    if main:
        stopsound=False
    musicGroups={"starting_battles":["Luchemos!","La Revuelta","¡Despiértense!","Estrellas en el Campo de Batalla"],"credits":["Credits"],
    "muslim":["Gran Oración","Sol","¡Despiértense!","Luchemos!","Gloria Espera"],"agua":["Debajo del Agua"],"garden":["En El Jardín"],
    "advanced_battles":["Gloria Espera","Alas Doradas","Luchemos!","¡Despiértense!"],
    "endgame_battles":["Gloria Espera","Alas Doradas","¡Bienvenidos a Cataluña!","¡Despiértense!","Gran Oración"],"menu":["Siesta"],
    "queen_fight":["Mi amor, mi diablesa!"],"dead_queen":["Black Tulip"],"dead_king":["Resignación"],"who":["¿Quién ¿Quién"]}
    group=musicGroups.get(name)
    music_to_play=group[0] if len(group)==1 else random.choice([i for i in group if i!=lastmusic])
    if play_particular_song_first!=None:
        music_to_play=play_particular_song_first
    if group and (wait:=play_music(music_to_play)):
        root.after(wait*1000+1500,lambda: play_from_music_group(name,None,False))
    

def stop_music():
    global stopsound
    stopsound=True
    mixer.stop()

def stop_music_with_fadeout(fadeTime):
    global stopsound
    stopsound=True
    mixer.fadeout(fadeTime)

def pause_music():
    mixer.pause()

def unpause_music(group):
    mixer.unpause()
    tracks_playing=0
    for i in music:
        tracks_playing+=mixer.Sound.get_num_channels(music[i])
    if tracks_playing==0:
        play_from_music_group(group)

#----------------------------------------------------
#End of music

#Settings
settings={"move_helper":True,"highlight":True,"is_white_ai":False,"is_black_ai":True,"permanent_death":False,"story_mode":False,"move_delay":500,
"cheats":False,"engine_depth":4,"difficulty":None}
#Loading in settings
with open("data/settings.txt",'r') as file:
	for i in file.read().splitlines():
		curr=i.split("#")[0].split("=")
		if len(curr)>=2:
			if curr[1][0].lower()=="o": settings[curr[0]]=False if "off" in curr[1].lower() else True
			else: settings[curr[0]]=int(curr[1])

defaults={"time_effects":True,"full_screen":True,"move_delay":500,"font_size":2,"drag_frames":5,"reading_time":7000}

for i in defaults:
	if i not in settings:
		settings[i]=defaults[i]

settings["reading_time"]=np.clip(settings["reading_time"],2000,12000)

#Start with full screen?
if settings["full_screen"]:
	root.attributes("-fullscreen",True)

#Loading screen
images["loading_screen"]=ImageTk.PhotoImage(Image.open(f"images/menu/Title screen 1.jpg").resize((fullheight,fullwidth),0))
BackgroundLabel=Label(root,image=images["loading_screen"])
BackgroundLabel.place(relx=0.5,rely=0.5,anchor=CENTER)
root.update()
#Loading music
load_music()
play_from_music_group("menu")
#Loading images
root.after(1,load_images())

#  ----GAME----
#----------------------------------------------------

#ChessPiece object
class ChessPiece():
	def __init__(self,value,position,index,image_name,canvas,name=None,title=None):
		self.colour=value>0 #white: True, black: False
		self.value=abs(value) #king: 15, queen: 90, ...
		self.position=position #(x,y) - tuple
		self.index=index #an index is required to indicate which piece is which
		if value not in (-15,-90): #If current piece is not the black king or queen: normal names and titles
			self.name=name #name for the selected piece if there is none its value will be None
			self.title=title #title for the selected piece -||-
		#Else: hard coded names and titles
		elif value==-15:
			self.name=titles_and_names["emperor_names"][title_indexes["emperors"]]
			self.title=titles_and_names["emperor_titles"][title_indexes["emperors"]]
		else:
			self.name=titles_and_names["empress_names"][title_indexes["empresses"]]
			self.title=titles_and_names["empress_titles"][title_indexes["empresses"]]
		if not self.name and self.title!=None:
			self.name=leader_names[current_opponent]
		#Special hidden Napoleon easter egg
		if self.title=='Napoleon III': self.name,self.title='Cristopher Moïse LeMahieu','"Napoleon III"'
		self.image_name=image_name #name with which you can access the piece's image in the images dictionary
		self.canvas=canvas
		self.visual=None
		self.update_position()

	#Updates the image's position based on self.position
	def update_position(self):
		if self.visual: self.canvas.delete(self.visual) #Deletes past image if there is one
		#Creates new image based on TIME
		if TIME!=None: self.visual=self.canvas.create_image((self.position[0]-1)*tile_size,(self.position[1]-1)*tile_size,anchor=NW,image=images[f"{self.image_name}_{int(TIME) if 6<=int(TIME)<=18 else 'night'}"])
		#If TIME is None then act according to image_name (fish and chess)
		elif "fish" in self.image_name: self.visual=self.canvas.create_image((self.position[0]-1)*tile_size,(self.position[1]-1)*tile_size,anchor=NW,image=images[self.image_name])
		else: self.visual=self.canvas.create_image(self.position[0]*tile_size,self.position[1]*tile_size,anchor=NW,image=images[self.image_name])

#Loads chessboard from file (2d str list with indexes)
def load_chessboard_from_file(ind):
	#Index for chessPieces
	index=0
	with open(f"data/chessboards/{ind}.txt","r") as file:
		chessboard=[i.split() for i in file.read().splitlines()]
		for i,row in enumerate(chessboard):
			for j,square in enumerate(row):
				if square!='x':
					#If square is not empty add index
					chessboard[i][j]+=str(index)
					#Then increment it
					index+=1
	return chessboard

#Loads names into a dictionary
def load_names_from_file(ind):
	with open(f"data/names/{ind}.txt","r") as file:
		names={int((curr:=i.replace(" ","=").split("="))[0]):[j.replace("_"," ") for j in curr[1:]] for i in file.read().splitlines()}
	return names

#Loads chessboard and chess pieces onto the passed canvas
def load_chessboard(board_number,game_id,chessCanvas,promCanvas):
	#Reading chessboard from file
	chessboard=np.array(load_chessboard_from_file(game_id))
	#Reading names from file
	names=load_names_from_file(game_id)
	#Adding board image to chessBoardCanvas and promotion image to promotionCanvas
	board=chessCanvas.create_image(0,0, anchor=NW, image=images[f"board_{board_number}"])
	promCanvas.create_image(0,0, anchor=NW, image=images[f"promotion_{board_number}"])

	#Chesspieces on the board (list of ChessPiece objects)
	chessPieces=[None]*64

	#Loading all ChessPiece objects to a list
	for y,row in enumerate(chessboard):
		for x,square in enumerate(row):
			if square!='x':
				index=int(square[1:]) #index of the current piece (in chessPieces list)
				square={"r":50,"n":30,"b":35,"q":90,"p":10,"k":15,"R":-50,"N":-30,"B":-35,"Q":-90,"P":-10,"K":-15}[square[0]] #reduce square into an integer
				image_name="black" if square<0 else "white" #piece colour for image_name
				image_name+="_"+{15:"king",90:"queen",10:"pawn",30:"knight",35:"bishop",50:"rook"}[abs(square)] #piece value for image_name
				if game_id=='fish': #If the game is fish add _fish to image_name (to identify loaded image in ChessPiece creation)
					image_name+="_fish"
				if index in names: #If the piece has a name, pass it onto the ChessPiece object
					chessPieces[index]=ChessPiece(square,(x,y),index,image_name,chessCanvas,*names[index])
				else: #If the piece doesn't have a name, don't pass anything
					chessPieces[index]=ChessPiece(square,(x,y),index,image_name,chessCanvas)
	chessPieces=[i for i in chessPieces if i] #Eliminate None in the chessPieces list
	return chessboard,chessPieces,board

#Return a ChessBoard object from a 2d array filled with strings
def make_int_chessboard(chessboard):
	return ChessBoard(np.array([[{"x":0,"r":50,"n":30,"b":35,"q":90,"p":10,"k":15,"R":-50,"N":-30,"B":-35,"Q":-90,"P":-10,"K":-15}[chessboard[i,j][0]] for j in range(8)] for i in range(8)][::-1]).transpose())

#Setting up the promotionCanvas
def setupPromotionCanvas(turn):
	#Showing canvas on window
	promotionCanvas.grid(row=2,column=2)
	#Showing pieces according to colour of moved pawn
	for i,name in enumerate(["knight","bishop","rook","queen","king"]):
		value={"knight":30,"bishop":35,"rook":50,"queen":90,"king":15}[name]*(1 if turn else -1)
		#Create ChessPiece objects on promotionCanvas (we only need their images)
		ChessPiece(value,(i,0),i,f"{['black','white'][turn]}_{name}",promotionCanvas)

#Remove a rendered chesspiece from canvas
def kill(index,chessPieces):
	#Define current (it's a shortcut and works solely of aliasing)
	current=chessPieces[index]
	#If story mode is on add important characters to graveyard
	if settings["story_mode"]:
		#If current is a black king append it to the list of dead kings
		if current.value==15 and not current.colour and current.title!=None:
			deadOnTheBattlefield["kings"].append([False,current.name,current.title])
			for i in chessPieces:
				if i!=None and i.value==15 and not i.colour and i.name!=titles_and_names["emperor_names"][title_indexes["emperors"]]:
					new_emperor_name=i.name
					title_indexes["emperors"]+=1
					titles_and_names["emperor_names"].append(new_emperor_name)
					break
		#If current is a black queen append it to the list of dead queens
		elif current.value==90 and not current.colour and current.title!=None:
			deadOnTheBattlefield["queens"].append([False,current.name,current.title])
			title_indexes["empresses"]+=1
		#If current has a title add it to the other dead pieces
		elif current.title not in [None,"None",'',' '] and type(current.title)==str:
			deadOnTheBattlefield["ordinary"].append([current.colour,current.name,current.title])
	#Delete current from canvas
	current.canvas.delete(current.visual)
	#"Remove" it from chessPieces -> substitute it with None (because of the indexes)
	chessPieces[index]=None
	return chessPieces

#Execute move on str array
def execute_str_move(chessboard,move):
    chessboard=chessboard[::-1].transpose()
    #En passant
    if chessboard[move[0],move[1]][0].lower()=='p' and (abs(move[0]-move[2]),abs(move[1]-move[3]))==(1,1) and chessboard[move[2],move[3]]=='x':
        chessboard[move[2],move[1]]='x'
    #Promotion
    if (chessboard[move[0],move[1]][0]=='p' and move[3]==0) or (chessboard[move[0],move[1]][0]=='P' and move[3]==7):
        chessboard[move[0],move[1]]={0:'x',50:'r',30:'n',35:'b',90:'q',10:'p',15:'k',-50:'R',-30:'N',-35:'B',-90:'Q',-10:'P',-15:'K'}[move[4]]+chessboard[move[0],move[1]][1:]
    #Castling
    if chessboard[move[0],move[1]][0].lower()=='k' and abs(move[0]-move[2])==2:
        ch1=a if move[0]-move[2]>0 else h
        ch2=move[2]+np.sign(move[0]-move[2])
        chessboard[ch2,move[1]]=chessboard[ch1,move[1]]
        chessboard[ch1,move[1]]='x'
    #Normal moves
    chessboard[move[2],move[3]]=chessboard[move[0],move[1]]
    chessboard[move[0],move[1]]='x'
    #END
    chessboard=chessboard.transpose()[::-1]
    return chessboard

#Change the board setup based on move (it gets completed before calling execute_str_move on chessboard)
def change_rendered(move,chessPieces):
	#Make used_chessboard compatible with a chessboard layout
	used_chessboard=chessboard[::-1].transpose()
    #En passant
	if used_chessboard[move[0],move[1]][0].lower()=='p' and (abs(move[0]-move[2]),abs(move[1]-move[3]))==(1,1) and used_chessboard[move[2],move[3]]=='x':
		chessPieces=kill(int(used_chessboard[move[2],move[1]][1:]),chessPieces)
	#Promotion
	if (used_chessboard[move[0],move[1]][0]=='p' and move[3]==0) or (used_chessboard[move[0],move[1]][0]=='P' and move[3]==7):
		current=chessPieces[int(used_chessboard[move[0],move[1]][1:])]
		#Modify value
		current.value=abs(move[4])
		#And image_name
		piece_name={10:"pawn",15:"king",30:"knight",35:"bishop",50:"rook",90:"queen"}[current.value]
		current.image_name=f"{'white' if current.colour else 'black'}_{piece_name}"
		#Then refresh it on canvas
		current.update_position()
    #Castling
	if used_chessboard[move[0],move[1]][0].lower()=='k' and abs(move[0]-move[2])==2:
		ch1=a if move[0]-move[2]>0 else h
		ch2=move[2]+np.sign(move[0]-move[2])
		index=used_chessboard[ch2,move[1]][1:]
		#If there is any piece where the rook will move (although it's impossible) it will kill it
		if index!='':
			kill(int(index),chessPieces)
		index=used_chessboard[ch1,move[1]][1:]
		#Move rook to its designated position
		if index!='':
			index=int(index)
			chessPieces[index].position=(ch2,7-move[1])
			chessPieces[index].update_position()
    #Normal moves
	index=used_chessboard[move[2],move[3]][1:]
	#If there is any piece on move location kill it
	if index!='':
		kill(int(index),chessPieces)
	index=used_chessboard[move[0],move[1]][1:]
	#Then modify the position of the selected piece
	if index!='':
		index=int(index)
		chessPieces[index].position=(move[2],7-move[3])
		chessPieces[index].update_position()
	return chessPieces

#Executes all moves on the three different boards and updates position
def execute_move_on_all(move):
	global POSITION,chessboard,chessPieces,TIME
	#Modify POSITION (which stores lastMove, turnIndex and castling score)
	POSITION=next_move(POSITION,move)
	#Modify root background to match whose turn it is
	if type(POSITION)!=int: root["bg"]="white" if turns[POSITION.tIndex] else "black"
	chessBoardCanvas["bg"]=root["bg"]
	promotionCanvas["bg"]=root["bg"]
	#If the game is not over yet...
	if type(POSITION)!=int:
		#Make move on canvas
		chessPieces=change_rendered(move,chessPieces)
		#Then make move on chessboard (2d np.array str)
		chessboard=execute_str_move(chessboard,move)
		#Store move in move history
		move_history.append(move)
	#If the game is over end it
	if -15 not in POSITION.chess.board:
		end_game(True)
		return True
	if POSITION.wLeader not in POSITION.chess.board:
		end_game(False)
		return True
	#Update TIME
	if TIME!=None:
		#Add 1/4 to time
		TIME+=0.25
		if TIME==int(TIME):
			for current in chessPieces:
				if current!=None: #If current is not Empty update its visual on canvas
					current.update_position()
		while TIME>=24:
			TIME-=24

#After a move is done this starts another (homan or engine)
def followUpMove():
	if (settings["is_black_ai"] and not turns[POSITION.tIndex]) or (settings["is_white_ai"] and turns[POSITION.tIndex]):
		#Human play
		chessBoardCanvas.bind("<Button-1>",select_piece) #Return to piece selection
	else:
		#Engine
		root.update()
		start=time()
		if current_opponent!="FIS":
			func=alphaBetaMax if turns[POSITION.tIndex] else alphaBetaMin
			move,_=func(POSITION,-100000,100000,settings["engine_depth"])
		else:
			move=random.choice(generate(POSITION.chess,turns[POSITION.tIndex],POSITION.move,POSITION.castling))
		end=time()
		wait=settings["move_delay"]-int((end-start)*1000)
		if wait>0:
			sleep(wait/1000)
		make_move(move)

#Completes promotion (it's binded to promotionCanvas upon promotion)
def promote_piece(event,move,turn):
	#Modify the 5th element of the move to match selected piece value
	move[4]=(30,35,50,90,15)[np.clip(event.x//tile_size,0,4)]*(1 if turn else -1)
	promotion_history.append(move[4])
	#Then execute said move
	execute_move_on_all(move)

	#Delete all but the very first image on promotionCanvas (which is the promotion board layout)
	item_ids=promotionCanvas.find_all()
	for i in item_ids[1:]:
		promotionCanvas.delete(i)
	#Bind and unbind unnecessary functions
	promotionCanvas.unbind("<Button-1>")
	#Hide promotionCanvas
	promotionCanvas.grid_forget()
	followUpMove()

#Sets up helping symbols (move indicator and highlight)
def setup_move_helper(move):
	#Delete all previous move indications and highlights
	for i in move_helper:
		chessBoardCanvas.delete(i)
	#Add highlight to selected piece
	move_helper.clear()
	if settings["highlight"]:
		move_helper.append(chessBoardCanvas.create_rectangle(move[0]*tile_size,(7-move[1])*tile_size,(move[0]+1)*tile_size,(8-move[1])*tile_size,fill='#181818',outline='white'))
	#Add move indication to selected piece
	if settings["move_helper"]:
		for i in generate(POSITION.chess,turns[POSITION.tIndex],POSITION.move,POSITION.castling):
			if i[:2]==move:
				#If it is a normal move add a small white circle
				if i[-1]==0:
					move_helper.append(chessBoardCanvas.create_oval(int((i[2]+0.25)*tile_size),int((7.25-i[3])*tile_size),int((i[2]+0.75)*tile_size),(7.75-i[3])*tile_size,fill='#f3f3f3',outline="black"))
				#If it is a capture add a big red one
				else:
					move_helper.append(chessBoardCanvas.create_oval(int((i[2])*tile_size),int((7-i[3])*tile_size),int((i[2]+1)*tile_size),(8-i[3])*tile_size,fill='red',outline="black"))
	#Bring move indication behind the pieces
	for i in move_helper:
		chessBoardCanvas.tag_lower(i)
	#Bring the board behind the move indications
	chessBoardCanvas.tag_lower(board)

#Delete move indication and highlight
def hide_move_helper():
	for i in move_helper:
		chessBoardCanvas.delete(i)

#Select piece on board (moving images on canvas)
def select_piece(event):
	#Get the selected piece
	move=[np.clip(event.x//tile_size,0,7),np.clip(7-event.y//tile_size,0,7)]
	#Get piece value
	piece_value={"x":0,"r":50,"n":30,"b":35,"q":90,"p":10,"k":15,"R":-50,"N":-30,"B":-35,"Q":-90,"P":-10,"K":-15}[chessboard[7-move[1],move[0]][0]]

	#Helping symbols (highlight and move indicator)
	setup_move_helper(move)
	
	def move_piece(event,move,image=None):
		chessBoardCanvas.unbind("<Button-1>")
		chessBoardCanvas.unbind("<ButtonRelease-1>")
		chessBoardCanvas.unbind("<B1-Motion>")
		#Reset image position if needed
		if image!=None:
			image.update_position()
		#Delete all move indications
		hide_move_helper()
		#Store to which square to move to
		move+=[np.clip(event.x//tile_size,0,7),np.clip(7-event.y//tile_size,0,7)]
		#Get square value
		square_value={"x":0,"r":50,"n":30,"b":35,"q":90,"p":10,"k":15,"R":-50,"N":-30,"B":-35,"Q":-90,"P":-10,"K":-15}[chessboard[7-move[3],move[2]][0]]
		#Complete move storage
		move+=[piece_value,square_value]
		#If move is possible: execute it
		make_move(move)


	#Drag and drop, move held image to cursor
	def move_image_to_cursor(event,current):
		global drag_frames
		if drag_frames>settings["drag_frames"]:
			image=current.visual
			if len(chessBoardCanvas.coords(image))>=2:
				x,y=chessBoardCanvas.coords(image)[0],chessBoardCanvas.coords(image)[1]
				if settings["time_effects"]:
					chessBoardCanvas.move(image,event.x-x-(tile_size*3)//2,event.y-y-(tile_size*3)//2)
				else:
					chessBoardCanvas.move(image,event.x-x-tile_size//2,event.y-y-tile_size//2)
			chessBoardCanvas.bind("<ButtonRelease-1>",lambda event: move_piece(event,move,current))
		drag_frames+=1
	
	#If selected piece is not nothing try to move it
	if piece_value!=0:
		global drag_frames
		drag_frames=0
		current=chessPieces[int(chessboard[7-move[1],move[0]][1:])]
		chessBoardCanvas.tag_raise(current.visual)
		chessBoardCanvas.unbind("<ButtonRelease-1>")
		chessBoardCanvas.bind("<B1-Motion>",lambda event: move_image_to_cursor(event,current))
		chessBoardCanvas.bind("<Button-1>",lambda event: move_piece(event,move))

#Make move, deal with promotion and rebind if necessary
def make_move(move):
	#It's only necessary for promotion
	rebind=True
	#Normal moves
	if move in generate(POSITION.chess,turns[POSITION.tIndex],POSITION.move,POSITION.castling):
		if execute_move_on_all(move):
			return
	#Promotion
	elif move in generate(POSITION.chess,turns[POSITION.tIndex],POSITION.move,POSITION.castling,True):
		#Set up promotionCanvas
		setupPromotionCanvas(turns[POSITION.tIndex])
		#Bind promote_piece to it
		promotionCanvas.bind("<Button-1>",lambda event:promote_piece(event,move,turns[POSITION.tIndex]))
		#Unbind move_piece from chessboardCanvas
		chessBoardCanvas.unbind("<Button-1>")
		chessBoardCanvas.unbind("<ButtonRelease-1>")
		chessBoardCanvas.unbind("<B1-Motion>")
		#Do not rebind to select_piece
		rebind=False
	if len(move_history)%11==0:
		clear_evaluated_positions()
	#Rebind if necessary
	if rebind:
		followUpMove()

#Initialises game
def initialise_game(board_number,game_id,time=6,castling=1,wLeader=15):
	global chessboard,chessPieces,board,POSITION,TIME,background_colour
	if settings["story_mode"]:
		open("data/saves/autosave.save","w").close()
	for i in deadOnTheBattlefield:
		deadOnTheBattlefield[i].clear()
	clear_evaluated_positions()
	move_history.clear()
	promotion_history.clear()
	#Store background colour
	background_colour=root["bg"]
	root["bg"]="black"
	chessBoardCanvas["bg"]=root["bg"]

	MAP.grid_forget()
	for i in Buttons:
		i.grid_forget()

	#Grid cheats(win and lose)
	if settings["cheats"]:
		current_row=7
		for i in CheatButtons:
			i.grid(row=current_row,column=2,sticky='wens')
			current_row+=1

	#Set TIME
	TIME=time if settings["time_effects"] else None
	#Load chessboard and chessPieces
	chessboard,chessPieces,board=load_chessboard(board_number,game_id,chessBoardCanvas,promotionCanvas)
	#Setup POSITION
	POSITION=Position(make_int_chessboard(chessboard),castling,[-1]*6,0,wLeader)

	#Show chessBoardCanvas
	chessBoardCanvas.grid(row=1,column=2)
	#Start game (first move)
	followUpMove()

#Ends a game
def end_game(winner):
	global game_number
	clear_evaluated_positions()
	stop_music()
	if current_opponent=="Coronel":
		end_tutorial(winner)
		return
	if not settings["story_mode"]:
		if not winner:
			statistics["games"][0]+=1
			statistics["fastest"][0]=min(statistics["fastest"][0],len(move_history))
		else:
			statistics["games"][1]+=1
			statistics["fastest"][1]=min(statistics["fastest"][1],len(move_history))
		statistics["moves"]+=len([i for i in move_history if i[4]<0])
		for i,piece in enumerate([15,90,50,35,30,10]):
			statistics["captures"][i]+=len([i for i in move_history if i[5]==piece])
			statistics["pieces_lost"][i]+=len([i for i in move_history if i[5]==-piece])
		for i,piece in enumerate([-15,-90,-50,-35,-30]):
			statistics["promotions"][i]+=len([i for i in promotion_history if i==piece])
	elif current_opponent=="SRB" and not winner and [False,"Ignacio Coronel","The faithful bishop"] not in deadOnTheBattlefield["ordinary"]:
		root["bg"]="black"
		quien_quien()
	#Restore original background colour
	root["bg"]=background_colour
	#Delete all pieces and images
	chessBoardCanvas.delete("all")
	promotionCanvas.delete("all")
	#Unbind all functions
	chessBoardCanvas.unbind("<Button-1>")
	chessBoardCanvas.unbind("<B1-Motion>")
	promotionCanvas.unbind("<Button-1>")
	chessBoardCanvas.unbind("<ButtonRelease-1>")
	#Hide everything
	chessBoardCanvas.grid_forget()
	promotionCanvas.grid_forget()
	chessPieces.clear()
	if settings["cheats"]:
		for i in CheatButtons:
			i.grid_forget()
	
	
	#If winner is white: back to menu or back to last game (according to difficulty)
	if settings["permanent_death"] and winner:
		main_menu()
		return
	
	#If winner is black: next game
	if not winner:
		game_number+=1
		for i in deadPieces:
			deadPieces[i]+=deadOnTheBattlefield[i]
		if current_opponent not in (None,"FIS"):
			defeated_countries.append(return_countries()[current_opponent[:3]].name)
		if current_opponent=="MAR":
			defeated_countries.append(return_countries()["SEB"].name)
			defeated_countries.append(return_countries()["AND"].name)
			defeated_countries.append(return_countries()["CAT"].name)
		if current_opponent=="MAG":
			defeated_countries.append(return_countries()["MOR"].name)


	#Back to map menu according to difficulty and winner
	update_map(not winner)

#Cheats
CheatButtons=[Button(root,text="Win",command=lambda: end_game(False)),Button(root,text="Lose",command=lambda: end_game(True))]

#Global variables for games
TIME=None
move_helper=[]
chessPieces=[]
move_history=[]
promotion_history=[]

#Graveyard mechanic in ShadowChess
deadPieces={"ordinary":[],"queens":[],"kings":[]}
deadOnTheBattlefield={"ordinary":[],"queens":[],"kings":[]}
defeated_countries=[]

#Hard coded names and titles
titles_and_names={"emperor_titles":['The Shadow Emperor','The Infinite Emperor','The Sick Emperor','The Magnificent Emperor','The Genious Emperor','The Pious Emperor','The Fishy Emperor','The Wrathful Emperor','The Brave Emperor','The Resourceful Emperor','The Mad Emperor','The Controversal Emperor','The Emperor','The King','The figurehead','The president'],
"empress_titles":['The Golden Empress','The Emerald Empress','The Silver Empress','The Iron Empress','The Bronze Empress','The Ruby Empress','The Terracotta Empress','The Empress','The Queen'],
"empress_names":['Yasmin Nayara Garcia',"Caitlin O'Lynn",'Barbara Valdes','Marie von Bismarck','Amense','Agnes Holland','Tan Huo','Lara Sastre','Olivia Ruiz'],
"emperor_names":['Xefinrac Delictum']}
title_indexes={"emperors":0,"empresses":0}
leader_names={'CAC':'Xabier Sánchez','BAD':'Galez Cueto','HLV':'Jamaal el-Hadi','GAL':['Remedios Vallin','Ernesto Seoane'],'ORA':['Kaatje van der Harst','Pieter-Jan Stroeve'], 'LEO':['Nuria Miguélez','Mateo Saldaña'], 'SAN':['Itziar Villarreal','Xavier Prado'],'BIL':['Inmaculada Álvarez','Alfonso Sabaté'],'LOG':['Jimena Tarragona','Canus Vedius Vitalis'],'VAL': 'Agostín Cebrián','GRA':'Isaam al-Ghattas','MAL':'Ali Tazi','MUR':'Jørn Davidsen','LIN':'Zain al-Azimi','SEV':'Mubarak al-Akel','LRA':'Bandar al-Jaffer'}

#----------------------------------------------------
#End of game

#  ----MAPS----
#----------------------------------------------------

img=load_map("data/maps/")
images["img"]=ImageTk.PhotoImage(img.resize((int(538*(tile_size/75)),int(346*(tile_size/75)))))
MAP=Label(image=images["img"])


#----------------------------------------------------
#End of maps

#  ----MAP MENU----
#----------------------------------------------------

#Launch next game based on decision
def launch_next_game(choice=None):
	global current_opponent
	if game_number==1:
		current_opponent="SRB"
		initialise_game(1,1,11,143)
		play_from_music_group("starting_battles","La Revuelta")
	elif game_number==2:
		current_opponent="TOL"
		initialise_game(1,2,6,143)
		play_from_music_group("starting_battles")
	elif game_number==3:
		current_opponent="MAD"
		initialise_game(1,3,6,143)
		play_from_music_group("starting_battles")
	elif game_number in (4,5):
		if choice==1:
			current_opponent="ALB"
			if [True,"Abel Artigas","The traitorous bishop"] in deadPieces["ordinary"]:
				initialise_game(2,4,19,143,90)
			else:
				modify_countries("ALB","name","Order of the Holy Red Sea")
				current_opponent+="2"
				initialise_game(2,"4_ALB",5,143,35)
		if choice==2:
			current_opponent="DON"
			initialise_game(1,5,6,143)
			play_from_music_group("starting_battles")
	elif game_number in (6,7):
		if choice==1:
			current_opponent="ARC"
			initialise_game(1,6,6,143)
		elif choice==2:
			current_opponent=countries_from_region((54, 120, 43))[0].tag
			initialise_game(1,7,6,143)
		play_from_music_group("starting_battles")
	elif game_number==8:
		current_opponent=countries_from_region((250, 189, 0),False)[0].tag
		countries=return_countries()
		if "CRS" in countries:
			initialise_game(2,"8_CRS",8,1,35)
		elif "SPA" in countries:
			initialise_game(3,"8_SPA")
		elif "SPR" in countries:
			initialise_game(3,"8_SPR")
		else:
			initialise_game(3,8)
		play_from_music_group("advanced_battles")
	elif game_number==9:
		current_opponent=countries_from_region((16, 88, 18),False)[0].tag
		initialise_game(3,9)
		play_from_music_group("muslim","Gran Oración")
	elif game_number==10:
		current_opponent=countries_from_region((41, 158, 84),False)[0].tag
		countries=return_countries()
		if "POC" in countries:
			initialise_game(2,"10_POC",13,1,90)
		elif "POM" in countries:
			initialise_game(3,"10_POM")
		else:
			initialise_game(3,10)
		play_from_music_group("advanced_battles")
	elif game_number==11:
		current_opponent="MAR"
		initialise_game(3,11)
		play_from_music_group("endgame_battles","¡Bienvenidos a Cataluña!")
	else:
		if choice==1:
			current_opponent="FRA"
			initialise_game(4,12)
			play_from_music_group("endgame_battles","Alas Doradas")
		elif choice==2:
			current_opponent="BAL"
			initialise_game(3,13)
			play_from_music_group("muslim","Gran Oración")
		elif choice==3:
			current_opponent="ENG"
			initialise_game(3,14)
			play_from_music_group("advanced_battles")
		elif choice==6:
			current_opponent="MAG"
			initialise_game(3,15)
			play_from_music_group("muslim","Sol")
		elif choice==4:
			current_opponent="FIS"
			initialise_game(4,"fish")
			play_from_music_group("agua")
		else:
			for i in Buttons:
				i.grid_forget()
			if settings["story_mode"]:
				finalButton["text"]="Take me to the graveyard"
				finalButton["command"]=lambda: load_graveyard_layout(1)
			else:
				finalButton["text"]="Take me to the statistics"
				finalButton["command"]=display_statistics
			finalButton["font"]=("Segoe UI",font_small)
			finalButton['bg']=root['bg']
			finalButton['fg']='white' if conquest_points>60 else 'black'
			finalButton['activebackground']=f"gray{min(107-conquest_points,97)}"
			finalButton['activeforeground']='white' if conquest_points>70 else 'black'
			finalButton.grid(row=2,column=2,sticky='wens')

#Updates map and Labels
def update_map(winner):
	global conquest_points
	stop_music()
	for i in Buttons:
		i.grid_forget()
	
	#Change map (and conquest points)
	if winner:
		if game_number==2:
			annex_country("SHD","SRB",img)
			conquest_points+=2
		if game_number==3:
			annex_country("SHD","TOL",img)
			for i in [(255, 132, 17),(250, 189, 0),(54, 120, 43),(144, 243, 95)]:
				expand_random_from_region(i,img)
			conquest_points+=5
		if game_number==4:
			annex_country("SHD","MAD",img)
			for i in [(255, 132, 17),(250, 189, 0),(144, 243, 95),(41, 158, 84),(110, 169, 112)]:
				expand_random_from_region(i,img)
			conquest_points+=7
		if game_number in (5,6):
			if current_opponent[:3]=="ALB":
				annex_country("SHD","ALB",img)
				for i in [(54, 120, 43),(255, 132, 17)]:
					expand_random_from_region(i,img)
				conquest_points+=5
			if current_opponent=="DON":
				annex_country("SHD","DON",img)
				for i in [(255, 132, 17),(250, 189, 0),(110, 169, 112)]:
					expand_random_from_region(i,img)
				conquest_points+=4
		if game_number in (7,8):
			if current_opponent=="ARC":
				annex_country("SHD","ARC",img)
				expand_random_from_region((250, 189, 0),img,False)
				conquest_points+=6
			else:
				annex_country("SHD",current_opponent,img)
				expand_random_from_region((16, 88, 18),img,False)
				conquest_points+=4
		if game_number==9:
			annex_country("SHD",current_opponent,img)
			for i in [(16, 88, 18),(41, 158, 84)]:
				expand_random_from_region(i,img,False)
			conquest_points+=10
		if game_number in (10,11):
			annex_country("SHD",current_opponent,img)
			conquest_points+=9 if game_number==10 else 11
		if game_number==12:
			for i in ("MAR","SEB","CAT","AND"):
				annex_country("SHD",i,img)
			conquest_points+=14
		if game_number>12:
			if current_opponent not in ("MAG","FIS"):
				annex_country("SHD",current_opponent,img)
			elif current_opponent=="FIS":
				annex_country("BWA","WAT",img)
			else:
				for i in ("MAG","MOR"):
					annex_country("SHD",i,img)
			if current_opponent!="FIS":
				conquest_points+=5

	images["img"]=ImageTk.PhotoImage(img.resize((int(538*(tile_size/75)),int(346*(tile_size/75)))))
	MAP['image']=images["img"]

	root["bg"]=f"gray{97-conquest_points}"
	MAP["bg"]=root["bg"]

	if not winner:
		if current_opponent=="FIS":
			Buttons[4]['text']="..."
			Buttons[4]['state']=DISABLED

	#Lock and unlock necessary buttons
	if winner:
		if game_number==5:
			if current_opponent[:3]=="ALB":
				if len(current_opponent)==3:
					Buttons[1]['text']=lockedTexts[0][0]
				else:
					Buttons[1]['text']=lockedTexts[0][3]
				Buttons[1]['state']=DISABLED
			else:
				Buttons[2]['text']=lockedTexts[1][0]
				Buttons[2]['state']=DISABLED
		elif game_number in (6,8):
			Buttons[1]['state']=NORMAL
			Buttons[2]['state']=NORMAL
		elif game_number==7:
			if current_opponent=="ARC":
				Buttons[1]['text']=lockedTexts[0][1]
				Buttons[1]['state']=DISABLED
			else:
				Buttons[2]['text']=lockedTexts[1][1]
				Buttons[2]['state']=DISABLED
		elif game_number>12:
			if current_opponent=="FRA":
				Buttons[1]['text']=lockedTexts[0][2]
				Buttons[1]['state']=DISABLED
			elif current_opponent=="MAG":
				Buttons[2]['text']=lockedTexts[1][2]
				Buttons[2]['state']=DISABLED
			elif current_opponent=="ENG":
				Buttons[3]['text']=lockedTexts[2][2]
				Buttons[3]['state']=DISABLED
			elif current_opponent=="FIS":
				Buttons[4]['text']=lockedTexts[3][2]
				Buttons[4]['state']=DISABLED

	#Set buttons' text
	for i in range(3):
		if Buttons[i]['state']!=DISABLED: Buttons[i]["text"]=buttonTexts[i][game_number-1 if game_number<12 else 11]
	if game_number>=12:
		countries=return_countries()
		if "BAL" not in countries and Buttons[2]['state']!=DISABLED:
			Buttons[2]["text"]='North African Colonies and Slaves'
			Buttons[2]["command"]=lambda: launch_next_game(6)
		if Buttons[3]['state']!=DISABLED: Buttons[3]["text"]='Conquer Aquitaine'
		if Buttons[4]['state']!=DISABLED: Buttons[4]["text"]='Conquer the ocean'
		if Buttons[5]['state']!=DISABLED: Buttons[5]['text']="It is the End"
	else:
		for i in range(3,6):
			if Buttons[i]['state']!=DISABLED: Buttons[i]['text']=''
	
	#Display every non-empty button
	MAP.grid(row=1,column=2,sticky='wens')
	current_row=2
	for i in Buttons:
		if i['text']!='':
			if Buttons.index(i)!=4 or title_indexes["emperors"] in (6,10):
				i.grid(row=current_row,column=2,sticky='wens')
				current_row+=1
		i['font']=("Segoe UI",font_small)
		i['bg']=root['bg']
		i['fg']='white' if conquest_points>60 else 'black'
		i['activebackground']=f"gray{min(107-conquest_points,97)}"
		i['activeforeground']='white' if conquest_points>70 else 'black'
	save_game_state()

#Storing which game we're on
game_number=1

#Conquest points define the background colour
conquest_points=0

#opponent tag for leader_names dictionary
current_opponent=None

#Buttons displaying the choices the player has
Buttons=[Button(root,text="Action button",command=launch_next_game),Button(root,text="Choice 1",command=lambda: launch_next_game(1)),
Button(root,text="Choice 2",command=lambda: launch_next_game(2)),Button(root,text="Choice 3",command=lambda: launch_next_game(3)),
Button(root,text="Choice 4",command=lambda: launch_next_game(4)),Button(root,text="Choice 5",command=lambda: launch_next_game(5))]

#The button which takes you to the credits or the graveyard
finalButton=Button(root)

buttonTexts=[['Crush Rebellion','Conquer Toledo','Conquer Madrid','','','','','Invade the North','Finish Reconquista','Portugal Shall Be Ours','Iberia is for Iberians',''],
['','','','Crush the Communist Threat','Crush the Communist Threat','End Aragon','End Aragon','','','','','Triumph Against the Revolution'],
['','','','Liberate the Fascists','Liberate the Fascists','Limit Muslim Extension','Limit Muslim Extension','','','','','Invade the Balearic Islands']]
#Texts for the disabled buttons
lockedTexts=[['NO MORE REVOLUTIONS!','We shall extend further','Napoleon is Dead, he MUST be DEAD! ...','Goodbye old foe!'],
['Welcome aboard!','Those with an inferior fate must be destroyed','Peace Over Africa'],
['','','ENGLAND is Over'],['','','The oceans are ours!']]

#----------------------------------------------------
#End of map menu

#  ----Graveyard----
#----------------------------------------------------

#If story mode is off instead of a graveyard you get statistics (Yay!)
def display_statistics():
	#Erasing save data
	open("data/saves/autosave.save","w").close()
	play_from_music_group("credits")
	root.unbind("<Escape>")
	hide_everything()
    #Resetting texts
	for i in statisticsTexts:
		l=i[0]
		l['text']=l['text'].split(":")[0]
		l.grid_forget()
	bgImage.place(relx=0.5,rely=0.5,anchor=CENTER)
    #Sending bgImage to the back
	bgImage.lower()
    #Adjusting time
	statistics['time']+=time()-game_start
    
    #Placing frames
	for i,frame in enumerate(frames):
		frame.grid(row=1,column=i+1)
    
    #Displays the current statistic
	def display_current(statistic,row):
		[l,form]=statistic[:2]
		used_font=int({"Title1":font_big,"Title2":font_medium,"Title3":font_small}[form]*(5/4))
		l["font"]=("Times New Roman",used_font)
		l["bg"]="#e8cb60"
		l["fg"]="#713e08"
		l['anchor']=W

		l.grid(row=row,column=0,sticky=W)
		root.update()
		if len(statistic)==3:
			num=eval(statistic[2])
			wait=settings['reading_time']/6000 if num==0 or type(num)!=int else settings['reading_time']/(num*2000)
			ran=range(num+1) if type(num)==int else [num]
			for i in ran:
				l["text"]=l['text'].split(":")[0]+f": {i}"
				root.update()
				sleep(wait)

    #Displaying statistics
	current_row=1
	for statistic in statisticsTexts:
		display_current(statistic,current_row)
		current_row+=1
	#Placing backToMenu button
	backToMenu["font"]=("Times New Roman",font_medium)
	backToMenu.grid(row=2,column=2)
	#Rebinding Escape
	root.bind("<Escape>",main_menu)

#Statistics data
statistics={"games":[0,0],"time":0,"moves":0,"captures":[0,0,0,0,0,0],"pieces_lost":[0,0,0,0,0,0],"promotions":[0,0,0,0,0],"fastest":[np.inf,np.inf]}
#Data for displaying favourite piece in promotion
pieces_for_promotion=["king","queen","rook","bishop","knight"]
#Frames which the Labels are fitted in
frames=[Frame(root,bg="#e8cb60"),Frame(root,width=tile_size*2,bg="#e8cb60"),Frame(root,bg="#e8cb60")]
#Background Image
bgImage=Label(root,image=images["Statistics"])
#All labels for statistics
statisticsTexts=[[Label(frames[0],text="Games"),"Title1"],[Label(frames[0],text="Games played"),"Title2","sum(statistics['games'])"],[Label(frames[0],text="Games won"),"Title2","statistics['games'][0]"],
[Label(frames[0],text="Games lost"),"Title2","statistics['games'][1]"],[Label(frames[0],text="Time played"),"Title2","int(statistics['time'])"],[Label(frames[0],text="Moves"),"Title1"],[Label(frames[0],text="Moves made"),"Title2","statistics['moves']"],
[Label(frames[0],text="Captures"),"Title2","sum(statistics['captures'])"],[Label(frames[0],text="Kings"),"Title3","statistics['captures'][0]"],[Label(frames[0],text="Queens"),"Title3","statistics['captures'][1]"],[Label(frames[0],text="Rooks"),"Title3","statistics['captures'][2]"],
[Label(frames[0],text="Bishops"),"Title3","statistics['captures'][3]"],[Label(frames[0],text="Knights"),"Title3","statistics['captures'][4]"],[Label(frames[0],text="Pawns"),"Title3","statistics['captures'][5]"],[Label(frames[0],text="Pieces lost"),"Title2","sum(statistics['pieces_lost'])"],
[Label(frames[0],text="Kings"),"Title3","statistics['pieces_lost'][0]"],[Label(frames[0],text="Queens"),"Title3","statistics['pieces_lost'][1]"],[Label(frames[0],text="Rooks"),"Title3","statistics['pieces_lost'][2]"],[Label(frames[0],text="Bishops"),"Title3","statistics['pieces_lost'][3]"],
[Label(frames[0],text="Knights"),"Title3","statistics['pieces_lost'][4]"],[Label(frames[0],text="Pawns"),"Title3","statistics['pieces_lost'][5]"],[Label(frames[2],text="Promotions"),"Title2","sum(statistics['promotions'])"],[Label(frames[2],text="Favourite promotion"),"Title3","pieces_for_promotion[statistics['promotions'].index(max(statistics['promotions']))] if sum(statistics['promotions'])!=0 else None"],
[Label(frames[2],text="Fastest win"),"Title2","statistics['fastest'][0] if statistics['fastest'][0]!=np.inf else None"],[Label(frames[2],text="Fastest loss"),"Title2","statistics['fastest'][1] if statistics['fastest'][1]!=np.inf else None"],[Label(frames[2],text="Countries"),"Title1"],[Label(frames[2],text="Countries annexed"),"Title2","len(defeated_countries)"],
[Label(frames[2],text="Opponent in the North"),"Title3","defeated_countries[7] if len(defeated_countries)>=10 else None"],[Label(frames[2],text="Opponent in the South"),"Title3","defeated_countries[8] if len(defeated_countries)>=10 else None"],[Label(frames[2],text="Opponent in Portugal"),"Title3","defeated_countries[9] if len(defeated_countries)>=10 else None"],
[Label(frames[2],text="Won against France"),"Title3","'France' in defeated_countries"],[Label(frames[2],text="Difficulty"),"Title1"],[Label(frames[2],text="Difficulty"),"Title2","settings['difficulty']"],
[Label(frames[2],text="Cheats"),"Title3","settings['cheats']"],[Label(frames[2],text="Permanent death"),"Title3","settings['permanent_death']"],[Label(frames[2],text="Move helper"),"Title3","settings['move_helper']"],[Label(frames[2],text="Engine depth"),"Title3","settings['engine_depth']"]]

#Displaying background
fake_background=Canvas(root,width=fullheight,height=fullwidth)

#Text which is displayed upon interacting with a grave
graveText=Label(root)

#List of all fonts the user has
fonts=list(font.families())

roll_credits_after_move=False

#All objects in the graveyard
class GraveyardObject:
	def __init__(self,image_name,position,canvas,content=[],king_time=None):
		self.image_name=image_name #Image name for canvas
		self.king_time=king_time #Time for choosing image of the king
		self.position=position #Position (x,y) -> (int, int)
		self.canvas=canvas #Where to put the image
		if "cross" in image_name.lower() and content==[]:
			self.content=["Nameless",None]
		else:
			self.content=content
		self.visual=None
		self.update_position()

	def update_position(self):
		if self.visual: self.canvas.delete(self.visual)
		if self.king_time!=None and settings["time_effects"]:
			#Rendering the king
			self.visual=self.canvas.create_image((self.position[0]-1)*tile_size,(self.position[1]-1)*tile_size,anchor=NW,image=images[f"{self.image_name}_{self.king_time}"])
		else:
			minus=1 if self.image_name!="black_king" else 0
			#Rendering all other objects
			self.visual=self.canvas.create_image((self.position[0]-minus)*tile_size,(self.position[1]-minus)*tile_size,anchor=NW,image=images[self.image_name])
	
    #Displaying to the screen what the object holds
	def display_content(self):
        #Making it cinematic
		root.unbind("<Escape>")
		root.config(cursor="none")
        #If content is text
		if len(self.content)==2:
			pause_music()
			text=self.content[0]+'\n'+self.content[1] if self.content[1]!=None else self.content[0]
			setup_grave_text(text)
			font_change(settings["reading_time"],font_enormous)
			unpause_music('garden')
        #If content is image
		elif len(self.content)==1:
			pause_music()
			setup_grave_text('')
			fake_background.create_image((fullheight//2,fullwidth//2),image=self.content[0])
			root.update()
			sleep(settings["reading_time"]//1000)
        #If content is animation/video
		elif len(self.content)==3:
			stop_music()
			setup_grave_text('')
			with open("images/graveyard/tree/framerates.txt") as file:
				frames=[i.replace(" ","").replace(":","->").split("->") for i in file.read().splitlines()]
			animate_sequence(frames)

def setup_grave_text(text,bg='black',fg='white'):
	fake_background.delete("all")
	fake_background["bg"]=bg
	fake_background.place(relx=0.5,rely=0.5,anchor=CENTER)
	graveText["text"]=text
	graveText["bg"]=bg
	graveText["fg"]=fg
	if text!='': graveText.place(relx=0.5,rely=0.5,anchor=CENTER)

#Change grave text
def font_change(time_left,font_size,used_fonts=None):
	if used_fonts==None: used_fonts=fonts
	for i in range(0,time_left,1000):
		font_size+=random.randint(-3,3)
		graveText.config(font=(random.choice(used_fonts),font_size))
		root.update()
		sleep(1)

#Hide grave text
def hide_content():
	root.bind("<Escape>",main_menu)
	root.config(cursor="circle")
	graveText.place_forget()
	fake_background.place_forget()
	root.update()

#The last words of the emperor and/or empress
def final_words(text,emperor=True):
	root.unbind("<Escape>")
	root.config(cursor="none")
	(bg,fg)=('black','white') if emperor else ('white','black')
	setup_grave_text(text,bg,fg)
	font_change(settings["reading_time"],font_enormous,['Times New Roman','Vivaldi','Onyx','Franklin Gothic Book','Sitka Banner'])

#Tree animation
def animate_sequence(frames):
	for current in range(int(frames[0][-1].split("-")[0]),int(frames[-1][-1].split("-")[-1])+1):
		fake_background.delete("all")
		fake_background.create_image((fullheight//2,fullwidth//2),image=images[str(current)])
		root.update()
		for frame in frames:
			[start,end]=frame[-1].split("-")
			if current in range(int(start),int(end)+1):
				if 'fps' in frame[0]:
					wait=1/float(frame[1])
					sleep(wait)
				elif 'spf' in frame[0]:
					wait=float(frame[1])
					sleep(wait)
				break


def load_graveyard_layout_from_file(ind):
	with open(f"data/graveyard layout/graveyard{ind}.txt","r") as file:
		graveyard=[i.split() for i in file.read().splitlines()]
	return graveyard

#Moving the king on the graveyard layout
def select_king(event,graveyard_id):
	#Get the selected piece
	move=[np.clip(event.x//tile_size,0,7),np.clip(event.y//tile_size,0,7)]
	#Get piece value
	piece_value=-15 if chessPieces[-1].position==tuple(move) else 0

	#Helping symbols (highlight and move indicator)
	hide_move_helper()
	move_helper.clear()
	if settings["highlight"]:
		move_helper.append(chessBoardCanvas.create_rectangle(move[0]*tile_size,(move[1])*tile_size,(move[0]+1)*tile_size,(move[1]+1)*tile_size,fill='#181818',outline='white'))
	chessBoardCanvas.tag_lower(move_helper[0])
	chessBoardCanvas.tag_lower(board)
		
	def move_king(event,move,image=None):
		chessBoardCanvas.unbind("<B1-Motion>")
		#Roll credits after ending 1's last choice
		global roll_credits_after_move
		if roll_credits_after_move:
			roll_credits_after_move=False
			credits()
			return

		#Reset image position if needed
		if image!=None:
			image.update_position()
		#Delete all move indications
		hide_move_helper()
		#Store to which square to move to
		move+=[np.clip(event.x//tile_size,0,7),np.clip(event.y//tile_size,0,7)]
		#If move is possible: execute it
		if (move[0]-move[2])**2+(move[1]-move[3])**2<=2:
			if graveyard_layout[move[3]][move[2]][0] in 'xrs':
				if (move[3],move[2])==(7,7) and graveyard_id!=3 and graveyard_layout[7][7]!='x':
					load_graveyard_layout(graveyard_id+1)
					return
				chessPieces[-1].position=tuple(move[2:4])
				chessPieces[-1].update_position()
				chessBoardCanvas.tag_raise(chessPieces[0].visual)
			elif (current:=graveyard_layout[move[3]][move[2]])[0] in "g":
				chessPieces[int(current[1:])].display_content()
				hide_content()
			elif (current:=graveyard_layout[move[3]][move[2]])[0] in "Y":
				ending_selector(int(current[1:]),graveyard_id)
		chessBoardCanvas.bind("<Button-1>",lambda e:select_king(e,graveyard_id))
		chessBoardCanvas.unbind("<ButtonRelease-1>")

	#Drag and drop, move held image to cursor
	def move_image_to_cursor(event,current):
		global drag_frames
		if drag_frames>settings["drag_frames"]:
			image=current.visual
			if len(chessBoardCanvas.coords(image))>=2:
				x,y=chessBoardCanvas.coords(image)[0],chessBoardCanvas.coords(image)[1]
				if settings["time_effects"]:
					chessBoardCanvas.move(image,event.x-x-(tile_size*3)//2,event.y-y-(tile_size*3)//2)
				else:
					chessBoardCanvas.move(image,event.x-x-tile_size//2,event.y-y-tile_size//2)
			chessBoardCanvas.bind("<ButtonRelease-1>",lambda event: move_king(event,move,current))
		drag_frames+=1
	
	#If selected piece is not nothing try to move it
	if piece_value==-15:
		global drag_frames
		drag_frames=0
		current=chessPieces[-1]
		chessBoardCanvas.tag_raise(current.visual)
		chessBoardCanvas.unbind("<ButtonRelease-1>")
		chessBoardCanvas.bind("<B1-Motion>",lambda event: move_image_to_cursor(event,current,))
		chessBoardCanvas.bind("<Button-1>",lambda event: move_king(event,move))
	else:
		chessBoardCanvas.unbind("<ButtonRelease-1>")
		chessBoardCanvas.unbind("<B1-Motion>")

#Graveyard
def load_graveyard_layout(ind):
	global graveyard_layout,board,chessPieces
	hide_everything()
	chessBoardCanvas.grid(row=1,column=2)
	graveyard_layout=load_graveyard_layout_from_file(ind)
	board=chessBoardCanvas.create_image(0,0,anchor=NW,image=images["board_5"])
	deadType=("ordinary","queens","kings")[ind-1]
	root["bg"]=("white","gray","black")[ind-1]
	chessBoardCanvas["bg"]=root["bg"]
	maxindex=len(deadPieces[deadType])-1
	chessPieces=[None]*64

	if ind==2 and len(deadPieces['kings'])==0:
		graveyard_layout[7][7]='x'

	for i,row in enumerate(graveyard_layout):
		for j,square in list(enumerate(row))[::-1]:
			picture_name={'r':"right",'s':"down",'g':"cross",'w':"horizontal_wall",'v':"vertical_wall",'W':"bottom_corner_wall",
			'M':"two_corner_wall",'Y':"Grand Memorial"}.get(square[0])
			if square[0]=='g':
				if (index:=int(square[1:]))<=maxindex:
					content=deadPieces[deadType][index]
					chessPieces[index]=GraveyardObject(f"{'white' if content[0] else 'black'}_{picture_name}_{ind}", (j,i), chessBoardCanvas, content[1:])
				elif ind==1:
					chessPieces[index]=GraveyardObject(f"black_{picture_name}_{ind}", (j,i), chessBoardCanvas)
				else:
					graveyard_layout[i][j]='x'
			elif 'r' in square or 's' in square:
				chessPieces.append(GraveyardObject(picture_name, (j,i), chessBoardCanvas))
			elif picture_name!=None and 'wall' in picture_name:
				chessPieces.append(GraveyardObject(f"{picture_name}_{ind}", (j,i), chessBoardCanvas))
			elif picture_name!=None:

				if ind==2:
					gm_id=0 if maxindex==-1 else 1 if maxindex<4 else 2
				elif ind==3:
					gm_id=1 if maxindex<14 else 2

				if gm_id==0:
					cont=["Trees","Are","Great!"] if len(deadPieces['kings'])==0 else [images["1"]]
					chessPieces[0]=GraveyardObject("Great Tree", (j,i), chessBoardCanvas, cont)
				else:
					index=(ind-2)*2+gm_id
					chessPieces[0]=GraveyardObject(f"{picture_name} {index}", (j,i), chessBoardCanvas, [images[f"Grand Memorial Interaction {index}"]])
	chessPieces=[i for i in chessPieces if i!=None]
	coords=(0,0) if ind==2 else (7,0)
	chessPieces.append(GraveyardObject("black_king", coords, chessBoardCanvas,[],6*ind))
	chessBoardCanvas.bind("<Button-1>",lambda e: select_king(e,ind))
	play_from_music_group("garden")


#ENDINGS
def ending_selector(index,ind):
	current=chessPieces[index]
	current.display_content()
	chessBoardCanvas.unbind("<Button-1>")
	chessBoardCanvas.unbind("<ButtonRelease-1>")
	chessBoardCanvas.unbind("<B1-Motion>")
	if current.image_name=="Great Tree" and len(current.content)==3:
		ending_1(ind)
	elif current.image_name=="Grand Memorial 1" and len(deadPieces["kings"])==0:
		ending_2()
	elif current.image_name=="Grand Memorial 2" and len(deadPieces["kings"])==0:
		ending_3()
	elif current.image_name=="Grand Memorial 3":
		ending_4()
	elif current.image_name=="Grand Memorial 4":
		ending_5()
	else:
		hide_content()
		chessBoardCanvas.bind("<Button-1>",lambda e: select_king(e,ind))
		unpause_music('garden')


#Queen and king alive
def ending_1(ind):
	global TIME,roll_credits_after_move
	TIME=ind*6 if settings["time_effects"] else None

	#Text
	final_words("Cuando éramos jóvenes prometimos...")
	final_words("...que seríamos enterrados juntos.",False)

	#Making the queen and updating the king's position
	king=chessPieces[-1]
	king.position=(3,5)
	king.update_position()
	queen=ChessPiece(-90,(4,5),12,"black_queen",chessBoardCanvas)
	chessBoardCanvas.tag_raise(chessPieces[0].visual)

	#Quitting the text
	graveText.place_forget()
	fake_background.place_forget()
	root.update()
    
	play_from_music_group("queen_fight")

	#Cutscene
	sleep(2)

	def move_piece(piece,x,y,wait=0):
		chessBoardCanvas.move(piece,x,y)
		chessBoardCanvas.tag_raise(chessPieces[0].visual)
		root.update()
		sleep(wait)

	move_piece(king.visual,tile_size,-tile_size,1.8)
	move_piece(queen.visual,0,-tile_size//2,0.2)
	move_piece(queen.visual,0,-tile_size//2)

	for i in range(12):
		move_piece(king.visual,tile_size//4,-tile_size//4,0.1)

	sleep(0.2)
	move_piece(queen.visual,tile_size*3,0,0.3)
	move_piece(king.visual,-tile_size,-tile_size,0.2)
	move_piece(queen.visual,0,-4*tile_size)

	king.position=(6,0)
	king.update_position()

	root.config(cursor="circle")

	roll_credits_after_move=True
	#Final choice
	chessBoardCanvas.bind("<Button-1>",lambda e: select_king(e,ind))

#King alive but queen dead
def ending_2():
	play_from_music_group("dead_queen")
	final_words("...que seríamos enterrados juntos.")
	credits()

#King alive but queen super dead
def ending_3():
	play_from_music_group("dead_queen")
	final_words("...que seríamos enterrados juntos.")
	credits()

#King dead
def ending_4():
	play_from_music_group("dead_king")
	credits()

#King super dead
def ending_5():
	chessPieces[0].content=[images["Grand Memorial Interaction 5"]]
	chessPieces[0].image_name="Grand Memorial 5"
	chessPieces[0].update_position()
	chessPieces[0].display_content()

	graveText.place_forget()
	fake_background.place_forget()
	root.update()

	king=chessPieces[-1]
	king.position=(3,5)
	king.update_position()

	def move_king(x,y,wait=1):
		chessBoardCanvas.move(king.visual,x,y)
		root.update()
		sleep(wait)

	move_king(tile_size,0)
	move_king(tile_size,-tile_size)
	move_king(0,-tile_size)
	for i in range(2):
		move_king(tile_size,-tile_size)
	move_king(0,-tile_size)

	chessBoardCanvas.delete(king.visual)
	root.update()
	sleep(1)
    
	play_from_music_group("dead_king")
    
	credits()

#End credits (defeated countries and more)
#2 - 65; 7 - 90; 12 - 115
def credits(Time=90-5*(7-settings["reading_time"]/1000)):
	#Erasing save data
	open("data/saves/autosave.save","w").close()
    #Making it cinematic
	root.config(cursor="none")
	setup_grave_text("Defeated Countries")
	graveText["font"]=("Times New Roman",font_enormous)
	root.update()

	if len(defeated_countries)==0: defeated_countries.append("None")

	sleep(1.5)

	def show_text(text,wait=0):
		fake_background.delete("all")
		graveText["text"]=text
		graveText.place(relx=0.5,rely=0.5,anchor=CENTER)
		root.update()
		sleep(wait)
	
	def show_image(image,wait=0):
		fake_background.delete("all")
		setup_grave_text('')
		graveText.place_forget()
		fake_background.create_image((fullheight//2,fullwidth//2),image=images[image])
		root.update()
		sleep(wait)

	for country in defeated_countries:
		show_text(country,Time/len(defeated_countries))
	
	show_text("Created by\n\n...",5)
	show_text("Shadow9876",6)
	show_image("Ruins",6)
	show_image("Title",3)
	show_image("Guernica",0.1)
	show_image("Title",2.9)
	show_text("Fine",7)
	main_menu()
	
#----------------------------------------------------
#End of graveyard

#  ----MAIN MENU----
#----------------------------------------------------
#Normal difficulties
def select_difficulty():
	for i in MenuButtons:
		i.grid_forget()
	current_column=1
	for i,label in enumerate(DifficultyTexts):
		FONT=['Calibri',"Times New Roman","Chiller"][i]
		label["font"]=(FONT,font_medium)
		label.grid(row=1,column=current_column,sticky="we")
		current_column+=1
	current_column=1
	for i,button in enumerate(DifficultyButtons):
		if i!=3:
			button.grid(row=2,column=current_column)
			current_column+=1
		if i==3:
			button.grid(row=3,column=1,columnspan=3,sticky="we")

def set_difficulty(name):
	if name=="game":
		for i in difficulties[0]:
			settings[i]=difficulties[0][i]
	elif name=="real life":
		for i in difficulties[1]:
			settings[i]=difficulties[1][i]
	if settings["time_effects"]:
		settings["time_effects"]="black_king_6" in images
	new_game()

#Saves
def save_game_state(save_name="autosave"):
	global game_start
	content=str(settings)
	content+="\n###\n"
	content+=return_map_data()
	content+="\n###\n"
	content+=f"{game_number},{current_opponent},{conquest_points}"
	content+="\n###\n"
	if settings["story_mode"]:
		content+=str(deadPieces)
	else:
		statistics['time']+=time()-game_start
		game_start=time()
		content+=str(statistics)
	content+="\n###\n"
	content+=str(defeated_countries)
	content+="\n###\n"
	for i in range(1,6):
		content+=str(Buttons[i]["state"])+','
	with open(f"data/saves/{save_name}.save","w") as file:
		file.write(content)

def load_save(save_name="autosave"):
	global game_start,statistics,game_number,current_opponent,deadPieces,conquest_points,defeated_countries
	#Reset everything
	reset_everything()
	#Hiding everything
	hide_everything()

	with open(f"data/saves/{save_name}.save","r") as file:
		data=file.read()
    
	data=data.split("\n###\n")
	exec(f"data[0]={data[0]}")
	data[0]={i:data[0][i] for i in data[0] if i not in defaults}
	for i in data[0]:
		settings[i]=data[0][i]
    
	load_map_data(data[1],img)

	game_number,current_opponent,conquest_points=int(data[2].split(",")[0]),data[2].split(",")[1],int(data[2].split(",")[2])

	if settings["story_mode"]:
		exec(f"global deadPieces\ndeadPieces={data[3]}")
	else:
		game_start=time()
		exec(f"global statistics\nstatistics={data[3].replace('inf','np.inf')}")
	exec(f"global defeated_countries\ndefeated_countries={data[4]}")
	for i in range(1,6):
		Buttons[i]["state"]=data[5].split(',')[i-1]
	del(data)
	
	#Start game
	update_map(False)
	
#Tutorial
def start_tutorial():
    global current_opponent
    stop_music()
    hide_everything()
    root.unbind("<Escape>")
    root.config(cursor="none")
    def change_text(text,emperor=False):
        (bg,fg)=('black','white') if emperor else ('white','black')
        font=['Times New Roman','Vivaldi','Onyx','Franklin Gothic Book','Sitka Banner'] if emperor else ['Times New Roman','Arial','Franklin Gothic Book','Verdana']
        setup_grave_text(text,bg,fg)
        font_change(settings["reading_time"]//2,int(font_enormous*5/8),font)
    change_text("¿Le he enseñado ajedrez, su majestad?")
    change_text("No, señor Coronel",True)
    change_text("Lo siento, a menudo olvido lo que enseño a quién")
    change_text("Pero déjame enseñarle, su majestad")
    change_text('La primera lección es...')
    change_text("El alma del ajedrez está en los peones\n\nThe soul of chess lies in the pawns")
    change_text("No comprendo",True)
    change_text("Permítame mostrarle, su majestad\n\nLet me show you, your majesty")
    change_text("¡Capture a mi rey!\n\nCapture my king!")
    hide_everything()
    current_opponent="Coronel"
    change_turns([False,True])
    root.config(cursor="circle")
    for i in difficulties[0]:
        settings[i]=difficulties[0][i]
    initialise_game(1,"tutorial",None,143)

def end_tutorial(winner):
    change_turns([False,True,True,False])
    root.config(cursor="none")
    hide_everything()
    def change_text(text,emperor=False):
        (bg,fg)=('black','white') if emperor else ('white','black')
        font=['Times New Roman','Vivaldi','Onyx','Franklin Gothic Book','Sitka Banner'] if emperor else ['Times New Roman','Arial','Franklin Gothic Book','Verdana']
        setup_grave_text(text,bg,fg)
        font_change(settings["reading_time"]//2,int(font_enormous*5/8),font)
    if winner:
        change_text("No esté triste so majestad, lo hizo bien\n\nDon't be sad your majesty, you did well")
    else:
        change_text("Su majestad, lo hizo muy bien\n\nYou majesty, you did really well")
    change_text("Gracias",True)
    change_text("Pero no pierdámos más nuestro tiempo")
    change_text("Su padre ya nos está esperando")
    main_menu()
    
#Custom difficulty selector
def custom_difficulty():
	hide_everything(True)

	for i in CustomDifficultySliders:
		if type(i)==Label:
			i.configure(font=("Times New Roman",font_medium))
		elif type(i)==list:
			i[0].configure(font=("Times New Roman",font_small))
			if type(i[1])!=customtkinter.CTkSlider:
				i[1].configure(font=("Times New Roman",font_small))
		else:
			i.configure(font=("Times New Roman",font_small))
	ComplementaryLabels[0]["font"]=("Times New Roman",font_small)
	CustomDifficultySliders[-1]["font"]=("Times New Roman",font_medium)
	backToMenu["font"]=("Times New Roman",font_medium)
	del(ComplementaryLabels[2])
	ComplementaryLabels.append(customtkinter.CTkEntry(master=root,placeholder_text=str(settings["engine_depth"])))
	ComplementaryLabels[2]["font"]=("Times New Roman",font_small)

	def select_deselect(condition,obj):
		if condition:
			obj.select()
		else:
			obj.deselect()

	select_deselect(settings["highlight"],CustomDifficultySliders[1][1])
	select_deselect(settings["move_helper"],CustomDifficultySliders[2][1])
	select_deselect(settings["is_white_ai"],CustomDifficultySliders[4][1])
	select_deselect(settings["is_black_ai"],CustomDifficultySliders[5][1])
	select_deselect(settings["permanent_death"],CustomDifficultySliders[7][1])
	select_deselect(settings["time_effects"],CustomDifficultySliders[8][1])
	select_deselect(settings["story_mode"],CustomDifficultySliders[9][1])
	select_deselect(settings["cheats"],CustomDifficultySliders[14][1])
	for i in (1,2,4,5,7,8,9,14):
		switch_event(CustomDifficultySliders[i][1])

	CustomDifficultySliders[13][1].set(settings["engine_depth"])
	ComplementaryLabels[0]["text"]=str(settings["engine_depth"])

	current_row=1
	current_column=1
	for i in CustomDifficultySliders:
		if type(i)==Button:
			i.grid(row=current_row+1,column=current_column,columnspan=2,sticky="we")
		elif type(i)==Label:
			if i["text"]=="Misc":
				current_row=1
				current_column=4
			i.grid(row=current_row,column=current_column,columnspan=2,sticky="wens")
		elif type(i)==list:
			if type(i[1])!=customtkinter.CTkSlider:
				i[0].grid(row=current_row,column=current_column,sticky="wens")
				i[1].grid(row=current_row,column=current_column+1,sticky="wens")
			else:
				if not CustomDifficultySliders[12].get():
					i[0].grid(row=current_row,rowspan=2,column=current_column,sticky="wens")
					ComplementaryLabels[0].grid(row=current_row,column=current_column+1,sticky="wens")
					i[1].grid(row=current_row+1,column=current_column+1,sticky="wens")
					current_row+=1
				else:
					i[0].grid(row=current_row,column=current_column,sticky="wens")
					ComplementaryLabels[2].grid(row=current_row,column=current_column+1,sticky="wens")
		else:
			i.grid(row=current_row,column=current_column,columnspan=2,sticky="wens")
		current_row+=1
	backToMenu.grid(row=current_row+1,column=current_column,columnspan=2,sticky="we")

def load_difficulty_settings(name):
	if name=="Game":
		index=0
	elif name=="Real Life":
		index=1
	else: return
	for i in difficulties[index]:
		settings[i]=difficulties[index][i]
	
	custom_difficulty()

def set_engine_depth(value):
	settings["engine_depth"]=int(value)
	display_relative_difficulty()

def display_relative_difficulty():
	relative_difficulty=1
	if settings["time_effects"] and "black_king_6" not in images:
		settings["time_effects"]=False
		CustomDifficultySliders[8][1].toggle()
		messagebox.showinfo("Information","Time only works if rendered images are loaded in. If you want to enable this feature set Time Effects to True in Settings then restart ShadowChess.")
	for i in settings:
		value={"move_helper":-0.2,"highlight":-0.1,"permanent_death":0.7,"story_mode":0.3,"cheats":-1000,"time_effects":0.1}.get(i,0)
		if settings[i] and value!=0:
			relative_difficulty+=value
	if settings["engine_depth"]<=0: settings["engine_depth"]=1
	if settings["engine_depth"]>150: settings["engine_depth"]=150
	relative_difficulty+={1:-0.7,2:-0.1,3:0.3,4:0.6}.get(settings["engine_depth"],round((min(2**settings["engine_depth"],2800))/28,1))

	if relative_difficulty<2.5 and settings["story_mode"]:
		settings["story_mode"]=False
		relative_difficulty-=0.3
		CustomDifficultySliders[9][1].toggle()
		messagebox.showinfo("Information","You must achieve Real Life Difficulty (2.5) to enable Story Mode. (You must have a score of 2.2 before enabling it as Time has a 0.3 effect on difficulty)")
	if settings["story_mode"] and not (not settings["is_white_ai"] and settings["is_black_ai"]):
		settings["story_mode"]=False
		relative_difficulty-=0.3
		CustomDifficultySliders[9][1].toggle()
		messagebox.showinfo("Information","Story mode can only be accessed while the player plays black and the ai plays white")

	ranks={0.5:"No",0.9:"Baby",1.5:"Game",2.5:"Normal",3.1:"Real Life"}
	rank="Impossible"
	for i in ranks:
		if relative_difficulty<i:
			rank=ranks[i]
			break

	CustomDifficultySliders[11][1]["text"]=f"{rank} Difficulty - {round(relative_difficulty,1)}"

def launch_custom_difficulty():
	if CustomDifficultySliders[12].get() and (current:=ComplementaryLabels[2].get()).isdigit():
		settings["engine_depth"]=int(current)
	if settings["engine_depth"]<=4 or messagebox.askyesno("Warning","Your depth is more than 4. Some encounters might not be winnable. Also you might not get a reply from the engine (as it takes a long time to process an answer at higher depths). Do you wish to proceed?"):
		settings["difficulty"]="Custom"
		set_difficulty("custom")

difficulties=[{"difficulty":"Game","move_helper":True,"highlight":True,"is_black_ai":True,"permanent_death":False,"story_mode":False,
"is_white_ai":False,"cheats":False,"time_effects":False,"engine_depth":3},{"difficulty":"Real Life","highlight":True,"is_black_ai":True,
"permanent_death":True,"story_mode":True,"move_helper":False,"is_white_ai":False,"cheats":False,"time_effects":"black_king_6" in images,
"engine_depth":4}]

custom_descriptions=["A square indicating the selection of a piece","Displays all legal moves with the selected piece",
"Whether black is a player (On) or an ai (Off)","Whether white is a player (On) or an ai (Off)",
"If on player gets sent back to main menu upon losing its king","If off rendered pieces won't be displayed even if they're loaded in",
"Whether there is an underlying story or just a game","How difficult is the game (rank - number)","Engine depth, how far does the engine see","...","With Game and Real Life difficulty options"]

CustomDifficultySliders=[Label(root,text="Moves"),[Label(root,text="Highlight"),customtkinter.CTkSwitch(master=root, text=("Off","On")[settings["highlight"]], onvalue=True, offvalue=False,command=lambda: switch_event(CustomDifficultySliders[1][1]))],
[Label(root,text="Move helper"),customtkinter.CTkSwitch(master=root, text=("Off","On")[settings["move_helper"]], onvalue=True, offvalue=False,command=lambda: switch_event(CustomDifficultySliders[2][1]))],
Label(root,text="Players"),[Label(root,text="White is player"),customtkinter.CTkSwitch(master=root, text=("Off","On")[settings["is_white_ai"]], onvalue=True, offvalue=False,command=lambda: switch_event(CustomDifficultySliders[4][1]))],
[Label(root,text="Black is player"),customtkinter.CTkSwitch(master=root, text=("Off","On")[settings["is_black_ai"]], onvalue=True, offvalue=False,command=lambda: switch_event(CustomDifficultySliders[5][1]))],
Label(root,text="Difficulty"),[Label(root,text="Permanent death"),customtkinter.CTkSwitch(master=root, text=("Off","On")[settings["permanent_death"]], onvalue=True, offvalue=False,command=lambda: switch_event(CustomDifficultySliders[7][1]))],
[Label(root,text="Time"),customtkinter.CTkSwitch(master=root, text=("Off","On")[settings["time_effects"]], onvalue=True, offvalue=False,command=lambda: switch_event(CustomDifficultySliders[8][1]))],
[Label(root,text="Story mode"),customtkinter.CTkSwitch(master=root, text=("Off","On")[settings["story_mode"]], onvalue=True, offvalue=False,command=lambda: switch_event(CustomDifficultySliders[9][1]))],
Label(root,text="Misc"),[Label(root,text="Current difficulty"),Label(root,text="0")],customtkinter.CTkCheckBox(master=root, text="Enable infinite depth", onvalue=True, offvalue=False,command=custom_difficulty),
[Label(root,text="Engine depth"),customtkinter.CTkSlider(master=root,number_of_steps=3, from_=1, to=4,command=lambda val: [slider_event(val,ComplementaryLabels[0]),set_engine_depth(val)])],
[Label(root,text="Cheats"),customtkinter.CTkSwitch(master=root, text=("Off","On")[settings["cheats"]], onvalue=True, offvalue=False,command=lambda: switch_event(CustomDifficultySliders[14][1]))],
[Label(root,text="Load template"),customtkinter.CTkOptionMenu(master=root,values=["-----------","Game", "Real Life"],command=load_difficulty_settings)],Button(root,text="Start",command=launch_custom_difficulty)]

def show_settings():
	for i in MenuButtons:
		i.grid_forget()
	for [label,widget,_] in SettingWidgets:
		label.configure(font=("Times New Roman",font_medium))
		if type(widget)!=customtkinter.CTkSlider:
			widget.configure(font=("Times New Roman",font_small))
	for widget in ComplementaryLabels:
		widget.configure(font=("Times New Roman",font_small))
	resetButton.configure(font=("Times New Roman",font_medium))
	backToMenu.configure(font=("Times New Roman",font_medium))
	
	root.bind("<Escape>",update_settings)
	backToMenu.configure(command=update_settings)

	if settings["time_effects"]:
		SettingWidgets[0][1].select()

	else:
		SettingWidgets[0][1].deselect()
	switch_event(SettingWidgets[0][1])
	if settings["full_screen"]:
		SettingWidgets[1][1].select()
	else:
		SettingWidgets[1][1].deselect()
	switch_event(SettingWidgets[1][1])
	SettingWidgets[2][1].delete(0,1000)
	SettingWidgets[2][1].configure(placeholder_text=str(settings["move_delay"]))
	SettingWidgets[3][1].set(settings["font_size"])
	SettingWidgets[4][1].delete(0,1000)
	SettingWidgets[4][1].configure(placeholder_text=str(settings["drag_frames"]))
	SettingWidgets[5][1].set(settings["reading_time"])
	ComplementaryLabels[0]["text"]=str(settings["font_size"])
	ComplementaryLabels[1]["text"]=str(settings["reading_time"])
	current_row=1
	lIndex=0
	for [label,widget,desc] in SettingWidgets:
		if type(widget)!=customtkinter.CTkSlider:
			label.grid(row=current_row,column=1,sticky="we")
			widget.grid(row=current_row,column=2,sticky="wens")
			current_row+=1
		else:
			label.grid(row=current_row,rowspan=2,column=1,sticky="we")
			ComplementaryLabels[lIndex].grid(row=current_row,column=2,sticky="wens")
			widget.grid(row=current_row+1,column=2,sticky="wens")
			current_row+=2
			lIndex+=1
	resetButton.grid(row=current_row,column=1,columnspan=2,sticky="we")
	backToMenu.grid(row=current_row+1,column=1,columnspan=2,sticky="we")

def changeOnHover(button,image):
	if DifficultyButtons.index(button)==2:
		button.bind("<Enter>",lambda event: [button.config(image=images[image]),DifficultyTexts[2].config(fg="red")])
		button.bind("<Leave>",lambda event: [button.config(image=images[image+" deselect"]),DifficultyTexts[2].config(fg="white")])
	else:
		button.bind("<Enter>",lambda event: button.config(image=images[image]))
		button.bind("<Leave>",lambda event: button.config(image=images[image+" deselect"]))

def fontsize_definitions():
	global font_enormous,font_big,font_medium,font_small
	font_enormous=int(tile_size*3/5) if settings["font_size"]==1 else (int(tile_size*4/5) if settings["font_size"]==2 else tile_size)
	font_big=tile_size//5 if settings["font_size"]==1 else (tile_size//4 if settings["font_size"]==2 else tile_size//3)
	font_medium=tile_size//6 if settings["font_size"]==1 else (tile_size//5 if settings["font_size"]==2 else tile_size//4)
	font_small=tile_size//10 if settings["font_size"]==1 else (tile_size//9 if settings["font_size"]==2 else tile_size//8)

fontsize_definitions()

MenuButtons=[Button(root,text="New Campaign",command=select_difficulty,font=('Algerian',font_big),borderwidth=font_big//5),
Button(root,text="Continue",command=load_save,font=('Algerian',font_big),borderwidth=font_big//5),
Button(root,text="Tutorial",command=start_tutorial,font=('Algerian',font_big),borderwidth=font_big//5),
Button(root,text="Settings",command=show_settings,font=('Algerian',font_big),borderwidth=font_big//5),
Button(root,text="Quit",command=exit,font=('Algerian',font_big),borderwidth=font_big//5)]

DifficultyButtons=[Button(root,image=images["game difficulty deselect"],command=lambda: set_difficulty("game"),borderwidth=0),
Button(root,image=images["real life difficulty deselect"],command=lambda: set_difficulty("real life"),borderwidth=0,bg="gray"),
Button(root,image=images["nightmare difficulty deselect"],borderwidth=0,bg="black"),Button(root,image=images["plus symbol"],borderwidth=font_medium//5,command=custom_difficulty)]

DifficultyTexts=[Label(root,text="Game Difficulty",font=('Calibri',font_medium)),
Label(root,text="Real Life Difficulty",font=('Times New Roman',font_medium),bg="gray"),
Label(root,text="Nightmare Difficulty",font=('Chiller',font_medium),bg="black",fg="white")]

changeOnHover(DifficultyButtons[0],"game difficulty")
changeOnHover(DifficultyButtons[1],"real life difficulty")
changeOnHover(DifficultyButtons[2],"nightmare difficulty")

def slider_event(value,label):
	label["text"]=str(int(value))

def switch_event(widget):
	widget.configure(text=("Off","On")[widget.get()])
	for i in CustomDifficultySliders:
		if type(i)==list and widget in i:
			index=CustomDifficultySliders.index(i)
			text={1:"highlight",2:"move_helper",4:"is_white_ai",5:"is_black_ai",7:"permanent_death",8:"time_effects",9:"story_mode",14:"cheats"}[index]
			settings[text]=widget.get()
			if CustomDifficultySliders[12].get():
				if ComplementaryLabels[2].get().isdigit():
					settings["engine_depth"]=int(ComplementaryLabels[2].get())
				elif ComplementaryLabels[2].cget("placeholder_text").isdigit():
					settings["engine_depth"]=int(ComplementaryLabels[2].cget("placeholder_text"))
			display_relative_difficulty()
			

def update_settings(event=None):
	settings["time_effects"]=SettingWidgets[0][1].get()
	settings["full_screen"]=SettingWidgets[1][1].get()
	if SettingWidgets[2][1].get().isdigit():
		settings["move_delay"]=min(int(SettingWidgets[2][1].get()),1000)
	settings["font_size"]=int(SettingWidgets[3][1].get())
	if SettingWidgets[4][1].get().isdigit():
		settings["drag_frames"]=int(SettingWidgets[4][1].get())
	settings["reading_time"]=int(SettingWidgets[5][1].get())

	with open("data/settings.txt","w") as file:
		ind=0
		for i in defaults:
			content=settings[i] if type(settings[i])!=bool else ("Off","On")[settings[i]]
			endline='\n' if ind!=5 else ''
			file.write(f"{i}={content} #{SettingWidgets[ind][2]}{endline}")
			ind+=1

	fontsize_definitions()
	main_menu()

def reset_settings():
	for i in defaults:
		settings[i]=defaults[i]
	
	show_settings()
	update_settings()
	show_settings()

def show_tip(event,text):
	tipLabel.configure(text=text,font=("tahoma",font_small))
	tipLabel.place(x=event.widget.winfo_rootx()+event.x,y=event.widget.winfo_rooty()+event.y)
	
def hide_tip(event):
	tipLabel.place_forget()

def bind_tip_to_widget(widget,tiptext):
	def make_lambda(func,event,*args):
		return lambda event: func(event,*args)
	widget.bind('<Enter>',make_lambda(show_tip,e,tiptext))
	widget.bind('<Leave>',hide_tip)

ComplementaryLabels=[Label(root,text=str(settings["font_size"])),Label(root,text=str(settings["reading_time"])),customtkinter.CTkEntry(master=root,placeholder_text=settings["engine_depth"])]

SettingWidgets=[[Label(root,text="Time effects"),customtkinter.CTkSwitch(master=root, text=("Off","On")[settings["time_effects"]],onvalue=True, offvalue=False,command=lambda: switch_event(SettingWidgets[0][1])),"Whether images appear as standard chess pieces (off) or rendered ones (on)"],
[Label(root,text="Automatic full screen"),customtkinter.CTkSwitch(master=root, text=("Off","On")[settings["full_screen"]], onvalue=True, offvalue=False,command=lambda: switch_event(SettingWidgets[1][1])),"Starts ShadowChess with fullscreen (but doesn't restrict the use of F11 to restore it to normal size)"],
[Label(root,text="Move delay"),customtkinter.CTkEntry(master=root,placeholder_text=settings["move_delay"]),"How much time should pass after calculating a move (in milliseconds)"],
[Label(root,text="Font size"),customtkinter.CTkSlider(master=root,number_of_steps=2, from_=1, to=3,command=lambda val: slider_event(val,ComplementaryLabels[0])),"Font size: 1 - small, 2 - normal, 3 - big ((any other value amounts to big))"],
[Label(root,text="Drag frames"),customtkinter.CTkEntry(master=root,placeholder_text=settings["drag_frames"]),"After how many frames does drag and drop mechanic start"],
[Label(root,text="Reading time"),customtkinter.CTkSlider(master=root,number_of_steps=10, from_=2000, to=12000,command=lambda val: slider_event(val,ComplementaryLabels[1])),"Time in milliseconds for reading certain texts in the tutorial and late game ((2000<=reading_time<=12000))"]]

for i,widgets in enumerate(SettingWidgets):
	text=SettingWidgets[i][2].split("((")[0]
	bind_tip_to_widget(widgets[0],text)

for j,widget in enumerate([i[0] for i in CustomDifficultySliders if type(i)==list]):
	bind_tip_to_widget(widget,custom_descriptions[j])

resetButton=Button(root,text="Reset settings",command=reset_settings)
tipLabel=Label(root,bg="#ffffd0",relief=SOLID,borderwidth=tile_size//100)

def hide_everything(except_background=False):
	for i in CustomDifficultySliders:
		if type(i)==list:
			i[0].grid_forget()
			i[1].grid_forget()
		else:
			i.grid_forget()
	resetButton.grid_forget()
	tipLabel.place_forget()
	for i in ComplementaryLabels:
		i.grid_forget()
	for i in SettingWidgets:
		i[0].grid_forget()
		i[1].grid_forget()
	backToMenu.grid_forget()
	finalButton.grid_forget()
	bgImage.place_forget()
	for i in frames:
		i.grid_forget()
	for i in MenuButtons:
		i.grid_forget()
	if not except_background:
		BackgroundLabel.place_forget()
	for i in DifficultyButtons:
		i.grid_forget()
	for i in Buttons:
		i.grid_forget()
	chessBoardCanvas.grid_forget()
	promotionCanvas.grid_forget()
	MAP.grid_forget()
	graveText.place_forget()
	fake_background.place_forget()
	#Delete all from canvases
	chessBoardCanvas.delete("all")
	promotionCanvas.delete("all")
	#Unbind all functions
	chessBoardCanvas.unbind("<Button-1>")
	chessBoardCanvas.unbind("<B1-Motion>")
	promotionCanvas.unbind("<Button-1>")
	chessBoardCanvas.unbind("<ButtonRelease-1>")
	for i in DifficultyTexts:
		i.grid_forget()
	if settings["cheats"]:
		for i in CheatButtons:
			i.grid_forget()

def reset_everything():
	global game_number,img,deadPieces,conquest_points,roll_credits_after_move,statistics
	statistics={"games":[0,0],"time":0,"moves":0,"captures":[0,0,0,0,0,0],"pieces_lost":[0,0,0,0,0,0],"promotions":[0,0,0,0,0,0],"fastest":[np.inf,np.inf]}
	roll_credits_after_move=False
	for i in Buttons:
		i["state"]=NORMAL
	img=load_map("data/maps/")
	images["img"]=ImageTk.PhotoImage(img.resize((int(538*(tile_size/75)),int(346*(tile_size/75)))))
	MAP["image"]=images["img"]
	title_indexes["emperors"]=0;title_indexes["empresses"]=0
	titles_and_names["emperor_names"]=['Xefinrac Delictum']

	for i in deadPieces:
		deadPieces[i].clear()
	defeated_countries.clear()
	chessPieces.clear()

	game_number=1
	root["bg"]="gray97"
	conquest_points=0

def main_menu(event=None,first_call=False):
	root.bind("<Escape>",main_menu)
	tracks_playing=0
	for i in music:
		tracks_playing+=mixer.Sound.get_num_channels(music[i])
	if tracks_playing==0:
		play_from_music_group("menu")
	elif mixer.Sound.get_num_channels(music["Siesta"])==0:
		stop_music_with_fadeout(3000)
		root.after(3200,lambda: play_from_music_group("menu"))
	#root.bind("<Control-s>",lambda e:save_game_state())
	root.config(cursor="circle")
	hide_everything(True)
	root["bg"]="white"
	backToMenu.configure(command=main_menu)
	if not first_call:
		ind=random.randint(1,11)
		ind=1 if ind!=11 else 2
		BackgroundLabel['image']=images[f"Title screen {ind}"]
	BackgroundLabel.place(relx=0.5,rely=0.5,anchor=CENTER)
	display_continue=True
	with open("data/saves/autosave.save","r") as file:
		if len(file.read().splitlines())==0:
			display_continue=False
	current_row=1
	for i,button in enumerate(MenuButtons):
		if (display_continue and i!=2) or (not display_continue and i!=1):
			button["font"]=('Algerian',font_big)
			button["borderwidth"]=font_big//5
			button.grid(row=current_row,column=2,sticky="we")
			current_row+=2

def new_game():
	#Game time for statistics
	global game_start
	if not settings["story_mode"]: game_start=time()
	#Reset everything
	reset_everything()
	#Hiding everything
	hide_everything()
	#Start game
	update_map(False)

backToMenu=Button(root,text="Back to Main Menu",command=main_menu)

#----------------------------------------------------
#End of main menu

def quien_quien():
    root.unbind("<Escape>")
    root.config(cursor="none")
    hide_everything()
    stop_music()
    play_from_music_group("who")
    setup_grave_text('')
    with open("images/quien/framerates.txt") as file:
        frames=[i.replace(" ","").replace(":","->").split("->") for i in file.read().splitlines()]
    animate_sequence(frames)
    hide_everything()
    root.bind("<Escape>",main_menu)
    root.config(cursor="circle")
    stop_music()

main_menu(None,True)

root.mainloop()
