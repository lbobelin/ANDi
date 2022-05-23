# ANDi.py
#Imports
import argparse
import csv
import sys
import psycopg2
import random
import time
import sys

from diffprivlib.mechanisms import LaplaceBoundedDomain
from diffprivlib.mechanisms import Exponential
from diffprivlib.utils import global_seed

#Extending lbd to include format information
class LaplaceBoundedDomainWithFormat(LaplaceBoundedDomain):
	def __init__(self, numberOfDigits, noneprobability):
		self.numberOfDigits = numberOfDigits
		self.noneprobability = noneprobability
		super().__init__()
	def setLowerAndUpper(self, mylower , myupper):
		self.mylower = mylower
		self.myupper = myupper

# Raw structure
class RawValue:
	def randomise(self, val):
		return val
	noneprobability = 0
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

#Starting and logging time

t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
eprint("Program started at ", current_time)
pstart = time.perf_counter()

#Parsing arguments
parser = argparse.ArgumentParser(description='ANDi (ANonymisation des Données d\'individus)')
parser.add_argument('database', type=str, help='nom de la base')
parser.add_argument('table', type=str, help='table')
parser.add_argument('user', type=str, help='utilisateur')
parser.add_argument('password', type=str, help='mot de passe')
parser.add_argument('epsilon', type=float, help='Epsilon pour les valeurs numériques')
parser.add_argument('delta', type=float, help='Delta pour les valeurs numériques')
parser.add_argument('sensitivity', type=float, help='Sensibilité pour les valeurs numériques')
parser.add_argument("-N", "--nullvalue", type=str, help='String pour dénoter null')
parser.add_argument("-n", "--varnum", type=str, help='Fichier contenant la liste des champs numériques à randomiser séparés par des virgules ou des sauts de lignes')
parser.add_argument("-c", "--varcat", type=str, help='Fichier contenant la liste des champs catégoriels à randomiser séparés par des virgules ou des sauts de lignes')
parser.add_argument("-i", "--index", action="store_true", help="Generates an index that will be the same for two inserts : one with raw values and one with values with noise")
parser.add_argument("-f", "--csv", action="store_true", help="To generate CSV")
parser.add_argument("-r", "--raw", type=str, help='Fichier contenant la liste des champs à transmettre sans modifications séparés par des virgules ou des sauts de lignes')
parser.add_argument('-d', "--distance", type=int, help='Distance par défaut pour l\'exponentiel (catégoriel)')
parser.add_argument("-v", "--verbose", action="store_true", help="increase output verbosity")
args = parser.parse_args()
parsetime = time.perf_counter()
eprint(f"Parsed command line input {parsetime - pstart:0.4f} seconds")

#connect to database and exit if fails
try:
  cnx = psycopg2.connect(user=args.user, password=args.password,
                              host='localhost',
                              database=args.database)
  cursor= cnx.cursor()
except Exception as error:
	print("Something went wrong while connecting to database, error : ", error)
	print("Error type:", type(error))
	sys.exit()

connectime = time.perf_counter()
eprint(f"Connected to database in {connectime - parsetime:0.4f} seconds")

nullvalue="NULL"
if args.nullvalue is not None:
	nullvalue = args.nullvalue

if args.varnum is None and args.varcat is None:
	print("Il faut au moins un champ à anonymiser, et aucun fichier de conf n'a été passé")
	sys.exit()
#Dealing with numerical values
if args.varnum is not None:
	#Checking if file exists
	try:
	    fvn = open(args.varnum)
	except IOError:
	    print("fichier valeur numerique introuvable mais requis")
	    sys.exit()

	#Getting the varnum list
	Lines = fvn.readlines()
	vnumlist = []
	for line in Lines:
		line = line.strip()
		vnumlist = vnumlist + line.split(", ")
	vnumlbd = {}
	for currvnumopt in vnumlist:
		#Parsing value
		vnopt = currvnumopt.split(":")
		currvnum = vnopt[0]
		# Initializing to default values
		curround =2
		currepsilon = args.epsilon
		currdelta = args.delta
		currsensitivity = args.sensitivity
		currnoneprobability = 0
		## None or not, digit après la virgule, ... Si spécifié des options
		if (len(vnopt) != 1 and len(vnopt) != 3 and len(vnopt) != 6):
			print("Invalid number of options passed for vnum :", vnopt)
			sys.exit()
		if (len(vnopt)>1):
			currnoneprobability = float(vnopt[1])
			curround = int(vnopt[2])
		if (len(vnopt) > 3):
			currepsilon = float(vnopt[3])
			currdelta = float(vnopt[4])
			currsensitivity = float(vnopt[5])
		#initializing laplace bounded domain
		lbd = LaplaceBoundedDomainWithFormat(curround, currnoneprobability)
		lbd.set_epsilon_delta(currepsilon, currdelta)
		lbd.set_sensitivity(currsensitivity)
		#find max and min
		cursor.execute("SELECT MIN("+ currvnum +") AS maximum FROM " + args.table)
		result = cursor.fetchall()
		for  i in result:
			lower = float(i[0])
		cursor.execute("SELECT MAX("+ currvnum +") AS minimum FROM " + args.table)
		result = cursor.fetchall()
		for  i in result:
			upper = float(i[0])
		#initialising domain bounds
		lbd.set_bounds(lower, upper)
		lbd.setLowerAndUpper(lower, upper)
		#adding it to the dict
		vnumlbd[currvnum] = lbd

vnumtime = time.perf_counter()
eprint(f"Prepared var num objects in  {vnumtime - connectime:0.4f} seconds")
#Dealing with category values
if args.varcat is not None:
	if args.distance is None:
		args.distance = 1;
#Checking if varcat file exists
	try:
	    fvc = open(args.varcat)
	except IOError:
	    print("fichier valeur categorie introuvable")
	    sys.exit()

	#Getting the varcat list
	Lines = fvc.readlines()
	vcatlist = []
	for line in Lines:
		line = line.strip()
		vcatlist = vcatlist + line.split(", ")

	vcatexpm = {}
	for currvcatopt in vcatlist:
		vcatopt = currvcatopt.split(":")
		currvcat = vcatopt[0]
		currnoneval = 0
		currdistance = args.distance
		currepsilon = args.epsilon
		if (len(vcatopt) !=1 and len(vcatopt) !=2 and len(vcatopt) !=4):
			print("Invalid number of options passed for vnum :", vcatopt)
			sys.exit()
		if (len(vcatopt)>1):
			currnoneval = float(vcatopt[1])
		if (len(vcatopt) > 2):
			currdistance = float(vcatopt[2])
			currepsilon =  float(vcatopt[3])
		#initializing exponential mechanism
		cem = Exponential()
		cutil = []
		#find distinct values in columns and generating utility list
		cursor.execute("SELECT DISTINCT "+ currvcat +" FROM " + args.table)
		result = cursor.fetchall()
		strlist = [i[0] for i in result]
		try:
			idxNull = strlist.index(None)
			del result[idxNull]
		except ValueError:
			#Does nothing
			pass
		if (currnoneval):
			result.append((nullvalue, ))
		for i in result:
			for j in result:
				if str(i[0]) != str(j[0]):
					cutil.append((str(i[0]),str(j[0]),currdistance))
		#adding it to the dict
		cem.set_utility(cutil)
		#Delta must be zero !
		cem.set_epsilon_delta(currepsilon, 0)
		vcatexpm[currvcat] = cem
vcattime = time.perf_counter()
eprint(f"Prepared var cat objects in  {vcattime - vnumtime:0.4f} seconds")
# Dealing with raw values
if args.raw is not None:
	#Checking if file exists
	try:
	    fvr = open(args.raw)
	except IOError:
	    print("fichier valeur brutes introuvable")
	    sys.exit()

	#Getting the varnum list
	Lines = fvr.readlines()
	rawlist = []
	for line in Lines:
		line = line.strip()
		rawlist = rawlist + line.split(", ")
	rawgen = RawValue()
	vrawgen = {}
	for currraw in rawlist:
		vrawgen[currraw] = rawgen

#for any line in the database, generating a noisy one
		# Mixing all generators together
randomgen = {}
if args.varcat is not None:
	randomgen.update(vcatexpm)
if args.varnum is not None:
	randomgen.update(vnumlbd)
if args.raw is not None:
	randomgen.update(vrawgen)

	#print(randomgen)
cursor.execute("SELECT " + ", ".join(randomgen.keys()) + " FROM " + args.table)
result = cursor.fetchall()
for  ridx, record in enumerate(result):
		randomthings = ""
		currvals = list(randomgen.values());

		for idx, val in enumerate(record):
			try:
				currand = random.random()
				if (currvals[idx].noneprobability < currand):
					randomthings = randomthings + ", " + str(round(currvals[idx].randomise(float(val)),currvals[idx].numberOfDigits))
				else:
					randomthings = randomthings + ", " + nullvalue + " "
			except (ValueError, AttributeError) as e :
				# Works because first eval is made on randomise so you don't have to check for numberOfdigits existence
				if val is None or val == "None":
					val = nullvalue
				try:
					randomthings = randomthings + ", " + currvals[idx].randomise(str(val))
				except ValueError:
					#Happens when I don't consider nullvalue as part of the domain, so it fails, and I should go to keep the nullvalue
					randomthings = randomthings + ", " + nullvalue
			except TypeError:
				# Should be random between lower and upper with uniform
				try:
					randomthings = randomthings + ", " + str(round(random.uniform(currvals[idx].mylower,currvals[idx].myupper),
					currvals[idx].numberOfDigits))
				except AttributeError:
					if val is None or val == "None":
						randomthings = randomthings + ", " + nullvalue + " "
					else:
						randomthings = randomthings + ", " + val
		randomthings = randomthings[1:]
		if (not args.csv):
			if (args.index):
				record_string = []
				for rec in record:
					if rec is None or rec == "None":
						record_string.append(nullvalue)
					else:
						record_string.append(str(rec))
				print("INSERT INTO " + args.table + " (AIDX, " + ", ".join(randomgen.keys()) + ") VALUES (" + str(ridx) + ", " + ",".join(record_string)+ ");")
				print("INSERT INTO " + args.table + " (AIDX, " + ", ".join(randomgen.keys()) + ") VALUES (" + str(ridx) + ", "+ randomthings[1:] + ");")
			else:
				print("INSERT INTO " + args.table + " (" + ", ".join(randomgen.keys()) + ") VALUES ("  + randomthings[1:]	+ ");")
		else:
			if (args.index):
				record_string = []
				for rec in record:
					if rec is None or rec == "None":
						record_string.append(nullvalue)
					else:
						record_string.append(str(rec))
				if ridx == 0:
					print("AIDX, " + ", ".join(randomgen.keys()))
				print(str(ridx) + ", " +  ",".join(record_string))
				print(str(ridx) + ", " + randomthings[1:])
			else:
				if ridx == 0:
					print(", ".join(randomgen.keys()))
				print(randomthings[1:])

#closing database connection
vrandomtime = time.perf_counter()
eprint(f"Prepared random values in  {vrandomtime - vcattime:0.4f} seconds")
cnx.close()

# saying goodbye as a polite person
current_time = time.strftime("%H:%M:%S", t)
eprint("ANDi has finished @ ", current_time)
eprint(f"Total time elapsed: {vrandomtime - pstart:0.4f} seconds")
