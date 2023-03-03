from PIL import Image,ImageDraw
import random
#Annexing a country
def annex_country(winner,loser,img):
	winner,loser=countries[winner],countries[loser]
	#Adjusting the map
	colour=winner.colour+(255,)

	for (x,y) in loser.provinces:
		ImageDraw.floodfill(img,(x,y),colour)
	
	#Adjusting winner's strength
	winner.strength*=random.randrange(85,95)/100
	winner.strength+=round(loser.strength*random.randrange(6,9)/10,1)
	#Updating neighbours
	winner.neighbours+=loser.neighbours
	winner.neighbours=list(set([i for i in winner.neighbours if i!=winner.tag and i!=loser.tag]))
	for tag in countries:
		if loser.tag in countries[tag].neighbours:
			countries[tag].neighbours=[i if i!=loser.tag else winner.tag for i in countries[tag].neighbours]
	#Updating provinces of the winner
	winner.provinces+=loser.provinces
	#Removing the loser from countries
	del(countries[loser.tag])

class Country:
	#Attributes of a country
	def __init__(self,tag,name,colour,neighbours):
		self.tag=tag #3 letter tag (MAD,ENG,FRA, ...)
		self.name=name.replace("_"," ") #Name of said country (Republic of Portugal)
		self.colour=tuple(map(int,colour.split("_"))) #What colour does said country represent on the map
		try:
			self.provinces=provinces[self.colour] #What provinces does said country own (x,y) of provinces
			self.size=len(self.provinces) #Number of owned provinces
			self.region=get_region(regions,self.provinces[0]) #Which region is this country in
			self.subregion=get_region(subregions,self.provinces[0]) #Which subregion -||-
		except:
			self.provinces=[]
			self.size=0
			self.region=list(regions.keys())[0]
			self.subregion=list(subregions.keys())[0]
		self.strength=round(self.size*random.randrange(5,20)/10,1) #A random number to simulate this country's strength (army size)
		self.neighbours=neighbours.split("_") #Which countries does this country neighbour - a list of tags (string)

	#Try annexing a country that is the caller's neighbour but also in the same (sub)region
	def try_expand(self,img,in_subregion=True):
		neighbours_in_scope=[]
		countries_in_region=countries_from_region(self.subregion if in_subregion else self.region,in_subregion)
		for i in self.neighbours:
			for j in countries_in_region:
				if i==j.tag:
					neighbours_in_scope.append(j) #neighbours_in_scope is a list of Country objects
		if len(neighbours_in_scope)==0: return False #If there are none to satisfy both criteria return
		target=random.choice(neighbours_in_scope) #Select a target randomly
			
		winner,loser=self,target
		st1,st2=self.strength*random.randrange(8,12)/10,target.strength*random.randrange(4,16)/10
		if st1<st2: winner,loser=target,self #If the target is stonger the caller will be eliminated
		
		#Winner annexes loser
		annex_country(winner.tag,loser.tag,img)

		return True

#Get a dictionary of all colours and provinces in said format: {colour:[province1, province2, ...], ...}
#colour - (r, g, b, a); province - (x, y)
def get_colour_provinces_pair(path):
	img=Image.open(path)
	pixels=img.load() #Pixels of the image
	dic={}
	for x in range(img.width):
		for y in range(img.height):
			#If this pixel is not black (if we haven't touched it yet)
			if pixels[x,y]!=(0,0,0,255):
				#If this colour is not in the dictionary we update it
				if pixels[x,y][:3] not in dic: dic[pixels[x,y][:3]]=[(x,y)]
				#If this colour was already in the dictionary we expand its list with the province's coordinates
				else: dic[pixels[x,y][:3]].append((x,y))
				#We floodfill the area with black to signal that we are done with this
				ImageDraw.floodfill(img,(x,y),(0,0,0,255))
	return dic

#Get (sub)region's colour based on the province's coordinate
def get_region(regions,province):
	for i in regions:
		for j in regions[i]:
			if j==province:
				return i

#Return list of all countries in a (sub)region
def countries_from_region(region,in_subregion=True):
	countries_in_region=[]
	for tag in countries:
		if (in_subregion and countries[tag].subregion==region) or (not in_subregion and countries[tag].region==region):
			countries_in_region.append(countries[tag])
	return countries_in_region

#Try to annex a random country from a (sub)region
def expand_random_from_region(region,img,in_subregion=True):
	countries_in_region=countries_from_region(region,in_subregion)
	random.choice(countries_in_region).try_expand(img,in_subregion)

#(Re)loading all variables associated with the map
def load_map(PATH):
	global provinces,regions,subregions,countries
	provinces=get_colour_provinces_pair(PATH+'map.png')
	regions=get_colour_provinces_pair(PATH+'regions.png')
	subregions=get_colour_provinces_pair(PATH+'subregions.png')

	#countries is a list of Country objects
	with open(PATH+"countries.txt") as file:
		countries={i.split()[0]:Country(*i.split()) for i in file.read().splitlines()}

	#the return value is the Image object of the map
	return Image.open(PATH+"map.png")

def modify_countries(tag,attribute_name,value):
	if attribute_name=="name":
		countries[tag].name=value

def return_countries():
	return countries

def return_map_data():
	output=""
	for i in countries:
		country=countries[i]
		output+=f"'{country.tag}','{country.name}',{country.colour},{country.provinces},{country.size},{country.region},{country.subregion},{country.strength},{country.neighbours}\n"
	return output

def load_map_data(data,img):
	global countries
	touched_tags=[]
	data=data.split("\n") if type(data)!=list else data
	for row in data:
		tag=row[1:4]
		if tag in countries:
			touched_tags.append(tag)
			command=f"countries['{tag}'].tag,countries['{tag}'].name,countries['{tag}'].colour,countries['{tag}'].provinces,countries['{tag}'].size,countries['{tag}'].region,countries['{tag}'].subregion,countries['{tag}'].strength,countries['{tag}'].neighbours={row}"
			exec(command)
	countries={i:countries[i] for i in countries if i in touched_tags}
	for tag in countries:
		for (x,y) in countries[tag].provinces:
			ImageDraw.floodfill(img,(x,y),countries[tag].colour+(255,))
	
