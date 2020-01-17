"""
Adapter module contains various adapters that can be used to change state, action or reward to a desired form.
"""
from typing import Iterable, Union, Callable
import numpy as np

import ezcoach.value as val


def adapt_object(obj, adapters: Union[Callable, Iterable]):
    """
    Applies adapter or adapters to an object. An object is usually a state or a reward.
    Parameter adapters can be a function or an iterable. If adapters are None the original object is returned.

    :param obj: an object to be adapted
    :param adapters: adapters as a single callable or an iterable of callables
    :return: an object transformed by applying the adapters
    """
    if adapters is None:
        return obj

    if isinstance(adapters, Iterable):
        for adapter in adapters:
            obj = adapter(obj)
    else:
        obj = adapters(obj)

    return obj


def round_adapter(obj, precisions=None):
    """
    Rounds the object elementwise. The object must be a numpy array or a compatible type
    and typically represent a state. Precisions may be provided as a single value
    or as an array of values with the same shape as the state.

    :param obj: a numpy array (or compatible type) typically representing a state
    :param precisions: single value or an array of values used as a precision for rounding
    :return: object rounded elementwise
    """
    if precisions is None:
        return np.round(obj)

    precisions = np.array(precisions)
    return np.round(obj / precisions) * precisions


def round_to_int(obj):
    """
    Rounds the object and casts it to a numpy int array.

    :param obj: a numpy array (or compatible) typically representing a state
    :return: rounded object cased to a numpy int array
    """
    return np.round(obj).astype(np.int)


def normalize_adapter(definition: val.BaseValue):
    """
    Returns the adapter that normalizes the object according to a state definition (obtained from the Manifest class).

    :param definition: a BaseValue class representing the definition of the object
    :return: adapter normalizing objects
    """
    def normalize_internal(obj):
        return definition.normalize(obj)
    return normalize_internal


def tuple_adapter(obj):
    """
    Flattens an object and casts it to a tuple.

    :param obj: a numpy array
    :return: an object flattened and casted to a tuple
    """
    return tuple(obj.flatten())


def squish_channels(image):
    """
    Averages the channels of an image. Assumes that channels are represented as the last dimension of an array.
    Removes the last dimension.

    :param image: a numpy array representing the image
    :return: image with no channels
    """
    if image.dtype.kind == 'i' or image.dtype.kind == 'u':  # integers and signed integers
        return np.sum(image, axis=-1, dtype=image.dtype) // image.shape[-1]
    else:
        return np.sum(image, axis=-1, dtype=image.dtype) / image.shape[-1]


def selection_adapter(indices):
    """
    Returns the adapter tht selects elements of an object based on indices parameter.

    :param indices: indices used to select elements
    :return: adapter which selects specified elements of a object
    """
    def select_internal(obj):
        return obj[..., indices]

    return select_internal


def add_value(obj, value):
    """
    Adds a value to an object.

    :param obj: an original object
    :param value: a value to be added
    :return: the object with the value added
    """
    return obj + value
