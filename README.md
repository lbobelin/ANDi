*ANDi (ANonymisation des Données d'individus)*

Scenario utilisateur : donner en paramètre l'ancienne base, les paramètres d'anonymisation, evt les paramètres de la nouvelle base, et obtenir des données générées en retour

misc : listes au format CSV
interface : 

Paramètres : 
- base actuelle + cred
- liste de valeurs numériques à randomiser (table, champ, max, min). 
- liste de valeurs catégorielles à randomiser (table, champ) équiprobabilité
- Epsilon 

Comportement :
- les valeurs qui ne sont pas dans la liste à randomiser sont ignorées
- Pour chaque entrée dans la table :	
	- 


Paramètre optionnels : 
- base actuelle + cred
- base nouvelle + cred
- liste généralisation (table, champ)
- champs texte à anonymiser (table, champ)
- liste de valeurs numériques à randomiser (table, champ) -> requête SQL à faire.
- liste de valeurs catégorielles à randomiser (table, champ, clef) -> valeur. Alternative à l'équiprobabilité
- liste de valeurs date (table, champ) à généraliser. 

Inutiles : 
- liste de champs identifiants : liste de champs dont les valeurs seront nulles dans la nouvelle base puisqu'identifiants. Format de la liste : (table, champ). Par défaut formée par la liste des champs qui ne sont pas dans les listes d'anonymisation

https://github.com/IBM/differential-privacy-library 

Installation de DiffPrivLib :
- install python 
- install pip 
	- curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
	- python get-pip.py 
pip install diffprivlib
