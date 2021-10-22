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
        attrs are the attributes collected by the view
        """
        id = Tournament.set_tournament_id()
        attrs["id"] = id
        Tournament.create(attrs)

    @classmethod
    def create_player(cls, attrs):
        """Create a new player in database
        attrs are the attributes collected by the view"""
        id = Tournament.set_player_id()
        attrs["id"] = id
        Player.create(attrs)

    @classmethod
    def generate_tour(cls, tournament_id_user_choice):
        """Generate a new round for an ongoing tournament
        The wished tournament is entered with the attribute tournament_id_user_choice
        """
        round = Tournament.generate_round(tournament_id_user_choice)
        return round

    @classmethod
    def set_tour_results(cls, matchs_results, round_id, tournament_id_user_choice,
                         match_id, player_one_score=None, player_two_score=None):
        """Allowes to register a round result
        matchs_results is a list of matches
        round_id is the concerned round
        tournament_id_user_choice is the concerned tournament
        match_id is the id of a match in the round
        player_one_score/player_two_score are the resuls of the match refered by match_id
        """
        Tournament.enter_results(tournament_id_user_choice, round_id,
                                 match_id, player_one_score,
                                 player_two_score, matchs_results)
        Tournament.save_results(matchs_results, round_id, tournament_id_user_choice)

    @classmethod
    def get_provisional_ranking(cls, tournament_id_user_choice):
        """Used to send the ranking of a tournament
        It returns a sorted by tournament_score list for the wished tournament
        """
        players = Tournament.get_players(tournament_id_user_choice)
        return players

    @classmethod
    def get_player_info(cls, player_choice=None):
        """send either informations about every players of the data base
        If the player_choice is not specified, all players in database are returned
        If the player_choice is specified with its id it only returns the concerned one
         """
        if not player_choice:
            players = Tournament.get_all_players()
            return players
        player_info = Tournament.get_player_info(player_choice)
        return player_info

    @classmethod
    def set_player_elo(cls, player, new_elo):
        """Allows the user to update a player's elo
        It takes the id of the player and the new value as arguments
        """
        Tournament.change_player_elo(player, new_elo)

    @classmethod
    def get_game_list(cls, tournament_id):
        """Return the games list of the ongoing round for the specified tournament"""
        return Tournament.get_game_list(tournament_id)

    @classmethod
    def get_report(cls, choice=0,
                   tournament_choice=None,
                   sorting=None,
                   round_choice=None,
                   choosing=None):
        """Return informations about a required subject
        5 kind of reports are possible:
                - All players in database sorted alphabetically or by rank
                - The list of all tournaments in database
                - The list of player in a tournament sorted alphabetically or by rank
                - The list of played and ongoing rounds in a tournament
                - The list of games in a round for a specified tournament
        """
        return Tournament.get_report(choice, tournament_choice, sorting, round_choice, choosing)
