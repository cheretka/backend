from uuid import UUID

from bots_battles.game_engine import Player


class CheckersPlayer(Player):

    def __init__(self, player_name: str, uuid: UUID, player_color: str):
        super().__init__(uuid, player_name)
        self.color = player_color
