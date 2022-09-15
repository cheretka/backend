from bots_battles.game_engine.config_options import IntOption
from bots_battles.game_engine.real_time_game_config import RealtimeGameConfig


class CheckersGameConfig(RealtimeGameConfig):

    def __init__(self):
        super().__init__()
        self._add_option('waiting_time', IntOption("After this time without player, session will be closed (in s)", 30, 20, 500), True)
        self._add_option('max_player_number', IntOption('Maximum number of players', 2, 2, 2), True)
