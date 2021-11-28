from __future__ import annotations
import asyncio
import logging
import orjson
from typing import Dict
from uuid import UUID

from .agarnt_game_logic import AgarntGameLogic
from .agarnt_game_config import AgarntGameConfig
from .agarnt_player import AgarntPlayer
from .board import Board
from bots_battles.game_engine import RealtimeGame, CommunicationHandler

class AgarntGame(RealtimeGame):
    instance_counter = 0

    def __init__(self, game_config: AgarntGameConfig, communication_handler: CommunicationHandler):
        self.__board = Board(game_config['food_number'], (game_config['board_size'], game_config['board_size']))
        super().__init__(AgarntGameLogic(self.__board), game_config, communication_handler)
        self._game_logic.set_players(self._players)

        AgarntGame.instance_counter = AgarntGame.instance_counter + 1
        self.object_counter = AgarntGame.instance_counter

        logging.info(f'create Agarnt game {self.object_counter}')
        

    def add_player(self, player_uuid: UUID, player_name: str):
        self._players[player_uuid] = AgarntPlayer(player_name, player_uuid)
    
    def get_state_for_player(self, player_uuid: UUID):
        n_digits = 3
        current_player = self._players[player_uuid]
        state = dict()

        state['p'] = {'x': round(current_player.x, n_digits), 'y': round(current_player.y, n_digits), 'r': round(current_player.radius, n_digits)}
        state['ps'] = [{'n': player.player_name, 'x': round(player.x, n_digits), 'y': round(player.y, n_digits), 'r': round(player.radius,n_digits)} for uuid, player in self._players.items() if uuid is not player_uuid]
        state['b'] = self.__board.max_size
        state['f'] = self.__board.foods
        
        return state

    def _is_end(self):
        '''Check if game should end.'''
        return False or self._is_terminated

    def _cleanup(self):
        pass
            