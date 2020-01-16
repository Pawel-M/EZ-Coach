import abc
from collections import namedtuple
from typing import Tuple, Dict, Iterable, Sized
import numpy as np

import ezcoach.value as val
from ezcoach.communication import Communicator, IncomingMessageTypes, MessageAttributes
from ezcoach.exception import Disconnected
from ezcoach.log import log

StateInfo = namedtuple('StateInfo', 'state, accumulated_reward, running')


class StatesInfo:
    """
    The class representing the states, rewards and flags indicating if an episode is running for each agent
    interacting with the environment.
    """

    def __init__(self, states, accumulated_rewards, running, game_metrics):
        """
        Initializes the object with states, rewards (accumulated through the episode) and a flags indicating
        if an episode is running.

        :param states: a list or numpy array representing state observations for each agent
        :param accumulated_rewards: a reward signal accumulated through the episode for each agent
        :param running: a flag indicating if an episode is running for each agent
        :param game_metrics: a list of floats representing game metrics
        """
        self.states = states
        self.accumulated_rewards = accumulated_rewards
        self.running = running
        self.game_metrics = game_metrics

    def __getitem__(self, item):
        """
        Returns a StateInfo object representing state, accumulated reward and a running flag for the given agent.

        :param item: an index of the agent
        :return: a StateInfo object consisting of a state, accumulated reward and a running flag for an agent
        identified by the specified index (item)
        """
        return StateInfo(self.states[item, ...], self.accumulated_rewards[item], self.running[item])


class Manifest:
    """
    The class representing the information about the connected game. It consists of a name, description,
    definitions of state observations, actions that can be performed by the agents and a list
    of possible number of players simultaneously interacting with the environment.
    """

    def __init__(self, name, description, actions_definition, states_definition, possible_players, metrics_names):
        """
        Initializes the object with the name of the game, textual description, actions and states definitions
        and a list of supported number of players.

        :param name: a name of the game
        :param description: a textual description of the game
        :param actions_definition: a class inheriting from BaseValue representing the definition of agent actions
        :param states_definition: a class inheriting from BaseValue representing the state observations
        :param possible_players: a list of supported number of players
        :param metrics_names: a list of metrics names that the game will send at the end of the episode
        """
        self._name = name
        self._description = description
        self._actions_definition = actions_definition
        self._states_definition = states_definition
        self._possible_players = tuple(possible_players)
        self._metrics_names = metrics_names

    @property
    def name(self) -> str:
        """
        Returns a name of the environment as a string.

        :return: the name of the environment
        """
        return self._name

    @property
    def description(self) -> str:
        """
        Returns the textual description of the environment.

        :return: the description of the environment
        """
        return self._description

    @property
    def actions_definition(self) -> val.BaseValue:
        """
        Returns the definition of the actions that can be performed by the agents.

        :return: a BaseValue object defining the actions accepted by the environment
        """
        return self._actions_definition

    @property
    def states_definition(self) -> val.BaseValue:
        """
        Returns the definition of the state observations that the environment sends to the agents.

        :return: a BaseValue object defining the state observations
        """
        return self._states_definition

    @property
    def possible_players(self) -> Tuple[int]:
        """
        Returns the tuple of supported number of players simultaneously interacting with the environment.

        :return: a tuple of integers representing the possible number of players
        """
        return self._possible_players

    @property
    def metrics_names(self) -> Iterable[str]:
        """
        Returns the list of names of metrics sent by the game at the end of the episode.

        :return: a list of strings representing the names of metrics
        """
        return self._metrics_names

    def __str__(self):
        return f'''Game: {self.name}
Description: {self.description}
Players: {self.possible_players if len(self.possible_players) > 1 else self.possible_players[0]}
States: {self.states_definition}
Actions: {self.actions_definition}
Metrics: {"None" if self.metrics_names is None or len(self._metrics_names) == 0 else self.metrics_names}'''


class BaseEnvironment(abc.ABC):
    """
    The abstract class representing the environment that the agents can interact with.
    """

    def __init__(self, verbose=None):
        self._verbose = verbose

        self._manifest = None

        self._connected = False
        self._running = False
        self._states = None
        self._states_ready = False

    @abc.abstractmethod
    def connect(self):
        """
        Connects the environment.
        """

    @abc.abstractmethod
    def reset(self, num_players=None, options=None):
        """
        Resets the environment and starts a new episode.

        :param num_players: a number of players simultaneously interacting with the environment
        :param options: a dictionary representing the options passed to the environment
        """

    @abc.abstractmethod
    def act(self, actions):
        """
        Performs selected actions.

        :param actions: a list of actions to be performed
        """
        self._states_ready = False
        self._check_actions(actions)

    @abc.abstractmethod
    def stop(self):
        """
        Stops the episode.
        """

    def _check_actions(self, actions):
        """
        Checks the actions against the manifest of the environment.

        :param actions: a list of actions to be checked
        :return: True if actions are correct, False otherwise
        """
        if not all(self._manifest.actions_definition.contains(action) or action is None for action in actions):
            raise ValueError(f'Actions {actions} not compatible with environment')

    def obtain_states(self) -> StatesInfo:
        """
        Returns the state observations as a StatesInfo object representing state observations, rewards,
        and running flag fo reach agent. States are cleared after this method is invoked.

        :return: a StatesInfo object representing state observations, rewards and running flag for each agent
        """
        return self._states

    @property
    def states_ready(self):
        """
        Returns True if there are states info to be obtained. Otherwise it returns False.

        :return: True if there are states to be obtained, False otherwise
        """
        return self._states_ready and self._states is not None

    @property
    def connected(self):
        """
        Indicated if the environment has been connected.

        :return: True if the environment has been connected, False otherwise
        """
        return self._connected

    @property
    def manifest(self):
        """
        The manifest of the environment. Manifest provides all the information about the environment necessary
        to design an agent interacting with it.

        :return: a Manifest object defining the environment
        """
        return self._manifest


class RemoteEnvironment(BaseEnvironment):
    """
    The class representing the environment that is running in separate thread. It needs the Communicator to send
    and receive messages with the process. It inherits from the BaseEnvironment.
    """

    def __init__(self, communicator: Communicator = None, verbose=None):
        """
        Initializes the object with the communicator used to exchange messages with the process running the game.

        :param communicator: a Communicator object
        :param verbose: the value representing the frequency of logging
        """
        super(RemoteEnvironment, self).__init__(verbose)

        if communicator is None:
            communicator = Communicator.with_tcp_connection()

        self._communicator = communicator

    def connect(self):
        self._communicator.start()

        if self._connected:
            log('Environment already connected', self._verbose, level=2)
            return

        self._communicator.connect()

        while not self._connected:
            self._update()

        log('Environment connected', self._verbose, level=2)

    def reset(self, num_players=None, options=None):
        if num_players is None:
            num_players = self._manifest.possible_players[0]

        self._running = False
        self._states = None

        self._communicator.send_start(num_players, options)
        while not self.states_ready:
            self._update()
        else:
            self._running = True
            log(f'Environment reset for {num_players} players.', self._verbose, level=2)

    def act(self, actions):
        log(f'Environment acting: {actions}', self._verbose, level=2)
        self._states_ready = False
        self._check_actions(actions)
        self._communicator.send_actions(actions)
        while not self.states_ready:
            self._update()

        log(f'Environment states are ready: {self._states}', self._verbose, level=2)

    def stop(self):
        self._communicator.send_stop()
        while self._running:
            self._update()

    def _update(self):
        """
        Obtains the messages from the communicator and invokes parse_messages method.
        """
        messages = self._communicator.get_messages()
        self._parse_messages(messages)

    def _parse_messages(self, messages):
        """
        Parses the messages received from the game.

        :param messages: list of messages received from the game
        """
        state_message = None
        num_state_messages = 0
        for message in messages:
            log(f'Environment received message {message}', self._verbose, level=3)
            message_type = message[MessageAttributes.TYPE]
            if message_type == IncomingMessageTypes.STATE:
                num_state_messages += 1
                state_message = message

            else:
                handling_method = getattr(self, '_parse_' + message_type)
                handling_method(message)

        if state_message is not None:
            if num_state_messages > 1:
                log('Warning!!!!! Received multiple state messages - consider sending state less frequent.',
                    self._verbose, level=2)

            self._parse_states(state_message)

    def _parse_manifest(self, message):
        """
        Parses the manifest message and sets the manifest attribute according to the message.

        :param message: a message containing manifest
        """
        name = message[MessageAttributes.NAME]
        description = message[MessageAttributes.DESCRIPTION]
        actions_definition = val.from_json(message[MessageAttributes.ACTIONS])
        states_definition = val.from_json(message[MessageAttributes.STATES])
        metrics_names = message[MessageAttributes.METRICS_NAMES]
        possible_players = message[MessageAttributes.PLAYERS]

        self._manifest = Manifest(name, description, actions_definition, states_definition,
                                  possible_players, metrics_names)
        self._connected = True

        log(f'Connected to a game with manifest:\n{self._manifest}', self._verbose, level=1)

    def _parse_disconnected(self, message):
        """
        Parses a disconnected message and rises the Disconnected exception.

        :param message: a disconnected message
        """
        log(f'disconnected - message: {message}', self._verbose, level=1)
        self._connected = False
        raise Disconnected()

    def _parse_states(self, states_message):
        """
        Parses a states message and sets the states attribute according to the message.

        :param states_message: a states message
        """
        # self._running = True
        raw_states = states_message[MessageAttributes.STATES]
        states = self._manifest.states_definition.parse(raw_states)
        accumulated_rewards = np.array(states_message[MessageAttributes.ACCUMULATED_REWARDS])
        running = np.array(states_message[MessageAttributes.RUNNING])
        metrics = tuple(states_message[MessageAttributes.METRICS])

        self._states = StatesInfo(states, accumulated_rewards, running, metrics)
        self._states_ready = True
