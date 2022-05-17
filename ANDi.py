# ANDi.py
#Imports
import argparse
import csv
import sys
import psycopg2 

from diffprivlib.mechanisms import LaplaceBoundedDomain
from diffprivlib.mechanisms import Exponential
from diffprivlib.utils import global_seed

#Parsing arguments
parser = argparse.ArgumentParser(description='ANDi (ANonymisation des Données d\'individus)')
parser.add_argument('database', type=str, help='nom de la base')
parser.add_argument('table', type=str, help='table')
parser.add_argument('user', type=str, help='utilisateur')
parser.add_argument('password', type=str, help='mot de passe')
parser.add_argument('epsilon', type=float, help='Epsilon pour les valeurs numériques')
parser.add_argument('delta', type=float, help='Delta pour les valeurs numériques')
parser.add_argument('sensitivity', type=float, help='Sensibilité pour les valeurs numériques')
parser.add_argument("-n", "--varnum", type=str, help='Fichier contenant la liste des champs numériques à randomiser séparés par des virgules ou des sauts de lignes')
parser.add_argument("-c", "--varcat", type=str, help='Fichier contenant la liste des champs catégoriels à randomiser séparés par des virgules ou des sauts de lignes')
parser.add_argument('-d', "--distance", type=int, help='Distance par défaut pour l\'exponentiel (catégoriel)')
parser.add_argument("-v", "--verbose", action="store_true", help="increase output verbosity")
args = parser.parse_args()

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

if args.varnum is None and args.varcat is None:
	print("Il faut au moins un champ à anonymiser, et aucun fichier de conf n'a été passé")
	sys.exit()
#Dealing with numerical values
if args.varnum is not None:
	#Checking if file exists
	try:
	    fvn = open(args.varnum)
	except IOError:
	    print("fichier valeur numerique introuvable")
	    sys.exit()	
	
	#Getting the varnum list
	Lines = fvn.readlines() 
	vnumlist = []
	for line in Lines: 
		line = line.strip()
		vnumlist = vnumlist + line.split(", ") 
	vnumlbd = {}
	for currvnum in vnumlist:
		#initializing laplace bounded domain
		lbd = LaplaceBoundedDomain()
		lbd.set_epsilon_delta(args.epsilon, args.delta)
		lbd.set_sensitivity(args.sensitivity)
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
		#adding it to the dict
		vnumlbd[currvnum] = lbd
	
#Dealing with category values
if args.varcat is not None:
	if args.distance is None:		
		args.distance = 1; 
#Checking if file exists
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
	for currvcat in vcatlist:
		#initializing exponential mechanism
		cem = Exponential()
		cutil = []
		#find distinct values in columns and generating utility list
		cursor.execute("SELECT DISTINCT "+ currvcat +" FROM " + args.table)
		result = cursor.fetchall()
		for i in result:
			for j in result:	
				if i != j:	
					cutil.append((str(i[0]),str(j[0]),args.distance))
		#adding it to the dict
		cem.set_utility(cutil)
		#Delta must be zero !
		cem.set_epsilon_delta(args.epsilon, 0)
		vcatexpm[currvcat] = cem

#for any line in the database, generating a noisy one
		# Mixing all generators together  
randomgen = {}
if args.varcat is not None: 
	randomgen.update(vcatexpm)
if args.varnum is not None: 
	randomgen.update(vnumlbd)
	#print(randomgen)
cursor.execute("SELECT " + ", ".join(randomgen.keys()) + " FROM " + args.table)
result = cursor.fetchall()

for  record in result:	
		randomthings = ""
		currvals = list(randomgen.values());		
		for idx, val in enumerate(record):
			try:
				randomthings = randomthings + ", " + str(currvals[idx].randomise(float(val)))
			except ValueError:
				randomthings = randomthings[1:] + ", " + currvals[idx].randomise(val)
			except TypeError:
				randomthings = randomthings + ", None" #TODO : check 

		randomthings = randomthings[1:]
		print("INSERT INTO " + args.table + " (" + ", ".join(randomgen.keys()) + ") VALUES ("  + randomthings	+ ");")
			
#closing database connection

cnx.close()

# saying goodbye as a polite person
print("ANDi has finished")

# if args.verbose:    print "the square of {} equals {}".format(args.square, answer) else:    print answer
