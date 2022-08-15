from typing import Dict

from bots_battles.game_engine.game_logic import GameLogic
from .checkers_board import CheckersBoard


class CheckersGameLogic(GameLogic):

    def __init__(self, board: CheckersBoard):
        self.board = board
        self.players = None
        self.history_of_moves = []


    def process_input(self, player_uuid: str, message: Dict[str, str], delta: float):

        components_to_update = set()
        player = self.players.get(player_uuid, None)
        if player is None:
            return components_to_update

        user_move = message['move']

        if self.is_move_possible(user_move):
            #  move is possible
            pass
        else:
            # chosen move isn't possible
            pass

        return components_to_update

    def is_move_possible(self, move):

        possible_moves = self.board.get_possible_moves()

        for pm in possible_moves:
            if pm[0] == move[0] and pm[-1] == move[1]:
                return True

        return False
