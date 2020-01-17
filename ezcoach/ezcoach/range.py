import typing
from numbers import Number

import numpy as np

_minimum = min
_maximum = max
_length = len


_range_classes = []
_range_classes_names = []


def range_definition(definition):
    """
    Registers class as a range definition. It must inherit from Range class.

    :param definition: a class to registered
    :return: the provided class without any changes
    """
    _range_classes.append(definition)
    _range_classes_names.append(definition.__name__)
    return definition


@range_definition
class Range:
    """
    The class representing the range of a value. It is limited by the minimum and maximum values.
    """
    @classmethod
    def from_len(cls, len):
        """
        Creates the Range object for the list of given length.

        :param len: the length of a list
        :return: a Range object
        """
        return Range(min=0, max=int(len) - 1)

    @classmethod
    def from_sized(cls, sized: typing.Sized):
        """
        Creates the Range object based on the list or other Sized type.

        :param sized: a Sized object on which the Range object will be based
        :return: a Range object
        """
        return Range(min=0, max=_length(sized) - 1)

    @classmethod
    def from_json(cls, json):
        """
        Creates the Range object based on the JSON-like dictionary if the JSON represents the class.
        Raises the ValueError if provided JSON is not representing the class.

        :param json: a JSON-like dictionary
        :return: a Range object
        """
        if json['type'] != __class__.__name__:
            raise ValueError('Type not recognised.')
        return cls(json['min'], json['max'])

    def __init__(self, min, max):
        """
        Initializes the object with minimum and maximum values.

        :param min: a minimum value
        :param max: a maximum value
        """
        self._min = _minimum(min, max)
        self._max = _maximum(min, max)
        self._range = max - min
        self._half_range = self._range / 2
        self._is_int = isinstance(min, int) and isinstance(max, int)

    def contains(self, value):
        """
        Checks if a provided value is contained in the range.

        :param value: a value to be checked
        :return: True if value is in the Range, False otherwise
        """
        return self._min <= value <= self._max

    def random(self, size=None):
        """
        Returns a random value from the range. If size is provided, a random numpy array of this size is returned.

        :param size: a size of a numpy array
        :return: a random value or a random numpy array if a size parameter is provided
        """
        size = (size, 1) if isinstance(size, int) else size
        if self._is_int:
            return np.random.randint(self._min, self._max + 1, size=size)

        return np.random.random(size) * self._range + self._min

    def normalize(self, value, zero_centered=True):
        """
        Normalizes the given value based on the range.

        :param value: a value to be normalized
        :param zero_centered: if True values from range [-1, 1] are returned, else [0, 1]
        :return: a normalized value
        """
        if zero_centered:
            return (value - self._min - self._half_range) / self._half_range
        else:
            return (value - self._min) / self._range

    @property
    def min(self):
        """
        Returns the lower bound of the range.

        :return: a minimum value
        """
        return self._min

    @property
    def max(self):
        """
        Returns the upper bound of the range.

        :return: a maximum value
        """
        return self._max

    def to_json(self):
        """
        Creates the dictionary that can be converted to a JSON object based on the range.

        :return: a dictionary that can be converted to JSON object
        """
        return {'type': 'Range',
                'min': self._min,
                'max': self._max}

    def __str__(self):
        return f'Range({self._min}, {self._max})'


@range_definition
class UnboundRange(Range):
    """
    The class representing unbound range. It inherits from Range class.
    """

    _instance = None
    @classmethod
    def instance(cls):
        """
        Creates the instance of the UnboundRange class if invoked for the first time then returns the instance.

        :return: the instance of the UnboundRange class
        """
        if cls._instance is None:
            cls._instance = UnboundRange()
        return cls._instance

    @classmethod
    def from_json(cls, json):
        """
        Creates the UnboundRange object based on the JSON-like dictionary if the JSON represents the class.
        Raises the ValueError if provided JSON is not representing the class.

        :param json: a JSON-like dictionary
        :return: a Range object
        """
        if json['type'] != cls.__name__:
            raise ValueError('Type not recognised.')
        return cls.instance()

    def __init__(self):
        inf = float('inf')
        super().__init__(-inf, inf)

    def contains(self, value):
        return isinstance(value, Number)

    def random(self, size=None):
        size = (size, 1) if isinstance(size, int) else size
        return np.random.randn(size)

    def normalize(self, value, zero_centered=True):
        return value

    def to_json(self):
        return {'type': self.__class__.__name__}

    def __str__(self):
        return 'UnboundRange()'


@range_definition
class BoolRange(Range):
    """
    The class representing a range of boolean type.
    """
    _instance = None

    @classmethod
    def instance(cls):
        """
        Creates the instance of the BoolRange class if invoked for the first time then returns the instance.

        :return: the instance of the BoolRange class
        """
        if cls._instance is None:
            cls._instance = UnboundRange()
        return cls._instance

    @classmethod
    def from_json(cls, json):
        """
        Creates the BoolRange object based on the JSON-like dictionary if the JSON represents the class.
        Raises the ValueError if provided JSON is not representing the class.

        :param json: a JSON-like dictionary
        :return: a Range object
        """
        if json['type'] != cls.__name__:
            raise ValueError('Type not recognised.')
        return cls.instance()

    def __init__(self):
        super(BoolRange, self).__init__(0, 1)

    def contains(self, value):
        return isinstance(value, bool)

    def random(self, size=None):
        size = (size, 1) if isinstance(size, int) else size
        return np.random.choice([True, False], size=size)

    def to_json(self):
        return {'type': self.__class__.__name__}

    def __str__(self):
        return 'BoolRange()'


def from_json(json):
    """
    Parses the JSON-like dictionary and creates a range definition. Checks the classes marked with
    the @range_definition class annotation.
    If no corresponding range class exist ValueError will be raised.

    :param json: a JSON-like dictionary
    :return: an object of the class inheriting from Range
    """
    if json['type'] not in _range_classes_names:
        raise ValueError(f'Type {json["type"]} not recognised')

    cls = _range_classes[_range_classes_names.index(json['type'])]
    return cls.from_json(json)
