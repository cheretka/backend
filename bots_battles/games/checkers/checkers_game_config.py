from bots_battles.game_engine.config_options import IntOption
from bots_battles.game_engine.real_time_game_config import GameConfig


class CheckersGameConfig(GameConfig):

    def __init__(self):
        super().__init__()
        self._add_option('waiting_time', IntOption("After this time without player, session will be closed (in s)", 600, 30, 1500), True)
