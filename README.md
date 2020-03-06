**ANDi (ANonymisation des Données d'individus)**

*Principe* : Se connecte à une base Postgres, et sur une table choisie par l'utilisateur, y ajoute du bruit et retourne des commandes d'insertion pour populer une nouvelle table qui sera, elle,
anonymisée par le buit. 

*Détails techniques* Fonctionne en appliquant le principe de la [differential privacy](https://fr.wikipedia.org/wiki/Confidentialit%C3%A9_diff%C3%A9rentielle), en ajoutant du [bruit Laplacien](https://en.wikipedia.org/wiki/Differential_privacy#The_Laplace_mechanism) pour les données numériques, 
et du bruit grâce au [mécanisme Exponentiel](https://en.wikipedia.org/wiki/Exponential_mechanism_(differential_privacy))  

Ces 2 méthodes nécessitent de leur donner les paramètres suivants :



*Détails d'implémentation* les listes contenues dans les fichiers dont les noms sont passés en paramètre doivent être au format CSV (Comma Separated Value).

*interface* 

Paramètres : 
- base actuelle + cred
- liste de valeurs numériques à randomiser (table, champ, max, min). 
- liste de valeurs catégorielles à randomiser (table, champ) équiprobabilité
- Epsilon 

Comportement :
- les valeurs qui ne sont pas dans la liste à randomiser sont ignorées
- Pour chaque entrée dans la table 

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
