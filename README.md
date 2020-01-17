# EZ-Coach
EZ-Coach is an open-source framework written in Python for training and testing machine learning algorithms as game controllers. The core concept is to connect algorithms to games (or virtual environment in general) built in various technologies. Currently the plugin for integrating games is available only for Unity, but the support for other game engines can be added. This project is a part of the engineering thesis written at the Wrocław University of Science and Technology.

Algorithms must implement one of the three protocols (Player, Learner or MultiLearner) defined in the ezcoach.agent module. In the following example the random algorithm is created. This algorithm ignores states and rewards, and selects random actions.

```python
from ezcoach.agent import Learner
from ezcoach.enviroment import Manifest

class RandomAlgorithm(Learner):
  def __init__(self, num_episodes):
    self._num_episodes = num_episodes
    self._manifest: Manifest = None

  def do_start_episode(self, episode: int) -> bool:
    return episode <= self._num_episodes

  def initialize(self, manifest: Manifest):
    self._manifest = manifest

  def act(self, state):
    return self._manifest.actions_definition.random()
```

To train the algorithm the Runner class is used. The algorithm is passed in the constructor. The training and testing procedures can only be performed if the game process is running. The following code initiates the training procedure for the random algorithm defined above:

```python
from ezcoach import Runner

random_agent = RandomAlgorithm(num_episodes=10)
runner = Runner(random_agent, verbose=1)
runner.train()
```
