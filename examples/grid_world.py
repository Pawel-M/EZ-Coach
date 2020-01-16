import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import ezcoach as ez
import random_algorithm
import simple_learning
from ezcoach.enviroment import Manifest


def train(algorithm_getter, environment, runs):
    ep_rewards = None
    for run in range(runs):
        print(f'run [{run + 1}/{runs}]')
        algorithm = algorithm_getter()
        adapter = simple_learning.LearningAdapter(algorithm, num_episodes)
        runner = ez.Runner(adapter, environment=environment, verbose=2)
        runner.train()
        current_ep_rewards = runner.metrics.get_episode_reward().to_numpy()
        if ep_rewards is None:
            ep_rewards = current_ep_rewards
        else:
            ep_rewards = np.vstack([ep_rewards, current_ep_rewards])

    print('mc rewards', ep_rewards)
    mean_ep_rewards = np.mean(ep_rewards, axis=0)
    return ep_rewards, mean_ep_rewards


environment = ez.RemoteEnvironment()
environment.connect()
actions_definition = environment.manifest.actions_definition
num_actions = actions_definition.ranges[0].max - actions_definition.ranges[0].min + 1


def get_mc():
    return simple_learning.MonteCarloAlgorithm(simple_learning.DictQFunction(num_actions, 0.),
                                               alpha=alpha, gamma=gamma, epsilon=epsilon)


def get_ql():
    return simple_learning.QLearningAlgorithm(simple_learning.DictQFunction(num_actions, 0.),
                                              alpha=alpha, gamma=gamma, epsilon=epsilon)


gamma = 1  # discount rate
alpha = .1  # learning rate
epsilon = (.1, 0.)
num_episodes = 100
runs = 20

mc_rewards, mc_mean_rewards = train(get_mc, environment, runs)
ql_rewards, ql_mean_rewards = train(get_ql, environment, runs)

plt.plot(range(1, num_episodes + 1), mc_mean_rewards, marker='.', label='Monte Carlo')
plt.plot(range(1, num_episodes + 1), ql_mean_rewards, marker='.', label='Q-learning')
plt.xlabel('episode')
plt.ylabel('reward')
plt.legend()
plt.show()

data = pd.DataFrame({'mc': mc_mean_rewards, 'ql': ql_mean_rewards})
data.index.name = 'episode'
data.to_csv('grid_world_mean_rewards.csv')
