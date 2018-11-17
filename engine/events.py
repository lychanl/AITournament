def default_on_start(config, game, train_players, train_pools, test_players, test_pools):
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


def default_on_finished():
    print("Finished!")


def default_on_epoch_started(n):
    print("\nEpoch {}".format(n))


def default_on_test_run_finished(results_by_players, results_by_pools):
    print("Test results:")

    for obj, res in zip(results_by_players.keys(), results_by_players.values()):
        print("{}\t{}".format(obj, res))

    for obj, res in zip(results_by_pools.keys(), results_by_pools.values()):
        print("{}\t{}".format(obj, res))
