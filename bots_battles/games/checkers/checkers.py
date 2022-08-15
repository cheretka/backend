from __future__ import annotations

import time
from uuid import UUID
import logging
import orjson

from bots_battles.game_engine import CommunicationHandler, JSONGame, TurnGame
from .checkers_board import CheckersBoard
from .checkers_game_config import CheckersGameConfig
from .checkers_player import CheckersPlayer
from .checkers_game_logic import CheckersGameLogic

class CheckersGame(TurnGame):

    def __init__(self, game_config: CheckersGameConfig, communication_handler: CommunicationHandler):

        self.board_state = CheckersBoard()
        super().__init__(CheckersGameLogic(self.board_state), game_config, communication_handler)

        self._game_logic.set_players(self._players)

        self.__empty_server_timer = 0.0
        self.__no_2_players = True

        # game_type will be also used for storage directory
        info = {'game_type': 'checkers'}
        self.archive_record = JSONGame(info)

    async def run(self):
        logging.info("run()")
        # while self.__no_2_players and not self._is_end():
        #     print("---", len(self._players), " PLAYERS----")
        #     time.sleep(6)
        #
        # logging.info("------------------2 PLAYERS------------------")

        # while not self._is_end():
        #
        #     components_to_update = self._communication_handler.handle_incomming_messages(self._game_logic.process_input, delta)
        #     # delta = await self._clock.tick(self._game_config['fps'])
        #     # await self.update_game_state(components_to_update, round(delta, self.__n_digits))
        #     #
        #     if self.__no_2_players:
        #         print("---",  len(self._players), " PLAYERS----")
        #         time.sleep(6)
        #         # self.__empty_server_timer += delta
        #     else:
        #         print("------------------2 PLAYERS------------------")
        #         # self.__empty_server_timer = 0
        #    # await self.send_ping(delta)

        delta = 0
        while not self._is_end():
            components_to_update = self._communication_handler.handle_incomming_messages(self._game_logic.process_input, delta)
            delta = await self._clock.tick(self._game_config['fps'])
            # print("components_to_update delta")
            # print(components_to_update)
            # print(delta)
            await self.update_game_state(components_to_update)

            if self.__no_2_players:
                self.__empty_server_timer += delta
            else:
                self.__empty_server_timer = 0

            print("---", len(self._players), " PLAYERS----")
            time.sleep(6)

            await self.send_ping(delta)

        self.archive_record.dump_to_archive()
        self._cleanup()

    def add_player(self, player_uuid: UUID, player_name: str) -> str:

        print("add_player() len:", len(self._players))
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
        print("end")
        return orjson.dumps(player_state).decode("utf-8")

    def remove_player(self, player_uuid: UUID):
        super().remove_player(player_uuid)
        if len(self._players) < 2:
            self.__no_2_players = True

    def get_state_for_player(self, components_to_update: Set[str], player_uuid: UUID):
        current_player = self._players[player_uuid]
        state = dict()

        if current_player.letter == 'a':
            state['board'] = self.board_state.board
        elif current_player.letter == 'r':
            state['board'] = self.turn_over_board(self.board_state.board)

        if self.board_state.current_player == current_player.letter:
            state['your_move'] = True
        else:
            state['your_move'] = False

        state['last_move'] = self.board_state.last_move

        if self.board_state.get_win() == None:
            state['game_status'] = "on"
        else:
            state['game_status'] = "off"

        return state

    def turn_over_board(b):

        board = deepcopy(b)

        board =board[::-1]
        for i in range(len(board)):
            board[i] = board[i][::-1]

        return board

    def _is_end(self):
        '''Check if game should end.'''
        return self._is_terminated \
               or self.__empty_server_timer >= self._game_config["waiting_time"]
               # or self.board_state.get_win() != None

    def _cleanup(self):
        pass

    def get_state_for_spectator(self, components_to_update: Set[str]):
        pass
        return None
