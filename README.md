# Outil de gestion de tournois d'échec

## Installation de l'environnement et démarage du programme

### Installation de l'environnement

La totalité des librairies nécessaires pour le bon fonctionnement du programme sont indiqués dans le fichier requirements.txt. La première étape est d'ouvrir l'invite de commande de votre ordinateur et de vous rendre dans le bon dossier. Il faut alors rentrer la ligne de commande suivante:

> pip install -r requirements.txt

### Démarrage du programme

Une fois que les librairies on été installées il faut lancer manuellement le programme. POur cela il faut écrire la ligne de commande qui suit:

> python main.py

Vous arriverez alors sur l'écran du menu principal qui vous sera décrit dans la partie suivante.



## Manuel
Après avoir lancé le programme celui-ci affiche le menu principal. Sur ce menu, huit actions sont possibles, chacun décrite par un numéro et une phrase.
Ainsi vous pouvez: 
    - Créer un nouveau tournoi
    - Générer un nouveau round pôur un tournoi en cours
    - Rentrer les résultats d'un round
    - Consulter des informations sur un tournois ou générer un rapport
    - Rentrer un nouveau joueurs sur votre base de données
    - Consulter les informations d'un joueur en particulier
    - Modifier le classement d'un joueur
    - Consulter le classement d'un tournoi
Pour pouvoir accéder à l'une de ces actions il faut rentrer le numéro correspondant.

### Créer un nouveau tournoi
Pour créer un tournoi il vous faudra rentrer les informations demandées à l'écran:
    - Le nom du tournoi
    - Le lieu où s'organise le tournoi
    - Des commentaires si nécessaire (optionel)
    - Le nombre de tours que comportera le tournoi (le nombre de tours par défaut est de 4)
    - Les joueurs qui participera au tournoi (il vous faut impérativement rentrer les huit joueurs, un nombre insuffisant de joueurs ou un joueur n'existant pas en base provoquera l'annulation de la création du tournoi et vous serez redirigé vers le menu principal)
    - Le type des parties qui seront jouées (bullet, blitz, coup rapide)
Une fois toutes les informations saisies vous serez rediriger vers le menu principal.

### Générer un round pour un tournoi en cours
La deuxième possibilité depuis le menu principal est de générer un round pour un des tournois en cours.
Après avoir rentré le numéro de la commande, le programme vous affichera la liste des tournois qui ne sont pas encore terminés. Il vous faudra alors rentrer l'id du tournoi pour lequel vous voulez générer un round.
Une fois validé,  le programme vous affichera les quatre matchs automatiquement générés. La génération des matchs se base sur une version simplifiée du système suisse. Deux joueurs s'étant déjà rencontré ne pourront pas rejouer l'un contre l'autre.
### Rentrer les résultats d'un round
La troisième action du menu principal est de rentrer les résultats d'un round terminé. Le programme vous affichera alors la liste des tournois qui sont en cours. Comme lors de la génération de round il faudra rentrer l'id du tournoi concerné. Les quatre matchs seront alors affichés avec leur numéro en base de données.

```sh
match-id-1: [player-id-1] vs [player-id-2]
match-id-2: [player-id-1] vs [player-id-2]
match-id-3: [player-id-1] vs [player-id-2]
match-id-4: [player-id-1] vs [player-id-2]
```

Pour pouvoir rentrer le résultat d'un match il faut saisir le numéro de ce match mettre un espace, rentrer le score du premier joueur ( 1 si il a gagné, 0.5 si il y a match nul, 0 si il a perdu), mettre à nouveau un espace et rentrer le score du deuxième joueur. Le programme vérifiera la cohérence des résultats rentrés. Si le résultat saisie ne lui semble pas cohérent un message d'erreur s'affichera vous demendant de resaisir le résultat du match.

```sh
> match-id-1 1 0 # (Ajout)
> match-id-2 0 1 # (Ajout)
> match-id-3 0.5 0.5 # (Ajout)
> match-id-3 1 0 # (Modification car l\'id du match exist déjà.)
> 0
```
Si vous vous êtes trompé lors de la saisie d'un résultat, vous pouvez à nouveau saisir le numéro du match pour rentrer les bonnes valeurs. Le résultat du match sera automatiquement mis à jour dans la base de donnée.

### Consulter un tournoi ou obtenir un rapport
Après acoir choisi la quatrième action un nouveau menu s'affichera pour vous demander l'information qui vous intéresse. Pour choisir il faudra saisir le numéro affiché devant l'action que vous voulez effectuer.

#### La liste des joueurs existants en base de donnée
Avant d'avoir accé à la liste il faudra renseigner si vous voulez que la liste soit classée par ordre alphabétique ou par classement décroissant des joueurs. Saisir la lettre 'a' signifiera que la liste sera triée alphabétiquement. Saisir la lettre 'c' triera la liste par classement des joueurs.

#### Liste des tournois
Le programme affichera la liste des tournois finis et en cours par date de création. Vous pourrez alors voir les informations que le créateur du tournoi avait renseigné. En plus, il sera possible d'avoir le nombre de tours qui ont été joués pendant le tournois, la date de début et la date de fin.

#### Liste des joueurs d'un tournoi en particulier
Comme pour la liste des joueurs en base de donnée,  le programme vous demandera la règle pour trier la liste,  puis vous affichera le nom et le numéro des tournois existant en base de données. Il faudra alors saisir le numéro du tournoi qui vous intéresse. Vous verrez alors la liste des joueurs avec les informations disponibles en base de données

#### Liste des rounds d'un tournoi
Le programme vous demandera de renseigner quel est le tournoi qui vous intéresse en vous présentant la liste des tournois en base de données qu'ils soient finis ou en cours.
Après avoir saisi le numé