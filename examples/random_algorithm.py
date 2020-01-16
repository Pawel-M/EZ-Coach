from ezcoach import Runner
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


if __name__ == '__main__':
    random_agent = RandomAlgorithm(10)
    runner = Runner(random_agent, verbose=1)
    runner.train()
