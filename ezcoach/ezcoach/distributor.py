"""
This module introduces the Distributor classes which are used by the Runner class (ezcoach.core module) to distribute
state observations and rewards to the agents, and obtain agents' action selections.
"""

import abc
import statistics
import time
from typing import Any, Iterable, Optional, Union, Sized

from ezcoach.adapter import adapt_object
from ezcoach.agent import MultiLearner, Player, Learner
from ezcoach.enviroment import StateInfo, Manifest, StatesInfo
from ezcoach.log import log
from ezcoach.metrics import Recorder, MultiRecorder


class _AgentRunningState:
    """
    The class representing the current state of the single agent. It consists of the state, action, reward
    and a flag indicating if the current episode is running. Additionally, it contains the number of actions
    and the time of the start of the current episode.
    """

    def __init__(self):
        """
        Initializes the class with the default attributes.
        """
        self.running = True
        self.state = None
        self.action = None
        self.accumulated_reward = None
        self.num_actions = 0
        self.start_time = None
        self.episode_time = None

    def start(self):
        """
        Informs the class that en episode has started. The start_time attribute is set to a current time.
        """
        self.start_time = time.time()

    def update(self, state, action, accumulated_reward):
        """
        Updates the class witht he information about the state, action and reward.

        :param state: the current state for the agent
        :param action: the last action selected by the agent
        :param accumulated_reward: the reward accumulated by the agent
        """
        self.state = state
        self.action = action
        self.accumulated_reward = accumulated_reward

        if action is not None:
            self.num_actions += 1

    def ended(self):
        """
        Informs the class that the episode has ended. The time of the episode is calculated
        from the current time and the start of the episode.
        """
        self.running = False
        self.episode_time = time.time() - self.start_time


# TODO: check if method is used
def _log_metrics(metrics, metrics_list, episode, verbose):
    """
    Logs the metrics.

    :param metrics:
    :param metrics_list:
    :param episode:
    :param verbose:
    :return:
    """
    metrics_len = len(metrics_list)
    metrics_message = f'Metrics for episodes {episode - metrics_len + 1} - {episode}:\n'
    for i, metric in enumerate(metrics):
        metrics = tuple(m[i] for m in metrics_list)
        mean = statistics.mean(metrics)
        stdev = statistics.stdev(metrics)
        metrics_message += f'\t{metric} - mean: {mean}, stdev: {stdev}\n'
    log(metrics_message, verbose, 1)


class BaseDistributor(abc.ABC):
    """
    The base class for all distributors used by the Runner class. The distributors are an abstraction
    of the single- and multi-agent procedures and are responsible for distributing states and rewards
    to and obtaining the actions from the agents.
    """

    def __init__(self, state_adapters=None, action_adapters=None, reward_adapters=None, verbose=None):
        """
        Initializes the distributor with the states, actions and rewards adapters.

        :param state_adapters: an iterable of state adapters or a single state adapter
        :param action_adapters: an iterable of action adapters or a single action adapter
        :param reward_adapters: an iterable of reward adapters or a single reward adapter
        :param verbose: the value representing the frequency of logging
        """
        self._state_adapters = state_adapters
        self._action_adapters = action_adapters
        self._reward_adapters = reward_adapters
        self._manifest = None
        self._verbose = verbose

    @abc.abstractmethod
    def is_training_supported(self) -> bool:
        """
        Returns if training is supported by the agents.

        :return: a bool value indicating if training is supported by the agents
        """

    @abc.abstractmethod
    def initialize_players(self, manifest: Manifest):
        """
        Initializes the agents with the manifest provided by the game.

        :param manifest: a Manifest class of the connected environment
        """
        self._manifest = manifest

    @abc.abstractmethod
    def select_players_num(self, selected_players: int = None) -> int:
        """
        Select the number of players simultaneously interacting with the environment.
        The optional parameter is preferred but if the selected number of players is not supported
        than other value may be returned.

        :param selected_players: the selected number of players
        :return: the number of players supported by the environment and provided agents
        """

    @abc.abstractmethod
    def initialize_episode(self, episode: int):
        """
        Informs the agents that the episode is started.

        :param episode: the number of the current episode
        """

    @abc.abstractmethod
    def do_start_episode(self, episode: int) -> bool:
        """
        Checks weather the next episode should be started. This method is used during the training episode
        when the algorithms control the number of episodes.

        :param episode: the number of the episode to be started
        :return: the bool value indicating if the next episode should be started
        """

    @abc.abstractmethod
    def is_episode_running(self):
        """
        Returns weather the episode is running for any agent.

        :return: bool value indicating if the episode is running for any agent
        """

    @abc.abstractmethod
    def react_to_states(self, states: StatesInfo) -> Optional[Iterable[Any]]:
        """
        Distributes the states to the agents and returns the selected actions. In the case of mutli-agent
        procedures the None will be selected by the agents for whom the episode has ended.
        Actions will not be returned if the episode has ended for each agent.

        :param states: the information about states and rewards for each agent as a StatesInfo object
        :return: an iterable of actions selected by each agent
        """

    @abc.abstractmethod
    def learn_from_states(self, states: StatesInfo) -> Optional[Iterable[Any]]:
        """
        Distributes the states and obtained rewards to the agents and returns the actions selected by the agents.
        Actions will not be selected if the episode has ended.

        :param states: the information about states and rewards for each agent as a StatesInfo object
        :return: an iterable of actions selected by each agent
        """

    @property
    @abc.abstractmethod
    def metrics(self) -> Recorder:
        """
        Returns the metrics gathered during the last training or testing procedure.

        :return: a Recorder instance containing metrics gathered during the last procedure
        """

    def _react_to_state(self, training: bool, agent: Union[Player, Learner], state_info: StateInfo,
                        agent_state: _AgentRunningState) -> Optional[Any]:
        """
        Passes the state to the agent. In case of training the agent is also informed about the reward.
        The action selected by the agent is returned.

        :param training: a flag indicating if an agent should be informed about the reward
        :param agent: an agent that will react to a state and select an action
        :param state_info: a StateInfo object representing state and reward information
        :param agent_state: an AgentRunningState object representing current state of the agent
        :return: an action selected by the agent or None if the episode has ended
        """
        if not agent_state.running:
            return None

        state, accumulated_reward, running = state_info
        state = adapt_object(state, self._state_adapters)
        accumulated_reward = adapt_object(accumulated_reward, self._reward_adapters)

        if training and agent_state.state is not None:
            agent.receive_reward(agent_state.state, agent_state.action,
                                 accumulated_reward - agent_state.accumulated_reward,
                                 accumulated_reward,
                                 state)

            log(f'Learner receive_reward(): previous_state: {agent_state.state},'
                f' previous_action:{agent_state.action},'
                f' accumulated_reward: {accumulated_reward}'
                f' previous_accumulated_reward: {agent_state.accumulated_reward},'
                f' next_state: {state}',
                self._verbose, level=4)

        action = agent.act(state) if running else None
        if agent_state.running:
            agent_state.update(state, action, accumulated_reward)
            if not running:
                agent_state.ended()

        if action is not None:
            return adapt_object(action, self._action_adapters)
        else:
            return None

    # TODO: change to throwing an error?
    def assert_training_supported(self):
        """
        Checks if the training is supported by the agent or agents provided in the constructor.
        """
        assert self.is_training_supported(), 'Learning is not supported for this agent.'


class SingleAgentDistributor(BaseDistributor):
    """
    The class distributing the states and rewards for a single algorithm representing single agent.
    It inherits from the BaseDistributor class.
    """

    def __init__(self, agent: Union[Player, Learner],
                 state_adapters=None, action_adapters=None, reward_adapters=None, verbose=None):
        """
        Initializes the class with a single agent that implements Player or Learner interfaces.
        State, action and reward adapters can be provided as an iterable of callables or a single callable.

        :param agent: an object that implements Player or Learner interface representing an agent
        :param state_adapters: an iterable of state adapters or a single state adapter
        :param action_adapters: an iterable of action adapters or a single action adapter
        :param reward_adapters: an iterable of reward adapters or a single reward adapter
        :param verbose: the value representing the frequency of logging
        """
        super().__init__(state_adapters, action_adapters, reward_adapters, verbose)
        self._agent = agent

        self._learning_supported = isinstance(self._agent, Learner)
        self._agent_state = _AgentRunningState()
        self._recorder = None

    def is_training_supported(self) -> bool:
        return self._learning_supported

    def initialize_players(self, manifest: Manifest):
        super(SingleAgentDistributor, self).initialize_players(manifest)

        self._recorder = Recorder(additional_metrics_names=manifest.metrics_names)
        self._agent.initialize(manifest)

    # TODO: change to throwing an exception?
    def select_players_num(self, selected_players: int = None) -> int:
        if selected_players is not None:
            assert selected_players == 1, f'{__class__.__name__} does not support selected number of players' \
                                          f' ({selected_players}).'
        else:
            selected_players = 1

        return selected_players

    def initialize_episode(self, episode: int):
        self._agent_state = _AgentRunningState()
        self._agent_state.start()

        self._agent.episode_started(episode)

    def do_start_episode(self, episode: int) -> bool:
        return self._agent.do_start_episode(episode)

    def react_to_states(self, states: StatesInfo) -> Optional[Iterable[Any]]:
        action = self._react_to_state(False, self._agent, states[0], self._agent_state)

        if not self._agent_state.running:
            self._collect_metrics(states)

        return (action,) if action is not None else None

    def learn_from_states(self, states: StatesInfo) -> Optional[Iterable[Any]]:
        self.assert_training_supported()

        state_info: StateInfo = states[0]
        action = self._react_to_state(True, self._agent, state_info, self._agent_state)

        if not self._agent_state.running:
            self._agent.episode_ended(self._agent_state.state, self._agent_state.accumulated_reward)
            self._collect_metrics(states)

        return (action,) if action is not None else None

    def _collect_metrics(self, states: StateInfo):
        metrics = (self._agent_state.episode_time,
                   self._agent_state.num_actions,
                   self._agent_state.accumulated_reward)

        if states.game_metrics is not None:
            metrics += states.game_metrics

        self._recorder.add_episode_metrics(metrics)

    def is_episode_running(self):
        return self._agent_state.running

    @property
    def metrics(self):
        return self._recorder


class AgentListDistributor(BaseDistributor):
    """
    The class distributing states and rewards to a list of agents. It is the basic type of multi-agent training
    and testing. It inherits from the BaseDistributor class.
    """

    def __init__(self, agents: Iterable[Union[Player, Learner]],
                 state_adapters=None, action_adapters=None, reward_adapters=None, verbose=None):
        """
        Initializes the class with an iterable of agents that implements Player or Learner interfaces.
        State, action and reward adapters can be provided as an iterable of callables or a single callable.

        :param agents: an iterable of objects that implements Player or Learner interface representing agents
        :param state_adapters: an iterable of state adapters or a single state adapter
        :param action_adapters: an iterable of action adapters or a single action adapter
        :param reward_adapters: an iterable of reward adapters or a single reward adapter
        :param verbose: the value representing the frequency of logging
        """
        super().__init__(state_adapters, action_adapters, reward_adapters, verbose)
        self._agents = tuple(agents)

        self._num_agents = len(self._agents)
        self._learning_supported = all(isinstance(agent, Learner) for agent in self._agents)

        self._agents_states = None
        self._recorder = None

    def is_training_supported(self) -> bool:
        return self._learning_supported

    def initialize_players(self, manifest: Manifest):
        super(AgentListDistributor, self).initialize_players(manifest)

        for agent in self._agents:
            agent.initialize(manifest)

    # TODO: change to throwing an exception?
    def select_players_num(self, selected_players: int = None) -> int:
        if selected_players is not None:
            assert selected_players == self._num_agents, \
                f'{__class__.__name__} with {self._num_agents} agents' \
                f' does not support selected number of players ({selected_players}).'
        else:
            selected_players = self._num_agents

        self._recorder = MultiRecorder(selected_players, self._manifest.metrics_names)
        return selected_players

    def initialize_episode(self, episode: int):
        self._agents_states = [_AgentRunningState() for __ in range(self._num_agents)]

        for agent, agent_state in zip(self._agents, self._agents_states):
            agent_state.start()
            agent.episode_started(episode)

    def do_start_episode(self, episode: int) -> bool:
        return any(agent.do_start_episode(episode) for agent in self._agents)

    def is_episode_running(self):
        return any(agent_state.running for agent_state in self._agents_states)

    def _react_to_states(self, training: bool, states: StatesInfo) -> Optional[Iterable[Any]]:
        """
        Reacts to states. Internal method that distributes the states and rewards (in case of training procedure)
        to the agents.

        :param training: a flag indicating if the rewards should be reported to the agents
        :param states: a StatesInfo object representing states and rewards for each agent
        :return: an iterable of actions selected by the algorithms or None if an episode has ended for all agents
        """
        if training:
            self.assert_training_supported()

        selected_actions = []
        for agent, state_info, agent_state in zip(self._agents, states, self._agents_states):
            action = self._react_to_state(training, agent, state_info, agent_state)
            selected_actions.append(action)

        if all(not agent_state.running for agent_state in self._agents_states):
            metrics = []
            for agent, agent_state in zip(self._agents, self._agents_states):
                if training:
                    agent.episode_ended(agent_state.state, agent_state.accumulated_reward)

                metrics.append((agent_state.episode_time, agent_state.num_actions, agent_state.accumulated_reward))

            self._recorder.add_episode_metrics(metrics, states.game_metrics)
            return None

        return selected_actions

    def react_to_states(self, states: StatesInfo) -> Optional[Iterable[Any]]:
        return self._react_to_states(False, states)

    def learn_from_states(self, states) -> Optional[Iterable[Any]]:
        return self._react_to_states(True, states)

    @property
    def metrics(self):
        return self._recorder


class MultiLearnerDistributor(BaseDistributor):
    """
    The class distributing states and rewards to a single multi-agent. A multi-agent is an algorithm capable
    or representing a number of agents and it must implement MultiLearner interface.
    This class inherits from the BaseDistributor class.
    """

    def __init__(self, learner: MultiLearner,
                 state_adapters=None, action_adapters=None, reward_adapters=None, verbose=None):
        """
        Initializes the class with a multi-agent algorithm - representing a number of agents
        and implements MultiLearner interface.
        State, action and reward adapters can be provided as an iterable of callables or a single callable.

        :param learner: an objects that implements MultiLearner interface representing a number of agents
        :param state_adapters: an iterable of state adapters or a single state adapter
        :param action_adapters: an iterable of action adapters or a single action adapter
        :param reward_adapters: an iterable of reward adapters or a single reward adapter
        :param verbose: the value representing the frequency of logging
        """
        super().__init__(state_adapters, action_adapters, reward_adapters, verbose)
        self._agent = learner

        self._num_players = None
        self._agents_states = None
        self._recorder = None

    def is_training_supported(self) -> bool:
        return True

    def initialize_players(self, manifest: Manifest):
        super(MultiLearnerDistributor, self).initialize_players(manifest)

        self._agent.initialize(manifest)

    def select_players_num(self, selected_players: int = None) -> int:
        if selected_players is None:
            selected_players = max(self._manifest.possible_players)

        self._num_players = selected_players
        self._recorder = MultiRecorder(selected_players, self._manifest.metrics_names)
        return selected_players

    def initialize_episode(self, episode: int):
        self._agents_states = [_AgentRunningState() for __ in range(self._num_players)]
        for agent_state in self._agents_states:
            agent_state.start()

        self._agent.set_players(range(self._num_players))
        self._agent.episode_started(episode)

    def do_start_episode(self, episode: int) -> bool:
        return self._agent.do_start_episode(episode)

    def is_episode_running(self):
        return any(agent_state.running for agent_state in self._agents_states)

    def _react_to_states(self, training: bool, states) -> Optional[Iterable[Any]]:
        """
        Reacts to states. Internal method that distributes the states and rewards (in case of training procedure)
        to the agents.

        :param training: a flag indicating if the rewards should be reported to the agents
        :param states: a StatesInfo object representing states and rewards for each agent
        :return: an iterable of actions selected by the algorithms or None if an episode has ended for all agents
        """
        if training:
            self.assert_training_supported()

        selected_actions = []
        for player, (state_info, agent_state) in enumerate(zip(states, self._agents_states)):
            self._agent.set_acting_player(player)
            action = self._react_to_state(training, self._agent, state_info, agent_state)
            selected_actions.append(action)

        if all(not agent_state.running for agent_state in self._agents_states):
            metrics = []
            for player, agent_state in enumerate(self._agents_states):
                if training:
                    self._agent.set_acting_player(player)
                    self._agent.episode_ended(agent_state.state, agent_state.accumulated_reward)

                metrics.append((agent_state.episode_time, agent_state.num_actions, agent_state.accumulated_reward))

            self._recorder.add_episode_metrics(metrics, states.game_metrics)
            return None

        return selected_actions

    def react_to_states(self, states) -> Optional[Iterable[Any]]:
        return self._react_to_states(False, states)

    def learn_from_states(self, states) -> Optional[Iterable[Any]]:
        return self._react_to_states(True, states)

    @property
    def metrics(self):
        return self._recorder
