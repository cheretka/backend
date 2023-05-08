from typing import Dict
from uuid import UUID

from bots_battles.game_engine.game_logic import GameLogic
from .checkers_board import CheckersBoard
from .checkers_player import CheckersPlayer


class CheckersGameLogic(GameLogic):

    def __init__(self):
        self.board_state = CheckersBoard()
        print(self.board_state.board)
        print(self.board_state.current_player)
        print(self.board_state.get_possible_moves())
        self.players = None
        self.history_of_moves = []
        self.step_is_taken = False


    def process_input(self, player_uuid: str, message: Dict[str, str], delta: float):

        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++from frontend/bot: ", message)

        player = self.players[player_uuid]
        if player is None:
            return None

        if "move" in message:

            user_move = message['move']

            if player.letter == 'r':
                user_move[0][0] = 7 - user_move[0][0]
                user_move[0][1] = 7 - user_move[0][1]
                user_move[1][0] = 7 - user_move[1][0]
                user_move[1][1] = 7 - user_move[1][1]

            if self.is_move_possible(user_move) != False:
                self.board_state = self.board_state.make_move(self.is_move_possible(user_move))
                print(self.board_state.board)
                print(self.board_state.current_player)
                print(self.board_state.get_possible_moves())
                self.step_is_taken = True
            else:
                self.step_is_taken = False

        return None

    def is_move_possible(self, move):

        possible_moves = self.board_state.get_possible_moves()
        print("possible_moves", possible_moves)

        # return move if move in self.board_state.get_possible_moves() else False

        for pm in possible_moves:
            if pm[0] == move[0] and pm[-1] == move[-1]:
                print("move", move, "corect")
                return pm

        print("move", move, "not corect!!!!!!")
        return False

    def set_players(self, players: Dict[UUID, CheckersPlayer]):
        self.players = players
