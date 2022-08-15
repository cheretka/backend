from typing import Dict
from uuid import UUID

from bots_battles.game_engine.game_logic import GameLogic
from .checkers_board import CheckersBoard
from .checkers_player import CheckersPlayer

class CheckersGameLogic(GameLogic):

    def __init__(self, board: CheckersBoard):
        self.board = board
        self.players = None
        self.history_of_moves = []


    def process_input(self, player_uuid: str, message: Dict[str, str], delta: float):

        player = self.players.get(player_uuid, None)
        if player is None:
            return None

        user_move = message['move']

        if self.is_move_possible(user_move):
            self.board = self.board.make_move(user_move)
            return self.board

        return None

    def is_move_possible(self, move):

        possible_moves = self.board.get_possible_moves()

        for pm in possible_moves:
            if pm[0] == move[0] and pm[-1] == move[1]:
                return True

        return False

    def set_players(self, players: Dict[UUID, CheckersPlayer]):
        self.__players = players
