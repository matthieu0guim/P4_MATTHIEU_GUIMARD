"""
This module is the one communicating with the database.
It is called by the controllers and performs either creation/updates
or return information from the database

The database used here is TinyDB
"""
import itertools
import json

from datetime import datetime
from tinydb import TinyDB, where, Query
from tinydb.operations import increment, add
from copy import deepcopy


class Field:

    def __init__(self, key, value):
        self.key = key
        self.value = value


class Item:
    """ Turns dictionnary keys into attributs"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            # transforme un dictionnaire en objets d'une classe
            setattr(self, key, Field(key, value))

    def __repr__(self):
        return self.to_json()

    def to_json(self):
        item = {}
        for attr in dir(self):
            if isinstance(getattr(self, attr), Field):
                item[attr] = getattr(self, attr).value
        return json.dumps(item)


class Collection:
    """Take a dictionnary in argument and turns items into attributes and corresponding values"""
    def __init__(self, data=None):
        """Initiate Collection with items from a dictionnary

        Args:
            data (dictionnary, optional): [description]. Defaults to None.
        """  
        self._items = []
        for item in data:
            self._items.append(Item(**item))

    @property
    def items(self):
        return self._items


db = TinyDB('db.json')


class Model:
    """Used as a parent class for orther classes that need to write into the database"""
    def __init__(cls):
        pass

    @classmethod
    def create(cls, attrs):
        """Writte data in the database

        Args:
            attrs (dictionnary): will insert the dictionnary at the correct table
        """        
        cls.__table__.insert(attrs)


class Tournament(Model):
    """Contains all methods used in database relations"""
    __table__ = db.table('tournaments')

    def __init__(self):
        super().__init__()

    @classmethod
    def set_tournament_id(cls):
        """Automatically returns the id of a new tournament
        It measures the lengh of the table 'tournaments' in the database
            Return:
                integer: it will be the id of the tournament in the database
        """
        return len(cls.__table__) + 1

    @classmethod
    def set_player_id(cls):
        """Automatically returns the id of a new tournament
        It measures the lengh of the table 'players' in the database
            Return:
                integer: it will be the id of the player in the database
        """
        return len(db.table('players')) + 1

    @classmethod
    def get_players(cls, tournament_id):
        """Store players competing in the wished tournament
        Creates a list composed of Player's objects
        Then it sorts this list according to the tournament_score of each player.
        In case of equality it takes the elo rank.
            
            Args:
                tournament_id (integer): get the dictionnary of the tournament in the table 'tournaments'

            Return:
                list: sorted list of tournament's players
        """
        P = Query()
        tournament = cls.__table__.search(where('id') == tournament_id)

        # on crée notre liste  d'objets players participant au tournoi
        collection = Collection(data=Player.__table__.search(P.id.one_of(tournament[0]["players"])))
        players = sorted(collection.items,
                         key=lambda x: (Tournament.get_tournament_score(
                             x.id.value, tournament_id), x.elo.value),
                         reverse=True)  # on trie cette liste avec l'elo comme critère de trie.

        for player in players:
            setattr(player, 'tournament_score', Tournament.get_tournament_score(
                player.id.value, tournament_id) or 0)
        return players  # on renvoie la liste triée par le score et l'elo des joueurs participants au tournoi.

    @classmethod
    def listing_all_possible_games(cls, tournament_id):
        """Make a list with all possible game configurations
        This is made with itertools combinations methods.
        Then cases as [[P1 vs P2], [P2 vs P1]] are avoided
            
            Args:
                tournament_id: id of the wished tournament
            
            Return:
                list: contains all possible games configurations
        """
        players = [player.id.value for player in Tournament.get_players(tournament_id)]
        setattr(Tournament, 'list_of_possible_games', [
                game for game in itertools.combinations(players, 2)])
        return Tournament.list_of_possible_games

    @classmethod
    def generate_first_round(cls, players, tournament_id, count_rounds, round_id, match):
        all_possible_games = Tournament.listing_all_possible_games(tournament_id)
        cls.__table__.update({"list_of_possible_games": all_possible_games},
                                where("id") == tournament_id)
        top = 0
        bottom = int(len(players)/2)
        while top < len(players)/2:
            player_one_id = players[top].id.value
            player_two_id = players[bottom].id.value
            score_one = 0
            score_two = 0
            player_one_name = players[top].firstname.value
            player_two_name = players[bottom].firstname.value
            game = Match(player_one_id, player_two_id, score_one, score_two,player_one_name, player_two_name, count_rounds)
            match.append(game.to_json())
            Match.create({'joueur1': f"{player_one_name}(id:{players[top].id.value})",
                            'joueur2': f"{player_two_name}(id:{players[bottom].id.value})",
                            'score_one': 0,
                            'score_two': 0,
                            'round_id': round_id,
                            'match_id': len(db.table('matchs')) + 1})
            top += 1
            bottom += 1
        pass

    @classmethod
    def authorized_game(cls, player_one_id,
                             player_two_id,
                             score_one,
                             score_two,
                             count_rounds,
                             match,
                             nb_of_games,
                             ids,
                             round_id,
                             tournament_id):
        player_one_name = Tournament.get_player_info(player_one_id)[0].split()[1]
        player_two_name = Tournament.get_player_info(player_two_id)[0].split()[1]
        game = Match(player_one_id,
                    player_two_id,
                    score_one,
                    score_two,
                    player_one_name,
                    player_two_name,
                    count_rounds
                    )
        match.append(game.to_json())
        nb_of_games += 1
        if len(match) == 4:
            for game in ids:
                Match.create({'joueur1': game[0],
                                'joueur2': game[1],
                                'score_one': 0,
                                'score_two': 0,
                                'round_id': round_id,
                                'match_id': len(db.table('matchs')) + 1})
                id_players = game
                to_remove = db.table('tournaments').search(
                    where("id") == tournament_id)
                to_remove[0]["list_of_possible_games"].remove(id_players)
        return nb_of_games
        
    @classmethod
    def enter_round_in_database(cls,round_id, tournament_id, count_rounds, match ):
        Round.create({
            'round_id': round_id,
            'tournament_id': tournament_id,
            'name': f"Round {count_rounds + 1}",
            'beginning_date': str(datetime.now()),
            "ending_date": ""
        })
        db.table('tournaments').update(increment('nb_of_played_round'),
                                       where("id") == int(tournament_id))
        db.table('rounds').update({"games": match},
                                  (where("tournament_id") == tournament_id)
                                  & (where("round_id") == round_id))
        round = db.table('rounds').get((where("tournament_id") == tournament_id)
                                       & (where("round_id") == round_id))
        rounds = cls.__table__.get(where("id") == tournament_id)["rounds"]
        rounds.append(round_id)
        db.table('tournaments').update({'rounds': rounds},
                                       where("id") == tournament_id)
        return round

    @classmethod
    def generate_round(cls, tournament_id):
        """Generate a round according to the tournament ranking and the if it is the first round or not
        Two cases are presents here:
            - if it is the first round of the tournament, one take the sorted list of players
              and split it into two lists.
              From these two lists each players at the same index of each list
              are confronted.
            - if it is not the first round, one take the sorted list of players.
              The first of the list encounters the second, the third encounters the fourth and so on
              If the generated game has already occured. For exemple the first vs the second.
              The second of the list shall be replaced by the third
              and so on until a configuration is found that
              haven't already been played."""
        nb_of_played_round = db.table('tournaments').get(
            where('id') == tournament_id)['nb_of_played_round']
        nb_rounds = db.table('tournaments').get(
            where('id') == tournament_id)['nb_rounds']
        if nb_of_played_round >= nb_rounds:
            return None
        count_rounds = db.table('tournaments').get(
            where('id') == tournament_id)['nb_of_played_round']
        round_id = len(db.table('rounds')) + 1
        is_first_round = count_rounds == 0
        match = []
        players = Tournament.get_players(tournament_id)
        if is_first_round:
            Tournament.generate_first_round(players, tournament_id, count_rounds, round_id, match)
        else:
            copy_players = deepcopy(players)
            ids = []
            to_reindex = 1 # used to solve the case where the two last player have already encountered.
            while True:
                nb_of_games = 0
                nb_of_players = len(players)
                try:
                    while nb_of_games < nb_of_players/2:
                        authorized_game = False
                        player_one = 0
                        player_two = 1
                        while not authorized_game:
                            player_one_id = copy_players[player_one].id.value
                            player_two_id = copy_players[player_two].id.value
                            score_one, score_two = 0, 0
                            if [player_one_id, player_two_id] in db.table('tournaments').search(
                                    where("id") == tournament_id)[0]["list_of_possible_games"]:
                                authorized_game = True
                                ids.append([player_one_id, player_two_id])
                                copy_players.remove(copy_players[player_two])
                                copy_players.remove(copy_players[player_one])
                            elif [player_two_id, player_one_id] in db.table('tournaments').search(
                                    where("id") == tournament_id)[0]["list_of_possible_games"]:
                                authorized_game = True
                                ids.append([player_two_id, player_one_id])
                                copy_players.remove(copy_players[player_two])
                                copy_players.remove(copy_players[player_one])
                            if not authorized_game:
                                player_two += 1
                                if player_two > 7:
                                    print(f"il ne trouve pas d'adversaire pour le joueur {player_one_id}")
                        nb_of_games = Tournament.authorized_game(player_one_id,
                                                    player_two_id,
                                                    score_one,
                                                    score_two,
                                                    count_rounds,
                                                    match,
                                                    nb_of_games,
                                                    ids,
                                                    round_id,
                                                    tournament_id)
                except IndexError:
                    copy_players = deepcopy(players)
                    to_reindex += 1 # Incremented each time the case is encountered
                    copy_players[-1], copy_players[-to_reindex] = copy_players[-to_reindex], copy_players[-1]
                    match, ids = [], []
                    continue
                if nb_of_games == 4:
                    break
        return Tournament.enter_round_in_database(round_id, tournament_id, count_rounds, match)

    @classmethod
    def get_game_list(cls, tournament_id_user_choice):
        """Returns the list of games for the ongoing round in the wished tournament

        Args:
            tournament_id_user_choice (integer): id of the wished tournament

        Returns:
            list: game's list of the ongoing tournament
            integer: id of the ongoing round
        """        
        
        T = Query()
        chosen_tournament = Collection(cls.__table__.search(
            where('id') == tournament_id_user_choice))

        rounds = Collection(db.table('rounds').search(
            where("tournament_id") == tournament_id_user_choice))
        round_items = rounds.items[chosen_tournament.items[0].nb_of_played_round.value - 1]
        round_id = round_items.round_id.value
        if len(rounds.items) == 0:
            return [], None

        games_list = Collection(db.table('matchs').search(
            T.round_id == rounds.items[len(rounds.items) - 1].round_id.value))
        return games_list, round_id

    @classmethod
    def enter_results(cls,
                      tournament_id,
                      round_id,
                      match_id,
                      player_one_score,
                      player_two_score,
                      matchs_results):
        """Updates the results of a round in the database
        The update is perfomed either
        in the table rounds and the table matchs
        The method is thought so the user can re-enter results
        for a game if previous ones were incorrect.
        The method also check if scores are possible
        as the sum of each player score is expected to be 1

        Args:
            tournament_id (integer): id of the wished tournament in the database
            round_id (integer): id of the ongoing round in the database
            match_id (integer): id of the match in the database
            player_one_score (float): 0, 0.5 or 1
            player_two_score (float): 0, 0.5 or 1
            matchs_results (list): list of the games with the results 
        """

        player_one_id = int(db.table('matchs').search(where("match_id") == int(match_id))[0]["joueur1"][-2])
        player_two_id = int(db.table('matchs').search(where("match_id") == int(match_id))[0]["joueur2"][-2])
        player_one_name = db.table('players').get(where("id") == player_one_id)["firstname"]
        player_two_name = db.table('players').get(where("id") == player_two_id)["firstname"]

        db.table('matchs').update({'score_one': player_one_score},
                                  (where('match_id') == match_id) & (where('round_id') == round_id))
        db.table('matchs').update({'score_two': player_two_score},
                                  (where('match_id') == match_id) & (where('round_id') == round_id))

        if [player_one_id, player_two_id] in db.table('tournaments').search(
                where("id") == tournament_id)[0]["list_of_possible_games"]:
            to_remove = [player_one_id, player_two_id]
            db.table('tournaments').search(
                where("id") == tournament_id)[0]["list_of_possible_games"].remove(to_remove)
            list_of_possible_games = db.table('tournaments').search(
                where("id") == tournament_id)[0]["list_of_possible_games"]
            db.table('tournaments').update({"list_of_possible_games": list_of_possible_games},
                                           where("id") == tournament_id)

        game = Match(player_one_id, player_two_id, player_one_score, player_two_score, player_one_name, player_two_name, match_id)

        if db.table('scores').get((where('tournament_id') == tournament_id) &
                                  (where("player_id") == player_one_id)):
            db.table('scores').update(add("score", player_one_score),
                                      (where('player_id') == player_one_id) &
                                      (where('tournament_id') == tournament_id))
            db.table('scores').update(add("score", player_two_score),
                                      (where('player_id') == player_two_id) &
                                      (where('tournament_id') == tournament_id))
        else:
            Score.create({
                "player_id": player_one_id,
                "tournament_id": tournament_id,
                "score": player_one_score
            })
            Score.create({
                "player_id": player_two_id,
                "tournament_id": tournament_id,
                "score": player_two_score
            })

        already_in = False
        for n, match in enumerate(matchs_results):
            if f"[{player_one_id}" in match:
                matchs_results.pop(n)
                already_in = True
                matchs_results.insert(n, game.to_json())

        if not already_in:
            matchs_results.append(game.to_json())

    @classmethod
    def save_results(cls, matchs_results, round_id, tournament_id_user_choice):
        """Updates a round results in the table 'rounds'
        It also give an ending date to the corresponding round

        Args:
            matchs_results (list): list of the games with the results 
            round_id (integer): id of the round in database
            tournament_id_user_choice (integer): id of the tournament in database
        """
        db.table('rounds').update({"games": matchs_results},
                                  (where("tournament_id") == tournament_id_user_choice) &
                                  (where("round_id") == round_id))
        nb_of_played_round = db.table('tournaments').get(
            where('id') == tournament_id_user_choice)['nb_of_played_round']
        nb_rounds = db.table('tournaments').get(
            where('id') == tournament_id_user_choice)['nb_rounds']
        if nb_of_played_round == int(nb_rounds):
            db.table('tournaments').update({"ending_date": str(datetime.now())})

        db.table('rounds').update({"ending_date": str(datetime.now())},
                                  (where("tournament_id") == tournament_id_user_choice) &
                                  (where("round_id") == round_id))

    @classmethod
    def get_tournament_score(cls, player_id, tournament_id):
        """Calculates the tournament score of a player in a wished tournament
        The method identify all games the player has played in the tournament
        and sums all player's score for each.

        Args:
            player_id (integer): id of the player in database
            tournament_id (integer): id of the concerned tournament in database

        Returns:
            float: score of the player in the wished tournament 
        """        
        """"""
        if not db.table('scores').search(where('tournament_id') == tournament_id):
            return 0

        tournament_score = db.table('scores').get((where('player_id') == player_id) &
                                                  (where('tournament_id') == tournament_id))
        if tournament_score is None:
            return 0
        return tournament_score["score"]

    @classmethod
    def change_player_elo(cls, player_choice, new_elo):
        """Changes the elo of a player in the table 'players'

        Args:
            player_choice (integer): id of the player in database
            new_elo (integer): new value updated in database
        """  
        P = Query()
        db.table('players').update({'elo': new_elo}, P.id == player_choice)

    @classmethod
    def get_player_info(cls, player_choice):
        """Return the corresponding dictionnary of the wished player

        Args:
            player_choice (integer): id of the player in database

        Returns:
            list: list displaying all infos about the player
        """
        player = db.table('players').get(where('id') == player_choice)
        player_display = [f"Prénom: {player['firstname']}",
                          f"Nom: {player['lastname']}",
                          f"Date de naissance: {player['birth_date']}",
                          f"Classement elo: {player['elo']}",
                          f"Sex: {player['gender']}"]
        return player_display

    @classmethod
    def get_all_players(cls):
        """Return a list with all components of the 'players' table
        Returns:
            list: a list with all components of the 'players' table
        """        
        return db.table('players').all()

    @classmethod
    def get_all_tournaments(cls):
        """Return a list with all components of the 'tournaments' table

        Returns:
            list: all components of the 'tournaments' table

        """
        return db.table('tournaments').all()

    @classmethod
    def get_tournament_rounds(cls, tournament_choice):
        """Return a list with all components of the 'rounds' table for a given
        tournament

        Args:
            tournament_choice (integer): tournament id in database

        Returns:
            list: all components of the 'rounds' table for a given
        tournament
        """
        return db.table('rounds').search(where('tournament_id') == tournament_choice)

    @classmethod
    def report_1(cls, sorting, returned_report):
        """generate a report with all players in database

        Args:
            sorting (string): a for alphabetical, c for rank
            returned_report (list): each element is a list with player info
        """        
        if sorting == "a":
                report = sorted(Tournament.get_all_players(), key=lambda x: x["firstname"].lower())
        if sorting == "c":
            report = sorted(Tournament.get_all_players(), key=lambda x: x["elo"], reverse=True)
        for value in report:
            returned_report.append([f"Prénom: {value['firstname']}",
                                    f"Nom: {value['lastname']}",
                                    f"Date de naissance: {value['birth_date']}",
                                    f"Classement elo: {value['elo']}"])
    
    @classmethod
    def report_2(cls, report, returned_report, choosing):
        """generate a report with all tournaments in database 

        Args:
            report (list): intermediate list that will be cleaned
            returned_report (list): will receive clean data
            choosing (boolean): only use in this method as a trigger for cleaning

        Returns:
            list: list with clean data
        """        
        report = Tournament.get_all_tournaments()
        for value in report:
            if choosing:
                try:
                    del value["lists_of_possible_games"]
                except KeyError:
                    pass
                return report
            returned_report.append([f"Nom: {value['name']}",
                                    f"Lieu: {value['location']}",
                                    f"Nombre de tours prévus: {value['nb_rounds']}",
                                    f"Joueurs participants: {value['players']}",
                                    f"id des tours déjà joués: {value['rounds']}",
                                    f"Règles des partie: {value['game_rules']}",
                                    f"Date de début: {value['begin_date']}",
                                    f"Date de fin: {value['ending_date']}"])
        return returned_report
    
    @classmethod
    def report_3(cls, report, returned_report,tournament_choice, sorting):
        """generate a list with all players for a given tournament

        Args:
            report (list): empty list that will be fill with raw data
            returned_report (list): empty list that will be filled with fancy elements
            tournament_choice (integer): id of the wished tournament in database
            sorting (string): a for alphabetical, c for rank
        """        
        if sorting == "a":
                report = sorted(Tournament.get_players(tournament_choice),
                                key=lambda x: x.firstname.value.lower())
        if sorting == "c":
            report = sorted(Tournament.get_players(tournament_choice),
                            key=lambda x: x.elo.value, reverse=True)
        for value in report:
            returned_report.append([f"Prénom: {value.firstname.value}",
                                    f"Nom: {value.lastname.value}",
                                    f"Date de naissance: {value.birth_date.value}",
                                    f"Classement elo: {value.elo.value}",
                                    f"Score dans le tournoi: {value.tournament_score}"])
    
    @classmethod
    def report_4(cls, report, returned_report, tournament_choice):
        """generate a report ith all rounds from a given tournament

        Args:
            report (list): empty list that will be fill with raw data
            returned_report (list): empty list that will be filled with fancy elements
            tournament_choice (integer): id of the wished tournament in database

        Returns:
            list: list with fancy data
        """        
        report = Tournament.get_tournament_rounds(tournament_choice)
        display = deepcopy(report)
        for value in display:
            try:
                del value["round_id"]
                del value["tournament_id"]
            except KeyError:
                pass
            returned_report.append([f"Nom du tour: {value['name']}",
                                    f"Date de début: {value['beginning_date']}",
                                    f"Date de fin: {value['ending_date']}",
                                    f"Parties jouées: {value['games']}"])
        return returned_report

    @classmethod
    def get_report(cls, choice,
                   tournament_choice=None,
                   sorting=None,
                   round_choice=None,
                   choosing=None):
        """will generate a report according to the user choice

        Args:
            choice (integer): number of the wished report
            tournament_choice (integer, optional): id of the wished tournament in database. Defaults to None.
            sorting (string, optional): a for alphabetical, c for rank. Defaults to None.
            round_choice (integer, optional): id of the round in database. Defaults to None.
            choosing (boolean, optional): only used in report 2. Defaults to None.

        Returns:
            list: list filled with data to display
        """                   
                   
        report = []
        returned_report = []
        if choice == 1:
            Tournament.report_1(sorting, returned_report)
        if choice == 2:
            return Tournament.report_2(report, returned_report, choosing)
        if choice == 3:
            Tournament.report_3(report, returned_report, tournament_choice, sorting)
        if choice == 4:
            Tournament.report_4(report, returned_report, tournament_choice)
        if choice == 5:
            first_report = Tournament.get_tournament_rounds(tournament_choice)
            for value in first_report:
                if value["name"] == f"Round {round_choice}":
                    returned_report = value
        return returned_report


class Player(Model):
    __table__ = db.table('players')

    def __init__(self):
        super().__init__()

    def __repr__(self):
        return self.__table__[0]["firstname"]


class Match(Model):
    __table__ = db.table('matchs')

    def __init__(self, player_one_id, player_two_id, score_one=0, score_two=0, player_one_name=None, player_two_name=None, round_id=None):
        super().__init__()
        self.player_one_id = player_one_id
        self.player_two_id = player_two_id
        self.score_one = score_one
        self.score_two = score_two
        self.player_one_name = player_one_name
        self.player_two_name = player_two_name
        self.round_id = round_id

    def __repr__(self):
        return f"{([self.player_one_id, self.player_one_name, self.score_one],[self.player_two_id, self.player_two_name, self.score_two])} \n"

    def to_json(self):
        return json.dumps(([self.player_one_id, self.player_one_name, self.score_one],
                           [self.player_two_id, self.player_two_name, self.score_two]))


class Round(Model):
    __table__ = db.table('rounds')

    def __init__(self, list_of_match, tournament_id=None):
        super().__init__()
        self.tournament_id = tournament_id
        self.list_of_match = list_of_match
        self.begin_date = str(datetime.now())

    def __repr__(self):
        return f"{self.list_of_match}"


class Score(Model):
    __table__ = db.table('scores')

    def __init__(self, player_id, tournament_id, score=None):
        super().__init__()
        self.tournament_id = tournament_id
        self.player_id = player_id
        self.score = score
