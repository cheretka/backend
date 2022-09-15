from __future__ import annotations

import logging
import time
from copy import deepcopy
from uuid import UUID

import orjson

from bots_battles.game_engine import CommunicationHandler, JSONGame, TurnGame
from bots_battles.game_engine.player import Spectator
from .checkers_game_config import CheckersGameConfig
from .checkers_game_logic import CheckersGameLogic
from .checkers_player import CheckersPlayer


class CheckersGame(TurnGame):

    def __init__(self, game_config: CheckersGameConfig,
                 communication_handler: CommunicationHandler):

        super().__init__(CheckersGameLogic(), game_config, communication_handler)

        self._game_logic.set_players(self._players)

        self.__empty_server_timer = 0.0
        self.__no_2_players = True

        # game_type will be also used for storage directory
        info = {'game_type': 'checkers'}
        self.archive_record = JSONGame(info)

    async def run(self):
        logging.info("run()")

        delta = 0
        while not self._is_end():
            time.sleep(0.3)

            self._communication_handler.handle_incomming_messages(
                self._game_logic.process_input, delta)

            delta = await self._clock.tick(self._game_config['fps'])

            if self._game_logic.step_is_taken:
                await self.update_game_state()
                self._game_logic.step_is_taken = False

            if self.__no_2_players:
                self.__empty_server_timer += delta
            else:
                self.__empty_server_timer = 0

            await self.send_ping(delta)

        await self.update_game_state()
        self.archive_record.dump_to_archive()
        self._cleanup()

    def add_player(self, player_uuid: UUID, player_name: str) -> str:

        print("add_player() len:", len(self._players))
        match len(self._players):
            case 0:
                self._players[player_uuid] = CheckersPlayer(player_name, player_uuid, 'r')
                self._game_logic.set_players(self._players)
            case 1:
                self._players[player_uuid] = CheckersPlayer(player_name, player_uuid, 'a')
                self.__no_2_players = False
                self._game_logic.set_players(self._players)
            case 2:
                needless_player_state = dict()
                needless_player_state['game_status'] = "needless"
                return orjson.dumps(needless_player_state).decode("utf-8")

        player_state = self.get_state_for_player(player_uuid)
        self._game_logic.step_is_taken = True
        return orjson.dumps(player_state).decode("utf-8")

    def add_spectator(self, spectator_uuid: UUID, spectator_name: str) -> str:
        self._spectators[spectator_uuid] = Spectator(spectator_uuid, spectator_name)

        spectator_state = self.get_state_for_spectator(None)
        return orjson.dumps(spectator_state).decode("utf-8")

    def remove_player(self, player_uuid: UUID):

        current_player = self._players[player_uuid]
        print("=== remove_player", current_player.letter)
        self._game_logic.board_state.steps_without_hitting[current_player.letter] = -1

        super().remove_player(player_uuid)
        if len(self._players) < 2:
            self.__no_2_players = True

    def get_state_for_player(self, player_uuid: UUID):
        current_player = self._players[player_uuid]
        state = dict()

        if current_player.letter == 'a':
            state['board'] = self._game_logic.board_state.board
            state['last_move'] = self._game_logic.board_state.last_move
        elif current_player.letter == 'r':
            state['board'] = self.turn_over_board(self._game_logic.board_state.board)
            state['last_move'] = self.turn_over_move(self._game_logic.board_state.last_move)

        state['player'] = current_player.letter

        if self._game_logic.board_state.current_player == current_player.letter and not self.__no_2_players:
            state['your_move'] = True
        else:
            state['your_move'] = False

        if self.__no_2_players and self._game_logic.board_state.get_win() == None:
            state['game_status'] = "wait"
        else:
            match self._game_logic.board_state.get_win():
                case 'remis':
                    state['game_status'] = "draw"
                case None:
                    state['game_status'] = "on"
                case 'a':
                    if current_player.letter == 'a':
                        state['game_status'] = "won"
                    else:
                        state['game_status'] = "lost"
                case 'r':
                    if current_player.letter == 'r':
                        state['game_status'] = "won"
                    else:
                        state['game_status'] = "lost"

        print("state ", state)
        return state

    def get_state_for_spectator(self, components_to_update: Set[str]):
        state = dict()
        state['board'] = self._game_logic.board_state.board
        state['last_move'] = self._game_logic.board_state.last_move

        if self.__no_2_players and self._game_logic.board_state.get_win() == None:
            state['game_status'] = "Waiting for players..."
        else:
            match self._game_logic.board_state.get_win():
                case None:
                    if self._game_logic.board_state.current_player == 'r':
                        state['game_status'] = "Red's turn"
                    else:
                        state['game_status'] = "White's turn"
                case 'remis':
                    state['game_status'] = "Game finished as draw!"
                case 'a':
                    state['game_status'] = "White won!"
                case 'r':
                    state['game_status'] = "Red won!"

        return state

    def turn_over_board(self, b):

        board = deepcopy(b)

        board = board[::-1]
        for i in range(len(board)):
            board[i] = board[i][::-1]

        return board

    def turn_over_move(self, last_move):
        move = deepcopy(last_move)

        for i in range(len(move)):
            for j in range(len(move[i])):
                move[i][j] = 7 - move[i][j]

        print("...............move ", last_move, move)
        return move

    def _is_end(self):
        '''Check if game should end.'''
        return self._is_terminated or self.__empty_server_timer >= self._game_config[
            "waiting_time"] or self._game_logic.board_state.get_win() != None

    def _cleanup(self):
        pass

