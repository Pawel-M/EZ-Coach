"""
Metrics collected during the training and testing procedures are recorded by the Recorder class introduced in this
module. The Recorder object can be accessed by the metrics attribute of the Runner class (ezcoach.core module).
For multi-agent procedures MultiRecorder is used.
"""

from typing import Dict, Iterable, Tuple
import matplotlib.pyplot as plt
import pandas as pd

TIME = 'time'
REWARD = 'reward'
ACTIONS = 'actions'


def _plot_metric(metrics, name, zero_indexed=False):
    """
    Plots metrics for a single agent.

    :param metrics: a metrics to be plotted
    :param name: a name of the metric
    :param zero_indexed: if True than episodes are indexed from 0 and not from 1
    """
    episodes = range(len(metrics)) if zero_indexed else range(1, len(metrics) + 1)
    plt.plot(episodes, metrics)
    plt.xlabel('episode')
    plt.ylabel(name)
    plt.show()


def _plot_multi_metric(metrics, name, agent_names=None, zero_indexed_episodes=False, zero_indexed_agents=True):
    """
    Plots metrics for all agents.

    :param metrics: a list of metrics for each agent
    :param name: a name of the metric
    :param agent_names: a list of agent's names
    :param zero_indexed_episodes: if True then episodes are indexed from 0 and not from 1
    :param zero_indexed_agents: if True then agents are indexed from 0 and not from 1
    """
    num_episodes = len(metrics[0])
    episodes = range(num_episodes) if zero_indexed_episodes else range(1, num_episodes + 1)
    if agent_names is None:
        agent_names = (f'agent {agent}' for agent in range(0 if zero_indexed_agents else 1, len(metrics)))

    for agent, met in zip(agent_names, metrics):
        plt.plot(episodes, met, label=agent)

    plt.xlabel('episode')
    plt.ylabel(name)
    plt.legend()
    plt.show()


class Recorder:
    """
    The class representing recorder of the metrics for a single agent. Three metrics are included by default:
    time of the episode, number of actions during the episode and a reward signal accumulated (without discounting)
    during the episode. This class provides plotting methods for all collected metrics.
    """
    def __init__(self, metrics_names: Iterable[str] = (TIME, ACTIONS, REWARD),
                 additional_metrics_names: Iterable[str] = None):
        """
        Initializes the object with the name of the metrics and additional metrics (usually game specific metrics).

        :param metrics_names: an iterable of metrics names
        :param additional_metrics_names: an iterable of additional metrics names
        """
        self._metrics_names = tuple(metrics_names)
        if additional_metrics_names is not None:
            self._metrics_names += tuple(additional_metrics_names)

        self._metrics = pd.DataFrame(columns=self._metrics_names)
        self._metrics.index.name = 'episode'

    def add_episode_metrics(self, metrics: Iterable):
        """
        Adds metrics from the end of the episode. The length of provided metrics must be equal to the length
        of metrics names.

        :param metrics: an iterable of metrics values
        """
        episode_metrics = pd.DataFrame((metrics,), columns=self._metrics_names)
        self._metrics = pd.concat((self._metrics, episode_metrics), ignore_index=True)
        self._metrics.index.name = 'episode'

    def export_to_csv(self, filename):
        self._metrics.to_csv(filename)

    @property
    def metrics(self) -> pd.DataFrame:
        """
        Returns the pandas DataFrame containing all collected metrics.

        :return: a DataFrame with collected metrics
        """
        return self._metrics

    @property
    def metrics_names(self) -> Tuple[str]:
        """
        Returns the list of metrics names.

        :return: a tuple containing metrics names
        """
        return self._metrics_names

    def get_metric(self, name: str):
        """
        Returns the pandas Series of the metric with specified name.

        :param name: a name of the metric
        :return: a Series object containing metrics with specified name
        """
        if name not in self._metrics_names:
            # TODO: add throwing  exception
            pass
        return self._metrics[name]

    def get_episode_time(self):
        """
        Returns the episode time metric as pandas Series.

        :return: a Series object representing collected episode times
        """
        return self.get_metric(TIME)

    def get_episode_reward(self):
        """
        Returns the accumulated rewards (without discount) for each episode as pandas Series.

        :return: a Series object representing accumulated rewards for each episode
        """
        return self.get_metric(REWARD)

    def get_episode_actions(self):
        """
        Returns the number of actions in each episode as pandas Series.

        :return: a Series object representing the number of agent's actions for each episode
        """
        return self.get_metric(ACTIONS)

    def plot_episode_time(self, zero_indexed=False):
        """
        Plots the time of each episode.

        :param zero_indexed: if True than episodes are indexed from 0 and not from 1
        """
        _plot_metric(self.get_episode_time(), 'time [s]', zero_indexed)

    def plot_episode_reward(self, zero_indexed=False):
        """
        Plots the accumulated reward (wighout discounting) of each episode.

        :param zero_indexed: if True than episodes are indexed from 0 and not from 1
        """
        _plot_metric(self.get_episode_reward(), 'reward', zero_indexed)

    def plot_episode_actions(self, zero_indexed=False):
        """
        Plots the number of actions of each episode.

        :param zero_indexed: if True than episodes are indexed from 0 and not from 1
        """
        _plot_metric(self.get_episode_actions(), 'actions', zero_indexed)

    def plot_metric(self, name, zero_indexed=False):
        """
        Plots the metric corresponding to a specified name for each episode.

        :param zero_indexed: if True than episodes are indexed from 0 and not from 1
        """
        _plot_metric(self.get_metric(name), name, zero_indexed)

    def __len__(self):
        return len(self.metrics_names)

    def __getitem__(self, item):
        return self.get_metric(item)


class MultiRecorder:
    """
    The class responsible for recording the standard metrics for a number of agents along with the metrics provided
    by the game. The standard metrics are: time of the episode, number of actions during the episode
    and a reward signal accumulated (without discounting) during the episode. This class provides plotting methods
    for all collected metrics.
    """
    def __init__(self, num_recordings: int, game_metrics_names: Iterable[str] = None):
        """
        Initializes the object with the number of recordings (equal to the number of agents) and a list of game
        specific metrics.

        :param num_recordings: a number of recordings equal to the number of agents
        :param game_metrics_names: an iterable containing the names of game specific metrics
        """
        self._recorders = tuple(Recorder() for __ in range(num_recordings))

        if game_metrics_names is not None and len(tuple(game_metrics_names)) > 0:
            self._game_metrics_recorder = Recorder(game_metrics_names)
        else:
            self._game_metrics_recorder = None

    def add_episode_metrics(self, agent_metrics: Iterable, game_metrics: Iterable):
        """
        Adds metrics for the episode. Agents metrics are the default metrics for each agent. Game metrics are
        the metrics provided by the game and are game-specific.

        :param agent_metrics: an iterable of standard metrics for each agent
        :param game_metrics: an iterable of game specific metrics
        """
        for rec, met in zip(self._recorders, agent_metrics):
            rec.add_episode_metrics(met)

        if self._game_metrics_recorder is not None:
            self._game_metrics_recorder.add_episode_metrics(game_metrics)

    def export_to_csv(self, filename):
        combined_metrics = self.metrics
        combined_metrics.to_csv(filename)

    @property
    def metrics(self) -> pd.DataFrame:
        """
        Returns the pandas DataFrame containing all collected metrics. Joins agent metrics and game metrics.
        Names of agent metrics starts with 'agent[n]_' where [n] is the index of the agent (e.g. 'agent0_reward').

        :return: a DataFrame with collected metrics
        """
        combined_metrics = pd.DataFrame()
        for index, recorder in enumerate(self._recorders):
            combined_metrics = combined_metrics.join(recorder.metrics.copy().add_prefix(f'agent{index}_'), how='outer')

        if self._game_metrics_recorder is not None:
            combined_metrics = combined_metrics.join(self._game_metrics_recorder.metrics, how='outer')
        return combined_metrics

    def get_game_metrics(self):
        """
        Returns the game-specific metrics.

        :return: a Recorder containing metrics specific for the game
        """
        return self._game_metrics_recorder

    def get_game_metric(self, name: str):
        """
        Returns the game-specific metric corresponding the the given name.

        :param name: a name of the metric
        :return: a pandas Series object containing the specified metric
        """
        if self._game_metrics_recorder is None:
            # TODO: add throwing an exception
            pass

        return self._game_metrics_recorder.get_metric(name)

    def get_agent_metric(self, name: str):
        """
        Returns the list of metrics specified by the game for each agent. The metric must be one of the default metrics.

        :param name: a name of the metric
        :return: a tuple of pandas Series objects containing metrics for each agent
        """
        return tuple(rec.get_metric(name) for rec in self._recorders)

    def get_episode_time(self):
        """
        Returns the list of episode times for each agent.

        :return: a tuple fo pandas Series objects containing episode times for each agent
        """
        return self.get_agent_metric(TIME)

    def get_episode_reward(self):
        """
        Returns the list of rewards accumulated (without discounting) during each episode for each agent.

        :return: a tuple fo pandas Series objects containing rewards accumulated during each episode for each agent
        """
        return self.get_agent_metric(REWARD)

    def get_episode_actions(self):
        """
        Returns the list containing a number of actions during each episode for each agent.

        :return: a tuple fo pandas Series objects containing a number of actions during each episode for each agent
        """
        return self.get_agent_metric(ACTIONS)

    def plot_episode_time(self, agent_names=None, zero_indexed=False):
        """
        Plots the time of each episode for each agent.

        :param agent_names: a list of names of agents
        :param zero_indexed: if True than episodes are indexed from 0 and not from 1
        """
        _plot_multi_metric(self.get_episode_time(), 'time [s]', agent_names, zero_indexed)

    def plot_episode_reward(self, agent_names=None, zero_indexed=False):
        """
        Plots the reward accumulated during each episode for each agent.

        :param agent_names: a list of names of agents
        :param zero_indexed: if True than episodes are indexed from 0 and not from 1
        """
        _plot_multi_metric(self.get_episode_reward(), 'reward', agent_names, zero_indexed)

    def plot_episode_actions(self, agent_names=None, zero_indexed=False):
        """
        Plots the number of actions performed during each episode for each agent.

        :param agent_names: a list of names of agents
        :param zero_indexed: if True than episodes are indexed from 0 and not from 1
        """
        _plot_multi_metric(self.get_episode_actions(), 'actions', agent_names, zero_indexed)

    def plot_metric(self, name, agent_names=None, zero_indexed=False):
        """
        Plots the metric specified by the name for each agent.

        :param name: a name of the metric
        :param agent_names: a list of names of agents
        :param zero_indexed: if True than episodes are indexed from 0 and not from 1
        """
        _plot_multi_metric(self.get_agent_metric(name), name, agent_names, zero_indexed)

    def __len__(self):
        return len(self._recorders)

    def __getitem__(self, item):
        return self._recorders[item]
