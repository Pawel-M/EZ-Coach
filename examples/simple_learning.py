import abc
import pickle
import random
from collections import defaultdict, namedtuple
from typing import Iterable, Tuple

import numpy as np

import ezcoach.agent
from ezcoach.enviroment import Manifest
from ezcoach.value import IntList, IntValue

import tensorflow
import tensorflow.keras as kr


class QFunction(abc.ABC):
    @abc.abstractmethod
    def get_max_action_value(self, state) -> float:
        """

        :param state:
        :return:
        """

    @abc.abstractmethod
    def get_max_actions(self, state):
        """

        :param state:
        :return:
        """

    @abc.abstractmethod
    def get_value(self, state, action) -> float:
        """

        :param state:
        :param action:
        :return:
        """

    @abc.abstractmethod
    def update_values(self, states, actions, values, lr):
        """

        :param states:
        :param actions:
        :param values:
        :param lr:
        :return:
        """

    @abc.abstractmethod
    def save(self, file_name):
        """

        :param file_name:
        :return:
        """

    @abc.abstractmethod
    def load(self, file_name):
        """

        :param file_name:
        :return:
        """


class DictQFunction(QFunction):
    def __init__(self, num_actions, default_value=0., default_fn=None):
        self.actions = tuple(range(num_actions))

        if default_fn is None:
            def default_fn(): return default_value

        self.default_fn = default_fn
        self._values = {}

    def get_max_action_value(self, state) -> float:
        state = tuple(state)
        values = []
        for action in self.actions:
            if (state, action) not in self._values:
                values.append(self.default_fn())
            else:
                values.append(self._values[(state, action)])

        return max(values) if len(values) > 0 else 0.

    def get_max_actions(self, state):
        state = tuple(state)
        action_values = []
        for action in self.actions:
            if (state, action) not in self._values:
                action_values.append((action, self.default_fn()))
            else:
                action_values.append((action, self._values[(state, action)]))

        if not action_values:
            return None

        max_action_value = max(action_values, key=lambda x: x[1])[1]
        return tuple(a for (a, v) in action_values if v >= max_action_value)

    def get_value(self, state, action) -> float:
        state = tuple(state)
        state_action = state, action
        self._check_state_action(state, action)
        if state_action in self._values:
            return self._values[state_action]
        else:
            return self.default_fn()

    def set_value(self, state, action, value):
        state = tuple(state)
        state_action = state, action
        self._check_state_action(state, action)
        self._values[state_action] = value

    def update_values(self, states, actions, values, lr):
        for state, action, value in zip(states, actions, values):
            try:
                action = action[0]
            except (TypeError, IndexError):
                pass

            try:
                value = value[0]
            except (TypeError, IndexError):
                pass

            state = tuple(state)
            old_value = self.get_value(state, action)
            updated_value = old_value + lr * (value - old_value)
            self._values[(state, action)] = updated_value
            # print('q_dict, update', state, action, value[0], updated_value)

    def save(self, file_name):
        with open(file_name, 'wb') as file:
            d = dict(self._values)
            pickle.dump(d, file)

    def load(self, file_name):
        with open(file_name, 'rb') as file:
            d = pickle.load(file)

        if d is None:
            # TODO: change to specific exception
            raise Exception('Unable to load from specified file.')

        print(d)
        self._values = dict(d)

    def _check_state_action(self, state, action):
        assert state is not None and action is not None, 'Provide state_action as (state, action) tuple.'

    def __repr__(self):
        r = '{' + ',\n'.join([f'({s}, {a}): {v}' for (s, a), v in self._values.items()]) + '}'
        r += f'\n ---- len: {len(self._values)}'
        return r


class NNQFunction(QFunction):
    def __init__(self, state_dim, num_actions, layer_sizes, train_epochs=1, memory_size=512):
        self.train_epochs = train_epochs
        self.memory_size = 0 if memory_size is None else memory_size

        inputs = kr.Input(state_dim)
        layer = inputs
        for layer_size in layer_sizes:
            layer = kr.layers.Dense(layer_size, activation='relu')(layer)
        # layer = kr.layers.Dense(64, activation='relu')(layer)
        outputs = kr.layers.Dense(num_actions, activation='linear')(layer)
        self.model = kr.Model(inputs=inputs, outputs=outputs, name='QNN')
        self.memory = None

    def get_max_action_value(self, state) -> float:
        action_values = self.model(state[np.newaxis, :])
        return np.max(action_values)

    def get_max_actions(self, state):
        state = state[np.newaxis, :].astype('float')
        action_values = self.model(state[np.newaxis, :])[0]
        max_actions = tuple(np.where(action_values == np.max(action_values))[1])
        # print(f'action_values: {action_values}, max actions: {max_actions}')
        print('qnn, max actions', max_actions, action_values.numpy())
        return max_actions

    def get_value(self, state, action) -> float:
        action_values = self.model(state[np.newaxis, :])[0]
        return action_values[action]

    def update_values(self, states, actions, values, lr):
        if self.memory_size > 0:
            if self.memory is None:
                self.memory = states, actions, values
            else:
                memory_size = max(states.shape[0], self.memory_size)
                states_memory = np.vstack((self.memory[0], states))[:memory_size]
                actions_memory = np.vstack((self.memory[1], actions))[:memory_size]
                values_memory = np.vstack((self.memory[2], values))[:memory_size]
                self.memory = states_memory, actions_memory, values_memory
                states = self.memory[0]
                actions = self.memory[1]
                values = self.memory[2]

        action_values = self.model(states).numpy()
        for i in range(states.shape[0]):
            action_values[i, actions[i]] = values[i]

        self.model.compile(loss=kr.losses.mean_squared_error,
                           optimizer=kr.optimizers.Adam(learning_rate=lr, beta_1=0.9, beta_2=0.999, amsgrad=False),
                           metrics=[kr.metrics.mse])
        print(states, values, actions, action_values)
        self.model.fit(states, action_values, batch_size=states.shape[0], epochs=self.train_epochs)

    def reset(self, states, value, num_actions, lr, epochs, bs):
        self.model.compile(loss=kr.losses.mean_squared_error,
                           optimizer=kr.optimizers.Adam(learning_rate=lr, beta_1=0.9, beta_2=0.999, amsgrad=False),
                           metrics=[kr.metrics.mse])
        action_values = value * np.ones((states.shape[0], num_actions))
        self.model.fit(states, action_values, batch_size=bs, epochs=epochs)

    def save(self, file_name):
        with open(file_name, 'wb') as file:
            d = dict(self._values)
            pickle.dump(d, file)

    def load(self, file_name):
        with open(file_name, 'rb') as file:
            d = pickle.load(file)

        if d is None:
            # TODO: change to specific exception
            raise Exception('Unable to load from specified file.')

        self._values = defaultdict(d)

    def __str__(self):
        return 'NNQFunction'
        # return f'NNQFunction:\n{self.model.summary()}'


class MonteCarloAlgorithm:
    def __init__(self, q: QFunction, alpha, gamma, epsilon, epsilon_greedy=True):
        self.q = q
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_greedy = epsilon_greedy

        self._states = []
        self._actions = []
        self._rewards = []

    def episode_started(self):
        self._states = []
        self._actions = []
        self._rewards = []

    def get_action(self, state, actions, progress):
        try:
            epsilon = self.epsilon[0] + progress * (self.epsilon[1] - self.epsilon[0])
        except TypeError:
            epsilon = self.epsilon

        if self.epsilon_greedy and random.random() < epsilon:
            return random.choice(actions)
        else:
            max_actions = self.q.get_max_actions(state)
            if not max_actions:
                max_actions = actions

            return random.choice(max_actions)

    def report_reward(self, state, action, reward, next_state):
        self._states.append(state)
        self._actions.append(action)
        self._rewards.append(reward)

    def episode_ended(self, last_state):
        visited_state_actions = set()

        states = None
        actions = None
        values = None
        accumulated_reward = 0
        for state, action, reward in reversed(tuple(zip(self._states, self._actions, self._rewards))):
            if (tuple(state), action) in visited_state_actions:
                continue

            visited_state_actions.add((tuple(state), action))
            accumulated_reward = reward + self.gamma * accumulated_reward
            new_value = accumulated_reward

            states = state if states is None else np.vstack(
                (states, state))
            actions = action if actions is None else np.vstack((actions, action))
            values = new_value if values is None else np.vstack((values, new_value))

        self.q.update_values(states, actions, values, self.alpha)

    def __repr__(self):
        r = f'QLearning q: {self.q}'
        return r


class QLearningAlgorithm:
    def __init__(self, q: QFunction, alpha, gamma, epsilon, epsilon_greedy=True):
        self.q = q
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_greedy = epsilon_greedy

    def episode_started(self):
        pass

    def get_action(self, state, actions, progress):
        try:
            epsilon = self.epsilon[0] + progress * (self.epsilon[1] - self.epsilon[0])
        except TypeError:
            epsilon = self.epsilon

        if self.epsilon_greedy and random.random() < epsilon:
            return random.choice(actions)
        else:
            max_actions = self.q.get_max_actions(state)
            if not max_actions:
                return random.choice(actions)

            return random.choice(max_actions)

    def report_reward(self, state, action, reward, next_state):
        new_value = reward + self.gamma * self.q.get_max_action_value(next_state)
        self.q.update_values([state], [action], [new_value], self.alpha)

    def episode_ended(self, last_state):
        pass

    def __repr__(self):
        r = f'QLearning q: {self.q}'
        return r


class LearningAdapter(ezcoach.agent.Learner):
    def __init__(self, learning_algorithm, episodes):
        super().__init__()

        self.learning_algorithm = learning_algorithm
        self._episodes = episodes

        self._manifest = None
        self._current_episode = -1
        self._actions = None

    def initialize(self, manifest: Manifest):
        self._manifest = manifest

        if isinstance(self._manifest.actions_definition, IntValue):
            actions_definition = self._manifest.actions_definition
            self._actions = tuple(range(actions_definition.range.min, actions_definition.range.max + 1))

    def do_start_episode(self, episode: int) -> bool:
        return episode <= self._episodes

    def episode_started(self, episode: int):
        self._current_episode = episode
        self.learning_algorithm.episode_started()

    def act(self, state):
        action_indices = tuple(range(len(self._actions)))
        progress = self._current_episode / self._episodes
        selected_action_index = self.learning_algorithm.get_action(state, action_indices, progress)
        return self._actions[selected_action_index]

    def receive_reward(self, previous_state, action, reward, accumulated_reward, next_state):
        self.learning_algorithm.report_reward(previous_state, self._actions.index(action), reward, next_state)

    def episode_ended(self, terminal_state, accumulated_reward):
        self.learning_algorithm.episode_ended(terminal_state)

    def save(self, file_name: str):
        self.learning_algorithm.q.save(file_name)

    def load(self, file_name: str):
        self.learning_algorithm.q.load(file_name)

    def __repr__(self):
        return f'QLearningAdapter(\n{self.learning_algorithm})'


learner = namedtuple('Learner', 'agent')


class QLearningMultiAdapter(ezcoach.agent.MultiLearner):

    def __init__(self, learning_algorithm_fn, episodes):
        self._learning_algorithm_fn = learning_algorithm_fn
        self._episodes = episodes

        self._current_episode = None
        self._acting_player = None
        self._acting_learner = None

        self._manifest = None

        self._actions = None
        self._learners = None

    def initialize(self, manifest: Manifest):
        self._manifest = manifest
        if isinstance(manifest.actions_definition, IntValue):
            actions_definition = self._manifest.actions_definition
            self._actions = tuple(range(actions_definition.range.min, actions_definition.range.max + 1))

    def do_start_episode(self, episode: int) -> bool:
        return episode <= self._episodes

    def set_players(self, players: Iterable[int]):
        self._learners = {player: learner(self._learning_algorithm_fn()) for player in players}

    def episode_started(self, episode: int):
        self._current_episode = episode

        for l in self._learners.values():
            l.agent.episode_started()

    def set_acting_player(self, player):
        self._acting_player = player
        self._acting_learner = self._learners[player]

    def act(self, state):
        return self._acting_learner.agent.get_action(state, self._actions)

    def receive_reward(self, previous_state, action, reward, accumulated_reward, next_state):
        self._acting_learner.agent.report_reward(previous_state, action, reward, next_state)

    def episode_ended(self, terminal_state, accumulated_reward):
        self._acting_learner.agent.episode_ended(terminal_state)

    def save(self, file_name: str):
        pass

    def load(self, file_name: str):
        pass

    def __repr__(self):
        return f'QLearningAdapter(\n{self._learners.values()})'
