from __future__ import annotations

import asyncio
import logging
import orjson
from typing import List, Dict
from uuid import UUID
from websockets.legacy.client import WebSocketClientProtocol
from websockets.legacy.protocol import broadcast

from bots_battles.game_engine import game

from .game_client import GameClient
from ..game_engine import CommunicationHandler
from ..game_factory import GameFactory
from .. import Game, GameConfig


class Session:
    '''
    Define Session class, which handles one game instance and manage all it's players.
    Each session instance has a CommunicationHandler object which will be
    shared between all players.
    '''

    def __init__(self, game_factory: GameFactory, session_id: str):
        self.__session_id = session_id
        self.__players: Dict[UUID, GameClient] = dict()
        self.__game: Game = None
        self.__game_type =  ""
        self.__game_name = ""
        self.__game_factory = game_factory
        self.__communication_handler = CommunicationHandler(self.send_to)

        logging.info("Session created!")

    async def broadcast(self, msg: str):
        '''
        Async method which will send given message to all connected players (websockets).

        Parameters:
        msg: Message to send.
        '''

        # logging.info(msg)
        for w in self.__players:
            await w.send(msg)

    async def send_to(self, uuid: UUID, msg: str):
        '''
        Async method which will send given message to selected (by player_uuid argument) connected player or spectator (websocket).

        Parameters:
        uuid: UUID which will be used to select proper player or spectator.
        msg: Message to send.
        '''

        # logging.info(msg)
        try:
            await self.__players[uuid].send(msg)
            msg_dict = orjson.loads(msg)
            if 'd' in msg_dict and msg_dict['d'] == 1:
                print("---msg_dict ", msg_dict)
                self.__game.remove_player(uuid)
                client = self.__players.pop(uuid, None)
                if client is not None:
                    await client.terminate()
                logging.info('client disconnected via being defeated')
        except:
            print("--- except")
            self.__game.remove_player(uuid)
            self.__game.remove_spectator(uuid)
            self.__players.pop(uuid, None)
            logging.info('client disconnected')

    async def create_player(self, websocket: WebSocketClientProtocol, player_name: str):
        '''Async method to create player and add them to game
        Parameters:
        websocket - player websocket
        '''
        print("======= create_player()")
        game_client = GameClient(websocket, self.__communication_handler)
        self.__players[websocket.id] = game_client

        init_state = self.__game.add_player(websocket.id, player_name)
        await self.send_to(websocket.id, init_state)

        try:
            await game_client.handle_messages()
        except:
            print("--- except await game_client.handle_messages()")
            self.__game.remove_player(websocket.id)
            self.__players.pop(websocket.id, None)
            logging.info('client disconnected')

    async def create_spectator(self, websocket: WebSocketClientProtocol, spectator_name: str):
        '''Async method to create spectator and add them to game
        Parameters:
        websocket - spectator websocket
        '''

        game_client = GameClient(websocket, self.__communication_handler)
        self.__players[websocket.id] = game_client

        init_state = self.__game.add_spectator(websocket.id, spectator_name)
        await self.send_to(websocket.id, init_state)

        try:
            await game_client.handle_messages()
        except:
            self.__game.remove_spectator(websocket.id)
            self.__players.pop(websocket.id, None)
            logging.info('spectator disconnected')

    async def create_and_run_game(self, game_type: str, game_name: str, game_config: GameConfig):
        '''Async method to create game instance.
        If game exists in session instance, runtime execption will be raised
        Parameters:
        game_type - define game type to be created
        game_config - game config
        '''

        if self.__game != None:
            raise RuntimeError('Game in this session already exists!')

        self.__game_type = game_type
        self.__game_name = game_name
        self.__game = self.__game_factory.create_game(game_type, self.__communication_handler, game_config)

        logging.info(f"create new game in session {self.session_id},\n game type {game_type}")

        await asyncio.create_task(self.__game.run())

    async def terminate_game(self):
        '''Async method to terminate existing game.
        If game not exists in session instance, runtime execption will be raised
        '''

        if self.__game == None:
            raise RuntimeError(f'Game in this session (id={self.session_id}) do not exists!')

        logging.info(f'game in session {self.session_id} terminated')
        self.__game.terminate()
        self.__game = None
        self.__game_type = ""

    async def clear(self):
        '''Clears connections with clients'''
        [await player.terminate() for player in self.__players.values()]

    def is_full(self):
        if self.__game == None:
            raise RuntimeError(f'Game in this session (id={self.session_id}) do not exists!')
        return self.__game.is_full()

    def check_player_name_exists(self, name:str):
        return name in self.__game.player_names

    @property
    def session_id(self):
        '''Returns a unique session id.'''
        return self.__session_id

    @property
    def game_type(self):
        return self.__game_type

    @property
    def number_of_players(self):
        return self.__game.number_of_players

    @property
    def config(self):
        return self.__game.game_config

    @property
    def game_name(self):
        return self.__game_name


