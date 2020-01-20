"""
Classes introduced in this module represent the value definitions, and are used to define the state observations
and actions spaces. They are created during parsing of the game's manifest, which can be obtained from
the RemoteEnvironment class (ezcoach.environment module).
"""

import abc
import typing
from collections.abc import Iterable, Sized
from typing import Iterator

import numpy as np

import ezcoach.range

_range = range


# TODO: add __repr__ and __str__ to all value definitions
class BaseValue(abc.ABC, Iterable, Sized):
    """
    The abstract class representing the definition of a value. It consists of a textual description
    and a list of Range objects. It provides convenience methods like normalize, contains and random.
    """

    @abc.abstractmethod
    def contains(self, value) -> bool:
        """
        Checks if provided value is in the range or ranges in case of composite value. In case of composite value
        all components must be in their respective ranges.

        :param value: a value to be checked
        :return: True if the provided value is in range, False otherwise
        """

    @abc.abstractmethod
    def random(self, n=None, normalize=False):
        """
        Generates a random value compliant with the definition.

        :param n: a number of values to be generated
        :param normalize: a flag indicating if a normalized value should be generated
        :return: a random value compliant with the definition
        """

    def normalize(self, value, zero_centered=False):
        """
        Normalizes the provided value according to the value definition.

        :param value: a value to be normalized
        :param zero_centered: if True than returns values in range [-1, 1] else [0, 1]
        :return: a normalized value
        """
        for i, r in enumerate(self.ranges):
            value[..., i] = r.normalize(value[..., i])
        return value

    @property
    @abc.abstractmethod
    def ranges(self) -> typing.List[ezcoach.range.Range]:
        """
        Returns the ranges list.

        :return: a list of ranges
        """

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """
        Returns the textual description.

        :return: the textual description
        """

    def parse(self, raw_values):
        """
        Parses a raw value and returns the value as numpy array.

        :param raw_values: a raw value to be parsed
        :return: a numpy array
        """
        return np.array(raw_values)

    @abc.abstractmethod
    def to_json(self):
        """
        Converts the object to a JSON compliant dictionary.

        :return: a dictionary that can be converted to JSON object
        """

    def __str__(self):
        ranges_str = ''
        for range in self.ranges:
            ranges_str += str(range) + ', '

        ranges_str = ranges_str[:-2]
        return f'BaseValue({self.description}, ranges={ranges_str})'


_values_classes = []
_values_classes_names = []


def value_definition(definition):
    """
    Registers class as a value definition. It must implement BaseValue interface.

    :param definition: a class to registered
    :return: the provided class without any changes
    """
    assert issubclass(definition, BaseValue), f'A class definition must implement {BaseValue.__name__} interface.'
    _values_classes.append(definition)
    _values_classes_names.append(definition.__name__)
    return definition


@value_definition
class TypedList(BaseValue):
    """
    The abstract class representing a list of values of the different types. It inherits from the BaseValue class.
    Supported types are: int, float and bool
    """

    supported_types = {'int': int, 'float': float, 'bool': bool}

    @classmethod
    def from_json(cls, json):
        """
        Creates an instance of the class based on the JSON-like dictionary if the JSON represents the class.
        Raises the ValueError if provided JSON is not representing the class.

        :param json: a JSON-like dictionary
        :return: an instance of the class
        """
        if json['type'] != cls.__name__:
            raise ValueError('Type not recognised')

        types = (cls.supported_types[t] for t in json['types'])
        ranges = (ezcoach.range.from_json(r) for r in json['ranges'])
        return cls(types, ranges, json['description'])

    # TODO: change ot an exception
    def __init__(self, types: typing.Iterable[typing.Type], ranges: typing.Iterable[ezcoach.range.Range],
                 description: str = None):
        """
        Initializes the object with the list of types of elements, ranges and the textual description.
        The length of range objects indicates the length of the values.

        :param types: an iterable of types for all elements
        :param ranges: an iterable of Range objects corresponding to ranges of each element
        :param description: a textual description of the value
        """
        assert ranges is not None, 'Ranges must not be None. ' \
                                   'Use Iterable with UnboundRange or None to specify unbound value(s).'

        self._types = tuple(types)
        self._ranges = tuple(ranges)
        self._description = description

        assert len(self._types) == len(self._ranges), 'The length of types and ranges must be equal.'
        self._size = len(self._ranges)

        supported_type_values = self.supported_types.values()
        assert all(t in supported_type_values for t in self._types), f'Unsupported type.'

    def contains(self, value):
        if not isinstance(value, (Iterable, Sized)):
            return False

        if len(value) != self._size:
            return False

        if not all(isinstance(v, t) for v, t in zip(value, self._types)):
            return False

        return all((r is None or r.contains(v) for r, v in zip(self._ranges, value)))

    def random(self, n=None, normalize=False):
        result = np.hstack([r.random(n) for r in self._ranges])
        return self.normalize(result) if normalize else result

    def normalize(self, value, zero_centered=False):
        return np.hstack([r.normalize(v, zero_centered) for r, v in zip(self._ranges, value)])

    def __getitem__(self, item):
        return self._ranges[item]

    def __iter__(self):
        return self._ranges

    def __len__(self) -> int:
        return self._size

    @property
    def types(self):
        return self._types

    @property
    def ranges(self):
        return self._ranges

    @property
    def description(self):
        return self._description

    def to_json(self):
        json_dict = {'type': self.__class__.__name__,
                     'types': self._get_types_strings(),
                     'ranges': [r.to_json() for r in self._ranges],
                     'description': self._description}
        return json_dict

    def _get_types_strings(self):
        types = []
        for t in self.types:
            for k, v in self.supported_types.items():
                if t == v:
                    types.append(k)
                    break

        return types

    def __str__(self):
        types_and_ranges = ''
        for t, r in zip(self._types, self._ranges):
            types_and_ranges += f'    {t}:{r}\n'
        return f'TypedList: {self._description}\nElements:\n{types_and_ranges}'


class _SingleTypeList(TypedList, abc.ABC):
    """
    The abstract class representing a list of values of the same type. It inherits from the BaseValue class.
    It is a base class for IntList, FloatList and BoolList classes.
    """

    # TODO: change ot an exception
    def __init__(self, element_type: typing.ClassVar, ranges: typing.Iterable[ezcoach.range.Range],
                 description: str = None):
        """
        Initializes the list with the type fo elements, ranges and the textual description. The length of range objects
        indicates the length of the values.

        :param element_type: a type of all elements
        :param ranges: an iterable of Range objects corresponding to ranges of each element
        :param description: a textual description of the value
        """
        ranges_tuple = tuple(ranges)
        super().__init__((element_type for __ in ranges_tuple), ranges_tuple, description)

        self._element_type = element_type

    @property
    def element_type(self):
        return self._element_type

    def __str__(self):
        ranges = ''
        for r in self._ranges:
            ranges += f'    {r}\n'
        return f'{self.__class__.__name__}: {self._description}\nElements:\n{ranges}'


@value_definition
class IntList(_SingleTypeList):
    """
    The class representing a definition of a value in the form of list of integers. It inherits from TypedList class.
    """

    @classmethod
    def from_size(cls, size, range, description):
        """
        Returns the object initialized based on the size. It represents the value in the form of a list of given size
        where each element is in specified range.

        :param size: a size of the value
        :param range: a range for each element
        :param description: a textual description
        :return: an instance of the class
        """
        return cls((range for __ in _range(size)), description)

    @classmethod
    def from_json(cls, json):
        """
        Creates an instance of the class based on the JSON-like dictionary if the JSON represents the class.
        Raises the ValueError if provided JSON is not representing the class.

        :param json: a JSON-like dictionary
        :return: an instance of the class
        """
        if json['type'] != cls.__name__:
            raise ValueError('Type not recognised')
        return cls((ezcoach.range.from_json(r) for r in json['ranges']), json['description'])

    def __init__(self, ranges: typing.Iterable[ezcoach.range.Range], description: str = None):
        """
        Initializes the object with an iterable of ranges and a textual description. Defines the value in the form
        of an integer list with length equal to the length of provided ranges. Elements of the value are in range
        of corresponding Range objects.

        :param ranges: an iterable of Range objects
        :param description: a textual description
        """
        super(IntList, self).__init__(int, ranges, description)

    def __str__(self):
        ranges = ''
        for r in self._ranges:
            ranges += f'    {r}\n'
        return f'{self.__class__.__name__}: {self._description}\nElements:\n{ranges}'


@value_definition
class FloatList(_SingleTypeList):
    """
    The class representing a definition of a value in the form of list of floats. It inherits from TypedList class.
    """

    @classmethod
    def from_size(cls, size, range, description: str = None):
        """
        Returns the object initialized based on the size. It represents the value in the form of a list of given size
        where each element is in specified range.

        :param size: a size of the value
        :param range: a range for each element
        :param description: a textual description
        :return: an instance of the class
        """
        return cls((range for __ in _range(size)), description)

    @classmethod
    def from_json(cls, json):
        """
        Creates an instance of the class based on the JSON-like dictionary if the JSON represents the class.
        Raises the ValueError if provided JSON is not representing the class.

        :param json: a JSON-like dictionary
        :return: an instance of the class
        """
        if json['type'] != cls.__name__:
            raise ValueError('Type not recognised')
        return cls((ezcoach.range.from_json(r) for r in json['ranges']), json['description'])

    def __init__(self, ranges: typing.Iterable[ezcoach.range.Range], description: str = None):
        """
        Initializes the object with an iterable of ranges and a textual description. Defines the value in the form
        of a float list with length equal to the length of provided ranges. Elements of the value are in range
        of corresponding Range objects.

        :param ranges: an iterable of Range objects
        :param description: a textual description
        """
        super(FloatList, self).__init__(float, ranges, description)


@value_definition
class BoolList(_SingleTypeList):
    """
    The class representing a definition of a value in the form of list of floats. It inherits from TypedList class.
    """

    @classmethod
    def from_json(cls, json):
        """
        Creates an instance of the class based on the JSON-like dictionary if the JSON represents the class.
        Raises the ValueError if provided JSON is not representing the class.

        :param json: a JSON-like dictionary
        :return: an instance of the class
        """
        if json['type'] != cls.__name__:
            raise ValueError('Type not recognised')
        return cls(json['size'], json['description'])

    def __init__(self, size, description: str = None):
        """
        Initializes the object with a size and a textual description. Defines the value in the form of a bool list
        of a given size.

        :param size: a size (length) of the value
        :param description: a textual description
        """
        super(BoolList, self).__init__(bool, (ezcoach.range.BoolRange.instance() for __ in range(size)), description)

    # def to_json(self):
    #     return {'type': self.__class__.__name__,
    #             'size': self._size,
    #             'description': self._description}


class _SingleValue(BaseValue, abc.ABC):
    """
    The class representing a single value definition. It inherits from BaseValue class.
    It is a base class for IntValue, FloatValue and BoolValue classes.
    """

    def __init__(self, element_type: typing.ClassVar, range: ezcoach.range.Range, description: str = None):
        """
        Initializes the object with the type, range and a textual description.

        :param element_type: a Class type of the value
        :param range: a Range object
        :param description: a textual description
        """
        self._element_type = element_type
        self._range = range
        self._description = description

    def contains(self, value):
        if not isinstance(value, self._element_type):
            return False

        return self._range is None or self._range.contains(value)

    def random(self, n=None, normalize=False):
        result = self._range.random(n)
        return self.normalize(result) if normalize else result

    def normalize(self, value, zero_centered=True):
        return self._range.normalize(value, zero_centered)

    @property
    def range(self):
        """
        Returns a range of the value definition.

        :return: a Range object
        """
        return self._range

    @property
    def description(self):
        return self._description

    @property
    def ranges(self) -> typing.List[ezcoach.range.Range]:
        return [self._range]

    def __iter__(self) -> Iterator:
        return self.ranges

    def __len__(self) -> int:
        return 1

    def __str__(self):
        return f'{self.__class__.__name__}: {self._description}\n    {self._range}'


@value_definition
class IntValue(_SingleValue):
    """
    The class representing a definition of a single integer value. It inherits from SingleValue class.
    """

    @classmethod
    def from_json(cls, json):
        """
        Creates an instance of the class based on the JSON-like dictionary if the JSON represents the class.
        Raises the ValueError if provided JSON is not representing the class.

        :param json: a JSON-like dictionary
        :return: an instance of the class
        """
        if json['type'] != cls.__name__:
            raise ValueError('Type not recognised')
        return cls(ezcoach.range.from_json(json['range']), json['description'])

    def __init__(self, range: ezcoach.range.Range, description: str = None):
        """
        Initializes the object with a range and a textual description
        :param range: a Range object
        :param description: a textual description
        """
        super(IntValue, self).__init__(int, range, description)

    def to_json(self):
        return {
            'type': self.__class__.__name__,
            'range': self._range.to_json(),
            'description': self.description
        }


@value_definition
class FloatValue(_SingleValue):
    """
    The class representing a definition of a single floating-point value. It inherits from SingleValue class.
    """

    @classmethod
    def from_json(cls, json):
        """
        Creates an instance of the class based on the JSON-like dictionary if the JSON represents the class.
        Raises the ValueError if provided JSON is not representing the class.

        :param json: a JSON-like dictionary
        :return: an instance of the class
        """
        if json['type'] != cls.__name__:
            raise ValueError('Type not recognised')
        return cls(ezcoach.range.from_json(json['range']), json['description'])

    def __init__(self, range: ezcoach.range.Range, description: str = None):
        """
        Initializes the object with a range and a textual description.

        :param range: a Range object
        :param description: a textual description
        """
        super(FloatValue, self).__init__(float, range, description)

    def to_json(self):
        return {
            'type': self.__class__.__name__,
            'range': self._range.to_json(),
            'description': self.description
        }


@value_definition
class BoolValue(_SingleValue):
    @classmethod
    def from_json(cls, json):
        """
        Creates an instance of the class based on the JSON-like dictionary if the JSON represents the class.
        Raises the ValueError if provided JSON is not representing the class.

        :param json: a JSON-like dictionary
        :return: an instance of the class
        """
        if json['type'] != cls.__name__:
            raise ValueError('Type not recognised')
        return cls(json['description'])

    def __init__(self, description: str = None):
        """
        Initializes the object with a range and a textual description.

        :param range: a Range object
        :param description: a textual description
        """
        super(BoolValue, self).__init__(bool, ezcoach.range.BoolRange.instance(), description)

    def to_json(self):
        return {
            'type': self.__class__.__name__,
            'range': self._range.to_json(),
            'description': self.description
        }


@value_definition
class PixelList(BaseValue):
    """
    The class representing a definition of an image. It consists of dimensions of the image (width and height),
    a number of channels, a range of each pixel's channel, a numpy type and a textual description.
    There are common ranges that are defined, namely: bit8 (each value is an 8-bit integer) and normalized (each value
    is a normalized float).
    It inherits from BaseValue class.
    """
    DEFINED_RANGES = {
        'bit8': (ezcoach.range.Range(0, 255), np.uint8),
        'normalized': (ezcoach.range.Range(0., 1.), np.float)
    }

    @classmethod
    def from_json(cls, json):
        """
        Creates an instance of the class based on the JSON-like dictionary if the JSON represents the class.
        Instead of providing the JSON with range attribute, the channel_range attribute can be used with values
        defined in DEFINED_RANGES.
        Raises the ValueError if provided JSON is not representing the class.

        :param json: a JSON-like dictionary
        :return: an instance of the class
        """
        if json['type'] != cls.__name__:
            raise ValueError('Type not recognised')

        width = json['width']
        height = json['height']
        channels = json['channels']
        description = json['description']

        if 'channel_range' in json and json['channel_range'] is not None:
            channel_range = PixelList.DEFINED_RANGES[json['channel_range']]
            range, data_type = channel_range
        else:
            range = ezcoach.range.from_json(json['range'])
            data_type = np.float

        return cls(width, height, channels, range, data_type, description)

    def __init__(self, width: int, height: int, channels: int, range: ezcoach.range.Range, data_type, description: str):
        """
        Initializes the object with a size of the image (width and height), a number of channels, a range
        of each value, numpy data type and a textual description.

        :param width: a width of the image
        :param height: a height of the image
        :param channels: a number of channels
        :param range: a range of value of each channel of each pixel
        :param data_type: a type of numpy array
        :param description: a textual description
        """
        super(PixelList, self).__init__()
        self._width = width
        self._height = height
        self._channels = channels
        self._range = range
        self._data_type = data_type
        self._description = description

    def contains(self, value) -> bool:
        return all(self._channel_range.contains(v) for v in value)

    def normalize(self, value):
        return self._range.normalize(value)

    def random(self, n=None, normalize=False):
        if n is None:
            size = (self._height, self._width, self._channels)
        else:
            size = (n, self._height, self._width, self._channels)

        result = self._range.random(size)
        return self.normalize(result) if normalize else result

    @property
    def ranges(self) -> typing.List[ezcoach.range.Range]:
        return [self._range]

    @property
    def description(self) -> str:
        return self._description

    def __iter__(self) -> Iterator:
        return (self._channel_range for __ in range(len(self)))

    def __len__(self) -> int:
        return self._width * self._height * self._channels

    def parse(self, raw_values):
        values = np.array(raw_values, dtype=self._data_type)
        values = values.reshape((values.shape[0], self._height, self._width, self._channels))
        return values

    def to_json(self):
        json_dict = {'type': f'{self.__class__.__name__}',
                     'width': self._width,
                     'height': self._height,
                     'channels': self._channels,
                     'description': self._description,
                     'range': self._range}
        return json_dict


def from_json(json):
    """
    Parses the JSON-like dictionary and creates a value definition. Checks the classes marked with
    the @value_definition class annotation.
    If no corresponding value class exist ValueError will be raised.

    :param json: a JSON-like dictionary
    :return: an object of the class inheriting from BaseValue
    """
    if json['type'] not in _values_classes_names:
        raise ValueError(f'Type {json["type"]} not recognised')

    cls = _values_classes[_values_classes_names.index(json['type'])]
    return cls.from_json(json)
