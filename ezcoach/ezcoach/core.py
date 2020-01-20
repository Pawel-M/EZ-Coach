"""
This module contains the main class of the EZ-Coach framework, namely, the Runner class.
This class is used to perform training and testing procedures. In order to operate, Runner must be initialized
with the agent or a list of agents. Agents must subclass one of the three classes defined in the ezcoach.agent module:

* Player,
* Learner,
* MultiLearner.

Use train or play methods to conduct training or testing procedures.

"""

import time
from enum import Enum
from typing import Union, Iterable, Dict

from ezcoach.agent import MultiLearner, Player, Learner
from ezcoach.distributor import MultiLearnerDistributor, SingleAgentDistributor, AgentListDistributor
from ezcoach.enviroment import RemoteEnvironment, RemoteEnvironment
from ezcoach.exception import Disconnected
from ezcoach.log import log


class Mode(Enum):
    """
    The enum representing two procedures supported by the framework: playing and training.
    """
    Playing = 0
    Training = 1


def _assert_num_players_supported(num_players: int, possible_players: Iterable[int]):
    """
    Asserts if the provided number of players is supported by the game.

    :param num_players: a selected number of players
    :param possible_players: an iterable of supported number of players
    """

    # TODO: change throwing an error
    assert num_players in possible_players, f'Selected number of players {num_players}' \
                                            f' is not supported by the environment' \
                                            f' (possible number of players: {possible_players})'


# TODO: remove or change metrics
# TODO: add a recorder property passing the distributor recorder
class Runner:
    """
    The main class of the EZ-coach framework. It manages the training and testing procedures
    and is the main entry point for users. Algorithms are provided in the constructor.
    User can provide a single algorithm or a list (iterable) of algorithms to be used
    in the training or testing procedures. If the algorithm provided is a Player instance than it can only be used
    in testing procedures. Use algorithms that inherit from Learner or MultiLearner in order to use them
    in training procedures. Multi-agent procedures can be used if an iterable of algorithms
    representing agents is provided or if MultiLearner is provided as a single algorithm.
    The environment can optionally be provided in the constructor. If the environment is not provided the Runner
    will try to connect to the game using default parameters.
    Adapters for states, actions and rewards can be provided as a callable of a list of callables.
    Training procedure is initiated using the train method and testing testing is initiated using the play method.
    Metrics are gathered during both procedures and are available through the metrics property.
    """

    def __init__(self,
                 agent: Union[Player, Iterable[Player]],
                 environment: RemoteEnvironment = None,
                 state_adapters=None,
                 action_adapters=None,
                 reward_adapters=None,
                 verbose=None):
        """
        Initializes the runner with the algorithm or an iterable of algorithms and optionally with the environment.
        If a single agent is provided than a list of agents must be left as None. Similarly if the list of agents
        is provided than the single agent parameter must be left as None. If the environment is not provided
        than the default parameters will be used to create an environment.
        States, actions and rewards adapters can be provided as an iterable of callables or a single callable.

        :param agent: an algorithm implementing Player interface representing a single agent
        :param environment: an environment to be used in training and testing procedures
        :param state_adapters: an iterable of state adapters or a single state adapter
        :param action_adapters: an iterable of action adapters or a single action adapter
        :param reward_adapters: an iterable of reward adapters or a single reward adapter
        :param verbose: the value representing the frequency of logging
        """

        # TODO: change to an error?
        assert agent is not None, 'Provide single agent or list of agents'

        self._agent = agent
        self._state_adapters = state_adapters
        self._action_adapters = action_adapters
        self._reward_adapters = reward_adapters
        self._verbose = verbose

        if isinstance(self._agent, Iterable):
            self._distributor = AgentListDistributor(self._agent, self._state_adapters, verbose=self._verbose)
        elif isinstance(self._agent, MultiLearner):
            self._distributor = MultiLearnerDistributor(self._agent, self._state_adapters, verbose=self._verbose)
        else:
            self._distributor = SingleAgentDistributor(self._agent, self._state_adapters, verbose=self._verbose)

        if environment is not None:
            self._environment = environment
        else:
            self._environment = RemoteEnvironment(verbose=verbose)

    def play(self, num_episodes=1, options: Dict[str, str] = None):
        """
        Starts the testing procedure using agent or agents provided in the constructor.
        If an iterable of agents or a single MultiLearner agent was provided and the environment supports
        multi-agent training than it will be used. Otherwise the single-agent training will be performed.
        The metrics gathered during the testing procedure can be accessed using metrics property.

        :param num_episodes: a number of episodes to be run
        :param options: a dictionary representing the options sent to the environment
        """
        start_time = time.time()

        try:
            self._run(Mode.Playing, num_episodes=num_episodes, options=options)
        except KeyboardInterrupt:
            log(f'Playing interrupted by user.', level=1)
            self._environment.stop()
        except Disconnected:
            log(f'Disconnected from environment.', level=1)
        except ConnectionRefusedError:
            log(f'Error: Cannot connect to a game process. Make sure that the game is running.', level=0)
        else:
            log(f'Playing completed in {time.time() - start_time}s.', self._verbose, level=1)

    def train(self, num_players: int = None, options: Dict[str, str] = None):
        """
        Starts the training procedure using agent or agents provided in the constructor.
        This method will throw an error if training is not supported by the provided agents.
        Agents must implement Learner to be compatible with the training procedure.
        Number of players can optionally be provided. If the number of players is not provided the maximum supported
        number of players will be selected. Options in the form of dictionary can be provided to be sent
        to the environment at the start of each episode.
        The metrics gathered during the training procedure can be accessed by the metrics property.

        :param num_players: a number of players simultaneously interacting with the environment
        :param options: a dictionary representing the options sent to the environment
        """

        self._distributor.assert_training_supported()
        start_time = time.time()

        try:
            self._run(Mode.Training, num_players=num_players, options=options)
        except KeyboardInterrupt:
            log(f'Training interrupted by user.', level=1)
            self._environment.stop()
        except Disconnected:
            log(f'Disconnected from environment.', level=1)
        except ConnectionRefusedError:
            log(f'Error: Cannot connect to a game process. Make sure that the game is running.', level=0)
        else:
            log(f'Training completed in {round(time.time() - start_time)}s.', self._verbose, level=1)

    def _run(self, mode: Mode, num_episodes=None, num_players: int = None, options: Dict[str, str] = None):
        """
        Starts the training or testing procedure identified byt the mode enum.

        :param mode: an enum identifying the procedure
        :param num_episodes: a number of episodes used in the testing procedure
        :param num_players: a number of players used in the training procedure
        :param options: a dictionary representing options sent to the environment
        """
        self._environment.connect()
        self._distributor.initialize_players(self._environment.manifest)

        num_players = self._distributor.select_players_num(num_players)
        _assert_num_players_supported(num_players, self._environment.manifest.possible_players)

        episode = 0
        while (mode is Mode.Playing and episode < num_episodes
               or mode is mode.Training and self._distributor.do_start_episode(episode + 1)):

            episode += 1
            self._environment.reset(num_players, options)
            self._distributor.initialize_episode(episode)
            while self._distributor.is_episode_running():
                if mode is Mode.Playing:
                    actions = self._distributor.react_to_states(self._environment.obtain_states())
                else:  # mode is Mode.Learning
                    actions = self._distributor.learn_from_states(self._environment.obtain_states())

                if actions is not None:
                    self._environment.act(actions)
            else:
                log(f'Episode {episode} ended.', self._verbose, level=2)

    @property
    def metrics(self):
        """
        Returns the metrics gathered during the training or testing procedures.
        If the new procedure is started the existing metrics will be lost.

        :return: a Recorder class containing the metrics gathered during the current procedure
        """
        return self._distributor.metrics

    @property
    def agent(self):
        """
        Returns the agent initialized in the constructor.
        :return: the agent (or agents) operated by the runner
        """
        return self._agent


def train(agent: Union[Player, Iterable[Player]],
          environment: RemoteEnvironment = None,
          num_players: int = None,
          options: Dict[str, str] = None,
          state_adapters=None,
          action_adapters=None,
          reward_adapters=None,
          verbose=None):
    """
    Creates runner with the passed parameters and starts the training process.
    Returns the created runner when the process is finished.

    :param agent: an algorithm implementing Player interface representing a single agent
    :param environment: an environment to be used in training and testing procedures
    :param num_players: a number of players simultaneously interacting with the environment
    :param options: a dictionary representing the options sent to the environment
    :param state_adapters: an iterable of state adapters or a single state adapter
    :param action_adapters: an iterable of action adapters or a single action adapter
    :param reward_adapters: an iterable of reward adapters or a single reward adapter
    :param verbose: the value representing the frequency of logging
    :return: the runner instance used to conduct the training procedure
    """
    runner = Runner(agent, environment, state_adapters, action_adapters, reward_adapters, verbose)
    runner.train(num_players, options)
    return runner


def play(agent: Union[Player, Iterable[Player]],
         environment: RemoteEnvironment = None,
         num_episodes=1,
         options: Dict[str, str] = None,
         state_adapters=None,
         action_adapters=None,
         reward_adapters=None,
         verbose=None):
    """
    Creates runner with the passed parameters and starts the testing process.
    Returns the created runner when the process is finished.
    :param agent: an algorithm implementing Player interface representing a single agent
    :param environment: an environment to be used in training and testing procedures
    :param num_episodes: a number of episodes to be run
    :param options: a dictionary representing the options sent to the environment
    :param state_adapters: an iterable of state adapters or a single state adapter
    :param action_adapters: an iterable of action adapters or a single action adapter
    :param reward_adapters: an iterable of reward adapters or a single reward adapter
    :param verbose: the value representing the frequency of logging
    :return: the runner instance used to conduct the testing procedure
    """
    runner = Runner(agent, environment, state_adapters, action_adapters, reward_adapters, verbose)
    runner.play(num_episodes, options)
    return runner
