import argparse
import yaml
import importlib
import importlib.util
import engine.player
import engine.player_pool
import engine.game
import engine.events


def get_configuration():
    args = _parse_args()
    config_file = _load_config(args.config_path)
    configuration = Configuration(args, config_file)

    if not configuration.game:
        exit("Game must be configured")
    
    return configuration


def _parse_args():
    parser = argparse.ArgumentParser(description="AITournament - engine for training and testing AI players in games.")
    parser.add_argument("--config", dest="config_path", default="config.yaml", help="Configuration file")
    parser.add_argument("--epochs", dest="epochs", default=1, type=int, help="Number of train + test runs")
    parser.add_argument("--test-runs", dest="test_runs", default=1, type=int, help="Number of test runs per epoch")
    parser.add_argument("--train-runs", dest="train_runs", default=0, type=int, help="Number of train runs per epoch")

    return parser.parse_args()


def _load_config(path):
    try:
        with open(path) as file:
            return yaml.load(file)

    except FileNotFoundError:
        exit("File '{}' does not exist".format(path))
    except yaml.YAMLError:
        exit("File '{}' is not a valid YAML file".format(path))


def _is_built_in_name(name):
    return name in ("session", )


class Configuration:
    def __init__(self, args, config_file):
        self.tf_session_wrapper = None

        self.epochs = args.epochs
        self.test_runs = args.test_runs
        self.train_runs = args.train_runs

        self.modules = {}
        if "modules" in config_file:
            self._parse_modules(config_file["modules"])

        self.players = self._parse_players(config_file["players"]) if "players" in config_file else {}
        self.pools = self._parse_pools(config_file["pools"]) if "pools" in config_file else {}

        if not self.players or not self.pools:
            exit("Players or player pools must be configured")

        if "train" in config_file:
            self.train_players, self.train_pools = self._parse_object_lists(config_file["train"])
        else:
            if self.train_runs > 0:
                exit("No players or pools defined for train run")
            self.train_players = []
            self.train_pools = []

        if "test" in config_file:
            self.test_players, self.test_pools = self._parse_object_lists(config_file["test"])
        else:
            if self.test_runs > 0:
                exit("No players or pools defined for train run")
            self.test_players = []
            self.test_pools = []

        if "game" not in config_file:
            exit("Game is not configured")
        self.game = self._parse_game(config_file["game"])

        # default event handlers
        self.on_start = engine.events.default_on_start
        self.on_finished = engine.events.default_on_finished
        self.on_epoch_started = engine.events.default_on_epoch_started
        self.on_test_game_finished = self.on_train_game_finished = None
        self.on_train_run_finished = None
        self.on_test_run_finished = engine.events.default_on_test_run_finished
        self.on_test_step = self.on_train_step = None

        if "events" in config_file:
            self._parse_events(config_file["events"])

    def _parse_events(self, events_config):
        for event, config in zip(events_config.keys(), events_config.values()):
            parsed = self._parse_event(event, config)
            if event == "on_start":
                self.on_start = parsed
            elif event == "on_epoch_started":
                self.on_epoch_started = parsed
            elif event == "on_finished":
                self.on_finished = parsed

            elif event == "on_test_step":
                self.on_test_step = parsed
            elif event == "on_test_game_finished":
                self.on_test_game_finished = parsed
            elif event == "on_test_run_finished":
                self.on_test_run_finished = parsed

            elif event == "on_train_step":
                self.on_train_step = parsed
            elif event == "on_train_game_finished":
                self.on_train_game_finished = parsed
            elif event == "on_train_run_finished":
                self.on_train_run_finished = parsed

            else:
                exit("Unrecognized event: {}".format(event))

    def _parse_event(self, name, event_config):
        if "module" not in event_config or "func" not in event_config:
            exit("Module or function is not defined for {}".format(name))

        return self._symbol_getter(event_config["module"], event_config["func"])

    def _parse_modules(self, modules_config):
        if modules_config is None:
            return
        if type(modules_config) is not dict:
            exit("Invalid modules configuration")

        for name, path in zip(modules_config.keys(), modules_config.values()):
            if name in self.modules:
                exit("Module {} redefined".format(name))

            self._import_module(name, path)

    def _parse_object_lists(self, config):
        players = []
        pools = []

        if "players" in config:
            for player in config["players"]:
                if player not in self.players:
                    exit("Undefined player: {}".format(player))
                players.append(self.players[player])

        if "pools" in config:
            for pool in config["pools"]:
                if pool not in self.pools:
                    exit("Undefined pool: {}".format(pool))
                pools.append(self.pools[pool])

        return players, pools

    def _parse_players(self, players_config):
        return self._parse_players_or_pools(players_config, "players", engine.player.Player)

    def _parse_pools(self, pools_config):
        return self._parse_players_or_pools(pools_config, "pools", engine.player_pool.PlayerPool)

    def _parse_players_or_pools(self, config, name_to_display, class_):
        if config is None:
            return []
        if type(config) is not dict:
            exit("Invalid {} configuration".format(name_to_display))

        ret = {}
        for name, conf in zip(config.keys(), config.values()):
            ret[name] = ObjectConfig(name, conf, self._symbol_getter, self._obj_getter, class_)

        return ret

    def _parse_game(self, game_config):
        return ObjectConfig("Game", game_config, self._symbol_getter, self._obj_getter, engine.game.Game)

    def _symbol_getter(self, module, name):
        if module not in self.modules:
            self._import_module(module, None)

        mod = self.modules[module]

        if not hasattr(mod, name):
            exit("Name {} is not in module {}".format(name, module))

        return getattr(mod, name)

    def _import_module(self, name, path):
        try:
            if path is None:
                self.modules[name] = importlib.import_module(name)
            else:
                spec = importlib.util.spec_from_file_location(name, path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.modules[name] = module
        except ImportError:
            exit('Failed to load module {}'.format(name))

    def _obj_getter(self, obj):
        if obj == 'session':
            if self.tf_session_wrapper is None:
                self.tf_session_wrapper = TFSessionWrapper()
            return self.tf_session_wrapper

        return obj


class TFSessionWrapper:
    def __init__(self):
        self.session = None


class ObjectConfig:
    def __init__(self, name, config, class_getter, obj_getter, base_class):
        self.name = name
        if "module" not in config or "class" not in config:
            exit("Module or class is not defined for {}".format(name))

        self.class_ = class_getter(config["module"], config["class"])
        if not issubclass(self.class_, base_class):
            exit("Class {}.{} of {} does not extends correct base class"
                 .format(config["module"], config["class"], name))

        self.params = {}
        if "params" in config:
            if type(config["params"]) is not dict:
                exit("Params of {} must be a dictionary".format(name))

            for name, param in zip(config["params"].keys(), config["params"].values()):
                if type(name) is not str:
                    exit("Invalid param name for object {}".format(name))

                self.params[name] = obj_getter(param)

    def create(self):
        params = {key: value if type(value) is not TFSessionWrapper else value.session
                  for key, value in zip(self.params.keys(), self.params.values())}
        obj = self.class_(**params)
        if issubclass(self.class_, engine.player.Player) or issubclass(self.class_, engine.player_pool.PlayerPool):
            obj.set_name(self.name)

        return obj
