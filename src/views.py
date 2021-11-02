"""
    This module interacts with the user and send
    actions informations to the controller
"""
from src.controller import AppController
from datetime import datetime
import pprint


class Views:
    """The class where you find display methods """
    @staticmethod
    def create_tournament_view():
        """Interacts with the user to create a tournament
        First three parameters are optionals
        If nb_rounds is not informed the default value is 4

        ... raises:: If less than 8 players are informed it raises
                    an error and the user is rediricted to main menu
            returns:
             dictionnary : a dictionnary to write in base with all informations about the tournament  
        """
        players = []
        tournament_info = {}
        print("Vous devez renseigner les informations suivantes:")
        print("Nom du tournoi:")
        tournament_info["name"] = input()
        print("Lieu:")
        tournament_info["location"] = input()
        print("Commentaires:")
        tournament_info["description"] = input()
        print("nombre de tours: (4 par défaut)")
        nb_rounds = input()
        if nb_rounds == "":
            nb_rounds = 4
        tournament_info["nb_rounds"] = nb_rounds
        print("Joueurs participant:")
        while True:
            player = int(input())
            players.append(player)
            if len(players) == 8:
                tournament_info["players"] = players
                break
            else:
                pass
        print("Quels types de parties seront jouées?")
        print("bullet, blitz, coup rapide")
        tournament_info["rounds"] = []
        tournament_info["nb_of_played_round"] = 0
        tournament_info["game_rules"] = input()
        tournament_info["begin_date"] = str(datetime.now())
        tournament_info["ending_date"] = ""
        AppController.create_tournament(tournament_info)

    @staticmethod
    def create_player_view():
        """Used to enter a new player in database
        
        First four parameters are optionals.
            Raises: If the elo field is not informed it raises
                    an error and the user is rediricted to main menu"""
        player_info = {}
        print("Vous devez renseigner les informations suivantes:")
        print("Prénom:")
        player_info["firstname"] = input()
        print("Nom")
        player_info["lastname"] = input()
        print("Date de naissance:")
        player_info["birth_date"] = input()
        print("Genre:")
        player_info["gender"] = input()
        print("Classement")
        player_info["elo"] = int(input())
        AppController.create_player(player_info)

    @staticmethod
    def show_generated_round(round):
        """Show generated games for a newly generated round

        Args:
            round (dictionnary): Informations about the wished round in database
        """     
        if round:
            # print(round['games'])
            for game in round['games']:
                print(game)
            return
        print('Pas de round généré.')

    @staticmethod
    def tournament_choice_view(generating_rounds=False):
        """"Used to select a tournament
        The user enter the id of the wanted tournament

        Args:
            generating_rounds (bool, optional): Equal to true if generating a round for an ongoing tournament. Defaults to False.

        Returns:
            integer: the id of the wished tournament
        """
        tournament_list = AppController.get_report(choice=2, choosing=True)
        for tournament in tournament_list:
            if generating_rounds:
                if tournament['ending_date'] == "":
                    print(f"id: {tournament['id']}, name: {tournament['name']}")
            else:
                print(f"id: {tournament['id']}, name: {tournament['name']}")
        print("Quel tournoi cela concerne-t-il?")
        tournament_id_user_choice = input()
        return tournament_id_user_choice

    @staticmethod
    def generate_round_view():
        """Used to generate a round for an onging tournament
        If the tournament is over an error message is printed
        """
        tournament_id_user_choice = int(Views.tournament_choice_view(generating_rounds=True))
        round = AppController.generate_tour(tournament_id_user_choice)
        if round == None:
            print("Le tournoi est terminé. Il n'est plus possible de jouer de tours.")
        elif round == False:
            print("Il y a déjà un round en cours, vous devez d'abord rentrer les résultats avant d'en créer un autre")
        Views.show_generated_round(round)

    @staticmethod
    def get_match_id_view(games_list):
        """This method is called when the user wants to enter a round results
        The game list is printed on screen and the user have to chose
        the id of the game.

        Args:
            games_list (list): the list of round's matchs

        Returns:
            dictionnary: dictionnary with the results of matchs updated      
        """
        if not games_list:
            print("La liste des matchs est vide.")
            return
        print("\n")
        for game in games_list.items:
            print(f"{game.match_id.value}: {game.joueur1.value} vs {game.joueur2.value}")
        match_id_user_choice = input()
        return match_id_user_choice

    @staticmethod
    def get_round_results_view():
        """Used to enter a round results.
        This method prints all the ongoing tournaments.
        The user choose the id of the wanted tournament.
        Then the user choose the id of the match and the result.
        The validity is checked as the sum of each score shall be equal to 1.
        The user ends entering results by typing q or Q.
        """
        tournament_id_user_choice = int(Views.tournament_choice_view(generating_rounds=True))
        games_list, round_id = AppController.get_game_list(tournament_id_user_choice)
        if not games_list:
            print("Pas de matchs trouvé")
            return
        matchs_results = []
        while True:
            match_id_user_choice = Views.get_match_id_view(games_list)
            print("Vous pouvez quitter la saisie des résultats en rentrant 'Q'.")
            if match_id_user_choice.upper() == "Q":
                break
            match_id, player_one_score, player_two_score = list(map(float,
                                                                match_id_user_choice.split(" ")))
            if player_one_score + player_two_score != 1:
                print("Les scores rentrés ne sont pas corrects. Veuillez ressaisir le résultat.")
                continue

            AppController.set_tour_results(matchs_results, round_id, tournament_id_user_choice,
                                           match_id, player_one_score, player_two_score)

    @staticmethod
    def show_provisional_ranking():
        """Used to print a tournament ranking.
        Can be used either for an ongoing tournament or a finished one.
        This method prints all the ongoing tournaments.
        The user choose the id of the wanted tournament.
        """
        tournament_id_user_choice = int(Views.tournament_choice_view(generating_rounds=False))
        players = AppController.get_provisional_ranking(tournament_id_user_choice)
        for n, player in enumerate(players):
            print(f"n°{n + 1}: "
                  f"id: {player.id.value}"
                  f" | Prénom: {player.firstname.value}"
                  f" | score tournoi: {player.tournament_score}"
                  f" | elo: {player.elo.value}")
        input()

    @staticmethod
    def player_choice_view():
        """Used to consult informations about a player
        This method prints all player in database.
        The user must enter the id of the player.
        It must be an integer"""
        players = AppController.get_player_info()
        for player in players:
            print(
                f"{player['id']}: "
                f" {player['firstname']}")
        print("Quel est le joueur qui vous intéresse?")
        player_choice = int(input())
        try:
            if int(player_choice) in [player["id"] for player in players]:
                return int(player_choice)
        except ValueError:
            print("Votre demande ne correspond pas aux joueurs affichés...")

    @staticmethod
    def get_player_info_view():
        """Used to consult informations about a player
        This method calls player_choice_view to print all players in database.
        Then, it calls the controller to print the data"""
        player = Views.player_choice_view()
        pprint.pprint(AppController.get_player_info(player))
        return

    @staticmethod
    def set_new_elo_view():
        """Used to change a player's elo.
        This method calls player_choice_view to print all players in database.
        The user enter an integer as the new value."""
        player = Views.player_choice_view()
        while True:
            print("Quel est le nouvel elo du joueur?")
            new_elo = int(input())
            if new_elo >= 0:
                AppController.set_player_elo(player, new_elo)
                break
            print("La valeur rentrée n'est pas correcte.")

    @staticmethod
    def get_report_view():
        """Used to print a report about database.
        The user enter the integer facing his choice.
        For choice 1 and 3 the user can choose either between alphabetical
        or rank sorting by entering 'a' or 'c'.
        """
        tournament_choice = None
        round_choice = 0
        sorting = None
        print(
            "Quel rapport voulez-vous?:\n"
            "1: La liste des joueurs en base de données?\n"
            "2: La liste des tournois?\n"
            "3: La liste des joueurs d'un tournoi en particulier?\n"
            "4: La liste des rounds d'un tournoi en particulier?\n"
            "5: La liste des matchs d'un round?"
        )
        choice = int(input())
        if choice in {1, 3}:
            while True:
                print("Voulez vous que la liste soit triée par:\n"
                      "-'a': ordre alphabétique \n -'c': classement?")
                sorting = input()
                if sorting not in {"a", "c"}:
                    print("La réponse doit être 'a' ou 'c'")
                if sorting in {"a", "c"}:
                    break
        if choice > 2:
            tournament_choice = int(Views.tournament_choice_view(generating_rounds=False))
        if choice == 5:
            round_list = [round for round in AppController.get_report(4, tournament_choice)]
            for n, round in enumerate(round_list):
                print(f"{n + 1}: {round[0]}")
            print("Saisissez l'id du round qui vous intéresse:")
            round_choice = int(input())

        report = AppController.get_report(choice, tournament_choice, sorting, round_choice)
        if isinstance(report, dict):
            print(f"matchs joués: {report['games']}")
            input()
            return
        for value in report:
            pprint.pprint(value)
            print("\n")
        input()
        return

    @staticmethod
    def main_menue_view():
        """Used in the main.py file to print possible actions for the user.
           Return:
           integer: number of the wished action"""
        print("\nBienvenue dans le menu principal! Que souhaitez-vous faire?"
              "(rentrez le n° de l'action)\n")
        print(
            "1: Créer un tournoi.\n"
            "2: Générer un round pour un tournoi en cours?\n"
            "3: Rentrer les résultats d'un round?\n"
            "4: Consulter des tournois ou obtenir un rapport?\n"
            "5: Rentrer un nouveau joueur en base de donnée?\n"
            "6: Consulter les informations d'un joueurs en particulier?\n"
            "7: Modifier le classement d'un joueur?\n"
            "8: Consulter le classement d'un tournois en cours ou fini?\n"
              )
        user_choice = input()
        return user_choice

    @staticmethod
    def error_message_view():
        """Used to inform the user that his entry is not matching a functionnality."""

        print("\nDésolé mais votre réponse ne décrit pas une action possible.\n"
              "Veuillez essayer de nouveau\n")
