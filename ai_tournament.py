from engine.config import get_configuration
from engine.enigne import Engine


def create_tf_session(session_wrapper):
    if session_wrapper is not None:
        import tensorflow
        config = tensorflow.ConfigProto()
        config.gpu_options.allow_growth = True
        session_wrapper.session = tensorflow.Session(config=config)


def prepare_tf_session(session_wrapper):
    if session_wrapper is not None:
        import tensorflow
        session_wrapper.session.run(tensorflow.global_variables_initializer())


def close_tf_session(session_wrapper):
    if session_wrapper is not None:
        session_wrapper.session.close()


def main():
    config = get_configuration()

    try:
        create_tf_session(config.tf_session_wrapper)

        game = config.game.create()

        train_players = [pl.create() for pl in config.train_players]
        train_pools = [pl.create() for pl in config.train_pools]
        test_players = [pl.create() for pl in config.test_players]
        test_pools = [pl.create() for pl in config.test_pools]

        prepare_tf_session(config.tf_session_wrapper)

        if config.on_start:
            config.on_start(config, game, train_players, train_pools, test_players, test_pools)

        engine = Engine(game)
        engine.set_testing_players(test_players, test_pools)
        engine.set_training_players(train_players, train_pools)

        engine.test(config.test_runs,
                    config.on_test_run_finished,
                    config.on_test_game_finished,
                    config.on_test_step)

        for i in range(config.epochs):
            if config.on_epoch_started:
                config.on_epoch_started(i)

            engine.train(config.train_runs,
                         config.on_train_run_finished,
                         config.on_train_game_finished,
                         config.on_train_step)

            engine.test(config.test_runs,
                        config.on_test_run_finished,
                        config.on_test_game_finished,
                        config.on_test_step)

        if config.on_finished:
            config.on_finished()
    finally:
        close_tf_session(config.tf_session_wrapper)


if __name__ == "__main__":
    main()
