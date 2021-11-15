""""
This module receive user wishes from the view module and call
the correct methods in the model.
"""
from src.models import Tournament, Player


class AppController:
    _current_tournament = None

    @classmethod
    def create_tournament(cls, attrs):
        """Create the tournament in database

        Args:
            attrs (dictionnary): attributes collected by the view
        """
        tournament = Tournament(attrs["name"],
                                attrs["location"],
                                attrs["description"],
                                attrs["players"],
                                attrs["game_rules"],
                                attrs["nb_rounds"])
        id = Tournament.set_tournament_id()
        tournament.id = id
        tournament.save()

    @classmethod
    def create_player(cls, attrs):
        """Create a new player in database

        Args:
            attrs (dictionnary): attrs are the attributes collected by the view
        """
        id = Tournament.set_player_id()
        player = Player(firstname=attrs["firstname"],
                        lastname=attrs["lastname"],
                        birth_date=attrs["birth_date"],
                        gender=attrs["gender"],
                        elo=attrs["elo"],
                        id=id)
        player.save()

    @classmethod
    def generate_tour(cls, tournament_id_user_choice):
        """Generate a new round for an ongoing tournament

        Args:
            tournament_id_user_choice (integer): id of the concerned tournament

        Returns:
            list: a list containing all games of the round
        """        """"""
        round = Tournament.generate_round(tournament_id_user_choice)
        return round

    @classmethod
    def set_tour_results(cls, matchs_results, round_id, tournament_id_user_choice,
                         match_id, player_one_score=None, player_two_score=None):
        """[summary]

        Args:
            matchs_results (list): a list of matches
            round_id (integer): the concerned round
            tournament_id_user_choice (integer): the concerned tournament
            match_id (integer): id of a match in the round
            player_one_score (float, optional): resuls of the match refered by match_id. Defaults to None.
            player_two_score (float, optional): resuls of the match refered by match_id. Defaults to None.
        """
        Tournament.enter_results(tournament_id_user_choice, round_id,
                                 match_id, player_one_score,
                                 player_two_score, matchs_results)
        Tournament.save_results(matchs_results, round_id, tournament_id_user_choice)

    @classmethod
    def get_provisional_ranking(cls, tournament_id_user_choice):
        """Used to send the ranking of a tournament

        Args:
            tournament_id_user_choice (integer): id of thre  wished tournament

        Returns:
            list: sorted by tournament_score list for the wished tournament
        """
        players = Tournament.get_players(tournament_id_user_choice)
        return players

    @classmethod
    def get_player_info(cls, player_choice=None):
        """send either informations about every players of the data base

        Args:
            player_choice (integer, optional): id of the wished player

        Returns:
            if player-choice specified:
                list: contains all informations about the player
            else:
                list: list all list where each one is about a player
        """
        if not player_choice:
            players = Tournament.get_all_players()
            return players
        player_info = Tournament.get_player_info(player_choice)
        return player_info

    @classmethod
    def set_player_elo(cls, player, new_elo):
        """Allows the user to update a player's elo

        Args:
            player (integer): id of the player
            new_elo (integer): the new value of elo
        """
        Tournament.change_player_elo(player, new_elo)

    @classmethod
    def get_game_list(cls, tournament_id):
        """Return the games list of the ongoing round for the specified tournament

        Args:
            tournament_id (integer): id of the wished tournament

        Returns:
            list: list of the ongoing round
        """
        return Tournament.get_game_list(tournament_id)

    @classmethod
    def get_report(cls, choice=0,
                   tournament_choice=None,
                   sorting=None,
                   round_choice=None,
                   choosing=None):
        """

        Args:
            choice (int, optional): number of the command. Defaults to 0.
            tournament_choice (integer, optional): id of the wished tournament. Defaults to None.
            sorting (string, optional): choice of sorting, alphabetical or rank. Defaults to None.
            round_choice (integer, optional): id of the wished round. Defaults to None.
            choosing (Boolean, optional): used to delete the list of all possible games when the programm
                                          uploads all tournaments in base. Defaults to None.

        Returns:
            list or dictionnary: depends of the user choice.
                                5 kind of reports are possible:
                                - All players in database sorted alphabetically or by rank
                                - The list of all tournaments in database
                                - The list of player in a tournament sorted alphabetically or by rank
                                - The list of played and ongoing rounds in a tournament
                                - The list of games in a round for a specified tournament
        """
        return Tournament.get_report(choice, tournament_choice, sorting, round_choice, choosing)
