import numpy as np
import ezcoach as ez
import ezcoach.adapter as adapter
from random_algorithm import RandomAlgorithm

from simple_learning import LearningAdapter, MonteCarloAlgorithm, DictQFunction

env = ez.RemoteEnvironment(verbose=1)
env.connect()

num_actions = env.manifest.actions_definition.ranges[0].max - env.manifest.actions_definition.ranges[0].min + 1


def train_single_agent_mc(episodes=2000, csv_file='pong_tab_2000.csv', save_file='pong_tab_2000.tab'):
    epsilon = (.1, 0.)  # epsilon of a greedy policy
    alpha = .1  # learning rate
    gamma = .95  # discount rate
    state_adapters = [adapter.selection_adapter([0, 1, 2]), adapter.round_to_int]
    tab_q = DictQFunction(num_actions)
    tab_mc = LearningAdapter(MonteCarloAlgorithm(tab_q, alpha, gamma, epsilon), episodes)
    runner = ez.Runner(tab_mc, state_adapters=state_adapters, environment=env, verbose=2)
    runner.train()
    runner.metrics.export_to_csv(csv_file)
    runner.agent.save(save_file)


def train_self_play_mc(episodes=1000, csv_file='pong_tab_1000_adv.csv', save_file='pong_tab_1000_adv.tab'):
    epsilon = (.1, 0.)  # epsilon of a greedy policy
    alpha = .1  # learning rate
    gamma = .95  # discount rate
    state_adapters = [adapter.selection_adapter([0, 1, 2]), adapter.round_to_int]
    tab_q = DictQFunction(num_actions)
    tab_mc_1 = LearningAdapter(MonteCarloAlgorithm(tab_q, alpha, gamma, epsilon), episodes)
    tab_mc_2 = LearningAdapter(MonteCarloAlgorithm(tab_q, alpha, gamma, epsilon), episodes)
    runner = ez.Runner([tab_mc_1, tab_mc_2], state_adapters=state_adapters, environment=env, verbose=2)
    runner.train()
    runner.metrics.export_to_csv(csv_file)
    runner.agent[0].save(save_file)


def test_algorithms(episodes, first_load_file, second_load_file):
    alpha = 0  # learning rate (not used)
    gamma = 0  # discount rate (not used)
    state_adapters = [adapter.selection_adapter([0, 1, 2]), adapter.round_to_int]

    adv_tab_q = DictQFunction(num_actions)
    adv_tab_q.load(first_load_file)
    adv_tab_mc = MonteCarloAlgorithm(adv_tab_q, alpha, gamma, epsilon=0, epsilon_greedy=False)

    sp_tab_q = DictQFunction(num_actions)
    sp_tab_q.load(second_load_file)
    sp_tab_mc = MonteCarloAlgorithm(sp_tab_q, alpha, gamma, epsilon=0, epsilon_greedy=False)

    runner = ez.Runner([LearningAdapter(adv_tab_mc, episodes), LearningAdapter(sp_tab_mc, episodes)],
                       state_adapters=state_adapters, environment=env, verbose=2)

    runner.play(episodes)
    p1_rewards, p2_rewards = runner.metrics.get_episode_reward()
    p1_wins = p1_rewards[p1_rewards == 1.].count()
    p2_wins = p2_rewards[p2_rewards == 1.].count()
    print(f'Player 1 vs Player 2:\n{p1_wins}:{p2_wins} / {p1_wins + p2_wins}')


def test_adv_algorithm(episodes=10, load_file='pong_tab_1000_adv.tab'):
    alpha = 0  # learning rate (not used)
    gamma = 0  # discount rate (not used)
    state_adapters = [adapter.selection_adapter([0, 1, 2]), adapter.round_to_int]

    adv_tab_q = DictQFunction(num_actions)
    adv_tab_q.load(load_file)
    adv_tab_mc = MonteCarloAlgorithm(adv_tab_q, alpha, gamma, epsilon=0, epsilon_greedy=False)

    runner = ez.Runner(LearningAdapter(adv_tab_mc, episodes), state_adapters=state_adapters, environment=env, verbose=2)
    runner.play(episodes)
    p1_rewards = runner.metrics.get_episode_reward()
    p1_wins = p1_rewards[p1_rewards == 1.].count()
    p2_wins = episodes - p1_wins
    print(f'Player 1 vs Player 2:\n{p1_wins}:{p2_wins} / {p1_wins + p2_wins}')


# train_single_agent_mc()
# train_self_play_mc()
# test_algorithms(1000, 'pong_tab_1000_adv.tab', 'pong_tab_2000.tab')

# train_self_play_mc(episodes=3000, csv_file='pong_tab_3000_adv.csv', save_file='pong_tab_3000_adv.tab')
test_algorithms(100, 'pong_tab_1000_adv.tab', 'pong_tab_3000_adv.tab')
# test_adv_algorithm()
