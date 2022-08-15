from __future__ import annotations

from uuid import UUID

import orjson

from bots_battles.game_engine import CommunicationHandler, JSONGame, RealtimeGame
from .checkers_game_config import CheckersGameConfig
from .checkers_game_logic import CheckersGameLogic
from .checkers_player import CheckersPlayer


class CheckersGame(RealtimeGame):

    def __init__(self, game_config: CheckersGameConfig, communication_handler: CommunicationHandler):

        self.board = CheckersBoard()
        super().__init__(AgarntGameLogic(self.board), game_config, communication_handler)

        self._game_logic.set_players(self._players)

        self.__empty_server_timer = 0.0
        self.__no_2_players = True

        # game_type will be also used for storage directory
        info = {'game_type': 'checkers'}
        self.archive_record = JSONGame(info)

    async def run(self):
        delta = 0
        while not self._is_end():
            components_to_update = self._communication_handler.handle_incomming_messages(self._game_logic.process_input, delta)
            delta = await self._clock.tick(self._game_config['fps'])
            await self.update_game_state(components_to_update, round(delta, self.__n_digits))

            if self.__no_2_players:
                self.__empty_server_timer += delta
            else:
                self.__empty_server_timer = 0

            await self.send_ping(delta)

        self.archive_record.dump_to_archive()
        self._cleanup()

    def add_player(self, player_uuid: UUID, player_name: str) -> str:

        match len(self._players):
            case 0:
                self._players[player_uuid] = CheckersPlayer(player_name, player_uuid, 'r')
            case 1:
                self._players[player_uuid] = CheckersPlayer(player_name, player_uuid, 'a')
                self.__no_2_players = False
            case 2:
                # nie dodaje nowego gracza
                pass

        components = set()
        components.add("board")
        components.add("your_move")

        player_state = self.get_state_for_player(components, player_uuid)
        return orjson.dumps(player_state).decode("utf-8")

    def remove_player(self, player_uuid: UUID):
        super().remove_player(player_uuid)
        if len(self._players) < 2:
            self.__no_2_players = True

    def get_state_for_player(self, components_to_update: Set[str], player_uuid: UUID):
        # current_player = self._players[player_uuid]
        state = dict()

        if "board" in components_to_update:
            # state['board'] = [self.board if current_player.color == 'r']
            pass
        if "your_move" in components_to_update:
            pass
        if "your_move" in components_to_update:
            pass

        # if "position" in components_to_update:
        #     state['p'] = {'x': round(current_player.x, self.__n_digits),
        #                   'y': round(current_player.y, self.__n_digits),
        #                   'r': round(current_player.radius, self.__n_digits)}
        #     state['ps'] = [{'n': player.player_name,
        #                     'x': round(player.x, self.__n_digits),
        #                     'y': round(player.y, self.__n_digits),
        #                     'r': round(player.radius, self.__n_digits)}
        #                    for uuid, player in self._players.items()
        #                    if uuid is not player_uuid]
        #     state['d'] = 1 if current_player.is_defeated else 0
        # if "score" in components_to_update:
        #     state['s'] = current_player.score

        return state

    def _is_end(self):
        '''Check if game should end.'''
        return self._is_terminated or self.__empty_server_timer >= self._game_config["waiting_time"]
