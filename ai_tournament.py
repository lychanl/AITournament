from engine.config import get_configuration


def log_info(config, game, train_players, train_pools, test_players, test_pools):
    print("Run info:\n")
    print("Game: {}".format(game))
    print("Epochs: {}".format(config.epochs))

    print("\nTraining runs per epoch: {}".format(config.train_runs))
    if config.train_runs > 0:
        if len(train_players) > 0:
            print("Trained players:")
            for player in train_players:
                print(" - {}".format(player))
        if len(train_pools) > 0:
            print("Trained player pools:")
            for pool in train_pools:
                print(" - {}".format(pool))

    print("\nTesting runs per epoch: {}".format(config.test_runs))
    if config.test_runs > 0:
        if len(test_players) > 0:
            print("Tested players:")
            for player in test_players:
                print(" - {}".format(player))
        if len(test_pools) > 0:
            print("Tested player pools:")
            for pool in test_pools:
                print(" - {}".format(pool))


tf = None


def create_tf_session(session_wrapper):
    if session_wrapper is not None:
        import tensorflow
        session_wrapper.session = tensorflow.Session()


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

        log_info(config, game, train_players, train_pools, test_players, test_pools)

        prepare_tf_session(config.tf_session_wrapper)
    finally:
        close_tf_session(config.tf_session_wrapper)


if __name__ == "__main__":
    main()
