# ANDi (ANonymisation des Données d'individus)
## Principe
Se connecte à une base Postgres, et sur une table choisie par l'utilisateur, y ajoute du bruit et retourne des commandes d'insertion pour populer une nouvelle table qui sera, elle,
anonymisée par le buit. 

## Détails techniques
 Fonctionne en appliquant le principe de la [differential privacy](https://fr.wikipedia.org/wiki/Confidentialit%C3%A9_diff%C3%A9rentielle), en ajoutant du [bruit Laplacien](https://en.wikipedia.org/wiki/Differential_privacy#The_Laplace_mechanism) pour les données numériques, 
et du bruit aux données catégorielles grâce au [mécanisme Exponentiel](https://en.wikipedia.org/wiki/Exponential_mechanism_(differential_privacy)). Permet aussi de passer des données brutes sans bruits. L'idée est que l'on donne 
des listes d'attributs (par type : numérique, catégorielle et brute) que l'on veut retrouver dans des commandes INSERT qui sortent sur la sortie standard. Les colonnes présentes dans la base mais qui ne 
sont pas listées sont ignorées. 

## Usage
```
usage: ANDi.py [-h] [-N NULLVALUE] [-n VARNUM] [-c VARCAT] [-i] [-f] [-r RAW] [-d DISTANCE] [-v] database table user password epsilon delta sensitivity

ANDi (ANonymisation des Données d'individus)

positional arguments:
  database              nom de la base
  table                 table
  user                  utilisateur
  password              mot de passe
  epsilon               Epsilon pour les valeurs numériques
  delta                 Delta pour les valeurs numériques
  sensitivity           Sensibilité pour les valeurs numériques

optional arguments:
  -h, --help            show this help message and exit
  -N NULLVALUE, --nullvalue NULLVALUE
                        String pour dénoter null
  -n VARNUM, --varnum VARNUM
                        Fichier contenant la liste des champs numériques à randomiser séparés par des virgules ou des sauts de lignes
  -c VARCAT, --varcat VARCAT
                        Fichier contenant la liste des champs catégoriels à randomiser séparés par des virgules ou des sauts de lignes
  -i, --index           Generates an index that will be the same for two inserts : one with raw values and one with values with noise
  -f, --csv             To generate CSV instead of INSERT - default : INSERT
  -r RAW, --raw RAW     Fichier contenant la liste des champs à transmettre sans modifications séparés par des virgules ou des sauts de lignes
  -d DISTANCE, --distance DISTANCE
                        Distance par défaut pour l'exponentiel (catégoriel)
  -v, --verbose         increase output verbosity

```

## Détails d'implémentation
### Contenus des fichiers de paramètres
Les listes contenues dans les fichiers doivent être au format CSV (Comma Separated Value). Pour chacun des atrtributs on peut personnaliser les valeurs des attributs, suivant leur type :
- numérique : [:0|X:nombre_de_digit_après_la_virgule[:epsilon:delta:sentivity]]) dans un fichier, option -n
- catégorielles champ[:0|1[:distance:epsilon]]

### Exemples
#### Numériques
```
taille, age:0.1:0, poids:0:1:0.1:0.1:0.1 
```
- taille : avec les valeurs epsilon delta et sensitivity données en ligne de commande (ou par défaut si non spécifiées en ligne de commandes)
- age : 0.1/1 probabilité d'être remplacé par NULL, arrondi à l'entier le plus proche
- poids : 0% de chances d'être NULL, Arrrondi au dixième le plus proche, epsilon 0.1, delta 0.1, sentivity 0.1

#### Catégorielles
```
titre, profession:1, code_postal:1:0.1:0.1
```
- titre : avec les valeurs epsilon et delta données en ligne de commande (ou par défaut si non spécifiées en ligne de commandes). les valeurs NULL sont conservées
- profession : idem, mais NULL est une catégorie comme une autre
- code_postal : NULL est une catégorie comme une autre,  epsilon 0.1, delta 0.1 

Nota : toutes les valeurs sont symétriques dans cette implémentatin de la matrice du mécanisme exponentiel.

#### Données non transformées 
```
bmi, fumeur
```
(pas d'options)
# Exemple de ligne de commandes
```
venv/bin/python3.8 ANDi/ANDi.py -n ANDi/varnum.txt -c ANDi/varcat.txt -d 1  adopterrealdata volontaire adopter adopter  0.5 0.1 0.2 > outputscript.sql
```
