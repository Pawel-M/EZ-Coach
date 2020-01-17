"""
The agent module contains three abstract classes that are subclassed in order to create algorithms.
The classes are:

* Player - for an algorithm that cannot learn and can only play
* Learner - for a learning algorithm controlling a single agent
* MultiLearner - for a learning algorithm of controlling a number of agents
"""
import abc
from typing import List, Iterable

from ezcoach.enviroment import Manifest


class Player(abc.ABC):
    """
    The abstract class representing a playing agent. It can be initialized with the manifest of the game
    and can react to states by selecting actions.
    Both methods are empty and must be implemented in the concrete class.
    A class that inherits from the Player class can be used with the Runner's test procedure.
    """

    @abc.abstractmethod
    def initialize(self, manifest: Manifest):
        """
        Initializes the object with the manifest that describe the game.

        :param manifest: a Manifest class obtained from the environment.
        """

    @abc.abstractmethod
    def act(self, state):
        """
        Selects an action to be performed in the given state.

        :param state: a state received from the environment
        :return: an action compliant with the manifest provided in initialize method
        """

    @classmethod
    def __subclasshook__(cls, obj):
        if cls is Player:
            methods = ('initialize', 'act')

            if all(any(method in superclass.__dict__
                       for superclass in obj.__mro__)
                   for method in methods):
                return True

        return NotImplemented


class Learner(Player):
    """
    The abstract class representing an agent that is capable of learning. It inherits from the Player class
    and thus it is capable of playing.
    Only do_start_episode method must be implemented. Other methods can be left unimplemented and consequently empty.
    Rewards are received on the step basis in receive_reward method and on episode basis with episode_ended method.
    Methods that ensure persistence are added for convenience.
    An agent derived from Learner can be used in both training and testing procedures.
    """

    @abc.abstractmethod
    def do_start_episode(self, episode: int) -> bool:
        """
        Decides if next episode should be started.

        :param episode: the number of an episode to be started (starting from 1)
        :return: the decision if the next episode should be started
        """

    def episode_started(self, episode: int):
        """
        Informs the algorithm that the episode was started.

        :param episode: the number of the started episode (starting from 1)
        """

    def receive_reward(self, previous_state, action, reward: float, accumulated_reward: float, next_state):
        """
        Receives a reward from an environment.

        :param previous_state: the state that precedes the reward
        :param action: the action that precedes the reward
        :param reward: the numerical reward signal
        :param accumulated_reward: the reward accumulated during the current episode
        :param next_state: the state that follow the reward
        """

    def episode_ended(self, terminal_state, accumulated_reward):
        """
        Receives the accumulated reward for an episode. If a discount is used this value should be ignored
        and the actual reward should be calculated using receive_reward method during the episode.

        :param terminal_state: the last state of the episode
        :param accumulated_reward: the accumulated reward assuming no discount
        """

    @classmethod
    def __subclasshook__(cls, obj):
        if cls is Learner:
            methods = ('initialize', 'act',
                       'do_start_episode', 'episode_started', 'receive_reward', 'episode_ended')

            if all(any(method in superclass.__dict__
                       for superclass in obj.__mro__)
                   for method in methods):
                return True

        return NotImplemented


class MultiLearner(Learner):
    """
    The class representing a learning algorithm capable of controlling a number of agents.
    It inherits from Learner class. The list of player numbers is provided in set_players method before each episode.
    The number identifying currently acting player is set in set_acting_player method which is invoked before
    act and receive_reward methods during an episode and before episode_ended method at the end of an episode.
    """

    @abc.abstractmethod
    def set_players(self, players: Iterable[int]):
        """
        Informs the learner about the players that it will control.

        :param players: an iterable of numbers identifying players
        """

    @abc.abstractmethod
    def set_acting_player(self, player):
        """
        Sets the current player that will act, receive reward and end episode.

        :param player: a number identifying the acting player
        """

    @classmethod
    def __subclasshook__(cls, obj):
        if cls is MultiLearner:
            methods = ('initialize', 'act',
                       'do_start_episode', 'episode_started', 'receive_reward', 'episode_ended',
                       'set_players', 'set_acting_player')

            if all(any(method in superclass.__dict__
                       for superclass in obj.__mro__)
                   for method in methods):
                return True

        return NotImplemented
